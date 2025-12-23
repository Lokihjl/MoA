import sys
import os
import logging

# 设置日志级别，方便调试
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 将项目根目录添加到Python路径
project_root = 'e:/source/abu/abu-master'
sys.path.append(project_root)

print(f'项目根目录: {project_root}')
print(f'Python版本: {sys.version}')

# 尝试导入abupy模块
try:
    import abupy
    print('✅ ABU框架导入成功')
    
    # 尝试使用ABU框架的基本功能
    try:
        from abupy import ABuSymbolPd
        from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketTargetType, EMarketSubType
        from abupy.CoreBu import ABuEnv
        from abupy.MarketBu import ABuDataFeed, ABuSymbol
        
        print('✅ ABU框架核心模块导入成功')
        
        # 尝试设置数据源
        ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
        print(f'✅ 已将ABU数据源设置为: {ABuEnv.g_market_source}')
        
        # 直接测试腾讯财经API，使用简单URL
        import requests
        print('\n=== 直接测试腾讯财经API ===')
        simple_url = 'http://qt.gtimg.cn/q=sh600000'
        response = requests.get(simple_url, timeout=5)
        response.raise_for_status()
        print(f'✅ 直接调用腾讯财经API成功，状态码: {response.status_code}')
        print(f'返回数据: {response.text}')
        
        # 解析直接调用返回的数据
        data = response.text
        if data.startswith('v_'):
            parts = data.split('=')
            if len(parts) == 2:
                stock_data = parts[1].strip('";\r\n')
                stock_fields = stock_data.split('~')
                print(f'解析出{len(stock_fields)}个字段')
                print(f'股票名称: {stock_fields[1]}')
                print(f'当前价格: {stock_fields[3]}')
                print(f'今日开盘: {stock_fields[4]}')
                print(f'昨日收盘: {stock_fields[5]}')
                print(f'今日最高: {stock_fields[31]}')
                print(f'今日最低: {stock_fields[32]}')
        
        # 查看ABU框架中腾讯财经API的URL生成
        print('\n=== 查看ABU框架腾讯财经API URL ===')
        try:
            # 创建一个Symbol对象，使用正确的导入路径
            # 创建方法1：直接使用Symbol类构造函数
            symbol_obj = ABuSymbol.Symbol(EMarketTargetType.E_MARKET_TARGET_CN, EMarketSubType.CN_A, '600000')
            print(f'创建Symbol对象成功: {symbol_obj}')
            print(f'Symbol value: {symbol_obj.value}')
            
            # 创建方法2：使用ABuSymbolPd.make_kl_df的输入格式
            print(f'\n=== 尝试使用ABuSymbolPd.make_kl_df ===')
            # 直接使用ABuSymbolPd.make_kl_df，查看内部调用流程
            kl_df = ABuSymbolPd.make_kl_df('sh600000', n_folds=1, start='2025-01-01', end='2025-01-10')
            print(f'调用make_kl_df返回: {kl_df}')
            if kl_df is not None:
                print(f'返回数据类型: {type(kl_df)}')
                print(f'数据是否为空: {kl_df.empty}')
                if not kl_df.empty:
                    print(f'获取到的数据行数: {len(kl_df)}')
                    print(f'数据示例:')
                    print(kl_df.head())
                else:
                    print('⚠️ 获取到的数据为空')
            else:
                print('❌ 获取数据失败，返回None')
                
            # 检查ABU框架中TXApi的URL生成
            print('\n=== 检查ABU框架TXApi的URL ===')
            tx_api = ABuDataFeed.TXApi(symbol_obj)
            print(f'创建TXApi实例成功')
            
            # 手动执行TXApi.kline方法的URL生成部分
            from abupy.UtilBu import ABuStrUtil, ABuMd5, ABuDateUtil
            cuid = ABuStrUtil.create_random_with_num_low(40)
            cuid_md5 = ABuMd5.md5_from_binary(cuid)
            random_suffix = ABuStrUtil.create_random_with_num(5)
            dev_mod = ABuDataFeed.random_from_list(ABuDataFeed.StockBaseMarket.K_DEV_MODE_LIST)
            os_ver = ABuDataFeed.random_from_list(ABuDataFeed.StockBaseMarket.K_OS_VERSION_LIST)
            screen = ABuDataFeed.random_from_list(ABuDataFeed.StockBaseMarket.K_PHONE_SCREEN)
            
            days = ABuEnv.g_market_trade_year * 1 + 1
            market = ''
            url = ABuDataFeed.TXApi.K_NET_BASE % (
                market, symbol_obj.value, days,
                dev_mod, cuid, cuid, cuid_md5, screen[0], screen[1], os_ver, int(random_suffix, 10))
            
            print(f'ABU框架生成的腾讯财经API URL:')
            print(url)
            
            # 尝试直接访问ABU生成的URL
            print('\n=== 尝试访问ABU生成的URL ===')
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            print(f'✅ ABU生成的URL请求成功，状态码: {response.status_code}')
            print(f'返回数据类型: {type(response.text)}')
            print(f'返回数据长度: {len(response.text)}')
            print(f'返回数据前100字符: {response.text[:100]}...')
            
            # 解析返回的JSON数据
            try:
                json_data = response.json()
                print(f'✅ 成功解析为JSON数据')
                print(f'JSON数据结构: {list(json_data.keys())}')
                
                # 检查数据中是否包含股票数据
                if 'data' in json_data and json_data['code'] == 0:
                    data = json_data['data']
                    print(f'数据中包含的键: {list(data.keys())}')
                    
                    # 检查是否包含股票代码的数据
                    if symbol_obj.value in data:
                        stock_data = data[symbol_obj.value]
                        print(f'包含{symbol_obj.value}的数据，键: {list(stock_data.keys())}')
                        
                        # 检查是否包含日K线数据
                        if 'qfqday' in stock_data:
                            kline_data = stock_data['qfqday']
                            print(f'包含qfqday数据，共{len(kline_data)}条')
                            if len(kline_data) > 0:
                                print(f'第一条数据: {kline_data[0]}')
                                print(f'最后一条数据: {kline_data[-1]}')
                        elif 'day' in stock_data:
                            kline_data = stock_data['day']
                            print(f'包含day数据，共{len(kline_data)}条')
                            if len(kline_data) > 0:
                                print(f'第一条数据: {kline_data[0]}')
                                print(f'最后一条数据: {kline_data[-1]}')
                        else:
                            print(f'❌ 不包含日K线数据')
                    else:
                        print(f'❌ 不包含{symbol_obj.value}的数据')
                else:
                    print(f'❌ 数据格式不正确，code: {json_data.get("code")}')
                    
            except ValueError as e:
                print(f'❌ 无法解析为JSON数据: {e}')
                print(f'返回数据: {response.text}')
                
        except Exception as e:
            print(f'❌ 测试TXApi URL失败: {e}')
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f'❌ ABU框架核心模块使用失败: {e}')
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f'❌ ABU框架导入失败: {e}')
    import traceback
    traceback.print_exc()
