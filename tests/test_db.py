# -*- encoding:utf-8 -*-
"""
    简单的数据库测试脚本，直接连接到数据库，查看表结构和数据
"""

import sqlite3
import os

# 连接到正确的数据库路径
moa_db_path = os.path.join(os.path.dirname(__file__), 'MoA-ui', 'server', 'instance', 'abu_quant.db')
print(f"数据库路径: {moa_db_path}")
print(f"数据库文件是否存在: {os.path.exists(moa_db_path)}")

if os.path.exists(moa_db_path):
    # 连接到数据库
    conn = sqlite3.connect(moa_db_path)
    cursor = conn.cursor()
    
    print("\n=== 所有表列表 ===")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    for table in tables:
        print(f"   {table[0]}")
    
    # 查看kline_data表的结构
    print("\n=== kline_data表结构 ===")
    try:
        cursor.execute("PRAGMA table_info(kline_data)")
        columns = cursor.fetchall()
        if columns:
            for col in columns:
                print(f"   {col[1]}: {col[2]}")
        else:
            print("   kline_data表不存在")
    except sqlite3.Error as e:
        print(f"   查询kline_data表结构时出错: {e}")
    
    # 查看kline_data表的数据
    print("\n=== kline_data表数据 ===")
    try:
        cursor.execute("SELECT COUNT(*) FROM kline_data")
        count = cursor.fetchone()[0]
        print(f"   数据条数: {count}")
        
        if count > 0:
            cursor.execute("SELECT * FROM kline_data LIMIT 5")
            rows = cursor.fetchall()
            print("   数据样例:")
            for row in rows:
                print(f"   {row}")
    except sqlite3.Error as e:
        print(f"   查询kline_data表数据时出错: {e}")
    
    # 关闭数据库连接
    conn.close()
else:
    print("数据库文件不存在")
