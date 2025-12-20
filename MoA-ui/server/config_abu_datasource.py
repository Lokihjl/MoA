# 配置魔A框架的数据源
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

try:
    # 导入魔A框架
    from abupy.CoreBu import ABuEnv
    from abupy.CoreBu.ABuEnv import EMarketSourceType
    
    # 打印当前数据源配置
    print('当前数据源:', ABuEnv.g_market_source)
    print('可用数据源类型:')
    for attr in dir(EMarketSourceType):
        if not attr.startswith('_'):
            print(f'  - {attr}')
    
    # 设置数据源为腾讯财经
    print('\n正在将数据源设置为腾讯财经...')
    ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
    print('新的数据源:', ABuEnv.g_market_source)
    
    # 测试使用新数据源获取股票数据
    print('\n测试使用腾讯财经数据源获取股票数据...')
    from abupy import ABuSymbolPd
    kl_df = ABuSymbolPd.make_kl_df('000001', n_folds=1)
    if kl_df is not None and not kl_df.empty:
        print('✅ 成功获取股票数据！')
        print('数据形状:', kl_df.shape)
        print('最新数据:')
        print(kl_df.tail())
    else:
        print('❌ 获取股票数据失败')
        
except Exception as e:
    print(f'发生错误: {str(e)}')
    import traceback
    traceback.print_exc()
