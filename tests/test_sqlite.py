import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from abupy.MarketBu.ABuSQLiteCache import save_kline_to_sqlite, load_kline_from_sqlite

# 创建测试数据
print("Creating test data...")

# 生成日期范围
dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='B')

# 创建随机价格数据
np.random.seed(42)
close = pd.Series(100 + np.cumsum(np.random.randn(len(dates))) * 5, index=dates)
open = close.shift(1).fillna(100) + np.random.randn(len(dates)) * 2
high = np.maximum(open, close) + np.random.randn(len(dates)) * 1
low = np.minimum(open, close) - np.random.randn(len(dates)) * 1
volume = np.random.randint(100000, 1000000, len(dates))

# 创建DataFrame
df = pd.DataFrame({
    'date': [int(ts.strftime('%Y%m%d')) for ts in dates],
    'open': open,
    'high': high,
    'low': low,
    'close': close,
    'volume': volume,
    'amount': volume * close,
    'pre_close': close.shift(1).fillna(close[0]),
    'p_change': ((close - close.shift(1)) / close.shift(1) * 100).fillna(0)
}, index=dates)

print(f"Created test data with {len(df)} rows")
print(df.head())

# 保存到SQLite
print("\nSaving to SQLite...")
save_kline_to_sqlite(df, 'testTSLA', 20230101, 20231231)
print("Save completed")

# 从SQLite读取
print("\nReading from SQLite...")
loaded_df, start, end = load_kline_from_sqlite('testTSLA')
print(f"Loaded data with shape: {loaded_df.shape}")
print(f"Start date: {start}, End date: {end}")
print(loaded_df.head())

# 测试数据一致性
print("\nTesting data consistency...")
if loaded_df is not None and len(loaded_df) == len(df):
    print("Data length matches!")
    # 检查是否有任何NaN值
    if not loaded_df.isnull().values.any():
        print("No NaN values in loaded data!")
    else:
        print("Warning: NaN values found in loaded data!")
    print("SQLite save and load test passed!")
else:
    print("Error: Data length mismatch or no data loaded!")
    print(f"Original length: {len(df)}, Loaded length: {len(loaded_df) if loaded_df is not None else 0}")
