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
        from abupy.CoreBu.ABuEnv import EMarketSourceType
        from abupy.CoreBu import ABuEnv
        from abupy.MarketBu import ABuDataFeed
        
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
            from abupy.Symbol import Symbol
            from abupy.CoreBu.ABuEnv import EMarketTargetType
            
            # 创建一个Symbol对象
            symbol_obj = Symbol('sh600000', EMarketTargetType.E_MARKET_TARGET_CN)
            print(f'创建Symbol对象成功: {symbol_obj}')
            
            # 创建TXApi实例
            tx_api = ABuDataFeed.TXApi(symbol_obj)
            print(f'创建TXApi实例成功')
            
            # 手动调用kline方法，查看URL和返回数据
            import inspect
            kline_method = inspect.getsource(tx_api.kline)
            print(f'\nkline方法源码:')
            print(kline_method[:500] + '...')  # 只显示前500个字符
            
            # 尝试获取原始API数据
            print('\n=== 尝试使用ABU的TXApi获取数据 ===')
            try:
                # 手动构造URL，简化参数
                from abupy.UtilBu import ABuStrUtil, ABuMd5
                cuid = ABuStrUtil.create_random_with_num_low(40)
                cuid_md5 = ABuMd5.md5_from_binary(cuid)
                random_suffix = ABuStrUtil.create_random_with_num(5)
                
                # 使用简化的URL，类似直接测试时的URL
                simple_tx_url = f'http://qt.gtimg.cn/q=sh600000'
                print(f'使用简化URL: {simple_tx_url}')
                
                response = requests.get(simple_tx_url, timeout=5)
                response.raise_for_status()
                print(f'✅ 简化URL请求成功，状态码: {response.status_code}')
                print(f'返回数据: {response.text}')
                
            except Exception as e:
                print(f'❌ 简化URL请求失败: {e}')
                import traceback
                traceback.print_exc()
                
        except Exception as e:
            print(f'❌ 测试TXApi URL失败: {e}')
            import traceback
            traceback.print_exc()
            
        # 尝试使用ABuSymbolPd获取数据，但添加详细日志
        print('\n=== 尝试使用ABuSymbolPd获取数据 ===')
        try:
            # 使用较小的n_folds值，避免请求过多数据
            kl_df = ABuSymbolPd.make_kl_df('sh600000', n_folds=1, start='2023-01-01', end='2023-01-10')
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
                
        except Exception as e:
            print(f'❌ ABuSymbolPd.make_kl_df失败: {e}')
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f'❌ ABU框架核心模块导入失败: {e}')
        import traceback
        traceback.print_exc()
        
except Exception as e:
    print(f'❌ ABU框架导入失败: {e}')
    import traceback
    traceback.print_exc()
