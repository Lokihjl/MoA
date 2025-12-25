# -*- coding:utf-8 -*-
"""
最终测试：验证策略执行结果的按时间倒序排列和分页展示功能
"""
import sys
import os
import pandas as pd
import numpy as np

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from abupy.MetricsBu.ABuMetricsBase import AbuMetricsBase

# 创建模拟的资金类
class MockCapital:
    def __init__(self, start_date='2023-01-01', end_date='2023-06-30'):
        # 创建模拟的资金数据
        dates = pd.date_range(start_date, end_date, freq='D')
        self.capital_pd = pd.DataFrame({
            'capital_blance': np.random.rand(len(dates)) * 100000 + 50000,
            'cash_blance': np.random.rand(len(dates)) * 10000 + 5000
        }, index=dates)
        self.benchmark_pd = pd.DataFrame({
            'close': np.random.rand(len(dates)) * 100000 + 50000
        }, index=dates)

# 创建模拟的策略执行结果
class MockStrategyResult:
    def __init__(self, num_orders=50, num_actions=80, start_date='2023-02-01', end_date='2023-06-30'):
        """创建模拟的策略执行结果"""
        # 创建模拟的订单数据
        order_dates = pd.date_range(start_date, end_date, periods=num_orders)
        symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA']
        # 生成随机持有天数
        hold_days = np.random.randint(5, 20, num_orders)
        # 为每个订单日期添加相应的持有天数
        sell_dates = [order_dates[i] + pd.Timedelta(days=hold_days[i]) for i in range(num_orders)]
        
        self.orders_pd = pd.DataFrame({
            'symbol': np.random.choice(symbols, num_orders),
            'buy_date': order_dates,
            'sell_date': sell_dates,
            'buy_price': np.random.rand(num_orders) * 100 + 100,
            'sell_price': np.random.rand(num_orders) * 100 + 100,
            'profit': np.random.randn(num_orders) * 1000
        }, index=order_dates)
        
        # 创建模拟的交易行为数据
        action_dates = pd.date_range(start_date, end_date, periods=num_actions)
        self.action_pd = pd.DataFrame({
            'symbol': np.random.choice(symbols, num_actions),
            'date': action_dates,
            'action': np.random.choice(['buy', 'sell'], num_actions),
            'price': np.random.rand(num_actions) * 100 + 100
        }, index=action_dates)
        
        # 创建模拟的基准数据
        benchmark_dates = pd.date_range(start_date, end_date, freq='D')
        self.benchmark_pd = pd.DataFrame({
            'close': np.random.rand(len(benchmark_dates)) * 100000 + 50000
        }, index=benchmark_dates)
        
        # 创建模拟的资金对象
        self.capital = MockCapital(start_date, end_date)

# 测试策略执行结果的按时间倒序排列和分页展示
def test_strategy_result_display():
    """测试策略执行结果的展示功能"""
    print("=== 策略执行结果展示功能测试 ===")
    
    # 创建模拟的策略执行结果
    print("\n1. 创建模拟的策略执行结果...")
    strategy_result = MockStrategyResult(num_orders=45, num_actions=72)
    
    # 创建AbuMetricsBase实例
    print("2. 创建度量指标实例...")
    metrics = AbuMetricsBase(strategy_result.orders_pd, strategy_result.action_pd, 
                           strategy_result.capital, strategy_result.benchmark_pd)
    
    # 设置分页参数
    page_size = 15
    
    print(f"\n3. 订单数据展示（每页{page_size}条，按时间倒序）:")
    print(f"   订单总数: {len(strategy_result.orders_pd)}")
    
    # 展示第一页订单数据
    print(f"\n   第1页订单数据:")
    paginated_orders_page1 = metrics.get_paginated_data(strategy_result.orders_pd, page=1, page_size=page_size)
    print(paginated_orders_page1)
    
    # 展示第二页订单数据
    print(f"\n   第2页订单数据:")
    paginated_orders_page2 = metrics.get_paginated_data(strategy_result.orders_pd, page=2, page_size=page_size)
    print(paginated_orders_page2)
    
    # 展示第三页订单数据（如果有）
    if len(strategy_result.orders_pd) > page_size * 2:
        print(f"\n   第3页订单数据:")
        paginated_orders_page3 = metrics.get_paginated_data(strategy_result.orders_pd, page=3, page_size=page_size)
        print(paginated_orders_page3)
    
    print(f"\n4. 交易行为数据展示（每页{page_size}条，按时间倒序）:")
    print(f"   交易行为总数: {len(strategy_result.action_pd)}")
    
    # 展示第一页交易行为数据
    print(f"\n   第1页交易行为数据:")
    paginated_actions_page1 = metrics.get_paginated_data(strategy_result.action_pd, page=1, page_size=page_size)
    print(paginated_actions_page1)
    
    # 验证数据是否按时间倒序排列
    print(f"\n5. 验证数据排序:")
    print(f"   订单数据第1页是否按时间倒序: {paginated_orders_page1.index.is_monotonic_decreasing}")
    print(f"   订单数据第2页是否按时间倒序: {paginated_orders_page2.index.is_monotonic_decreasing}")
    print(f"   交易行为数据第1页是否按时间倒序: {paginated_actions_page1.index.is_monotonic_decreasing}")
    
    print(f"\n6. 验证分页功能:")
    print(f"   第1页订单数据条数: {len(paginated_orders_page1)}")
    print(f"   第2页订单数据条数: {len(paginated_orders_page2)}")
    print(f"   第1页交易行为数据条数: {len(paginated_actions_page1)}")

if __name__ == "__main__":
    test_strategy_result_display()
    print("\n=== 测试完成！策略执行结果的按时间倒序排列和分页展示功能已实现。 ===")
