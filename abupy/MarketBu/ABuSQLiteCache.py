# coding=utf-8
"""
    SQLite数据缓存模块
    将ABU框架的数据存储方式从CSV和HDF5改为只使用SQLite
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sqlite3
import pandas as pd
from datetime import datetime
from ..CoreBu import ABuEnv
from ..CoreBu.ABuEnv import EDataCacheType

# SQLite数据库文件路径
SQLITE_DB_PATH = os.path.join(ABuEnv.g_project_data_dir, 'abu_kl_data.sqlite')

# 创建数据库连接
def get_db_connection():
    """
    获取SQLite数据库连接
    :return: 数据库连接对象
    """
    conn = sqlite3.connect(SQLITE_DB_PATH)
    # 设置行工厂，返回字典而不是元组
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库表结构
def init_sqlite_db():
    """
    初始化SQLite数据库表结构
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建股票数据主表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_kl_data (
        symbol TEXT NOT NULL,
        date INTEGER NOT NULL,
        open REAL NOT NULL,
        high REAL NOT NULL,
        low REAL NOT NULL,
        close REAL NOT NULL,
        volume INTEGER NOT NULL,
        amount REAL NOT NULL,
        pre_close REAL NOT NULL,
        p_change REAL NOT NULL,
        PRIMARY KEY (symbol, date)
    ) WITHOUT ROWID
    ''')
    
    # 创建股票数据索引表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS stock_kl_index (
        symbol TEXT PRIMARY KEY,
        start_date INTEGER NOT NULL,
        end_date INTEGER NOT NULL,
        last_updated TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()

# 从SQLite加载K线数据
def load_kline_from_sqlite(symbol):
    """
    从SQLite数据库加载指定股票的K线数据
    :param symbol: 股票代码
    :return: (金融时间序列pd.DataFrame对象，开始日期int，结束日期int)
    """
    conn = get_db_connection()
    
    try:
        # 检查股票是否存在索引
        cursor = conn.cursor()
        cursor.execute('''
        SELECT start_date, end_date FROM stock_kl_index WHERE symbol = ?
        ''', (symbol,))
        index_row = cursor.fetchone()
        
        if not index_row:
            return None, 0, 0
        
        start_date = index_row['start_date']
        end_date = index_row['end_date']
        
        # 获取K线数据
        query = '''
        SELECT * FROM stock_kl_data WHERE symbol = ? ORDER BY date
        '''
        df = pd.read_sql_query(query, conn, params=(symbol,))
        
        if df.empty:
            return None, 0, 0
        
        # 设置索引为日期
        df['date_str'] = df['date'].astype(str)
        df['datetime'] = pd.to_datetime(df['date_str'])
        df.set_index('datetime', inplace=True)
        df.drop(['date_str'], axis=1, inplace=True)
        
        # 添加key列
        df['key'] = list(range(len(df)))
        
        return df, start_date, end_date
    except Exception as e:
        print(f"从SQLite加载数据失败: {e}")
        return None, 0, 0
    finally:
        conn.close()

# 保存K线数据到SQLite
def save_kline_to_sqlite(df, symbol, start_int, end_int):
    """
    将K线数据保存到SQLite数据库
    :param df: 需要存储的金融时间序列pd.DataFrame对象
    :param symbol: 股票代码
    :param start_int: 开始日期int
    :param end_int: 结束日期int
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 删除旧数据
        cursor.execute('DELETE FROM stock_kl_data WHERE symbol = ?', (symbol,))
        
        # 准备插入数据
        insert_data = []
        for _, row in df.iterrows():
            # 将日期转换为int格式
            date_int = int(row.name.strftime('%Y%m%d'))
            insert_data.append((
                symbol,
                date_int,
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row['amount'] if 'amount' in row else 0,
                row['pre_close'],
                row['p_change']
            ))
        
        # 批量插入数据
        cursor.executemany('''
        INSERT INTO stock_kl_data (symbol, date, open, high, low, close, volume, amount, pre_close, p_change)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', insert_data)
        
        # 更新或插入索引
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''
        INSERT OR REPLACE INTO stock_kl_index (symbol, start_date, end_date, last_updated)
        VALUES (?, ?, ?, ?)
        ''', (symbol, start_int, end_int, last_updated))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"保存数据到SQLite失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# 初始化数据库
init_sqlite_db()