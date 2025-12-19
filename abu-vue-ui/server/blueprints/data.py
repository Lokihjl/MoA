# 数据下载相关蓝图
from flask import request, jsonify
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
                # 转换日期格式
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
            
            # 批量插入新数据
            if new_records:
                db.session.add_all(new_records)
                db.session.commit()
            
            return len(new_records)
        
        # 实际调用ABU系统的run_kl_update函数并将数据保存到SQLite
        def actual_download():
            # 更新状态为运行中
            download_record.status = 'running'
            download_record.start_time = datetime.utcnow()
            download_record.error_message = '正在初始化下载任务...'
            db.session.commit()
            
            try:
                # 更新进度：初始化完成
                download_record.progress = 10
                download_record.error_message = '正在设置ABU环境...'
                db.session.commit()
                
                # 导入ABU系统的相关模块
                from abupy import run_kl_update, ABuSymbolPd
                from abupy.CoreBu.ABuEnv import EMarketTargetType, EMarketSourceType, EDataCacheType
                
                # 转换市场类型
                market_map = {
                    'us': EMarketTargetType.E_MARKET_TARGET_US,
                    'cn': EMarketTargetType.E_MARKET_TARGET_CN,
                    'hk': EMarketTargetType.E_MARKET_TARGET_HK,
                    'futures_cn': EMarketTargetType.E_MARKET_TARGET_FUTURES_CN,
                    'futures_global': EMarketTargetType.E_MARKET_TARGET_FUTURES_GLOBAL,
                    'tc': EMarketTargetType.E_MARKET_TARGET_TC
                }
                
                # 转换数据源类型
                source_map = {
                    'tx': EMarketSourceType.E_MARKET_SOURCE_tx,
                    'bd': EMarketSourceType.E_MARKET_SOURCE_bd,
                    'sn_us': EMarketSourceType.E_MARKET_SOURCE_sn_us,
                    'nt': EMarketSourceType.E_MARKET_SOURCE_nt
                }
                
                # 获取参数
                market = market_map.get(download_record.market, EMarketTargetType.E_MARKET_TARGET_US)
                source = source_map.get(download_params.get('dataSource', 'tx'), EMarketSourceType.E_MARKET_SOURCE_tx)
                
                # 设置ABU环境
                from abupy import ABuEnv
                ABuEnv.g_market_target = market
                ABuEnv.g_market_source = source
                
                # 调用run_kl_update函数
                start_date = download_params.get('startDate') if download_params.get('timeMode') == 'range' else None
                end_date = download_params.get('endDate') if download_params.get('timeMode') == 'range' else None
                n_folds = download_params.get('years', 2) if download_params.get('timeMode') == 'years' else 2
                
                # 更新进度：开始ABU CSV下载
                download_record.progress = 20
                download_record.error_message = '正在从ABU数据源下载CSV数据...'
                db.session.commit()
                
                # 执行实际下载
                run_kl_update(
                    n_folds=n_folds,
                    start=start_date,
                    end=end_date,
                    market=market,
                    n_jobs=10
                )
                
                # 更新进度：ABU CSV下载完成
                download_record.progress = 50
                download_record.error_message = 'ABU CSV数据下载完成，正在准备导入SQLite...'
                db.session.commit()
                
                # 获取已下载的股票列表
                symbols = download_params.get('symbols', [])
                if not symbols:
                    # 如果没有指定股票，获取市场所有股票
                    from abupy.MarketBu.ABuSymbol import all_symbol
                    symbol_list = all_symbol()
                    symbols = [sym for sym in symbol_list if sym is not None]
                
                # 更新进度：开始SQLite导入
                download_record.progress = 60
                download_record.error_message = f'开始将{len(symbols)}只股票导入SQLite...'
                db.session.commit()
                
                # 将下载的数据保存到SQLite数据库
                total_records = 0
                total_symbols = len(symbols)
                
                for index, symbol in enumerate(symbols):
                    try:
                        # 计算当前进度
                        progress_percent = 60 + int((index / total_symbols) * 30)  # 60%到90%之间
                        download_record.progress = progress_percent
                        download_record.error_message = f'正在处理第{index+1}/{total_symbols}只股票：{symbol}...'
                        db.session.commit()
                        
                        # 获取已下载的K线数据
                        kl_df = ABuSymbolPd.make_kl_df(symbol, start=start_date, end=end_date)
                        if kl_df is not None and not kl_df.empty:
                            # 保存到SQLite数据库
                            records_saved = save_kl_data_to_db(kl_df, symbol, download_record.market, download_record.data_type)
                            total_records += records_saved
                            
                            # 更新进度信息
                            download_record.error_message = f'已处理第{index+1}/{total_symbols}只股票：{symbol}，保存了{records_saved}条记录...'
                            db.session.commit()
                    except Exception as e:
                        error_msg = f'保存{symbol}数据失败: {str(e)}'
                        print(error_msg)
                        download_record.error_message = error_msg
                        db.session.commit()
                        continue
                
                # 下载完成
                download_record.progress = 100
                download_record.status = 'completed'
                download_record.end_time = datetime.utcnow()
                download_record.error_message = f'成功完成下载任务：共处理{total_symbols}只股票，保存{total_records}条K线数据到SQLite数据库'
                db.session.commit()
            except Exception as e:
                # 下载失败
                error_msg = f'下载任务失败: {str(e)}'
                download_record.status = 'failed'
                download_record.error_message = error_msg
                download_record.end_time = datetime.utcnow()
                db.session.commit()
                print(error_msg)
            finally:
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

# 云盘下载
@moA_bp.route('/data/download/cloud', methods=['POST'])
def cloud_download():
    try:
        # 导入ABU系统的云盘下载功能
        from abupy.MarketBu.ABuDataCheck import browser_down_csv_zip
        
        # 调用云盘下载功能
        browser_down_csv_zip(open_browser=False)
        
        return jsonify({'message': '云盘下载已启动'}), 200
    except Exception as e:
        print('云盘下载失败:', str(e))
        return jsonify({'error': f'云盘下载失败: {str(e)}'}), 500
