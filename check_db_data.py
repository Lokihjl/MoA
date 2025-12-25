# -*- encoding:utf-8 -*-
import sys
import os
import sqlite3
import pandas as pd

# 将项目根目录添加到Python路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 连接到数据库
db_path = 'e:/source/abu/abu-master/MoA-ui/server/instance/abu_quant.db'
conn = sqlite3.connect(db_path)

# 查看数据库中的所有表
print("数据库中的所有表:")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(table[0])
    
# 查看kline_data表的结构
print("\nkline_data表的结构:")
cursor.execute("PRAGMA table_info(kline_data);")
columns = cursor.fetchall()
for column in columns:
    print(column)
    
# 查询sh000001的日线数据
query = "SELECT * FROM kline_data WHERE symbol='sh000001' AND data_type='day' ORDER BY date LIMIT 10"
df = pd.read_sql(query, conn)

print(f"\n查询到{len(df)}条数据")
if len(df) > 0:
    print("前5条数据:")
    print(df.head())
    print("\n数据类型:")
    print(df.dtypes)
else:
    print("没有找到sh000001的日线数据")
    
# 查询所有symbol的日线数据
query = "SELECT DISTINCT symbol FROM kline_data WHERE data_type='day' LIMIT 10"
df_symbols = pd.read_sql(query, conn)
print(f"\n数据库中包含的股票代码:")
print(df_symbols)

conn.close()