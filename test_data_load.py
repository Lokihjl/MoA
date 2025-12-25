# -*- encoding:utf-8 -*-
"""
直接测试数据加载功能的脚本
"""

import os
import sys
import pandas as pd

# 将项目根目录添加到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 导入SQLite缓存模块
from abupy.MarketBu.ABuSQLiteCache import load_kline_from_sqlite

# 测试加载sh000003的数据
print("测试加载sh000003的数据...")
df, start_date, end_date = load_kline_from_sqlite("sh000003")

if df is not None:
    print(f"成功加载数据，数据形状: {df.shape}")
    print(f"开始日期: {start_date}")
    print(f"结束日期: {end_date}")
    print(f"前5行数据:")
    print(df.head())
    print(f"\n后5行数据:")
    print(df.tail())
    print(f"\n日期范围: {df['date'].min()} - {df['date'].max()}")
else:
    print("加载数据失败")

# 测试加载sh000001的数据
print("\n测试加载sh000001的数据...")
df2, start_date2, end_date2 = load_kline_from_sqlite("sh000001")

if df2 is not None:
    print(f"成功加载数据，数据形状: {df2.shape}")
    print(f"开始日期: {start_date2}")
    print(f"结束日期: {end_date2}")
else:
    print("加载数据失败")