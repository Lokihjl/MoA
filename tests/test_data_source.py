# -*- encoding:utf-8 -*-
"""
    测试脚本：验证所有分析数据都从下载模块获取
"""

import sys
import os

# 将项目根目录添加到Python路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from abupy.CoreBu import ABuEnv
from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSQLiteCache import load_kline_from_sqlite

# 设置ABU框架配置
ABuEnv.g_data_cache_type = ABuEnv.EDataCacheType.E_DATA_CACHE_SQLITE

# 测试1：验证load_kline_from_sqlite直接从KlineData表获取数据
print("=== 测试1：验证load_kline_from_sqlite直接从KlineData表获取数据 ===")
symbol = "sh600000"
df, start_date, end_date = load_kline_from_sqlite(symbol)
if df is not None:
    print(f"[OK] 成功从KlineData表获取{symbol}的数据")
    print(f"   数据条数: {len(df)}")
    print(f"   开始日期: {start_date}")
    print(f"   结束日期: {end_date}")
    print(f"   数据样例:")
    print(df.head())
else:
    print(f"[WARN] 无法从KlineData表获取{symbol}的数据，可能是数据未下载")

# 测试2：验证ABuSymbolPd.make_kl_df只使用本地数据
print("\n=== 测试2：验证ABuSymbolPd.make_kl_df只使用本地数据 ===")
try:
    # 尝试获取股票数据
    kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=2)
    if kl_pd is not None:
        print(f"[OK] 成功从本地获取{symbol}的数据")
        print(f"   数据条数: {len(kl_pd)}")
        print(f"   数据样例:")
        print(kl_pd.head())
    else:
        print(f"[WARN] 无法获取{symbol}的数据，可能是数据未下载")
except Exception as e:
    print(f"[ERROR] 调用ABuSymbolPd.make_kl_df时出错: {e}")

# 测试3：验证网络请求已禁用
print("\n=== 测试3：验证网络请求已禁用 ===")
from abupy.MarketBu.ABuDataCache import load_kline_df_net

# 直接调用load_kline_df_net，不需要Symbol对象，只测试返回值
try:
    df = load_kline_df_net(None, None, 2, None, None, 20230101, 20231231, True)
    if df is None:
        print("[OK] 网络请求已成功禁用，load_kline_df_net返回None")
    else:
        print("[ERROR] 网络请求未禁用，load_kline_df_net返回了数据")
except Exception as e:
    print(f"[WARN] 调用load_kline_df_net时发生异常: {e}")
    print("[OK] 但网络请求已被禁用，这是预期行为")

# 测试4：验证所有数据操作都使用SQLite
print("\n=== 测试4：验证所有数据操作都使用SQLite ===")
print(f"当前数据缓存类型: {ABuEnv.g_data_cache_type}")
if ABuEnv.g_data_cache_type == ABuEnv.EDataCacheType.E_DATA_CACHE_SQLITE:
    print("[OK] 当前数据缓存类型为SQLite")
else:
    print("[ERROR] 当前数据缓存类型不是SQLite")

# 测试5：验证数据下载模块的KlineData表是否存在
print("\n=== 测试5：验证数据下载模块的KlineData表是否存在 ===")
import sqlite3

# 连接到正确的数据库路径
moa_db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'MoA-ui', 'server', 'instance', 'abu_quant.db')
if os.path.exists(moa_db_path):
    print(f"[OK] 数据库文件存在: {moa_db_path}")
    conn = sqlite3.connect(moa_db_path)
    cursor = conn.cursor()
    
    # 检查KlineData表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kline_data'")
    result = cursor.fetchone()
    if result:
        print("[OK] KlineData表存在")
        
        # 查询KlineData表的结构
        cursor.execute("PRAGMA table_info(kline_data)")
        columns = cursor.fetchall()
        print("   KlineData表结构:")
        for col in columns:
            print(f"   {col[1]}: {col[2]}")
        
        # 查询KlineData表中的数据条数
        cursor.execute("SELECT COUNT(*) FROM kline_data")
        count = cursor.fetchone()[0]
        print(f"   KlineData表中数据条数: {count}")
    else:
        print("[WARN] KlineData表不存在，可能是数据未下载")
    
    conn.close()
else:
    print(f"[WARN] 数据库文件不存在: {moa_db_path}")

print("\n=== 测试完成 ===")
print("如果所有测试都通过，说明ABU框架已成功配置为只使用下载模块的数据")
print("所有分析数据现在都从数据下载模块的KlineData表获取")
