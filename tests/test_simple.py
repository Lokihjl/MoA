import sys
import os

# 将项目根目录添加到Python路径中，以便导入abupy模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# 初始化ABU框架配置
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketDataFetchMode

# 设置数据源为腾讯财经
ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
# 设置数据获取模式为强制网络模式
ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_FORCE_NET
# 设置使用SQLite缓存
ABuEnv.g_data_cache_type = ABuEnv.EDataCacheType.E_DATA_CACHE_SQLITE

# 导入ABuSymbolPd
from abupy import ABuSymbolPd

# 简单测试
def test_simple():
    print("=== 简单测试 ABuSymbolPd.make_kl_df ===")
    
    # 直接使用ABuSymbolPd.make_kl_df函数
    try:
        print("调用ABuSymbolPd.make_kl_df('sh600519')...")
        kl_pd = ABuSymbolPd.make_kl_df('sh600519', n_folds=20)
        
        if kl_pd is None:
            print("获取数据失败: 无法获取任何数据")
        elif kl_pd.shape[0] < 40:
            print(f"获取数据失败: 数据量不足 ({kl_pd.shape[0]} 条)，需要至少 40 条数据")
        else:
            print(f"获取数据成功: {kl_pd.shape[0]} 条数据")
            print(f"时间范围: {kl_pd.index[0].strftime('%Y-%m-%d')} 到 {kl_pd.index[-1].strftime('%Y-%m-%d')}")
    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        import traceback
        traceback.print_exc()

# 运行测试
if __name__ == "__main__":
    test_simple()
