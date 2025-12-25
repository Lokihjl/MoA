# -*- coding:utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import logging
from abupy.CoreBu.ABu import ABuEnv

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入AbuMetricsBase类
from abupy.MetricsBu.ABuMetricsBase import AbuMetricsBase

# 创建模拟数据
def create_mock_data():
    """创建模拟的策略执行结果数据"""
    # 创建模拟的资金数据
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    capital = np.random.rand(100) * 100000 + 50000
    benchmark = np.random.rand(100) * 100000 + 50000
    
    capital_pd = pd.DataFrame({
        'capital_blance': capital,  # 修改为AbuMetricsBase期望的列名
        'benchmark': benchmark,
        'return': np.random.randn(100) * 0.01,
        'benchmark_return': np.random.randn(100) * 0.01
    }, index=dates)
    
    # 创建模拟的订单数据
    order_dates = pd.date_range('2023-02-01', periods=30, freq='3D')
    orders_pd = pd.DataFrame({
        'symbol': ['AAPL'] * 15 + ['MSFT'] * 15,
        'buy_date': order_dates,
        'sell_date': order_dates + pd.Timedelta(days=10),
        'buy_price': np.random.rand(30) * 100 + 100,
        'sell_price': np.random.rand(30) * 100 + 100,
        'profit': np.random.randn(30) * 1000
    }, index=order_dates)
    
    # 创建模拟的交易行为数据
    action_dates = pd.date_range('2023-01-15', periods=40, freq='2D')
    action_pd = pd.DataFrame({
        'symbol': ['AAPL'] * 20 + ['MSFT'] * 20,
        'date': action_dates,
        'action': ['buy', 'sell'] * 20,
        'price': np.random.rand(40) * 100 + 100
    }, index=action_dates)
    
    return capital_pd, benchmark, orders_pd, action_pd

# 创建一个简单的类来模拟AbuResultTuple
class MockAbuResultTuple:
    def __init__(self, capital_pd, benchmark_pd, orders_pd, action_pd):
        self.capital = MockCapital(capital_pd, benchmark_pd)
        self.orders_pd = orders_pd
        self.action_pd = action_pd
        self.benchmark = pd.DataFrame({'close': benchmark_pd}, index=capital_pd.index)

class MockCapital:
    def __init__(self, capital_pd, benchmark_pd):
        self.capital_pd = capital_pd
        self.benchmark_pd = pd.DataFrame({'close': benchmark_pd}, index=capital_pd.index)
        self.cash_blance = capital_pd['capital_blance'] * 0.1  # 模拟现金余额

# 主测试函数
def main():
    print("正在创建模拟数据...")
    
    # 创建模拟数据
    capital_pd, benchmark, orders_pd, action_pd = create_mock_data()
    
    # 创建AbuMetricsBase实例
    mock_capital = MockCapital(capital_pd, benchmark)
    metrics = AbuMetricsBase(orders_pd, action_pd, mock_capital, 
                           pd.DataFrame({'close': benchmark}, index=capital_pd.index))
    
    # 创建模拟的abu_result_tuple
    abu_result_tuple = MockAbuResultTuple(capital_pd, benchmark, orders_pd, action_pd)
    
    # 检查数据是否按时间倒序排列
    print("\n=== 检查数据是否按时间倒序排列 ===")
    
    # 检查基准数据
    benchmark_index = capital_pd.index
    print("基准数据索引排序情况:")
    print(benchmark_index.is_monotonic_decreasing)
    print(benchmark_index)
    
    # 检查资金数据
    capital_index = capital_pd.index
    print("\n资金数据索引排序情况:")
    print(capital_index.is_monotonic_decreasing)
    print(capital_index)
    
    # 检查订单数据
    orders_index = orders_pd.index
    print("\n订单数据索引排序情况:")
    print(orders_index.is_monotonic_decreasing)
    print(orders_index)
    
    # 检查交易行为数据
    action_index = action_pd.index
    print("\n交易行为数据索引排序情况:")
    print(action_index.is_monotonic_decreasing)
    print(action_index)
    
    # 测试分页功能
    print("\n=== 测试分页功能 ===")
    
    # 测试get_paginated_data方法
    page_size = 10
    
    # 测试第一页
    print("\n测试订单数据分页功能:")
    paginated_data_page1 = metrics.get_paginated_data(orders_pd, page=1, page_size=page_size)
    print(f"第一页数据（共{page_size}条）:")
    print(paginated_data_page1)
    
    # 测试第二页
    if len(orders_pd) > page_size:
        paginated_data_page2 = metrics.get_paginated_data(orders_pd, page=2, page_size=page_size)
        print(f"\n第二页数据（共{page_size}条）:")
        print(paginated_data_page2)
    
    # 测试第三页（如果有）
    if len(orders_pd) > page_size * 2:
        paginated_data_page3 = metrics.get_paginated_data(orders_pd, page=3, page_size=page_size)
        print(f"\n第三页数据（共{page_size}条）:")
        print(paginated_data_page3)
    
    # 测试交易行为数据分页
    print("\n测试交易行为数据分页功能:")
    paginated_actions_page1 = metrics.get_paginated_data(action_pd, page=1, page_size=page_size)
    print(f"第一页数据（共{page_size}条）:")
    print(paginated_actions_page1)
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    main()