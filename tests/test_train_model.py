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

# 导入MLStrategyService
from MoA-ui.server.blueprints.ml_strategy import MLStrategyService

# 初始化服务
ml_strategy_service = MLStrategyService()

# 测试数据获取功能
def test_data_fetch(symbol):
    print(f"\n=== 测试获取 {symbol} 的数据 ===")
    
    # 尝试创建一个临时模型用于测试
    model_id = ml_strategy_service.create_model('random_forest', 'clf', f'test_{symbol}')
    print(f"创建测试模型: {model_id}")
    
    # 测试训练模型
    success, message, train_info = ml_strategy_service.train_model(model_id, symbol, lookback_days=20)
    print(f"\n训练结果: {'成功' if success else '失败'}")
    print(f"消息: {message}")
    
    # 打印训练步骤
    print("\n训练步骤:")
    for step in train_info['steps']:
        print(f"[{step['timestamp']}] {step['step']}: {step['message']}")
    
    # 打印训练时间
    print(f"\n训练时间: {train_info['start_time']} 到 {train_info['end_time']}")
    print(f"总耗时: {train_info['total_time']}")
    
    # 删除测试模型
    ml_strategy_service.delete_model(model_id)
    print(f"\n删除测试模型: {model_id}")

# 测试多个股票
test_symbols = ['sh600519', 'sz000002', 'sz000858', 'sh601398', 'sz300750']

for symbol in test_symbols:
    test_data_fetch(symbol)

print("\n=== 测试完成 ===")
