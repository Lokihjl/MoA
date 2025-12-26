# -*- coding:utf-8 -*-
"""
测试策略执行结果按时间倒序排列和分页展示功能
"""
import sys
import os
import pandas as pd
import numpy as np

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from abupy.MetricsBu.ABuMetricsBase import AbuMetricsBase

# 创建模拟数据的测试脚本
class MockCapital:
    def __init__(self):
        # 创建模拟的资金数据
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        self.capital_pd = pd.DataFrame({
            'capital_blance': np.random.rand(100) * 100000 + 50000,
            'cash_blance': np.random.rand(100) * 10000 + 5000
        }, index=dates)
        self.benchmark_pd = pd.DataFrame({
            'close': np.random.rand(100) * 100000 + 50000
        }, index=dates)

# 创建测试数据
def create_test_data():
    """创建测试用的模拟数据"""
    # 创建模拟的订单数据（按时间正序）
    order_dates = pd.date_range('2023-02-01', periods=30, freq='3D')
    orders_pd = pd.DataFrame({
        'symbol': ['AAPL'] * 15 + ['MSFT'] * 15,
        'buy_date': order_dates,
        'sell_date': order_dates + pd.Timedelta(days=10),
        'buy_price': np.random.rand(30) * 100 + 100,
        'sell_price': np.random.rand(30) * 100 + 100,
        'profit': np.random.randn(30) * 1000
    }, index=order_dates)
    
    # 创建模拟的交易行为数据（按时间正序）
    action_dates = pd.date_range('2023-01-15', periods=40, freq='2D')
    action_pd = pd.DataFrame({
        'symbol': ['AAPL'] * 20 + ['MSFT'] * 20,
        'date': action_dates,
        'action': ['buy', 'sell'] * 20,
        'price': np.random.rand(40) * 100 + 100
    }, index=action_dates)
    
    # 创建模拟的基准数据
    benchmark_dates = pd.date_range('2023-01-01', periods=100, freq='D')
    benchmark_pd = pd.DataFrame({
        'close': np.random.rand(100) * 100000 + 50000
    }, index=benchmark_dates)
    
    return orders_pd, action_pd, benchmark_pd

def test_pagination_and_reverse():
    """测试分页功能和按时间倒序排列"""
    print("=== 测试分页功能和按时间倒序排列 ===")
    
    # 创建测试数据
    orders_pd, action_pd, benchmark_pd = create_test_data()
    
    # 创建模拟的capital对象
    mock_capital = MockCapital()
    
    # 创建AbuMetricsBase实例
    metrics = AbuMetricsBase(orders_pd, action_pd, mock_capital, benchmark_pd)
    
    # 测试参数
    page_size = 10
    
    print("\n1. 原始订单数据（前10条，按时间正序）:")
    print(orders_pd.head(10))
    
    print("\n2. 分页后的数据（第一页，按时间倒序）:")
    paginated_orders = metrics.get_paginated_data(orders_pd, page=1, page_size=page_size)
    print(paginated_orders)
    
    print("\n3. 分页后的数据（第二页，按时间倒序）:")
    paginated_orders_page2 = metrics.get_paginated_data(orders_pd, page=2, page_size=page_size)
    print(paginated_orders_page2)
    
    print("\n4. 原始交易行为数据（前10条，按时间正序）:")
    print(action_pd.head(10))
    
    print("\n5. 分页后的交易行为数据（第一页，按时间倒序）:")
    paginated_actions = metrics.get_paginated_data(action_pd, page=1, page_size=page_size)
    print(paginated_actions)
    
    print("\n6. 测试关闭倒序排列:")
    paginated_orders_no_reverse = metrics.get_paginated_data(orders_pd, page=1, page_size=page_size, reverse=False)
    print(paginated_orders_no_reverse)
    
    # 验证数据是否按时间倒序排列
    print("\n7. 验证数据排序:")
    print("订单数据分页后是否按时间倒序:", paginated_orders.index.is_monotonic_decreasing)
    print("交易行为数据分页后是否按时间倒序:", paginated_actions.index.is_monotonic_decreasing)
    print("关闭倒序后是否按时间正序:", paginated_orders_no_reverse.index.is_monotonic_increasing)

if __name__ == "__main__":
    test_pagination_and_reverse()
