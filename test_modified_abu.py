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
        
        print('✅ ABU框架核心模块导入成功')
        
        # 尝试设置数据源
        ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
        print(f'✅ 已将ABU数据源设置为: {ABuEnv.g_market_source}')
        
        # 尝试使用ABuSymbolPd获取数据
        print('\n=== 尝试使用ABuSymbolPd.make_kl_df获取数据 ===')
        try:
            # 使用较小的n_folds值，只获取最新的一条数据
            kl_df = ABuSymbolPd.make_kl_df('sh600000', n_folds=1)
            print(f'调用make_kl_df返回: {kl_df}')
            
            if kl_df is not None:
                print(f'返回数据类型: {type(kl_df)}')
                print(f'数据是否为空: {kl_df.empty}')
                
                if not kl_df.empty:
                    print(f'获取到的数据行数: {len(kl_df)}')
                    print(f'数据示例:')
                    print(kl_df.head())
                    print(f'\n数据详情:')
                    print(f'索引: {kl_df.index}')
                    print(f'列名: {kl_df.columns.tolist()}')
                    print(f'最新价格: {kl_df.iloc[-1]["close"]}')
                    print(f'今日开盘: {kl_df.iloc[-1]["open"]}')
                    print(f'今日最高: {kl_df.iloc[-1]["high"]}')
                    print(f'今日最低: {kl_df.iloc[-1]["low"]}')
                    print(f'成交量: {kl_df.iloc[-1]["volume"]}')
                else:
                    print('⚠️ 获取到的数据为空')
                    print(f'数据结构: {kl_df}')
            else:
                print('❌ 获取数据失败，返回None')
                
        except Exception as e:
            print(f'❌ ABuSymbolPd.make_kl_df失败: {e}')
            import traceback
            traceback.print_exc()
            
        # 尝试获取多只股票的数据
        print('\n=== 尝试获取多只股票的数据 ===')
        try:
            symbols = ['sh600000', 'sh601398', 'sz000001']
            for symbol in symbols:
                print(f'\n--- 获取股票 {symbol} 的数据 ---')
                kl_df = ABuSymbolPd.make_kl_df(symbol, n_folds=1)
                if kl_df is not None and not kl_df.empty:
                    print(f'✅ 成功获取 {symbol} 的数据')
                    print(f'最新价格: {kl_df.iloc[-1]["close"]}')
                    print(f'成交量: {kl_df.iloc[-1]["volume"]}')
                else:
                    print(f'❌ 获取 {symbol} 的数据失败')
                    
        except Exception as e:
            print(f'❌ 获取多只股票数据失败: {e}')
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
