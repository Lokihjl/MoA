import sys
import os

# 将项目根目录添加到Python路径中，以便导入abupy模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# 初始化ABU框架配置
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketDataFetchMode

# 设置数据源为腾讯财经
ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
# 设置数据获取模式为正常模式（先本地，后网络）
ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
# 设置使用SQLite缓存
ABuEnv.g_data_cache_type = ABuEnv.EDataCacheType.E_DATA_CACHE_SQLITE

# 导入ABuSymbolPd
from abupy import ABuSymbolPd

# 测试数据获取功能
def test_data_fetch(symbol):
    print(f"\n=== 测试获取 {symbol} 的数据 ===")
    
    try:
        print(f"尝试获取 {symbol} 的K线数据...")
        kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=50)
        
        if kl_pd is None:
            print(f"获取 {symbol} 数据失败: 无法获取任何数据")
            return False, 0
        elif kl_pd.shape[0] < 40:
            print(f"获取 {symbol} 数据失败: 数据量不足 ({kl_pd.shape[0]} 条)，需要至少 40 条数据")
            return False, kl_pd.shape[0]
        else:
            print(f"获取 {symbol} 数据成功: {kl_pd.shape[0]} 条数据")
            print(f"时间范围: {kl_pd.index[0].strftime('%Y-%m-%d')} 到 {kl_pd.index[-1].strftime('%Y-%m-%d')}")
            print(f"数据列: {list(kl_pd.columns)}")
            print(f"前5条数据:\n{kl_pd.head()}")
            return True, kl_pd.shape[0]
    except Exception as e:
        print(f"获取 {symbol} 数据失败: {str(e)}")
        return False, 0

# 测试多个股票
test_symbols = ['sh600519', 'sz000002', 'sz000858', 'sh601398', 'sz300750']

results = []
for symbol in test_symbols:
    success, data_size = test_data_fetch(symbol)
    results.append({
        'symbol': symbol,
        'success': success,
        'data_size': data_size
    })

# 打印测试结果
def format_result(success):
    return "✅ 成功" if success else "❌ 失败"

print("\n=== 测试结果汇总 ===")
for result in results:
    print(f"{result['symbol']}: {format_result(result['success'])}, 数据量: {result['data_size']} 条")

# 统计成功率
success_count = sum(1 for r in results if r['success'])
print(f"\n总测试数: {len(results)}, 成功数: {success_count}, 成功率: {success_count/len(results)*100:.1f}%")

print("\n=== 测试完成 ===")
