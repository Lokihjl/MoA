# coding=utf-8
"""
    对数据采集进行存储，读取，以及数据更新merge策略等实现模块
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pandas as pd

from ..CoreBu.ABuEnv import EMarketTargetType, EMarketSubType
from ..CoreBu import ABuEnv
from ..UtilBu.ABuFileUtil import ensure_dir
# noinspection PyUnresolvedReferences
from ..CoreBu.ABuFixes import xrange, range, filter
from ..UtilBu.ABuProgress import AbuProgress


def _kl_unique_key(symbol, start, end):
    """
    通过symbol以及start, end信息生成数据存储唯一id
    :param symbol: Symbol对象
    :param start: str日期对象 eg 2015-02-14
    :param end: str日期对象 eg 2017-02-14
    :return: e.g : 'usTSLA_2015-02-14_2017-02-14'
    """
    return "{}_{}_{}".format(symbol.value, start, end)





# 导入SQLite缓存模块
from .ABuSQLiteCache import load_kline_from_sqlite, save_kline_to_sqlite

def load_kline_df(symbol_key):
    """
    从SQLite数据库读取对应的本地缓存金融时间序列对象数据
    :param symbol_key: str对象symbol
    :return: (金融时间序列pd.DataFrame对象，索引date_key中start请求日期int，索引date_key中end请求日期int)
    """
    return load_kline_from_sqlite(symbol_key)











def dump_kline_df(dump_df, symbol_key, date_key):
    """
    将金融时间序列存储到SQLite数据库
    储存方法 symbol_key->SQLite表->dump_df

    :param dump_df: 需要存储的金融时间序列实体pd.DataFrame对象
    :param symbol_key: str对象，eg. usTSLA
    :param date_key: str对象，eg. usTSLA_20100214_20170214 包含了df的时间开始时间与结束时间
    """
    # 从date_key中提取开始和结束日期
    _start = int(date_key[-17: -9])
    _end = int(date_key[-8:])
    
    # 直接使用SQLite存储，简化实现
    # 每次保存都会处理数据合并，确保数据的完整性和一致性
    
    # 尝试从SQLite加载现有数据
    existing_df, existing_start, existing_end = load_kline_from_sqlite(symbol_key)
    
    if existing_df is not None:
        # 存在现有数据，需要合并
        # 确保dump_df有date列
        if 'date' not in dump_df.columns:
            # 将索引转换为date列
            dump_df['date'] = dump_df.index.strftime('%Y%m%d').astype(int)
        
        # 合并新旧数据
        # 首先移除现有数据中与新数据重叠的部分
        existing_df = existing_df[~existing_df['date'].between(_start, _end)]
        
        # 合并数据
        merged_df = pd.concat([existing_df, dump_df])
        
        # 按date排序
        merged_df = merged_df.sort_values('date')
        
        # 去重，保留最新数据
        merged_df = merged_df.drop_duplicates(subset=['date'], keep='last')
        
        # 更新开始和结束日期
        final_start = min(merged_df['date'].min(), existing_start)
        final_end = max(merged_df['date'].max(), existing_end)
        
        # 保存合并后的数据
        save_kline_to_sqlite(merged_df, symbol_key, final_start, final_end)
    else:
        # 不存在现有数据，直接保存
        save_kline_to_sqlite(dump_df, symbol_key, _start, _end)





def save_kline_df(df, temp_symbol, start_int, end_int):
    """
    独立对外的保存kl数据接口
    :param df: 需要存储的金融时间序列实体pd.DataFrame对象
    :param temp_symbol: Symbbol对象
    :param start_int: 请求的开始日期int
    :param end_int: 请求的结束日期int
    :return:
    """
    if df is not None:
        # 通过emp_symbol, start_int, end_int拼接唯一保存df_key
        df_key = _kl_unique_key(temp_symbol, start_int, end_int)
        dump_kline_df(df, temp_symbol.value, df_key)


def load_kline_df_net(source, temp_symbol, n_folds, start, end, start_int, end_int, save):
    """
    通过网络请求数据源，获取temp_symbol以及参数时间日期对应的金融时间序列pd.DataFrame对象
    :param source: 数据源BaseMarket的子类，非实例化对象
    :param temp_symbol: Symbol类对象
    :param n_folds: 需要获取几年的回测数据，int
    :param start: 开始回测日期，str对象
    :param end: 结束回测日期，str对象
    :param start_int: 开始回测日期，int
    :param end_int: 结束回测日期，int
    :param save: 是否从网络成功获取数据后进行数据的保存
    """
    df = None
    # 实例化数据源对象
    data_source = source(temp_symbol)

    if data_source.check_support():
        # 通过数据源混入的SupportMixin类检测数据源是否支持temp_symbol对应的市场数据
        df = data_source.kline(n_folds=n_folds, start=start, end=end)

    if df is not None and save:
        """
            这里的start_int， end_int会记作下次读取的df_req_start, df_req_end，即就是没有完整的数据返回，也可通过索引匹配上，
            即如果今天刚刚请求了直到今天为止的数据，但是数据源没有返回到今天的数据，今天的还没有，但是由于记录了end_int为今天，所以
            再次发起请求时不会走网络，会从本地获取数据
        """
        df_key = _kl_unique_key(temp_symbol, start_int, end_int)
        dump_kline_df(df, temp_symbol.value, df_key)
    return df
