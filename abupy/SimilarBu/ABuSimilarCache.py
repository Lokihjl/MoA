from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import os
import sqlite3
import pandas as pd

from ..CoreBu import ABuEnv
from ..UtilBu import ABuFileUtil

SIMILAR_CACHE_PATH = os.path.join(ABuEnv.g_project_cache_dir, 'similar.db')


def init_similar_db():
    """
    初始化相似性数据的SQLite数据库
    """
    # 确保缓存目录存在
    ABuFileUtil.ensure_dir(ABuEnv.g_project_cache_dir)
    
    conn = sqlite3.connect(SIMILAR_CACHE_PATH)
    cursor = conn.cursor()
    
    # 创建相似性数据表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS similar_data (
        key TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()


# 模块加载时初始化数据库
init_similar_db()


def similar_key(symbol, cmp_cnt=None, n_folds=None, start=None, end=None, corr_type=None):
    return '{}_{}_{}_{}_{}_{}'.format(symbol, cmp_cnt, n_folds, start, end, corr_type)



def dump_2_hdh5(key, obj):
    """
    将对象存储到SQLite数据库中
    :param key: 存储键
    :param obj: 要存储的对象（必须是可序列化为JSON的对象）
    """
    conn = sqlite3.connect(SIMILAR_CACHE_PATH)
    cursor = conn.cursor()
    
    # 将对象转换为JSON字符串
    obj_str = obj.to_json() if isinstance(obj, pd.DataFrame) else str(obj)
    
    # 使用UPSERT语法插入或更新数据
    cursor.execute('''
    INSERT INTO similar_data (key, data) VALUES (?, ?)
    ON CONFLICT(key) DO UPDATE SET data = excluded.data
    ''', (key, obj_str))
    
    conn.commit()
    conn.close()



def load_2_hdh5(key):
    """
    从SQLite数据库中加载对象
    :param key: 存储键
    :return: 加载的对象
    """
    conn = sqlite3.connect(SIMILAR_CACHE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT data FROM similar_data WHERE key = ?', (key,))
    result = cursor.fetchone()
    
    conn.close()
    
    if result:
        # 尝试将JSON字符串转换回DataFrame
        try:
            return pd.read_json(result[0])
        except:
            return result[0]
    return None



def show_keys():
    """
    显示所有存储的键
    :return: 键列表
    """
    conn = sqlite3.connect(SIMILAR_CACHE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT key FROM similar_data')
    keys = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    return keys



def clear_cache(key=None):
    """
    清除缓存
    :param key: 可选，指定要清除的键，如果为None则清除所有缓存
    """
    conn = sqlite3.connect(SIMILAR_CACHE_PATH)
    cursor = conn.cursor()
    
    if key is not None:
        cursor.execute('DELETE FROM similar_data WHERE key = ?', (key,))
    else:
        cursor.execute('DELETE FROM similar_data')
    
    conn.commit()
    conn.close()
