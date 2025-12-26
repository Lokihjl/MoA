# -*- coding:utf-8 -*-
"""
测试A股数据获取功能
"""

import sys
sys.path.append('.')

from abupy import ABuSymbolPd
from abupy.MarketBu.ABuSymbolStock import query_stock_info, AbuSymbolCN

# 测试1: 获取A股股票信息
print("测试1: 获取A股股票信息")
try:
    stock_info = query_stock_info('sz000001')
    print(f"sz000001股票信息: {stock_info}")
    print("✓ 测试1通过")
except Exception as e:
    print(f"✗ 测试1失败: {e}")

# 测试2: 获取全市场A股股票代码
print("\n测试2: 获取全市场A股股票代码")
try:
    all_symbols = AbuSymbolCN().all_symbol()
    print(f"全市场A股股票数量: {len(all_symbols)}")
    print(f"部分A股股票代码: {all_symbols[:5]}")
    print("✓ 测试2通过")
except Exception as e:
    print(f"✗ 测试2失败: {e}")

# 测试3: 获取A股K线数据
print("\n测试3: 获取A股K线数据")
try:
    kl_df = ABuSymbolPd.make_kl_df('sz000001', n_folds=2)
    print(f"sz000001 K线数据行数: {len(kl_df)}")
    print(f"K线数据列名: {list(kl_df.columns)}")
    print("✓ 测试3通过")
except Exception as e:
    print(f"✗ 测试3失败: {e}")

print("\n所有测试完成！")
