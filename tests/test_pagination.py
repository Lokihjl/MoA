# -*- coding:utf-8 -*-
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np
from abupy.CoreBu.ABu import run_loop_back
from abupy.MetricsBu.ABuMetricsBase import AbuMetricsBase

# 设置中文显示
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)

# 运行一个简单的策略
print("正在运行策略...")

try:
    # 导入必要的因子
    from abupy.FactorBuyBu.ABuFactorBuyBreak import AbuFactorBuyXDBK
    from abupy.FactorSellBu.ABuFactorAtrNStop import AbuFactorAtrNStop
    
    # 运行策略
    abu_result_tuple = run_loop_back(100000, buy_factors=[{'xd': 60, 'class': AbuFactorBuyXDBK}], 
                                   sell_factors=[{'class': AbuFactorAtrNStop}])
    
    # 创建Metrics对象
    metrics = AbuMetricsBase(abu_result_tuple.capital, abu_result_tuple.orders_pd, abu_result_tuple.action_pd, abu_result_tuple.capital.benchmark_pd)
    
    if abu_result_tuple is None or metrics is None:
        print("策略运行未返回结果，可能没有找到交易机会")
        exit()
    
    # 检查数据是否按时间倒序排列
    print("\n=== 检查数据是否按时间倒序排列 ===")
    
    # 检查基准数据
    if hasattr(abu_result_tuple.capital, 'benchmark_pd') and len(abu_result_tuple.capital.benchmark_pd) > 0:
        基准索引 = abu_result_tuple.capital.benchmark_pd.index
        print("基准数据索引排序情况:")
        print(基准索引.is_monotonic_decreasing)
        print(基准索引)
    
    # 检查资金数据
    if len(abu_result_tuple.capital.capital_pd) > 0:
        资金索引 = abu_result_tuple.capital.capital_pd.index
        print("\n资金数据索引排序情况:")
        print(资金索引.is_monotonic_decreasing)
        print(资金索引)
    
    # 检查订单数据
    if len(abu_result_tuple.orders_pd) > 0:
        订单索引 = abu_result_tuple.orders_pd.index
        print("\n订单数据索引排序情况:")
        print(订单索引.is_monotonic_decreasing)
        print(订单索引)
    
    # 检查交易行为数据
    if len(abu_result_tuple.action_pd) > 0:
        行为索引 = abu_result_tuple.action_pd.index
        print("\n交易行为数据索引排序情况:")
        print(行为索引.is_monotonic_decreasing)
        print(行为索引)
    
    # 测试分页功能
    print("\n=== 测试分页功能 ===")
    
    # 测试get_paginated_data方法
    page_size = 10
    
    # 测试第一页
    if len(abu_result_tuple.orders_pd) > 0:
        paginated_data_page1 = metrics.get_paginated_data(abu_result_tuple.orders_pd, page=1, page_size=page_size)
        print(f"第一页数据（共{page_size}条）:")
        print(paginated_data_page1)
    
    # 测试第二页（如果有）
    if len(abu_result_tuple.orders_pd) > page_size:
        paginated_data_page2 = metrics.get_paginated_data(abu_result_tuple.orders_pd, page=2, page_size=page_size)
        print(f"\n第二页数据（共{page_size}条）:")
        print(paginated_data_page2)
    
    # 测试可视化分页
    print("\n=== 测试可视化分页 ===")
    metrics.plot_returns_cmp(only_show_returns=True, page=1, page_size=30)
    
except Exception as e:
    print(f"运行测试时出现错误: {e}")
    import traceback
    traceback.print_exc()