# 股票数据相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 腾讯财经API测试函数已移除，使用直接API调用

# =================== 魔A股票数据相关接口 ===================

# 获取股票基本信息
@moA_bp.route('/stock/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    try:
        # 尝试使用魔A量化框架获取真实数据
        try:
            # 导入魔A量化框架的股票数据函数
            from abupy import ABuSymbolPd
            from abupy.CoreBu.ABuEnv import EMarketSourceType
            from abupy.CoreBu import ABuEnv
            import requests
            
            # 设置数据源为腾讯财经
            ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
            print(f'已将魔A数据源设置为: {ABuEnv.g_market_source}')
            
            # 使用魔A框架获取股票K线数据
            kl_df = ABuSymbolPd.make_kl_df(symbol, n_folds=1)
            
            print(f'使用魔A获取数据结果: kl_df={kl_df}, empty={kl_df.empty if kl_df is not None else True}')
            
            # 直接调用腾讯财经API获取真实股票名称
            stock_name = symbol
            try:
                simple_url = f'http://qt.gtimg.cn/q={symbol}'
                response = requests.get(simple_url, timeout=5)
                response.raise_for_status()
                text_data = response.text
                if text_data.startswith('v_'):
                    parts = text_data.split('=')
                    if len(parts) == 2:
                        stock_data = parts[1].strip('";\r\n')
                        stock_fields = stock_data.split('~')
                        if len(stock_fields) >= 2:
                            stock_name = stock_fields[1]
            except Exception as e:
                print(f'获取股票名称失败: {e}')
            
            if kl_df is not None and not kl_df.empty:
                # 从K线数据中提取最新的股票信息
                latest_data = kl_df.iloc[-1]
                
                # 计算涨跌幅
                prev_close = kl_df.iloc[-2]['close'] if len(kl_df) > 1 else latest_data['close']
                change = latest_data['close'] - prev_close
                changePercent = (change / prev_close) * 100
                
                # 构造股票信息响应
                stock_info = {
                    'symbol': symbol,
                    'name': stock_name,  # 使用从腾讯财经API获取的真实股票名称
                    'price': float(latest_data['close']),
                    'change': float(change),
                    'changePercent': float(changePercent),
                    'volume': float(latest_data['volume']),
                    'marketCap': 0  # 暂不支持获取市值数据
                }
                
                return jsonify(stock_info), 200
        except Exception as e:
            import traceback
            if 'getaddrinfo failed' in str(e) or 'Failed to resolve' in str(e):
                print('使用魔A框架获取数据失败（网络连接问题），使用模拟数据:', str(e))
            else:
                print('使用魔A框架获取数据失败，使用模拟数据:', str(e))
                traceback.print_exc()
        
        # 如果魔A框架不可用或获取数据失败，尝试直接调用腾讯财经API
        try:
            simple_url = f'http://qt.gtimg.cn/q={symbol}'
            response = requests.get(simple_url, timeout=5)
            response.raise_for_status()
            text_data = response.text
            
            if text_data.startswith('v_'):
                parts = text_data.split('=')
                if len(parts) == 2:
                    stock_data = parts[1].strip('";\r\n')
                    stock_fields = stock_data.split('~')
                    if len(stock_fields) >= 45:
                        # 提取关键信息
                        stock_name = stock_fields[1]
                        current_price = float(stock_fields[3])
                        yesterday_close = float(stock_fields[5])
                        volume = float(stock_fields[6])
                        change = current_price - yesterday_close
                        changePercent = (change / yesterday_close) * 100
                        
                        # 构造股票信息响应
                        stock_info = {
                            'symbol': symbol,
                            'name': stock_name,
                            'price': current_price,
                            'change': change,
                            'changePercent': changePercent,
                            'volume': volume,
                            'marketCap': 0  # 暂不支持获取市值数据
                        }
                        
                        return jsonify(stock_info), 200
        except Exception as e:
            print(f'直接调用腾讯财经API失败: {e}')
        
        # 如果所有方法都失败，使用模拟数据
        mock_stock_info = {
            'symbol': symbol,
            'name': f'{symbol} Company',
            'price': 150 + (hash(symbol) % 50),
            'change': (hash(symbol) % 10) - 5,
            'changePercent': ((hash(symbol) % 10) - 5) / 2,
            'volume': abs(hash(symbol) % 10000000),
            'marketCap': abs(hash(symbol) % 100000000000)
        }
        
        return jsonify(mock_stock_info), 200
    except Exception as e:
        print('获取股票信息失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取股票信息失败: {str(e)}'}), 500

# 获取股票历史数据
@moA_bp.route('/stock/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    try:
        import requests
        import json
        import datetime
        import pandas as pd
        import numpy as np
        
        # 获取查询参数
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        
        # 1. 优化ABU量化框架获取真实数据的逻辑
        try:
            # 导入ABU量化框架的股票数据函数
            from abupy import ABuSymbolPd
            from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketDataFetchMode, EDataCacheType
            from abupy.CoreBu import ABuEnv
            
            print(f'获取股票历史数据: symbol={symbol}, start_date={start_date}, end_date={end_date}')
            
            # 设置数据源为腾讯财经
            ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
            print(f'已设置数据源为: {ABuEnv.g_market_source}')
            
            # 设置数据获取模式为正常模式，尝试从本地获取，如果没有则从网络获取
            ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
            print(f'已设置数据获取模式为: {ABuEnv.g_data_fetch_mode}')
            
            # 使用ABU框架获取股票历史K线数据，不指定start和end，使用默认的n_folds参数
            kl_df = ABuSymbolPd.make_kl_df(symbol)
            
            print(f'ABU框架返回数据: kl_df={kl_df}, shape={kl_df.shape if kl_df is not None else "None"}')
            
            if kl_df is not None and not kl_df.empty:
                # 根据start_date和end_date过滤数据
                if start_date is not None:
                    kl_df = kl_df[kl_df.index >= pd.to_datetime(start_date)]
                if end_date is not None:
                    kl_df = kl_df[kl_df.index <= pd.to_datetime(end_date)]
                
                if not kl_df.empty:
                    # 将DataFrame转换为字典格式
                    history_data = kl_df.reset_index().to_dict('records')
                    
                    # 提取开始和结束日期
                    if hasattr(kl_df.index.min(), 'date'):
                        start_date_str = str(kl_df.index.min().date())
                    else:
                        start_date_str = str(history_data[0]['date'])
                    
                    if hasattr(kl_df.index.max(), 'date'):
                        end_date_str = str(kl_df.index.max().date())
                    else:
                        end_date_str = str(history_data[-1]['date'])
                    
                    # 构造历史数据响应
                    response_data = {
                        'symbol': symbol,
                        'start_date': start_date_str,
                        'end_date': end_date_str,
                        'data': []
                    }
                    
                    # 转换数据格式，只保留需要的字段
                    for item in history_data:
                        # 处理日期字段
                        if isinstance(item['date'], pd.Timestamp):
                            date_str = item['date'].strftime('%Y-%m-%d')
                        elif isinstance(item['date'], (int, str)):
                            # 如果日期是整数或字符串，直接格式化为YYYY-MM-DD
                            date_str = str(item['date'])
                            if len(date_str) == 8:
                                # 格式化为YYYY-MM-DD
                                date_str = f'{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}'
                        else:
                            # 其他情况，直接转换为字符串
                            date_str = str(item['date'])
                        
                        response_data['data'].append({
                            'date': date_str,
                            'open': float(item['open']),
                            'high': float(item['high']),
                            'low': float(item['low']),
                            'close': float(item['close']),
                            'volume': float(item['volume'])
                        })
                    
                    print(f'成功获取真实历史数据，共{len(response_data["data"])}条记录')
                    return jsonify(response_data), 200
        except Exception as e:
            print('使用ABU框架获取数据失败:', str(e))
            import traceback
            traceback.print_exc()
        
        # 2. 如果ABU框架失败，尝试使用新浪财经API获取真实历史数据
        try:
            print('尝试使用新浪财经API获取真实历史数据')
            
            # 新浪财经API获取股票历史数据
            # 新浪财经股票历史数据API格式：http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol=sh600000&scale=240&ma=no&datalen=252
            scale = 240  # 日K线
            datalen = 252  # 获取252天的数据
            
            # 转换股票代码格式，新浪财经使用的格式是sh600000，与我们的格式一致
            sina_symbol = symbol
            
            sina_url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_symbol}&scale={scale}&ma=no&datalen={datalen}'
            print(f'调用新浪财经API: {sina_url}')
            
            response = requests.get(sina_url, timeout=10)
            response.raise_for_status()
            
            # 解析新浪财经返回的JSON数据
            sina_data = response.json()
            print(f'新浪财经API返回数据长度: {len(sina_data)}')
            
            if sina_data and len(sina_data) > 0:
                # 构造历史数据响应
                response_data = {
                    'symbol': symbol,
                    'start_date': sina_data[0]['day'],
                    'end_date': sina_data[-1]['day'],
                    'data': []
                }
                
                # 转换数据格式
                for item in sina_data:
                    response_data['data'].append({
                        'date': item['day'],
                        'open': float(item['open']),
                        'high': float(item['high']),
                        'low': float(item['low']),
                        'close': float(item['close']),
                        'volume': float(item['volume'])
                    })
                
                print(f'成功从新浪财经获取真实历史数据，共{len(response_data["data"])}条记录')
                return jsonify(response_data), 200
        except Exception as e:
            print('使用新浪财经API获取数据失败:', str(e))
            import traceback
            traceback.print_exc()
        
        # 3. 如果新浪财经API也失败，尝试使用东方财富API获取真实历史数据
        try:
            print('尝试使用东方财富API获取真实历史数据')
            
            # 东方财富API获取股票历史数据
            # 东方财富股票历史数据API格式：http://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600000&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt=101&fqt=1&beg=20200101&end=20231231
            
            # 转换股票代码格式，东方财富使用的格式是1.600000(沪市)或0.000001(深市)
            if symbol.startswith('sh'):
                secid = f'1.{symbol[2:]}'
            elif symbol.startswith('sz'):
                secid = f'0.{symbol[2:]}'
            else:
                secid = symbol
            
            klt = 101  # 日K线
            fqt = 1  # 前复权
            
            # 使用默认的日期范围
            eastmoney_url = f'http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61&klt={klt}&fqt={fqt}'
            print(f'调用东方财富API: {eastmoney_url}')
            
            response = requests.get(eastmoney_url, timeout=10)
            response.raise_for_status()
            
            # 解析东方财富返回的JSON数据
            eastmoney_data = response.json()
            print(f'东方财富API返回数据: {eastmoney_data}')
            
            if eastmoney_data['data'] and eastmoney_data['data']['klines']:
                klines = eastmoney_data['data']['klines']
                print(f'东方财富API返回K线数据长度: {len(klines)}')
                
                # 构造历史数据响应
                response_data = {
                    'symbol': symbol,
                    'start_date': '',
                    'end_date': '',
                    'data': []
                }
                
                # 转换数据格式，东方财富返回的是逗号分隔的字符串
                for kline in klines:
                    fields = kline.split(',')
                    if len(fields) >= 6:
                        response_data['data'].append({
                            'date': fields[0],
                            'open': float(fields[1]),
                            'close': float(fields[2]),
                            'high': float(fields[3]),
                            'low': float(fields[4]),
                            'volume': float(fields[5])
                        })
                
                if response_data['data']:
                    response_data['start_date'] = response_data['data'][0]['date']
                    response_data['end_date'] = response_data['data'][-1]['date']
                    
                    print(f'成功从东方财富获取真实历史数据，共{len(response_data["data"])}条记录')
                    return jsonify(response_data), 200
        except Exception as e:
            print('使用东方财富API获取数据失败:', str(e))
            import traceback
            traceback.print_exc()
        
        # 4. 如果所有真实数据获取方法都失败，返回空数据，不再生成模拟数据
        print(f'所有获取真实历史数据的方法都失败了，返回空数据')
        return jsonify({'symbol': symbol, 'start_date': start_date, 'end_date': end_date, 'data': []}), 200
    except Exception as e:
        print(f'获取股票历史数据失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取股票历史数据失败: {str(e)}'}), 500

# 获取财经API数据
def get_finance_api_data(api_type, symbol):
    """
    调用不同类型的财经API获取股票数据
    :param api_type: API类型，如'tx'、'sina'、'eastmoney'
    :param symbol: 股票代码
    """
    try:
        import requests
        # 根据API类型调用不同的函数
        if api_type == 'tx':
            # 直接调用腾讯财经API
            simple_url = f'http://qt.gtimg.cn/q={symbol}'
            response = requests.get(simple_url, timeout=5)
            response.raise_for_status()
            text_data = response.text
            
            if text_data.startswith('v_'):
                parts = text_data.split('=')
                if len(parts) == 2:
                    stock_data = parts[1].strip('";\r\n')
                    stock_fields = stock_data.split('~')
                    if len(stock_fields) >= 45:
                        # 提取关键信息
                        stock_name = stock_fields[1]
                        current_price = stock_fields[3]
                        today_open = stock_fields[5]
                        yesterday_close = stock_fields[4]
                        today_high = stock_fields[33]
                        today_low = stock_fields[34]
                        volume = stock_fields[6]
                        total_amount = stock_fields[7]
                        price_change = str(float(current_price) - float(yesterday_close))
                        change_percent = str((float(price_change) / float(yesterday_close)) * 100)
                        turnover_rate = stock_fields[38] if len(stock_fields) > 38 else '0.0'
                        
                        stock_data = {
                            'stock_name': stock_name,
                            'stock_code': symbol,
                            'current_price': current_price,
                            'today_open': today_open,
                            'yesterday_close': yesterday_close,
                            'today_high': today_high,
                            'today_low': today_low,
                            'volume': volume,
                            'total_amount': total_amount,
                            'price_change': price_change,
                            'change_percent': change_percent,
                            'turnover_rate': turnover_rate,
                            'api_type': 'tx'
                        }
        elif api_type == 'sina':
            # 新浪财经API暂未实现，返回模拟数据
            stock_data = {
                'stock_name': f'{symbol}',
                'stock_code': symbol,
                'current_price': '10.00',
                'today_open': '9.90',
                'yesterday_close': '9.80',
                'today_high': '10.10',
                'today_low': '9.85',
                'volume': '1000000',
                'total_amount': '10000',
                'price_change': '0.20',
                'change_percent': '2.04',
                'turnover_rate': '0.10',
                'api_type': 'sina'
            }
        elif api_type == 'eastmoney':
            # 东方财富API暂未实现，返回模拟数据
            stock_data = {
                'stock_name': f'{symbol}',
                'stock_code': symbol,
                'current_price': '20.00',
                'today_open': '19.80',
                'yesterday_close': '19.60',
                'today_high': '20.20',
                'today_low': '19.70',
                'volume': '2000000',
                'total_amount': '40000',
                'price_change': '0.40',
                'change_percent': '2.04',
                'turnover_rate': '0.20',
                'api_type': 'eastmoney'
            }
        else:
            return jsonify({'error': f'不支持的API类型: {api_type}'}), 400
        
        if stock_data:
            return jsonify(stock_data), 200
        else:
            return jsonify({'error': f'获取{api_type}财经API数据失败'}), 500
    except Exception as e:
        print(f'调用{api_type}财经API失败:', str(e))
        return jsonify({'error': f'调用{api_type}财经API失败: {str(e)}'}), 500

@moA_bp.route('/stock/<api_type>/<symbol>', methods=['GET'])
def get_stock_data_from_api(api_type, symbol):
    """
    从不同类型的财经API获取股票数据
    :param api_type: API类型，如'tx'、'sina'、'eastmoney'
    :param symbol: 股票代码
    """
    return get_finance_api_data(api_type, symbol)
