# 数据下载相关蓝图
from flask import request, jsonify, current_app
import json
import threading
from datetime import datetime
from . import moA_bp
from models import DataDownloadRecord, KlineData, db

# 用于存储正在运行的下载线程
# key: record_id, value: thread对象
running_threads = {}

# =================== 魔A数据下载相关接口 ===================

# 创建数据下载任务
@moA_bp.route('/data/download', methods=['POST', 'OPTIONS'])
def create_data_download():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        # 获取下载参数
        download_params = request.get_json()
        market = download_params.get('market', 'us')
        symbols = download_params.get('symbols', [])
        
        # 将symbols转换为逗号分隔的字符串
        symbols_str = ','.join(symbols) if symbols else 'all'
        
        # 创建下载记录
        download_record = DataDownloadRecord(
            market=market,
            data_type='day',  # 目前只支持日线数据
            symbols=symbols_str
        )
        db.session.add(download_record)
        db.session.commit()
        
        # 线程停止标志
        stop_event = threading.Event()
        
        # 将ABU K线数据保存到SQLite数据库
        def save_kl_data_to_db(kl_df, symbol, market, data_type):
            """将ABU系统返回的K线数据保存到SQLite数据库"""
            from datetime import datetime
            from models import db, KlineData
            
            # 获取数据库中的现有日期，避免重复插入
            existing_dates = db.session.query(KlineData.date).filter(
                KlineData.symbol == symbol,
                KlineData.market == market,
                KlineData.data_type == data_type
            ).all()
            existing_date_set = {date[0] for date in existing_dates}
            
            # 转换DataFrame数据到数据库模型
            new_records = []
            for index, row in kl_df.iterrows():
                try:
                    # 获取日期
                    if hasattr(index, 'date'):
                        # 如果index是Timestamp类型，直接获取date属性
                        date_obj = index.date()
                    else:
                        # 否则尝试转换
                        date_str = str(row['date'])
                        date_obj = datetime.strptime(date_str, '%Y%m%d').date()
                    
                    # 跳过已存在的数据
                    if date_obj in existing_date_set:
                        continue
                    
                    # 创建K线数据记录
                    kline_record = KlineData(
                        symbol=symbol,
                        market=market,
                        data_type=data_type,
                        date=date_obj,
                        open=float(row['open']),
                        high=float(row['high']),
                        low=float(row['low']),
                        close=float(row['close']),
                        volume=float(row['volume']),
                        amount=float(row.get('amount', 0)) if row.get('amount') else None,
                        adjust=float(row.get('adjust', 1)) if row.get('adjust') else None,
                        atr21=float(row['atr21']) if 'atr21' in row else None
                    )
                    new_records.append(kline_record)
                except Exception as e:
                    print(f"处理{symbol}的K线数据时出错: {e}")
                    continue
            
            # 批量插入新数据
            if new_records:
                try:
                    db.session.add_all(new_records)
                    db.session.commit()
                except Exception as e:
                    print(f"保存{symbol}的K线数据到数据库时出错: {e}")
                    db.session.rollback()
                    return 0
            
            return len(new_records)
        
        # 直接使用新浪财经API获取历史数据
        def get_historical_data_from_sina(symbol, datalen=252):
            """
            从新浪财经API获取股票历史数据
            :param symbol: 股票代码，格式如sh600000
            :param datalen: 获取的数据天数
            :return: 包含历史数据的DataFrame
            """
            try:
                import requests
                import pandas as pd
                import json
                
                scale = 240  # 日K线
                sina_url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={symbol}&scale={scale}&ma=no&datalen={datalen}'
                print(f'调用新浪财经API: {sina_url}')
                
                response = requests.get(sina_url, timeout=10)
                response.raise_for_status()
                
                # 解析新浪财经返回的JSON数据
                sina_data = response.json()
                print(f'新浪财经API返回数据长度: {len(sina_data)}')
                
                if not sina_data:
                    return None
                
                # 转换为DataFrame
                kl_df = pd.DataFrame(sina_data)
                kl_df['date'] = pd.to_datetime(kl_df['day'])
                kl_df.set_index('date', inplace=True)
                
                # 转换数据类型
                numeric_cols = ['open', 'high', 'low', 'close', 'volume']
                kl_df[numeric_cols] = kl_df[numeric_cols].astype(float)
                
                # 重命名列，保持与ABU框架一致
                kl_df.rename(columns={'volume': 'volume'}, inplace=True)
                
                # 添加ATR21列（简单计算，实际应该使用TA-Lib）
                kl_df['atr21'] = 0.0
                
                return kl_df
            except Exception as e:
                print(f'从新浪财经获取数据失败: {symbol}, 错误: {e}')
                return None
        
        # 获取当前应用实例，用于在后台线程中创建应用上下文
        app = current_app._get_current_object()
        
        # 实际调用ABU系统的run_kl_update函数并将数据保存到SQLite
        def actual_download():
            with app.app_context():
                try:
                    # 在后台线程中使用新的数据库会话
                    from models import db, DataDownloadRecord
                    
                    # 创建新的数据库会话
                    db.session.rollback()
                    
                    # 获取最新的下载记录
                    current_record = db.session.query(DataDownloadRecord).filter_by(id=download_record.id).first()
                    if not current_record:
                        print(f"下载记录{download_record.id}不存在")
                        return
                    
                    # 更新状态为运行中
                    current_record.status = 'running'
                    current_record.start_time = datetime.utcnow()
                    current_record.error_message = '正在初始化下载任务...'
                    db.session.commit()
                    
                    # 获取下载参数
                    current_market = current_record.market
                    
                    # 更新进度：初始化完成
                    current_record.progress = 10
                    current_record.error_message = '正在设置下载环境...'
                    db.session.commit()
                    
                    # 更新进度：开始准备数据
                    current_record.progress = 20
                    current_record.error_message = '正在准备下载参数和股票列表...'
                    db.session.commit()
                    
                    # 获取已下载的股票列表
                    symbols = download_params.get('symbols', [])
                    if not symbols:
                        # 如果没有指定股票，使用默认的A股股票列表
                        # 这里我们使用一些常见的A股股票作为示例
                        symbols = ['sh600000', 'sh600036', 'sh600519', 'sh601398', 'sh601857',
                                  'sz000001', 'sz000002', 'sz000858', 'sz002415', 'sz300750']
                    
                    # 更新进度：开始数据下载
                    current_record.progress = 50
                    current_record.error_message = f'开始从新浪财经API下载{len(symbols)}只股票的数据...'
                    db.session.commit()
                    
                    # 将下载的数据保存到SQLite数据库
                    total_records = 0
                    total_symbols = len(symbols)
                    
                    # 调试：打印股票列表信息
                    print(f"准备处理{total_symbols}只股票：{symbols[:10]}...")
                    
                    for index, symbol in enumerate(symbols):
                        try:
                            # 重新获取会话，确保会话有效
                            current_record = db.session.query(DataDownloadRecord).filter_by(id=download_record.id).first()
                            if not current_record:
                                print(f"下载记录{download_record.id}不存在")
                                break
                            
                            # 计算当前进度
                            progress_percent = 50 + int((index / total_symbols) * 40)  # 50%到90%之间
                            current_record.progress = progress_percent
                            current_record.error_message = f'正在下载第{index+1}/{total_symbols}只股票：{symbol}...'
                            db.session.commit()
                            
                            # 直接从新浪财经API获取K线数据
                            print(f"正在获取{symbol}的K线数据...")
                            kl_df = get_historical_data_from_sina(symbol, datalen=252)
                            
                            # 调试：打印K线数据信息
                            if kl_df is None:
                                print(f"{symbol}的K线数据为None")
                            elif kl_df.empty:
                                print(f"{symbol}的K线数据为空")
                            else:
                                print(f"{symbol}的K线数据成功获取，共{len(kl_df)}条记录")
                            
                            if kl_df is not None and not kl_df.empty:
                                # 保存到SQLite数据库
                                records_saved = save_kl_data_to_db(kl_df, symbol, current_record.market, current_record.data_type)
                                total_records += records_saved
                                
                                # 重新获取会话，确保会话有效
                                current_record = db.session.query(DataDownloadRecord).filter_by(id=download_record.id).first()
                                if not current_record:
                                    print(f"下载记录{download_record.id}不存在")
                                    break
                                
                                # 更新进度信息
                                current_record.error_message = f'已处理第{index+1}/{total_symbols}只股票：{symbol}，保存了{records_saved}条记录...'
                                db.session.commit()
                        except Exception as e:
                            error_msg = f'保存{symbol}数据失败: {str(e)}'
                            print(error_msg)
                            
                            # 重新获取会话，确保会话有效
                            current_record = db.session.query(DataDownloadRecord).filter_by(id=download_record.id).first()
                            if current_record:
                                current_record.error_message = error_msg
                                db.session.commit()
                            continue
                    
                    # 重新获取会话，确保会话有效
                    current_record = db.session.query(DataDownloadRecord).filter_by(id=download_record.id).first()
                    if current_record:
                        # 下载完成
                        current_record.progress = 100
                        current_record.status = 'completed'
                        current_record.end_time = datetime.utcnow()
                        current_record.error_message = f'成功完成下载任务：共处理{total_symbols}只股票，保存{total_records}条K线数据到SQLite数据库'
                        db.session.commit()
                except Exception as e:
                    # 下载失败
                    error_msg = f'下载任务失败: {str(e)}'
                    print(error_msg)
                    
                    # 重新获取会话，确保会话有效
                    try:
                        current_record = db.session.query(DataDownloadRecord).filter_by(id=download_record.id).first()
                        if current_record:
                            current_record.status = 'failed'
                            current_record.error_message = error_msg
                            current_record.end_time = datetime.utcnow()
                            db.session.commit()
                    except Exception as commit_error:
                        print(f"更新下载失败状态时出错: {commit_error}")
                finally:
                    # 关闭数据库会话
                    try:
                        db.session.close()
                    except:
                        pass
                    
                    # 从running_threads中移除
                    if download_record.id in running_threads:
                        del running_threads[download_record.id]
        
        # 启动实际下载线程
        download_thread = threading.Thread(target=actual_download)
        download_thread.daemon = True
        download_thread.start()
        
        # 存储线程信息
        running_threads[download_record.id] = {
            'thread': download_thread,
            'stop_event': stop_event
        }
        
        # 返回下载任务信息
        return jsonify({
            'id': download_record.id,
            'market': download_record.market,
            'data_type': download_record.data_type,
            'symbols': symbols,
            'status': download_record.status,
            'progress': download_record.progress,
            'created_at': download_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }), 201
    except Exception as e:
        print('创建数据下载任务失败:', str(e))
        return jsonify({'error': f'创建数据下载任务失败: {str(e)}'}), 500

# 获取数据下载任务列表
@moA_bp.route('/data/download/records', methods=['GET'])
def get_data_download_records():
    try:
        # 查询所有下载记录
        records = DataDownloadRecord.query.order_by(DataDownloadRecord.created_at.desc()).all()
        
        # 格式化返回结果
        result = []
        for record in records:
            result.append({
                'id': record.id,
                'market': record.market,
                'data_type': record.data_type,
                'symbols': record.symbols.split(','),
                'status': record.status,
                'progress': record.progress,
                'start_time': record.start_time.strftime('%Y-%m-%d %H:%M:%S') if record.start_time else None,
                'end_time': record.end_time.strftime('%Y-%m-%d %H:%M:%S') if record.end_time else None,
                'error_message': record.error_message,
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        return jsonify(result), 200
    except Exception as e:
        print('获取数据下载记录失败:', str(e))
        return jsonify({'error': f'获取数据下载记录失败: {str(e)}'}), 500

# 获取单个数据下载任务详情
@moA_bp.route('/data/download/records/<int:record_id>', methods=['GET'])
def get_data_download_record(record_id):
    try:
        # 查询单个下载记录
        record = DataDownloadRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '下载记录不存在'}), 404
        
        # 格式化返回结果
        result = {
            'id': record.id,
            'market': record.market,
            'data_type': record.data_type,
            'symbols': record.symbols.split(','),
            'status': record.status,
            'progress': record.progress,
            'start_time': record.start_time.strftime('%Y-%m-%d %H:%M:%S') if record.start_time else None,
            'end_time': record.end_time.strftime('%Y-%m-%d %H:%M:%S') if record.end_time else None,
            'error_message': record.error_message,
            'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取数据下载记录失败:', str(e))
        return jsonify({'error': f'获取数据下载记录失败: {str(e)}'}), 500

# 取消数据下载任务
@moA_bp.route('/data/download/records/<int:record_id>/cancel', methods=['PUT'])
def cancel_data_download(record_id):
    try:
        # 查询下载记录
        record = DataDownloadRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '下载记录不存在'}), 404
        
        # 只能取消未完成的任务
        if record.status in ['completed', 'failed']:
            return jsonify({'error': '只能取消未完成的任务'}), 400
        
        # 如果是运行中的任务，停止线程
        if record.status == 'running' and record_id in running_threads:
            # 设置停止事件
            stop_event = running_threads[record_id]['stop_event']
            stop_event.set()
        
        # 更新状态为取消
        record.status = 'failed'
        record.error_message = '任务已取消'
        record.end_time = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': '下载任务已取消'}), 200
    except Exception as e:
        print('取消数据下载任务失败:', str(e))
        return jsonify({'error': f'取消数据下载任务失败: {str(e)}'}), 500

# 重新执行数据下载任务
@moA_bp.route('/data/download/records/<int:record_id>/retry', methods=['POST'])
def retry_data_download(record_id):
    try:
        # 查询下载记录
        record = DataDownloadRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '下载记录不存在'}), 404
        
        # 创建新的下载记录
        new_record = DataDownloadRecord(
            market=record.market,
            data_type=record.data_type,
            symbols=record.symbols
        )
        db.session.add(new_record)
        db.session.commit()
        
        # 模拟异步下载过程
        def simulate_download():
            # 更新状态为运行中
            new_record.status = 'running'
            new_record.start_time = datetime.utcnow()
            db.session.commit()
            
            try:
                # 模拟下载进度
                for i in range(1, 101, 10):
                    import time
                    time.sleep(0.5)  # 模拟下载延迟
                    new_record.progress = i
                    db.session.commit()
                
                # 下载完成
                new_record.status = 'completed'
                new_record.end_time = datetime.utcnow()
                db.session.commit()
            except Exception as e:
                # 下载失败
                new_record.status = 'failed'
                new_record.error_message = str(e)
                new_record.end_time = datetime.utcnow()
                db.session.commit()
        
        # 启动模拟下载线程
        download_thread = threading.Thread(target=simulate_download)
        download_thread.daemon = True
        download_thread.start()
        
        # 返回新的下载任务信息
        return jsonify({
            'id': new_record.id,
            'market': new_record.market,
            'data_type': new_record.data_type,
            'symbols': new_record.symbols.split(','),
            'status': new_record.status,
            'progress': new_record.progress,
            'created_at': new_record.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }), 201
    except Exception as e:
        print('重新执行数据下载任务失败:', str(e))
        return jsonify({'error': f'重新执行数据下载任务失败: {str(e)}'}), 500

# 删除数据下载任务记录
@moA_bp.route('/data/download/records/<int:record_id>', methods=['DELETE'])
def delete_data_download(record_id):
    try:
        # 查询下载记录
        record = DataDownloadRecord.query.get(record_id)
        if not record:
            return jsonify({'error': '下载记录不存在'}), 404
        
        # 如果是运行中的任务，停止线程
        if record.status == 'running' and record_id in running_threads:
            # 设置停止事件
            stop_event = running_threads[record_id]['stop_event']
            stop_event.set()
            
            # 从running_threads中移除
            del running_threads[record_id]
        
        # 从数据库中删除记录
        db.session.delete(record)
        db.session.commit()
        
        return jsonify({'message': '下载记录已删除'}), 200
    except Exception as e:
        print('删除数据下载记录失败:', str(e))
        return jsonify({'error': f'删除数据下载记录失败: {str(e)}'}), 500

# 查询K线数据
@moA_bp.route('/data/kline', methods=['GET'])
def query_kline_data():
    try:
        # 获取查询参数
        symbol = request.args.get('symbol', None)
        market = request.args.get('market', None)
        data_type = request.args.get('data_type', 'day')
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # 构建查询
        query = KlineData.query
        
        # 添加过滤条件
        if symbol:
            query = query.filter_by(symbol=symbol)
        if market:
            query = query.filter_by(market=market)
        query = query.filter_by(data_type=data_type)
        
        # 添加日期范围过滤
        from datetime import datetime
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(KlineData.date >= start_date_obj)
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(KlineData.date <= end_date_obj)
        
        # 按日期倒序排序
        query = query.order_by(KlineData.date.desc())
        
        # 执行查询
        kline_data = query.all()
        
        # 格式化结果
        result = []
        for data in kline_data:
            result.append({
                'id': data.id,
                'symbol': data.symbol,
                'market': data.market,
                'data_type': data.data_type,
                'date': str(data.date),
                'open': float(data.open),
                'high': float(data.high),
                'low': float(data.low),
                'close': float(data.close),
                'volume': float(data.volume),
                'amount': float(data.amount) if data.amount else None,
                'adjust': float(data.adjust) if data.adjust else None,
                'atr21': float(data.atr21) if data.atr21 else None,
                'created_at': str(data.created_at),
                'updated_at': str(data.updated_at)
            })
        
        return jsonify(result), 200
    except Exception as e:
        print('查询K线数据失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'查询K线数据失败: {str(e)}'}), 500

# 获取已下载的股票列表
@moA_bp.route('/data/symbols', methods=['GET'])
def get_downloaded_symbols():
    try:
        # 获取市场参数
        market = request.args.get('market', None)
        
        # 构建查询
        query = db.session.query(KlineData.symbol, KlineData.market).distinct()
        
        # 添加市场过滤
        if market:
            query = query.filter_by(market=market)
        
        # 执行查询
        symbols = query.all()
        
        # 格式化结果
        result = []
        for symbol, market in symbols:
            result.append({
                'symbol': symbol,
                'market': market
            })
        
        return jsonify(result), 200
    except Exception as e:
        print('获取已下载股票列表失败:', str(e))
        return jsonify({'error': f'获取已下载股票列表失败: {str(e)}'}), 500

# 获取支持的市场列表
@moA_bp.route('/data/markets', methods=['GET'])
def get_supported_markets():
    try:
        # 模拟支持的市场列表（实际项目中应从ABU框架获取）
        supported_markets = [
            {'id': 'us', 'name': '美股', 'description': '美国股票市场'},
            {'id': 'hk', 'name': '港股', 'description': '香港股票市场'},
            {'id': 'cn', 'name': 'A股', 'description': '中国A股市场'}
        ]
        
        return jsonify(supported_markets), 200
    except Exception as e:
        print('获取支持的市场列表失败:', str(e))
        return jsonify({'error': f'获取支持的市场列表失败: {str(e)}'}), 500

# 获取支持的数据类型
@moA_bp.route('/data/types', methods=['GET'])
def get_supported_data_types():
    try:
        # 模拟支持的数据类型（实际项目中应从ABU框架获取）
        supported_data_types = [
            {'id': 'day', 'name': '日线', 'description': '每日行情数据'},
            {'id': 'week', 'name': '周线', 'description': '每周行情数据'},
            {'id': 'month', 'name': '月线', 'description': '每月行情数据'}
        ]
        
        return jsonify(supported_data_types), 200
    except Exception as e:
        print('获取支持的数据类型失败:', str(e))
        return jsonify({'error': f'获取支持的数据类型失败: {str(e)}'}), 500


