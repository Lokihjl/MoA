# -*- encoding:utf-8 -*-
"""针对交易回测结果存储，读取模块"""

import os
from collections import namedtuple
from enum import Enum
import datetime
import sqlite3

import numpy as np
import pandas as pd

from ..CoreBu import ABuEnv
from ..UtilBu import ABuFileUtil

# 定义SQLite数据库路径
STORE_DB_PATH = os.path.join(ABuEnv.g_project_cache_dir, 'abu_store.db')


def init_store_db():
    """
    初始化存储数据库
    """
    # 确保缓存目录存在
    ABuFileUtil.ensure_dir(ABuEnv.g_project_cache_dir)
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 创建回测结果索引表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS abu_index (
        custom_name TEXT PRIMARY KEY,
        description TEXT NOT NULL
    )
    ''')
    
    # 创建裁判训练索引表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ump_index (
        custom_name TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        ump_unique TEXT NOT NULL,
        is_main_ump TEXT NOT NULL
    )
    ''')
    
    # 创建回测结果数据表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS abu_results (
        result_key TEXT PRIMARY KEY,
        result_type TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()


# 模块加载时初始化数据库
init_store_db()


# noinspection PyClassHasNoInit
class AbuResultTuple(namedtuple('AbuResultTuple',
                                ('orders_pd',
                                 'action_pd',
                                 'capital',
                                 'benchmark'))):
    """
        使用abu.run_loop_back返回的nametuple对象：

        orders_pd：回测结果生成的交易订单构成的pd.DataFrame对象
        action_pd: 回测结果生成的交易行为构成的pd.DataFrame对象
        capital:   资金类AbuCapital实例化对象
        benchmark: 交易基准对象，AbuBenchmark实例对象
    """
    __slots__ = ()

    def __repr__(self):
        """打印对象显示：orders_pd.info, action_pd.info, capital, benchmark"""
        return "orders_pd:{}\naction_pd:{}\ncapital:{}\nbenchmark:{}".format(
            self.orders_pd.info(),
            self.action_pd.info(),
            self.capital, self.benchmark)


class EStoreAbu(Enum):
    """保存回测结果的enum类型"""

    """保存普通类型，存储文件后缀为空"""
    E_STORE_NORMAL = 0

    """保存训练集回测，存储文件后缀为train"""
    E_STORE_TRAIN = 1
    """保存测试集交易回测，存储文件后缀为test"""
    E_STORE_TEST = 2

    """保存测试集交易使用主裁ump进行回测，存储文件后缀为test_ump"""
    E_STORE_TEST_UMP = 3
    """保存测试集交易使用主裁＋边裁ump进行回测，存储文件后缀为test_ump_with_edge"""
    E_STORE_TEST_UMP_WITH_EDGE = 4

    """保存测回测，存储文件后缀为自定义字符串"""
    E_STORE_CUSTOM_NAME = 5


def dump_custom_abu_index_csv(custom_name, custom_desc):
    """
    将回测模块的回测结果文件做index描述记录的保存到SQLite数据库
    :param custom_name: custom_name为索引
    :param custom_desc: 描述内容
    """
    # 无描述显示No description
    custom_desc = 'No description' if custom_desc is None else custom_desc
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 使用UPSERT语法插入或更新数据
    cursor.execute('''
    INSERT INTO abu_index (custom_name, description) VALUES (?, ?)
    ON CONFLICT(custom_name) DO UPDATE SET description = excluded.description
    ''', (custom_name, custom_desc))
    
    conn.commit()
    conn.close()


def dump_custom_ump_index_csv(custom_name, ump_unique, is_main_ump, custom_desc):
    """
    将ump训练好的数据文件做index描述记录的保存到SQLite数据库
    :param custom_name: custom_name + ump_unique为索引
    :param ump_unique: ump类的标识str类型，ump.class_unique_id()
    :param is_main_ump: 是主裁还是边裁标识str类型，eg：main or edge
    :param custom_desc: ump训练数据的描述str
    """
    # 无描述显示No description
    custom_desc = 'No description' if custom_desc is None else custom_desc
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 使用完整的索引名
    full_index = '{}:{}'.format(ump_unique, custom_name)
    
    # 使用UPSERT语法插入或更新数据
    cursor.execute('''
    INSERT INTO ump_index (custom_name, description, ump_unique, is_main_ump) 
    VALUES (?, ?, ?, ?)
    ON CONFLICT(custom_name) DO UPDATE SET 
        description = excluded.description,
        ump_unique = excluded.ump_unique,
        is_main_ump = excluded.is_main_ump
    ''', (full_index, custom_desc, ump_unique, is_main_ump))
    
    conn.commit()
    conn.close()


def load_custom_abu_index():
    """从SQLite读取回测结果索引描述"""
    conn = sqlite3.connect(STORE_DB_PATH)
    
    # 直接读取为DataFrame
    index_df = pd.read_sql('SELECT * FROM abu_index', conn, index_col='custom_name')
    
    conn.close()
    return index_df


def load_custom_ump_index():
    """从SQLite读取裁判ump训练索引描述"""
    conn = sqlite3.connect(STORE_DB_PATH)
    
    # 直接读取为DataFrame
    index_df = pd.read_sql('SELECT * FROM ump_index', conn, index_col='custom_name')
    
    conn.close()
    return index_df


def del_custom_abu_index(custom_name):
    """从SQLite删除回测结果索引描述中某一特定行"""
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM abu_index WHERE custom_name = ?', (custom_name,))
    
    conn.commit()
    conn.close()


def del_custom_ump_index(custom_name):
    """从SQLite删除裁判ump训练索引描述中某一特定行"""
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM ump_index WHERE custom_name = ?', (custom_name,))
    
    conn.commit()
    conn.close()


def _cache_abu_result_path(n_folds, store_type, custom_name):
    """由外部参数返回所有单子存贮路径"""
    fn_root = ABuEnv.g_project_cache_dir
    fn_head = '' if n_folds is None else 'n{}_'.format(n_folds)

    # 根据EStoreAbu来决定fn_head
    if store_type == EStoreAbu.E_STORE_TEST:
        fn_head += 'test'
    elif store_type == EStoreAbu.E_STORE_TEST_UMP:
        fn_head += 'test_ump'
    elif store_type == EStoreAbu.E_STORE_TEST_UMP_WITH_EDGE:
        fn_head += 'test_ump_with_edge'
    elif store_type == EStoreAbu.E_STORE_TRAIN:
        fn_head += 'train'
    elif store_type == EStoreAbu.E_STORE_CUSTOM_NAME:
        fn_head += custom_name
    elif store_type != EStoreAbu.E_STORE_NORMAL:
        raise ValueError('store_type error!!!')

    # eg: n2_test_orders_pd
    orders_key = fn_head + '_orders_pd'
    orders_path = os.path.join(fn_root, orders_key)
    # 只需要ensure_dir第一个就可以了
    ABuFileUtil.ensure_dir(orders_path)

    # eg: n2_test_action_pd
    action_key = fn_head + '_action_pd'
    action_path = os.path.join(fn_root, action_key)

    # eg: n2_test_capital
    capital_path = os.path.join(fn_root, fn_head + '_capital')

    # eg: n2_test_benchmark
    benchmark_path = os.path.join(fn_root, fn_head + '_benchmark')

    return orders_path, orders_key, action_path, action_key, capital_path, benchmark_path


def store_abu_result_tuple(abu_result_tuple, n_folds=None, store_type=EStoreAbu.E_STORE_NORMAL,
                           custom_name=None):
    """
    保存abu.run_loop_back的回测结果AbuResultTuple对象到SQLite数据库，根据n_folds，store_type参数
    来定义存储的键名称

    :param abu_result_tuple: AbuResultTuple对象类型
    :param n_folds: 回测执行了几年，只影响存贮键名
    :param store_type: 回测保存类型EStoreAbu类型，只影响存贮键名
    :param custom_name: 如果store_type=EStoreAbu.E_STORE_CUSTOM_NAME时需要的自定义键名称
    """
    orders_path, orders_key, action_path, action_key, capital_path, benchmark_path = _cache_abu_result_path(
        n_folds, store_type, custom_name)
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 使用orders_key作为主键，存储orders_pd
    orders_content = abu_result_tuple.orders_pd.to_json()
    cursor.execute('''
    INSERT INTO abu_results (result_key, result_type, content) VALUES (?, ?, ?)
    ON CONFLICT(result_key) DO UPDATE SET content = excluded.content
    ''', (orders_key, 'orders_pd', orders_content))
    
    # 使用action_key作为主键，存储action_pd
    action_content = abu_result_tuple.action_pd.to_json()
    cursor.execute('''
    INSERT INTO abu_results (result_key, result_type, content) VALUES (?, ?, ?)
    ON CONFLICT(result_key) DO UPDATE SET content = excluded.content
    ''', (action_key, 'action_pd', action_content))
    
    # 使用capital_path作为主键，存储capital (使用pickle序列化)
    import pickle
    capital_content = pickle.dumps(abu_result_tuple.capital).hex()
    cursor.execute('''
    INSERT INTO abu_results (result_key, result_type, content) VALUES (?, ?, ?)
    ON CONFLICT(result_key) DO UPDATE SET content = excluded.content
    ''', (capital_path, 'capital', capital_content))
    
    # 使用benchmark_path作为主键，存储benchmark (使用pickle序列化)
    benchmark_content = pickle.dumps(abu_result_tuple.benchmark).hex()
    cursor.execute('''
    INSERT INTO abu_results (result_key, result_type, content) VALUES (?, ?, ?)
    ON CONFLICT(result_key) DO UPDATE SET content = excluded.content
    ''', (benchmark_path, 'benchmark', benchmark_content))
    
    conn.commit()
    conn.close()


def load_abu_result_tuple(n_folds=None, store_type=EStoreAbu.E_STORE_NORMAL, custom_name=None):
    """
    读取使用store_abu_result_tuple保存的回测结果，根据n_folds，store_type参数
    来定义读取的键名称，依次读取orders_pd，action_pd，capital，benchmark后构造
    AbuResultTuple对象返回

    :param n_folds: 回测执行了几年，只影响读取的键名
    :param store_type: 回测保存类型EStoreAbu类型，只影响读取的键名
    :param custom_name: 如果store_type=EStoreAbu.E_STORE_CUSTOM_NAME时需要的自定义键名称
    :return: AbuResultTuple对象
    """

    orders_path, orders_key, action_path, action_key, capital_path, benchmark_path = _cache_abu_result_path(
        n_folds, store_type, custom_name)
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 读取orders_pd
    cursor.execute('SELECT content FROM abu_results WHERE result_key = ?', (orders_key,))
    orders_content = cursor.fetchone()
    if orders_content is None:
        raise ValueError(f'orders_pd not found for key: {orders_key}')
    orders_pd = pd.read_json(orders_content[0])
    
    # 读取action_pd
    cursor.execute('SELECT content FROM abu_results WHERE result_key = ?', (action_key,))
    action_content = cursor.fetchone()
    if action_content is None:
        raise ValueError(f'action_pd not found for key: {action_key}')
    action_pd = pd.read_json(action_content[0])
    
    # 读取capital (使用pickle反序列化)
    import pickle
    cursor.execute('SELECT content FROM abu_results WHERE result_key = ?', (capital_path,))
    capital_content = cursor.fetchone()
    if capital_content is None:
        raise ValueError(f'capital not found for key: {capital_path}')
    capital = pickle.loads(bytes.fromhex(capital_content[0]))
    
    # 读取benchmark (使用pickle反序列化)
    cursor.execute('SELECT content FROM abu_results WHERE result_key = ?', (benchmark_path,))
    benchmark_content = cursor.fetchone()
    if benchmark_content is None:
        raise ValueError(f'benchmark not found for key: {benchmark_path}')
    benchmark = pickle.loads(bytes.fromhex(benchmark_content[0]))
    
    conn.close()
    
    # 构建返回AbuResultTuple对象
    return AbuResultTuple(orders_pd, action_pd, capital, benchmark)


def delete_abu_result_tuple(n_folds=None, store_type=EStoreAbu.E_STORE_NORMAL, custom_name=None, del_index=False):
    """
    从SQLite数据库中删除store_abu_result_tuple保存的回测结果，根据n_folds，store_type参数
    来定义删除的键名称

    :param n_folds: 回测执行了几年，只影响删除的键名
    :param store_type: 回测保存类型EStoreAbu类型，只影响删除的键名
    :param custom_name: 如果store_type=EStoreAbu.E_STORE_CUSTOM_NAME时需要的自定义键名称
    :param del_index: 是否删除index记录
    """

    orders_path, orders_key, action_path, action_key, capital_path, benchmark_path = _cache_abu_result_path(
        n_folds, store_type, custom_name)
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 获取各个键后依次删除
    keys_to_delete = [orders_key, action_key, capital_path, benchmark_path]
    for key in keys_to_delete:
        cursor.execute('DELETE FROM abu_results WHERE result_key = ?', (key,))
    
    conn.commit()
    conn.close()

    if del_index:
        # 删除回测所对应的描述文件索引行
        del_custom_abu_index(custom_name)


def store_abu_result_out_put(abu_result_tuple, show_log=True):
    """
    保存abu.run_loop_back的回测结果AbuResultTuple对象到SQLite数据库，根据当前时间戳生成唯一标识，
    保存在out_put表中，确保外部的可读性
    1. 交易单: orders_pd
    2. 行动单: action_pd
    3. 资金单: capital_pd
    4. 手续费: commission_pd
    """
    # 生成唯一标识
    unique_id = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    
    conn = sqlite3.connect(STORE_DB_PATH)
    cursor = conn.cursor()
    
    # 创建out_put表（如果不存在）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS out_put (
        unique_id TEXT PRIMARY KEY,
        create_time TEXT NOT NULL,
        result_type TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')
    
    create_time = datetime.datetime.now().isoformat()
    
    # 保存交易单
    orders_content = abu_result_tuple.orders_pd.to_json()
    cursor.execute('''
    INSERT INTO out_put (unique_id, create_time, result_type, content) VALUES (?, ?, ?, ?)
    ''', (unique_id + '_orders', create_time, 'orders', orders_content))
    if show_log:
        print('save orders_pd suc!')
    
    # 保存行动单
    actions_content = abu_result_tuple.action_pd.to_json()
    cursor.execute('''
    INSERT INTO out_put (unique_id, create_time, result_type, content) VALUES (?, ?, ?, ?)
    ''', (unique_id + '_actions', create_time, 'actions', actions_content))
    if show_log:
        print('save actions_pd suc!')
    
    # 保存资金单
    capital_content = abu_result_tuple.capital.capital_pd.to_json()
    cursor.execute('''
    INSERT INTO out_put (unique_id, create_time, result_type, content) VALUES (?, ?, ?, ?)
    ''', (unique_id + '_capital', create_time, 'capital', capital_content))
    if show_log:
        print('save capital_pd suc!')
    
    # 保存手续费
    commission_content = abu_result_tuple.capital.commission.commission_df.to_json()
    cursor.execute('''
    INSERT INTO out_put (unique_id, create_time, result_type, content) VALUES (?, ?, ?, ?)
    ''', (unique_id + '_commission', create_time, 'commission', commission_content))
    if show_log:
        print('save commission_pd suc!')
    
    conn.commit()
    conn.close()
