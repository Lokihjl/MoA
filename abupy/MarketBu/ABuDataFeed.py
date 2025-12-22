# coding=utf-8
"""
    内置数据源示例实现模块：

    所有数据接口仅供学习使用，以及最基本使用测试，如需进一步使用，请购买数据
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import os

import random
import math
import sqlite3 as sqlite

import pandas as pd

from ..CoreBu.ABuEnv import EMarketTargetType, EMarketSubType
from ..CoreBu import ABuEnv
from ..MarketBu import ABuNetWork
from ..MarketBu.ABuDataBase import StockBaseMarket, SupportMixin
from ..MarketBu.ABuDataParser import BDParser, TXParser
from ..UtilBu import ABuStrUtil, ABuDateUtil, ABuMd5
from ..UtilBu.ABuDTUtil import catch_error
from ..CoreBu.ABuDeprecated import AbuDeprecated
# noinspection PyUnresolvedReferences
from ..CoreBu.ABuFixes import xrange, range, filter

"""网络请求（连接10秒，接收60秒）超时时间"""
K_TIME_OUT = (10, 60)


def random_from_list(array):
    """从参数array中随机取一个元素"""
    # 在array长度短的情况下，测试比np.random.choice效率要高
    return array[random.randrange(0, len(array))]


@AbuDeprecated('only read old symbol db, miss update!!!')
def query_symbol_sub_market(symbol):
    path = TXApi.K_SYMBOLS_DB
    conn = sqlite.connect(path)
    cur = conn.cursor()
    symbol = symbol.lower()
    query = "select {} from {} where {} like \'{}.%\'" .format(TXApi.K_DB_TABLE_SN, TXApi.K_DB_TABLE_NAME,
                                                              TXApi.K_DB_TABLE_SN, symbol)
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    sub_market = ''
    if results is not None and len(results) > 0:
        try:
            if results[0][0].find('.') > 0:
                sub_market = '.' + results[0][0].split('.')[1].upper()
        except:
            logging.info(results)
    return sub_market


@catch_error(return_val=None, log=False)
def query_symbol_from_pinyin(pinyin):
    """通过拼音对symbol进行模糊查询"""
    path = TXApi.K_SYMBOLS_DB
    conn = sqlite.connect(path)
    cur = conn.cursor()
    pinyin = pinyin.lower()
    query = "select stockCode from {} where pinyin=\'{}\'," .format(TXApi.K_DB_TABLE_NAME, pinyin)
    cur.execute(query)
    results = cur.fetchall()
    conn.close()
    if len(results) > 0:
        code = results[0][0]
        # 查询到的stcok code eg：sh111111，usabcd.n
        start = 2
        end = len(code)
        if '.' in code:
            # 如果是美股要截取.
            end = code.find('.')
        return code[start:end]


class BDApi(StockBaseMarket, SupportMixin):
    """bd数据源，支持A股"""

    K_NET_CONNECT_START = '&start='
    K_NET_DAY = 'http://gp.baidu.com:80/stocks/stockkline?from=android&os_ver=21&format=json&vv=3.3.0' \
                '&uid=&BDUSS=&cuid=%s&channel=default_channel&device=%s&logid=%s&actionid=%s&device_net_type' \
                '=wifi&period=day&stock_code=%s&fq_type=front'

    MINUTE_NET_5D = 'http://gp.baidu.com:80/stocks/stocktimelinefive?from=android&os_ver=21&format=json' \
                    '&vv=3.3&uid=&BDUSS=&cuid=%s&channel=default_channel&device=%s&logid=%s&actionid=%s' \
                    '&device_net_type=wifi&stock_code=%s&step=10'

    def __init__(self, symbol):
        """
        :param symbol: Symbol类型对象
        """
        super(BDApi, self).__init__(symbol)
        self._action_id = int(ABuDateUtil.time_seconds())
        self._version2_log_cnt = 0
        self.data_parser_cls = BDParser

    def kline(self, n_folds=2, start=None, end=None):
        """日k线接口"""
        self._version2_log_cnt += 1
        log_id = self._action_id + self._version2_log_cnt * 66
        cuid = ABuStrUtil.create_random_with_num_low(40)
        device = random_from_list(StockBaseMarket.K_DEV_MODE_LIST)
        url = BDApi.K_NET_DAY % (cuid, device, str(log_id), str(self._action_id), self._symbol.value)
        # logging.info(url)
        next_start = None
        kl_df = None
        if start:
            # 需重新计算n_fold
            days = ABuDateUtil.diff(start, ABuDateUtil.current_str_date(), check_order=False)
            # 每次返回300条数据
            n_folds = int(days / 300.0)

        for _ in xrange(0, n_folds):
            if next_start:
                url = url + BDApi.K_NET_CONNECT_START + str(next_start)
            # logging.info(url)
            data = ABuNetWork.get(url=url, timeout=K_TIME_OUT)
            temp_df = None
            if data is not None:
                temp_df = self.data_parser_cls(self._symbol, data.json()).df

            if temp_df is not None:
                next_start = int(temp_df.loc[temp_df.index[0], ['date']].values[0])
            kl_df = temp_df if kl_df is None else pd.concat([temp_df, kl_df])
            # 因为是从前向后请求，且与时间无关，所以可以直接在for里面中断
            if kl_df is None:
                return None

            """由于每次放回300条>1年的数据，所以超出总数就不再请求下一组"""
            if kl_df.shape[0] > ABuEnv.g_market_trade_year * n_folds:
                break

        return StockBaseMarket._fix_kline_pd(kl_df, n_folds, start, end)

    def minute(self, n_folds=5, *args, **kwargs):
        self._version2_log_cnt += 1
        cuid = ABuStrUtil.create_random_with_num_low(40)
        log_id = self._action_id + self._version2_log_cnt * 66
        device = random_from_list(StockBaseMarket.K_DEV_MODE_LIST)
        url = BDApi.MINUTE_NET_5D % (cuid, device, str(log_id), str(self._action_id), self._symbol.value)

        return ABuNetWork.get(url=url, timeout=K_TIME_OUT).json()


class TXApi(StockBaseMarket, SupportMixin):
    """tx数据源，支持A股"""

    K_NET_BASE = "http://ifzq.gtimg.cn/appstock/app/%sfqkline/get?p=1&param=%s,day,,,%d," \
                 "qfq&_appName=android&_dev=%s&_devId=%s&_mid=%s&_md5mid=%s&_appver=4.2.2&_ifChId=303&_screenW=%d" \
                 "&_screenH=%d&_osVer=%s&_uin=10000&_wxuin=20000&__random_suffix=%d"

    K_DB_TABLE_NAME = "values_table"
    K_DB_TABLE_SN = "stockCode"
    p_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir))
    K_SYMBOLS_DB = os.path.join(p_dir, 'RomDataBu/symbols_db.db')

    def __init__(self, symbol):
        """
        :param symbol: Symbol类型对象
        """
        super(TXApi, self).__init__(symbol)
        # 设置数据源解析对象类
        self.data_parser_cls = TXParser

    def kline(self, n_folds=2, start=None, end=None):
        """日k线接口"""
        # 计算需要获取的天数
        days = n_folds * ABuEnv.g_market_trade_year
        
        # 构建完整的腾讯财经历史数据请求URL
        cuid = ABuStrUtil.create_random_with_num_low(40)
        cuid_md5 = ABuMd5.md5_from_binary(cuid)
        random_suffix = ABuStrUtil.create_random_with_num(5)
        dev_mod = random_from_list(StockBaseMarket.K_DEV_MODE_LIST)
        os_ver = random_from_list(StockBaseMarket.K_OS_VERSION_LIST)
        screen = random_from_list(StockBaseMarket.K_PHONE_SCREEN)
        
        # 使用K_NET_BASE常量构建URL，获取历史数据
        url = TXApi.K_NET_BASE % (self._symbol.value.split('.')[0], self._symbol.value, days, 
                                 dev_mod, cuid, cuid, cuid_md5, screen[0], screen[1], os_ver, 
                                 int(random_suffix, 10))
        
        # 发送请求获取真实历史数据
        data = ABuNetWork.get(url=url, timeout=K_TIME_OUT)
        if data is not None:
            try:
                # 解析返回的JSON数据
                json_data = data.json()
                # 获取子市场信息
                sub_market = '.' + self._symbol.value.split('.')[1] if '.' in self._symbol.value else ''
                # 正确调用TXParser类，传递所有必要的参数
                kl_pd = self.data_parser_cls(self._symbol, sub_market, json_data).df
            except Exception as e:
                print(f'解析腾讯财经历史数据失败: {e}')
                kl_pd = None
        else:
            kl_pd = None

        return StockBaseMarket._fix_kline_pd(kl_pd, n_folds, start, end)

    def minute(self, n_fold=5, *args, **kwargs):
        """分钟k线接口"""
        raise NotImplementedError('TXApi minute NotImplementedError!')
