# -*- encoding:utf-8 -*-
"""
    手续费模块
"""

from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import logging
from contextlib import contextmanager

import numpy as np
import pandas as pd

from ..CoreBu import ABuEnv
from ..CoreBu.ABuEnv import EMarketTargetType
from .ABuOrder import OrderMarket
from ..MarketBu import ABuMarket

__author__ = '阿布'
__weixin__ = 'abu_quant'


def calc_commission_cn(trade_cnt, price):
    """
    A股计算交易费用：印花税＋佣金： 印花税万3，佣金万2.5
    :param trade_cnt: 交易的股数（int）
    :param price: 每股的价格（人民币）
    :return: 计算结果手续费
    """
    cost = trade_cnt * price
    # 印花税万3，
    tax = cost * 0.0003
    # 佣金万2.5
    commission = cost * 0.00025
    # 佣金最低5
    commission = commission if commission > 5 else 5
    commission += tax
    return commission


class AbuCommission(object):
    """交易手续费计算，记录，分析类，在AbuCapital中实例化"""

    def __init__(self, commission_dict):
        """
        :param commission_dict: 代表用户自定义手续费计算dict对象，
                                key：buy_commission_func， 代表用户自定义买入计算费用方法
                                key：sell_commission_func，代表用户自定义卖出计算费用方法
        """
        self.commission_dict = commission_dict
        # 对象内部记录交易的pd.DataFrame对象，列设定
        self.df_columns = ['type', 'date', 'symbol', 'commission']
        # 构建手续费记录pd.DataFrame对象commission_df
        self.commission_df = pd.DataFrame(columns=self.df_columns)

    def __str__(self):
        """打印对象显示：如果有手续费记录，打印记录df，否则打印commission_df.info"""
        if self.commission_df.shape[0] == 0:
            return str(self.commission_df.info())
        return str(self.commission_df)

    __repr__ = __str__

    # noinspection PyMethodMayBeStatic
    def _commission_enter(self, a_order):
        """
        通过a_order对象进行交易对象市场类型转换，分配对应手续费计算方法
        :param a_order: 交易单对象AbuOrder实例
        :return: 佣金计算函数
        """
        # 只支持A股
        calc_commission_func = calc_commission_cn
        return calc_commission_func

    @contextmanager
    def buy_commission_func(self, a_order):
        """
        外部用with as 返回的list中需要加入计算的最终结果，否则不进行内部交易费用记录
        :param a_order: 买单对象AbuOrder实例
        """
        if self.commission_dict is not None and 'buy_commission_func' in self.commission_dict:
            # 如果有自定义计算交易费的方法使用自定义的
            buy_func = self.commission_dict['buy_commission_func']
        else:
            buy_func = self._commission_enter(a_order)

        # 使用list因为是可变类型，需要将外面的结果带回来
        commission_list = list()
        yield buy_func, commission_list

        # 如果有外部有append，说明需要记录手续费，且执行计算成功
        if len(commission_list) == 1:
            commission = commission_list[0]
            # 将买单对象AbuOrder实例中的数据转换成交易记录需要的np.array对象
            record = np.array(['buy', a_order.buy_date, a_order.buy_symbol, commission]).reshape(1, 4)
            record_df = pd.DataFrame(record, columns=self.df_columns)
            self.commission_df = pd.concat([self.commission_df, record_df], ignore_index=True)
        else:
            logging.info('buy_commission_func calc error')

    @contextmanager
    def sell_commission_func(self, a_order):
        """
        外部用with as 返回的list中需要加入计算的最终结果，否则不进行内部交易费用记录
        :param a_order: 卖单对象AbuOrder实例
        """
        if self.commission_dict is not None and 'sell_commission_func' in self.commission_dict:
            # 如果有自定义计算交易费的方法使用自定义的
            sell_func = self.commission_dict['sell_commission_func']
        else:
            sell_func = self._commission_enter(a_order)
        # 使用list因为是可变类型，需要将外面的结果带回来
        commission_list = list()

        yield sell_func, commission_list

        if len(commission_list) == 1:
            commission = commission_list[0]
            # 将卖单对象AbuOrder实例中的数据转换成交易记录需要的np.array对象
            record = np.array(['sell', a_order.sell_date, a_order.buy_symbol, commission]).reshape(1, 4)
            record_df = pd.DataFrame(record, columns=self.df_columns)
            self.commission_df = pd.concat([self.commission_df, record_df], ignore_index=True)
        else:
            logging.info('sell_commission_func calc error!!!')
