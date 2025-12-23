# coding=utf-8
"""
    SQLite数据缓存模块
    将ABU框架的数据存储方式从CSV和HDF5改为只使用SQLite
    直接使用应用主数据库的KlineData表，确保所有数据从下载模块获取
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

# 从应用配置中获取数据库路径，默认使用应用主数据库
# 注意：在实际运行时，这个路径会被Flask应用的配置覆盖
# 强制使用MoA-ui/server目录下的数据库文件

# 获取当前文件的绝对路径
current_file_path = os.path.abspath(__file__)
print(f"当前文件路径: {current_file_path}")

# 获取ABuSQLiteCache.py所在目录
abupy_marketbu_dir = os.path.dirname(current_file_path)
print(f"ABuSQLiteCache.py所在目录: {abupy_marketbu_dir}")

# 获取项目根目录
# ABuSQLiteCache.py的路径是E:\source\abu\abu-master\abupy\MarketBu\ABuSQLiteCache.py
# 所以向上走两级目录得到E:\source\abu\abu-master
project_root = os.path.abspath(os.path.join(abupy_marketbu_dir, '../..'))
print(f"项目根目录: {project_root}")

# 构建MoA-ui/server/instance/abu_quant.db的绝对路径，使用正确的路径分隔符
# 数据下载模块使用的数据库文件是instance/abu_quant.db，这是Flask应用的实例文件夹
MOA_DB_PATH = os.path.join(project_root, 'MoA-ui', 'server', 'instance', 'abu_quant.db')

# 确保使用正确的数据库路径
SQLITE_DB_PATH = MOA_DB_PATH

# 输出当前使用的数据库路径，用于调试
print(f"当前使用的数据库路径: {SQLITE_DB_PATH}")
print(f"数据库文件是否存在: {os.path.exists(SQLITE_DB_PATH)}")

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



# 从SQLite加载K线数据
def load_kline_from_sqlite(symbol):
    """
    从SQLite数据库加载指定股票的K线数据，优先使用KlineData表，失败时回退到stock_kl_data表
    :param symbol: 股票代码
    :return: (金融时间序列pd.DataFrame对象，开始日期int，结束日期int)
    """
    conn = get_db_connection()
    
    try:
        try:
            # 尝试从kline_data表获取数据
            query = '''
            SELECT * FROM kline_data WHERE symbol = ? AND data_type = 'day' ORDER BY date
            '''
            df = pd.read_sql_query(query, conn, params=(symbol,))
            
            if not df.empty:
                # 设置索引为日期
                df['datetime'] = pd.to_datetime(df['date'])
                df.set_index('datetime', inplace=True)
                
                # 转换为ABU框架需要的格式
                abu_df = pd.DataFrame()
                abu_df['symbol'] = df['symbol']
                # 正确处理日期转换，确保date是datetime对象
                abu_df['date'] = df.index.year * 10000 + df.index.month * 100 + df.index.day
                abu_df['open'] = df['open']
                abu_df['high'] = df['high']
                abu_df['low'] = df['low']
                abu_df['close'] = df['close']
                abu_df['volume'] = df['volume']
                abu_df['amount'] = df['amount'] if 'amount' in df.columns else 0
                
                # 计算pre_close和p_change
                abu_df['pre_close'] = abu_df['close'].shift(1).fillna(abu_df['open'])
                abu_df['p_change'] = ((abu_df['close'] - abu_df['pre_close']) / abu_df['pre_close']) * 100
                
                # 添加key列
                abu_df['key'] = list(range(len(abu_df)))
                
                # 获取开始和结束日期
                start_date = abu_df['date'].min()
                end_date = abu_df['date'].max()
                
                return abu_df, start_date, end_date
        except Exception as e:
            print(f"从kline_data表加载数据失败，尝试使用stock_kl_data表: {e}")
            import traceback
            traceback.print_exc()
        
        # 如果kline_data表获取失败或为空，尝试从stock_kl_data表获取数据
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
        
        # 获取开始和结束日期
        start_date = df['date'].min()
        end_date = df['date'].max()
        
        return df, start_date, end_date
    except Exception as e:
        print(f"从SQLite加载数据失败: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, 0
    finally:
        conn.close()

# 保存K线数据到SQLite
def save_kline_to_sqlite(df, symbol, start_int, end_int):
    """
    将K线数据保存到SQLite数据库，直接使用KlineData表
    :param df: 需要存储的金融时间序列pd.DataFrame对象
    :param symbol: 股票代码
    :param start_int: 开始日期int
    :param end_int: 结束日期int
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 准备插入数据
        insert_data = []
        for _, row in df.iterrows():
            # 将日期转换为日期类型
            date_obj = row.name.date()
            insert_data.append((
                symbol,
                'cn',  # 默认市场为A股
                'day',  # 默认数据类型为日线
                date_obj,
                row['open'],
                row['high'],
                row['low'],
                row['close'],
                row['volume'],
                row['amount'] if 'amount' in row else 0,
                None,  # adjust
                None   # atr21
            ))
        
        # 批量插入数据，使用INSERT OR REPLACE避免重复
        cursor.executemany('''
        INSERT OR REPLACE INTO kline_data (symbol, market, data_type, date, open, high, low, close, volume, amount, adjust, atr21)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', insert_data)
        
        conn.commit()
        return True
    except Exception as e:
        print(f"保存数据到SQLite失败: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# 初始化数据库，现在只需要确保KlineData表存在即可，由Flask应用负责创建
# 保留这个函数以保持兼容性
def init_sqlite_db():
    """
    初始化SQLite数据库表结构
    现在只检查必要的索引，表结构由Flask应用管理
    如果kline_data表不存在，创建stock_kl_data和stock_kl_index表作为回退
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 尝试检查kline_data表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kline_data'")
        if cursor.fetchone():
            # kline_data表存在，创建索引
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_kline_data_symbol ON kline_data (symbol)
            ''')
            
            cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_kline_data_date ON kline_data (date)
            ''')
            
            conn.commit()
            print("✅ 数据库索引初始化成功")
        else:
            # kline_data表不存在，创建stock_kl_data和stock_kl_index表作为回退
            print("⚠️  kline_data表不存在，创建stock_kl_data和stock_kl_index表作为回退")
            
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
            print("✅ 回退表创建成功")
    except Exception as e:
        print(f"初始化数据库失败: {e}")
    finally:
        conn.close()

# 只在直接运行脚本时初始化数据库，模块导入时不初始化
if __name__ == '__main__':
    init_sqlite_db()