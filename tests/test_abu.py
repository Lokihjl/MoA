import sys
import os

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
        
        # 尝试获取股票数据（使用较小的n_folds值，避免请求过多数据）
        try:
            kl_df = ABuSymbolPd.make_kl_df('sh600000', n_folds=1, start='2023-01-01', end='2023-01-10')
            if kl_df is not None and not kl_df.empty:
                print('✅ ABU框架能够获取股票数据')
                print(f'获取到的数据行数: {len(kl_df)}')
                print(f'数据示例:')
                print(kl_df.head())
            else:
                print('⚠️ ABU框架获取到的股票数据为空')
        except Exception as e:
            print(f'❌ ABU框架获取股票数据失败: {e}')
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
