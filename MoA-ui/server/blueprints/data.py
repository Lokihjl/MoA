# 数据下载相关蓝图
from flask import request, jsonify, current_app
import json
import threading
from datetime import datetime
from . import moA_bp
from models import DataDownloadRecord, KlineData, StockBasic, db

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
            from ..models import db, KlineData, StockBasic
            import requests
            
            # 确保股票名称已存储到数据库
            existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
            if not existing_stock:
                try:
                    # 从新浪财经API获取股票名称
                    if symbol.startswith('sh'):
                        market_code = 'sh'
                        stock_code = symbol[2:]
                    elif symbol.startswith('sz'):
                        market_code = 'sz'
                        stock_code = symbol[2:]
                    else:
                        market_code = market
                        stock_code = symbol
                    
                    # 构造新浪财经股票信息API URL
                    stock_info_url = f'http://hq.sinajs.cn/list={market_code}{stock_code}'
                    response = requests.get(stock_info_url, timeout=10)
                    response.raise_for_status()
                    
                    # 解析新浪财经返回的股票信息
                    stock_info = response.text
                    stock_info = stock_info.split('"')[1]
                    stock_name = stock_info.split(',')[0]
                    
                    # 创建新的股票基本信息记录
                    stock_basic = StockBasic(
                        symbol=symbol,
                        name=stock_name,
                        market=market_code
                    )
                    db.session.add(stock_basic)
                    db.session.commit()
                    print(f'从新浪财经API获取并存储了股票{symbol}的名称: {stock_name}')
                except Exception as e:
                    print(f'从新浪财经API获取股票{symbol}的名称时出错: {e}')
                    try:
                        # 尝试从ABuSymbolStock.df获取股票名称
                        from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN
                        abu_symbol_cn = AbuSymbolCN()
                        
                        # 解析股票代码，去掉市场前缀
                        stock_code = symbol[2:] if symbol.startswith('sh') or symbol.startswith('sz') else symbol
                        
                        stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == stock_code]
                        if not stock_info.empty:
                            # 使用'co_name'列获取股票名称
                            stock_name = stock_info.iloc[0]['co_name']
                            
                            # 创建新的股票基本信息记录
                            stock_basic = StockBasic(
                                symbol=symbol,
                                name=stock_name,
                                market=market
                            )
                            db.session.add(stock_basic)
                            db.session.commit()
                            print(f'从ABuSymbolStock.df获取并存储了股票{symbol}的名称: {stock_name}')
                    except Exception as e2:
                        print(f'从ABuSymbolStock.df获取股票{symbol}的名称时出错: {e2}')
            
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
                    date_obj = None
                    
                    # 新浪财经API返回的DataFrame中，index是Timestamp类型
                    if hasattr(index, 'date'):
                        # 如果index是Timestamp类型，直接获取date属性
                        date_obj = index.date()
                    elif 'date' in row:
                        # 兼容其他数据源的date字段
                        date_str = str(row['date'])
                        if '-' in date_str:
                            # 格式：2025-12-20
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        else:
                            # 格式：20251220
                            date_obj = datetime.strptime(date_str, '%Y%m%d').date()
                    elif 'day' in row:
                        # 兼容原始API返回的day字段
                        date_str = str(row['day'])
                        if '-' in date_str:
                            # 格式：2025-12-20
                            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        else:
                            # 格式：20251220
                            date_obj = datetime.strptime(date_str, '%Y%m%d').date()
                    
                    if not date_obj:
                        print(f"无法获取日期: {row}")
                        continue
                    
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
                        amount=float(row['amount']) if row.get('amount') is not None and row.get('amount') != '' else None,
                        adjust=float(row['adjust']) if row.get('adjust') is not None and row.get('adjust') != '' else None,
                        atr21=float(row['atr21']) if 'atr21' in row and row['atr21'] is not None else None
                    )
                    new_records.append(kline_record)
                except Exception as e:
                    print(f"处理{symbol}的K线数据时出错: {e}")
                    print(f"出错行数据: {row}")
                    import traceback
                    traceback.print_exc()
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
        
        # 获取A股股票列表
        def get_a_share_stocks():
            """
            获取全A股股票列表
            :return: A股股票代码列表，格式如['sh600000', 'sz000001', ...]
            """
            try:
                # 优先使用ABU框架中的AbuSymbolCN获取股票列表
                try:
                    from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN
                    print('尝试使用ABU框架获取A股股票列表...')
                    abu_symbol_cn = AbuSymbolCN()
                    all_symbols = abu_symbol_cn.all_symbol()
                    print(f'从ABU框架获取到{len(all_symbols)}只A股股票')
                    
                    # 从ABU框架获取股票名称并存储到数据库
                    print('从ABU框架获取股票名称并存储到数据库...')
                    for idx, symbol in enumerate(all_symbols):
                        try:
                            # 解析股票代码，去掉市场前缀
                            if symbol.startswith('sh'):
                                pure_symbol = symbol[2:]
                                market = 'sh'
                            elif symbol.startswith('sz'):
                                pure_symbol = symbol[2:]
                                market = 'sz'
                            else:
                                continue
                            
                            # 从abu_symbol_cn.df中获取股票名称
                            stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == pure_symbol]
                            if not stock_info.empty:
                                stock_name = stock_info.iloc[0]['name']
                                # 检查数据库中是否已存在该股票信息
                                existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                if not existing_stock:
                                    # 创建新的股票基本信息记录
                                    stock_basic = StockBasic(
                                        symbol=symbol,
                                        name=stock_name,
                                        market=market
                                    )
                                    db.session.add(stock_basic)
                                else:
                                    # 更新现有股票信息
                                    existing_stock.name = stock_name
                                    existing_stock.market = market
                                
                                # 每100条提交一次
                                if (idx + 1) % 100 == 0:
                                    db.session.commit()
                        except Exception as e:
                            print(f'处理股票{symbol}的基本信息时出错: {e}')
                            continue
                    
                    # 提交剩余的记录
                    db.session.commit()
                    return all_symbols
                except Exception as abu_e:
                    print(f'使用ABU框架获取A股股票列表失败: {abu_e}')
                    print('尝试使用新浪财经API获取A股股票列表...')
                
                # ABU框架获取失败时，使用新浪财经API获取
                import requests
                import pandas as pd
                
                # 使用新浪财经获取A股股票列表（使用HTTP协议，避免SSL问题）
                # 主板A股
                sh_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=10000&sort=symbol&asc=1&node=sh_a&symbol=&_s_r_a=page'
                sz_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=10000&sort=symbol&asc=1&node=sz_a&symbol=&_s_r_a=page'
                
                stocks = []
                
                # 尝试多次请求，最多5次
                max_retries = 5
                for retry in range(max_retries):
                    try:
                        # 配置请求头，模拟浏览器访问
                        headers = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
                        }
                        
                        # 获取上海A股
                        print(f'尝试获取上海A股列表，第{retry+1}次...')
                        sh_response = requests.get(sh_url, timeout=20, headers=headers)
                        sh_response.raise_for_status()
                        sh_data = sh_response.json()
                        print(f'上海A股API返回数据长度: {len(sh_data)}')
                        
                        for stock in sh_data:
                            symbol = f'sh{stock["symbol"]}'
                            stocks.append(symbol)
                            # 存储股票名称到数据库
                            try:
                                existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                if not existing_stock:
                                    stock_basic = StockBasic(
                                        symbol=symbol,
                                        name=stock["name"],
                                        market='sh'
                                    )
                                    db.session.add(stock_basic)
                                else:
                                    existing_stock.name = stock["name"]
                                    existing_stock.market = 'sh'
                            except Exception as e:
                                print(f'存储股票{symbol}的名称到数据库时出错: {e}')
                                continue
                        
                        # 获取深圳A股
                        print(f'尝试获取深圳A股列表，第{retry+1}次...')
                        sz_response = requests.get(sz_url, timeout=20, headers=headers)
                        sz_response.raise_for_status()
                        sz_data = sz_response.json()
                        print(f'深圳A股API返回数据长度: {len(sz_data)}')
                        
                        for stock in sz_data:
                            symbol = f'sz{stock["symbol"]}'
                            stocks.append(symbol)
                            # 存储股票名称到数据库
                            try:
                                existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                if not existing_stock:
                                    stock_basic = StockBasic(
                                        symbol=symbol,
                                        name=stock["name"],
                                        market='sz'
                                    )
                                    db.session.add(stock_basic)
                                else:
                                    existing_stock.name = stock["name"]
                                    existing_stock.market = 'sz'
                            except Exception as e:
                                print(f'存储股票{symbol}的名称到数据库时出错: {e}')
                                continue
                        
                        # 提交数据库事务
                        db.session.commit()
                        break  # 成功获取数据，跳出重试循环
                    except Exception as retry_e:
                        print(f'第{retry+1}次尝试失败: {retry_e}')
                        if retry == max_retries - 1:
                            # 最后一次尝试失败，使用ABuSymbolStock中的数据
                            print('最后一次尝试失败，使用ABuSymbolStock中的数据')
                            from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN
                            abu_symbol_cn = AbuSymbolCN()
                            # 直接从abu_symbol_cn.df中获取股票代码
                            sh_stocks = abu_symbol_cn.df[abu_symbol_cn.df['exchange'] == 'SH']['symbol'].tolist()
                            sz_stocks = abu_symbol_cn.df[abu_symbol_cn.df['exchange'] == 'SZ']['symbol'].tolist()
                            all_stocks = [f'sh{code}' for code in sh_stocks] + [f'sz{code}' for code in sz_stocks]
                            print(f'从ABuSymbolStock.df获取到{len(all_stocks)}只A股股票')
                            
                            # 从ABuSymbolStock.df中获取股票名称并存储到数据库
                            print('从ABuSymbolStock.df获取股票名称并存储到数据库...')
                            for code in sh_stocks:
                                symbol = f'sh{code}'
                                stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == code]
                                if not stock_info.empty:
                                    stock_name = stock_info.iloc[0]['name']
                                    try:
                                        existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                        if not existing_stock:
                                            stock_basic = StockBasic(
                                                symbol=symbol,
                                                name=stock_name,
                                                market='sh'
                                            )
                                            db.session.add(stock_basic)
                                        else:
                                            existing_stock.name = stock_name
                                            existing_stock.market = 'sh'
                                    except Exception as e:
                                        print(f'存储股票{symbol}的名称到数据库时出错: {e}')
                                        continue
                            
                            for code in sz_stocks:
                                symbol = f'sz{code}'
                                stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == code]
                                if not stock_info.empty:
                                    stock_name = stock_info.iloc[0]['name']
                                    try:
                                        existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                        if not existing_stock:
                                            stock_basic = StockBasic(
                                                symbol=symbol,
                                                name=stock_name,
                                                market='sz'
                                            )
                                            db.session.add(stock_basic)
                                        else:
                                            existing_stock.name = stock_name
                                            existing_stock.market = 'sz'
                                    except Exception as e:
                                        print(f'存储股票{symbol}的名称到数据库时出错: {e}')
                                        continue
                            
                            # 提交数据库事务
                            db.session.commit()
                            
                            return all_stocks if all_stocks else []
                        import time
                        time.sleep(5)  # 等待5秒后重试
                
                print(f'从新浪财经API获取到A股股票数量: {len(stocks)}')
                return stocks
            except Exception as e:
                print(f'获取A股股票列表失败: {e}')
                import traceback
                traceback.print_exc()
                # 最后尝试从ABuSymbolStock.df中获取
                try:
                    from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN
                    abu_symbol_cn = AbuSymbolCN()
                    # 直接从abu_symbol_cn.df中获取股票代码
                    sh_stocks = abu_symbol_cn.df[abu_symbol_cn.df['exchange'] == 'SH']['symbol'].tolist()
                    sz_stocks = abu_symbol_cn.df[abu_symbol_cn.df['exchange'] == 'SZ']['symbol'].tolist()
                    all_stocks = [f'sh{code}' for code in sh_stocks] + [f'sz{code}' for code in sz_stocks]
                    print(f'从ABuSymbolStock.df获取到{len(all_stocks)}只A股股票')
                    
                    # 从ABuSymbolStock.df中获取股票名称并存储到数据库
                    print('从ABuSymbolStock.df获取股票名称并存储到数据库...')
                    for code in sh_stocks:
                        symbol = f'sh{code}'
                        stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == code]
                        if not stock_info.empty:
                            stock_name = stock_info.iloc[0]['name']
                            try:
                                existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                if not existing_stock:
                                    stock_basic = StockBasic(
                                        symbol=symbol,
                                        name=stock_name,
                                        market='sh'
                                    )
                                    db.session.add(stock_basic)
                                else:
                                    existing_stock.name = stock_name
                                    existing_stock.market = 'sh'
                            except Exception as e:
                                print(f'存储股票{symbol}的名称到数据库时出错: {e}')
                                continue
                    
                    for code in sz_stocks:
                        symbol = f'sz{code}'
                        stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == code]
                        if not stock_info.empty:
                            stock_name = stock_info.iloc[0]['name']
                            try:
                                existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                if not existing_stock:
                                    stock_basic = StockBasic(
                                        symbol=symbol,
                                        name=stock_name,
                                        market='sz'
                                    )
                                    db.session.add(stock_basic)
                                else:
                                    existing_stock.name = stock_name
                                    existing_stock.market = 'sz'
                            except Exception as e:
                                print(f'存储股票{symbol}的名称到数据库时出错: {e}')
                                continue
                    
                    # 提交数据库事务
                    db.session.commit()
                    
                    return all_stocks if all_stocks else []
                except Exception as final_e:
                    print(f'最后尝试获取A股股票列表失败: {final_e}')
                    # 返回空列表，让前端提示用户
                    return []
        
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
                
                # 检查新浪财经API返回数据是否为None
                if sina_data is None:
                    print(f'新浪财经API返回数据为None')
                    return None
                
                print(f'新浪财经API返回数据长度: {len(sina_data)}')
                
                if not sina_data:
                    return None
                
                # 转换为DataFrame
                kl_df = pd.DataFrame(sina_data)
                kl_df['date'] = pd.to_datetime(kl_df['day'])
                kl_df.set_index('date', inplace=True)
                
                # 转换数据类型
                numeric_cols = ['open', 'high', 'low', 'close', 'volume']
                
                # 检查是否包含成交额字段
                if 'amount' in kl_df.columns:
                    numeric_cols.append('amount')
                elif 'turnover' in kl_df.columns:
                    numeric_cols.append('turnover')
                
                kl_df[numeric_cols] = kl_df[numeric_cols].astype(float)
                
                # 重命名列，保持与ABU框架一致
                kl_df.rename(columns={'volume': 'volume', 'turnover': 'amount'}, inplace=True)
                
                # 如果没有成交额字段，添加一个默认值
                if 'amount' not in kl_df.columns:
                    kl_df['amount'] = kl_df['volume'] * kl_df['close']  # 成交额 = 成交量 * 收盘价
                
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
                    from ..models import db, DataDownloadRecord
                    
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
                    current_symbols_str = current_record.symbols
                    symbols = current_symbols_str.split(',') if current_symbols_str and current_symbols_str != 'all' else []
                    if not symbols:
                        # 如果没有指定股票，获取全A股股票列表
                        print('未指定股票，获取全A股股票列表...')
                        symbols = get_a_share_stocks()
                        print(f'获取到{len(symbols)}只A股股票')
                    else:
                        # 如果指定了股票，获取并存储这些股票的名称
                        print(f'指定了{len(symbols)}只股票，获取并存储股票名称...')
                        for symbol in symbols:
                            try:
                                # 从新浪财经API获取股票名称
                                import requests
                                import pandas as pd
                                
                                # 解析股票代码，去掉市场前缀
                                if symbol.startswith('sh'):
                                    market_code = 'sh'
                                    stock_code = symbol[2:]
                                elif symbol.startswith('sz'):
                                    market_code = 'sz'
                                    stock_code = symbol[2:]
                                else:
                                    continue
                                
                                # 构造新浪财经股票信息API URL
                                stock_info_url = f'http://hq.sinajs.cn/list={market_code}{stock_code}'
                                print(f'调用新浪财经股票信息API: {stock_info_url}')
                                
                                response = requests.get(stock_info_url, timeout=10)
                                response.raise_for_status()
                                
                                # 解析新浪财经返回的股票信息
                                stock_info = response.text
                                # 格式：var hq_str_sh600000="浦发银行,9.89,9.90,9.88,9.93,9.87,9.88,9.89,46033123,455734186,12345,9.88,12345,9.87,12345,9.86,12345,9.85,12345,9.84,12345,9.89,12345,9.90,12345,9.91,12345,9.92,12345,9.93,2025-12-22,15:00:00,00";
                                stock_info = stock_info.split('"')[1]
                                stock_name = stock_info.split(',')[0]
                                
                                # 检查数据库中是否已存在该股票信息
                                existing_stock = StockBasic.query.filter_by(symbol=symbol).first()
                                if not existing_stock:
                                    # 创建新的股票基本信息记录
                                    stock_basic = StockBasic(
                                        symbol=symbol,
                                        name=stock_name,
                                        market=market_code
                                    )
                                    db.session.add(stock_basic)
                                else:
                                    # 更新现有股票信息
                                    existing_stock.name = stock_name
                                    existing_stock.market = market_code
                            except Exception as e:
                                print(f'获取股票{symbol}的名称时出错: {e}')
                                continue
                        
                        # 提交数据库事务
                        db.session.commit()
                    
                    # 更新进度：开始数据下载
                    current_record.progress = 50
                    current_record.error_message = f'开始从新浪财经API下载{len(symbols)}只股票的数据...'
                    db.session.commit()
                    
                    # 将下载的数据保存到SQLite数据库
                    total_records = 0
                    incremental_records = 0  # 新增：统计增量更新的条数
                    total_symbols = len(symbols)
                    
                    # 调试：打印股票列表信息
                    print(f"准备处理{total_symbols}只股票：{symbols[:10]}...")
                    
                    # 统计成功获取数据的股票数量
                    success_count = 0
                    
                    # 更新下载记录的股票数量信息
                    current_record.total_symbols = total_symbols
                    db.session.commit()
                    
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
                            
                            # 获取当前记录的数据类型
                            current_data_type = current_record.data_type
                            
                            # 检查数据库中最新的日期，实现增量更新
                            latest_date = db.session.query(db.func.max(KlineData.date)).filter(
                                KlineData.symbol == symbol,
                                KlineData.market == current_record.market,
                                KlineData.data_type == current_data_type
                            ).scalar()
                            
                            # 如果有最新日期，获取该日期之后的数据，否则获取365天数据
                            if latest_date:
                                print(f"{symbol}已存在数据，最新日期为{latest_date}，执行增量更新...")
                                # 从新浪财经API获取数据
                                kl_df = get_historical_data_from_sina(symbol, datalen=365)
                                
                                if kl_df is not None and not kl_df.empty:
                                    # 确保latest_date是datetime64类型，与kl_df.index类型匹配
                                    import pandas as pd
                                    latest_date_dt = pd.to_datetime(latest_date)
                                    # 过滤出最新日期之后的数据
                                    kl_df = kl_df[kl_df.index > latest_date_dt]
                                    print(f"增量更新：过滤后有{len(kl_df)}条新数据")
                            else:
                                print(f"{symbol}不存在数据，执行首次下载...")
                                # 首次下载，获取365天数据
                                kl_df = get_historical_data_from_sina(symbol, datalen=365)
                            
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
                                
                                # 新增：判断是否是增量更新，如果是则累加增量更新的条数
                                if latest_date:
                                    incremental_records += records_saved
                                    print(f"{symbol}增量更新了{records_saved}条记录")
                                
                                success_count += 1
                                
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
                        current_record.total_downloaded = total_records
                        current_record.incremental_downloaded = incremental_records  # 新增：保存增量更新的条数
                        current_record.success_symbols = success_count
                        
                        # 根据下载结果设置不同的错误消息
                        if total_records == 0:
                            current_record.error_message = f'下载完成，但未获取到任何有效数据：共处理{total_symbols}只股票，成功{success_count}只，保存{total_records}条K线数据'
                        else:
                            current_record.error_message = f'成功完成下载任务：共处理{total_symbols}只股票，成功{success_count}只，保存{total_records}条K线数据到SQLite数据库，其中增量更新{incremental_records}条'
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
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'total_downloaded': record.total_downloaded,
                'incremental_downloaded': record.incremental_downloaded,
                'total_symbols': record.total_symbols,
                'success_symbols': record.success_symbols
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
                'created_at': record.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'total_downloaded': record.total_downloaded,
                'incremental_downloaded': record.incremental_downloaded,
                'total_symbols': record.total_symbols,
                'success_symbols': record.success_symbols
            }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取数据下载记录失败:', str(e))
        return jsonify({'error': f'获取数据下载记录失败: {str(e)}'}), 500

# 获取已下载的股票列表
@moA_bp.route('/data/download/symbols', methods=['GET'])
def get_downloaded_symbols():
    try:
        # 查询所有已下载的股票代码，去重
        symbols = db.session.query(KlineData.symbol, KlineData.market).distinct().all()
        
        # 转换为前端需要的格式
        symbols_list = []
        for symbol, market in symbols:
            # 查询股票名称
            stock_basic = StockBasic.query.filter_by(symbol=symbol).first()
            stock_name = stock_basic.name if stock_basic else ''
            symbols_list.append({
                'symbol': symbol,
                'market': market,
                'name': stock_name
            })
        
        return jsonify(symbols_list), 200
    except Exception as e:
        print('获取已下载股票列表失败:', str(e))
        return jsonify({'error': f'获取已下载股票列表失败: {str(e)}'}), 500

# 获取阻力位和支撑位数据
@moA_bp.route('/data/resistance-support', methods=['GET'])
def get_resistance_support():
    try:
        # 获取请求参数
        symbol = request.args.get('symbol', '')
        market = request.args.get('market', 'cn')
        data_type = request.args.get('data_type', 'day')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 查询K线数据
        kline_query = KlineData.query.filter_by(
            symbol=symbol,
            market=market,
            data_type=data_type
        )
        
        # 如果提供了日期范围，添加日期过滤
        if start_date:
            kline_query = kline_query.filter(KlineData.date >= start_date)
        if end_date:
            kline_query = kline_query.filter(KlineData.date <= end_date)
        
        # 按日期排序
        kline_records = kline_query.order_by(KlineData.date.asc()).all()
        
        # 转换为前端需要的格式
        kline_data = []
        for record in kline_records:
            kline_data.append({
                'date': record.date,
                'open': float(record.open),
                'high': float(record.high),
                'low': float(record.low),
                'close': float(record.close),
                'volume': record.volume,
                'amount': record.amount
            })
        
        # 计算阻力位和支撑位
        resistance_levels = []
        support_levels = []
        
        if kline_data:
            # 提取所有最高价和最低价
            all_highs = [item['high'] for item in kline_data]
            all_lows = [item['low'] for item in kline_data]
            
            # 合并所有价格点
            all_prices = all_highs + all_lows
            
            # 计算价格分布
            price_distribution = {}
            for price in all_prices:
                # 四舍五入到两位小数
                rounded_price = round(price, 2)
                if rounded_price in price_distribution:
                    price_distribution[rounded_price] += 1
                else:
                    price_distribution[rounded_price] = 1
            
            # 找出出现频率高的价格点
            sorted_prices = sorted(price_distribution.items(), key=lambda x: x[1], reverse=True)
            key_prices = [price for price, count in sorted_prices[:8]]
            
            # 计算最高价、最低价和平均价
            high_price = max(all_highs)
            low_price = min(all_lows)
            avg_price = sum(all_prices) / len(all_prices)
            
            # 添加关键价格点
            key_prices.extend([high_price, low_price, avg_price])
            
            # 去重并排序
            unique_key_prices = sorted(list(set([round(p, 2) for p in key_prices])))
            
            # 获取当前价格
            current_price = kline_data[-1]['close']
            
            # 计算阻力位和支撑位
            resistance_levels = [p for p in unique_key_prices if p > current_price][-3:]
            support_levels = [p for p in unique_key_prices if p < current_price][-3:]
            support_levels.reverse()  # 反转，使最接近当前价格的支撑位在前面
            
            # 如果阻力位或支撑位不足，使用价格百分比计算
            if len(resistance_levels) < 3:
                price_range = high_price - low_price
                for i in range(len(resistance_levels), 3):
                    resistance = current_price + (i + 1) * (price_range * 0.1)
                    resistance_levels.append(round(resistance, 2))
            
            if len(support_levels) < 3:
                price_range = high_price - low_price
                additional_supports = []
                for i in range(len(support_levels), 3):
                    support = current_price - (i + 1) * (price_range * 0.1)
                    additional_supports.append(round(support, 2))
                support_levels.extend(additional_supports)
                support_levels.reverse()
        
        # 返回结果
        return jsonify({
            'symbol': symbol,
            'market': market,
            'data_type': data_type,
            'start_date': start_date,
            'end_date': end_date,
            'kline_data': kline_data,
            'resistance_levels': resistance_levels,
            'support_levels': support_levels
        }), 200
    except Exception as e:
        print('获取阻力位支撑位数据失败:', str(e))
        return jsonify({'error': f'获取阻力位支撑位数据失败: {str(e)}'}), 500

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
        
        # 线程停止标志
        stop_event = threading.Event()
        
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
                    current_record = db.session.query(DataDownloadRecord).filter_by(id=new_record.id).first()
                    if not current_record:
                        print(f"下载记录{new_record.id}不存在")
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
                    symbols = record.symbols.split(',') if record.symbols != 'all' else []
                    if not symbols:
                        # 如果没有指定股票，获取全A股股票列表
                        print('未指定股票，获取全A股股票列表...')
                        symbols = get_a_share_stocks()
                        print(f'获取到{len(symbols)}只A股股票')
                    
                    # 更新进度：开始数据下载
                    current_record.progress = 50
                    current_record.error_message = f'开始从新浪财经API下载{len(symbols)}只股票的数据...'
                    db.session.commit()
                    
                    # 将下载的数据保存到SQLite数据库
                    total_records = 0
                    total_symbols = len(symbols)
                    
                    # 调试：打印股票列表信息
                    print(f"准备处理{total_symbols}只股票：{symbols[:10]}...")
                    
                    # 统计成功获取数据的股票数量
                    success_count = 0
                    
                    # 更新下载记录的股票数量信息
                    current_record.total_symbols = total_symbols
                    db.session.commit()
                    
                    for index, symbol in enumerate(symbols):
                        try:
                            # 重新获取会话，确保会话有效
                            current_record = db.session.query(DataDownloadRecord).filter_by(id=new_record.id).first()
                            if not current_record:
                                print(f"下载记录{new_record.id}不存在")
                                break
                            
                            # 计算当前进度
                            progress_percent = 50 + int((index / total_symbols) * 40)  # 50%到90%之间
                            current_record.progress = progress_percent
                            current_record.error_message = f'正在下载第{index+1}/{total_symbols}只股票：{symbol}...'
                            db.session.commit()
                            
                            # 直接从新浪财经API获取K线数据，获取365天数据确保增量更新
                            print(f"正在获取{symbol}的K线数据...")
                            kl_df = get_historical_data_from_sina(symbol, datalen=365)
                            
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
                                success_count += 1
                                
                                # 重新获取会话，确保会话有效
                                current_record = db.session.query(DataDownloadRecord).filter_by(id=new_record.id).first()
                                if not current_record:
                                    print(f"下载记录{new_record.id}不存在")
                                    break
                                
                                # 更新进度信息
                                current_record.error_message = f'已处理第{index+1}/{total_symbols}只股票：{symbol}，保存了{records_saved}条记录...'
                                db.session.commit()
                        except Exception as e:
                            error_msg = f'保存{symbol}数据失败: {str(e)}'
                            print(error_msg)
                            
                            # 重新获取会话，确保会话有效
                            current_record = db.session.query(DataDownloadRecord).filter_by(id=new_record.id).first()
                            if current_record:
                                current_record.error_message = error_msg
                                db.session.commit()
                            continue
                    
                    # 重新获取会话，确保会话有效
                    current_record = db.session.query(DataDownloadRecord).filter_by(id=new_record.id).first()
                    if current_record:
                        # 下载完成
                        current_record.progress = 100
                        current_record.status = 'completed'
                        current_record.end_time = datetime.utcnow()
                        current_record.total_downloaded = total_records
                        current_record.success_symbols = success_count
                        
                        # 根据下载结果设置不同的错误消息
                        if total_records == 0:
                            current_record.error_message = f'下载完成，但未获取到任何有效数据：共处理{total_symbols}只股票，成功{success_count}只，保存{total_records}条K线数据'
                        else:
                            current_record.error_message = f'成功完成下载任务：共处理{total_symbols}只股票，成功{success_count}只，保存{total_records}条K线数据到SQLite数据库'
                        db.session.commit()
                except Exception as e:
                    # 下载失败
                    error_msg = f'下载任务失败: {str(e)}'
                    print(error_msg)
                    
                    # 重新获取会话，确保会话有效
                    try:
                        current_record = db.session.query(DataDownloadRecord).filter_by(id=new_record.id).first()
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
                    if new_record.id in running_threads:
                        del running_threads[new_record.id]
        
        # 启动实际下载线程
        download_thread = threading.Thread(target=actual_download)
        download_thread.daemon = True
        download_thread.start()
        
        # 存储线程信息
        running_threads[new_record.id] = {
            'thread': download_thread,
            'stop_event': stop_event
        }
        
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
        
        # 先按日期升序查询，方便计算涨跌幅
        query = query.order_by(KlineData.date.asc())
        
        # 执行查询
        kline_data = query.all()
        
        # 按日期降序排序返回给前端
        kline_data.reverse()
        
        # 格式化结果并计算涨跌幅
        result = []
        pre_close = None
        
        # 先获取所有数据按日期升序，用于计算涨跌幅
        sorted_kline_data = sorted(kline_data, key=lambda x: x.date)
        
        # 计算涨跌幅
        for idx, data in enumerate(sorted_kline_data):
            # 对于第一条数据，前收盘价使用开盘价
            if idx == 0:
                p_change = 0.0
                pre_close = data.open
            else:
                p_change = ((data.close - pre_close) / pre_close) * 100
            
            # 存储当前收盘价作为下一条数据的前收盘价
            pre_close = data.close
            
            # 将计算好的涨跌幅保存到字典中
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
                'p_change': round(p_change, 2),  # 添加涨跌幅字段，保留两位小数
                'created_at': str(data.created_at),
                'updated_at': str(data.updated_at)
            })
        
        # 最后按日期降序返回结果
        result.reverse()
        
        return jsonify(result), 200
    except Exception as e:
        print('查询K线数据失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'查询K线数据失败: {str(e)}'}), 500

# 获取可用的股票列表
@moA_bp.route('/data/symbols', methods=['GET'])
def get_available_symbols():
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
            # 查询股票名称
            stock_basic = StockBasic.query.filter_by(symbol=symbol).first()
            stock_name = stock_basic.name if stock_basic else ''
            result.append({
                'symbol': symbol,
                'market': market,
                'name': stock_name
            })
        
        return jsonify(result), 200
    except Exception as e:
        print('获取可用股票列表失败:', str(e))
        return jsonify({'error': f'获取可用股票列表失败: {str(e)}'}), 500

# 获取股票基本信息
@moA_bp.route('/data/stock_basic', methods=['GET'])
def get_stock_basic_info():
    try:
        # 获取查询参数
        symbol = request.args.get('symbol', None)
        market = request.args.get('market', None)
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 从KlineData表中获取最新的价格数据
        query = KlineData.query.filter_by(symbol=symbol)
        if market:
            query = query.filter_by(market=market)
        latest_kline = query.order_by(KlineData.date.desc()).first()
        
        if not latest_kline:
            return jsonify({'error': '未找到该股票的数据'}), 404
        
        # 获取前一天的数据用于计算涨跌幅
        query = KlineData.query.filter_by(symbol=symbol)
        if market:
            query = query.filter_by(market=market)
        previous_kline = query.filter(KlineData.date < latest_kline.date).order_by(KlineData.date.desc()).first()
        
        # 计算涨跌幅
        change_percent = 0.0
        if previous_kline:
            change_percent = ((latest_kline.close - previous_kline.close) / previous_kline.close) * 100
        
        # 从StockBasic表中获取股票名称
        stock_basic = StockBasic.query.filter_by(symbol=symbol).first()
        stock_name = stock_basic.name if stock_basic else symbol
        
        # 格式化市场名称
        market_name_map = {
            'cn': 'A股',
            'us': '美股',
            'hk': '港股'
        }
        
        market_name = market_name_map.get(market, market)
        
        # 构建股票基本信息
        basic_info = {
            'symbol': symbol,
            'name': stock_name,
            'market': market_name,
            'currentPrice': float(latest_kline.close),
            'changePercent': round(change_percent, 2),
            'volume': float(latest_kline.volume),
            'amount': float(latest_kline.amount) if latest_kline.amount else 0.0,
            'open': float(latest_kline.open),
            'high': float(latest_kline.high),
            'low': float(latest_kline.low),
            'close': float(latest_kline.close),
            'latestDate': str(latest_kline.date)
        }
        
        return jsonify(basic_info), 200
    except Exception as e:
        print('获取股票基本信息失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取股票基本信息失败: {str(e)}'}), 500

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

# 原理查询接口
@moA_bp.route('/data/theory/query', methods=['GET'])
def query_theory():
    try:
        # 获取查询参数
        symbol = request.args.get('symbol', None)
        query = request.args.get('query', None)
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        if not symbol or not query:
            return jsonify({'error': '股票代码和查询条件不能为空'}), 400
        
        # 获取股票K线数据
        from datetime import datetime
        if start_date:
            start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            start_date_obj = None
            
        if end_date:
            end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            end_date_obj = None
            
        # 构建查询
        kline_query = KlineData.query.filter_by(
            symbol=symbol,
            market='cn',
            data_type='day'
        )
        
        if start_date_obj:
            kline_query = kline_query.filter(KlineData.date >= start_date_obj)
            
        if end_date_obj:
            kline_query = kline_query.filter(KlineData.date <= end_date_obj)
            
        kline_records = kline_query.order_by(KlineData.date.desc()).all()
        
        # 简单处理查询条件，这里可以根据实际需求扩展
        query_lower = query.lower()
        result = f"原理查询结果：\n"
        result += f"股票代码：{symbol}\n"
        result += f"查询条件：{query}\n"
        result += f"查询时间范围：{start_date} 至 {end_date}\n"
        result += f"数据条数：{len(kline_records)}\n\n"
        
        # 根据查询条件返回不同的结果
        if '均线' in query_lower or 'ma' in query_lower:
            if len(kline_records) >= 20:
                # 计算5日均线、10日均线、20日均线
                close_prices = [record.close for record in kline_records[:20]]
                ma5 = sum(close_prices[:5]) / 5 if len(close_prices) >= 5 else 0
                ma10 = sum(close_prices[:10]) / 10 if len(close_prices) >= 10 else 0
                ma20 = sum(close_prices) / 20
                
                result += "均线分析：\n"
                result += f"5日均线：{ma5:.2f}\n"
                result += f"10日均线：{ma10:.2f}\n"
                result += f"20日均线：{ma20:.2f}\n\n"
                
                # 简单的均线策略分析
                if close_prices[0] > ma5 > ma10 > ma20:
                    result += "短期均线呈多头排列，市场看涨。\n"
                elif close_prices[0] < ma5 < ma10 < ma20:
                    result += "短期均线呈空头排列，市场看跌。\n"
                else:
                    result += "均线无明显趋势，市场震荡。\n"
            else:
                result += "数据不足，无法进行均线分析。\n"
        elif '成交量' in query_lower or 'volume' in query_lower:
            if len(kline_records) >= 10:
                # 计算平均成交量
                volumes = [record.volume for record in kline_records[:10]]
                avg_volume = sum(volumes) / 10
                
                result += "成交量分析：\n"
                result += f"最新成交量：{volumes[0]:.2f}\n"
                result += f"10日平均成交量：{avg_volume:.2f}\n\n"
                
                # 简单的成交量分析
                if volumes[0] > avg_volume * 1.5:
                    result += "成交量明显放大，市场活跃度增加。\n"
                elif volumes[0] < avg_volume * 0.5:
                    result += "成交量明显萎缩，市场活跃度降低。\n"
                else:
                    result += "成交量正常，市场活跃度稳定。\n"
            else:
                result += "数据不足，无法进行成交量分析。\n"
        elif '涨跌' in query_lower or 'change' in query_lower:
            if len(kline_records) >= 2:
                # 计算涨跌幅
                current_close = kline_records[0].close
                previous_close = kline_records[1].close
                change = current_close - previous_close
                change_percent = (change / previous_close) * 100
                
                result += "涨跌分析：\n"
                result += f"当前收盘价：{current_close:.2f}\n"
                result += f"前收盘价：{previous_close:.2f}\n"
                result += f"涨跌额：{change:.2f}\n"
                result += f"涨跌幅：{change_percent:.2f}%\n\n"
                
                # 简单的涨跌分析
                if change_percent > 5:
                    result += "大幅上涨，市场情绪乐观。\n"
                elif change_percent > 0:
                    result += "小幅上涨，市场情绪平稳。\n"
                elif change_percent < -5:
                    result += "大幅下跌，市场情绪悲观。\n"
                elif change_percent < 0:
                    result += "小幅下跌，市场情绪平稳。\n"
                else:
                    result += "平盘，市场情绪稳定。\n"
        else:
            # 默认分析
            if len(kline_records) >= 1:
                latest_record = kline_records[0]
                result += "股票基本分析：\n"
                result += f"最新日期：{latest_record.date}\n"
                result += f"开盘价：{latest_record.open:.2f}\n"
                result += f"最高价：{latest_record.high:.2f}\n"
                result += f"最低价：{latest_record.low:.2f}\n"
                result += f"收盘价：{latest_record.close:.2f}\n"
                result += f"成交量：{latest_record.volume:.2f}\n"
                result += f"成交额：{latest_record.amount:.2f}\n\n"
                
                # 简单的价格分析
                if latest_record.close > latest_record.open:
                    result += "当日收阳线，买方力量较强。\n"
                elif latest_record.close < latest_record.open:
                    result += "当日收阴线，卖方力量较强。\n"
                else:
                    result += "当日收十字星，买卖双方力量均衡。\n"
            else:
                result += "数据不足，无法进行分析。\n"
        
        return jsonify(result), 200
    except Exception as e:
        print('原理查询失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'原理查询失败: {str(e)}'}), 500


