# -*- encoding:utf-8 -*-
"""
    基本面和另类数据因子模块
    包含财务比率、分析师评级、情绪数据等因子
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from .ABuFactorBuyBase import AbuFactorBuyBase, BuyCallMixin, BuyPutMixin
import numpy as np
import pandas as pd

__author__ = '量化策略师'


# noinspection PyAttributeOutsideInit
class AbuFactorFundamentalPE(AbuFactorBuyBase, BuyCallMixin):
    """基于市盈率(PE)的买入因子：低PE价值投资策略"""

    def _init_self(self, **kwargs):
        """初始化参数"""
        # PE阈值，默认15
        self.pe_threshold = kwargs.get('pe_threshold', 15)
        # 因子名称
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.pe_threshold)

    def fit_day(self, today):
        """
        拟合买入策略：当PE低于阈值时买入
        :param today: 当前交易日数据
        :return: 买入订单或None
        """
        # 检查是否有PE数据
        if not hasattr(today, 'fundamental') or 'pe' not in today.fundamental:
            return None
        
        # 获取当前PE值
        current_pe = today.fundamental['pe']
        
        # PE为正且低于阈值时买入
        if current_pe > 0 and current_pe < self.pe_threshold:
            return self.buy_tomorrow()
        
        return None


# noinspection PyAttributeOutsideInit
class AbuFactorFundamentalPB(AbuFactorBuyBase, BuyCallMixin):
    """基于市净率(PB)的买入因子：低PB价值投资策略"""

    def _init_self(self, **kwargs):
        """初始化参数"""
        # PB阈值，默认1.5
        self.pb_threshold = kwargs.get('pb_threshold', 1.5)
        # 因子名称
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.pb_threshold)

    def fit_day(self, today):
        """
        拟合买入策略：当PB低于阈值时买入
        :param today: 当前交易日数据
        :return: 买入订单或None
        """
        # 检查是否有PB数据
        if not hasattr(today, 'fundamental') or 'pb' not in today.fundamental:
            return None
        
        # 获取当前PB值
        current_pb = today.fundamental['pb']
        
        # PB为正且低于阈值时买入
        if current_pb > 0 and current_pb < self.pb_threshold:
            return self.buy_tomorrow()
        
        return None


# noinspection PyAttributeOutsideInit
class AbuFactorAnalystRating(AbuFactorBuyBase, BuyCallMixin):
    """基于分析师评级的买入因子：分析师上调评级时买入"""

    def _init_self(self, **kwargs):
        """初始化参数"""
        # 因子名称
        self.factor_name = self.__class__.__name__

    def fit_day(self, today):
        """
        拟合买入策略：分析师上调评级时买入
        :param today: 当前交易日数据
        :return: 买入订单或None
        """
        # 检查是否有分析师评级数据
        if not hasattr(today, 'analyst') or 'rating_change' not in today.analyst:
            return None
        
        # 获取评级变化
        rating_change = today.analyst['rating_change']
        
        # 分析师上调评级时买入
        if rating_change == 'upgrade':
            return self.buy_tomorrow()
        
        return None


# noinspection PyAttributeOutsideInit
class AbuFactorSentimentPositive(AbuFactorBuyBase, BuyCallMixin):
    """基于市场情绪的买入因子：正面情绪高涨时买入"""

    def _init_self(self, **kwargs):
        """初始化参数"""
        # 情绪阈值，默认0.7
        self.sentiment_threshold = kwargs.get('sentiment_threshold', 0.7)
        # 因子名称
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.sentiment_threshold)

    def fit_day(self, today):
        """
        拟合买入策略：当市场情绪高于阈值时买入
        :param today: 当前交易日数据
        :return: 买入订单或None
        """
        # 检查是否有情绪数据
        if not hasattr(today, 'sentiment') or 'score' not in today.sentiment:
            return None
        
        # 获取当前情绪得分
        sentiment_score = today.sentiment['score']
        
        # 情绪得分高于阈值时买入
        if sentiment_score > self.sentiment_threshold:
            return self.buy_tomorrow()
        
        return None


# noinspection PyAttributeOutsideInit
class AbuFactorSentimentNegative(AbuFactorBuyBase, BuyPutMixin):
    """基于市场情绪的卖出因子：负面情绪高涨时卖出"""

    def _init_self(self, **kwargs):
        """初始化参数"""
        # 情绪阈值，默认0.3
        self.sentiment_threshold = kwargs.get('sentiment_threshold', 0.3)
        # 因子名称
        self.factor_name = '{}:{}'.format(self.__class__.__name__, self.sentiment_threshold)

    def fit_day(self, today):
        """
        拟合卖出策略：当市场情绪低于阈值时卖出
        :param today: 当前交易日数据
        :return: 卖出订单或None
        """
        # 检查是否有情绪数据
        if not hasattr(today, 'sentiment') or 'score' not in today.sentiment:
            return None
        
        # 获取当前情绪得分
        sentiment_score = today.sentiment['score']
        
        # 情绪得分低于阈值时卖出
        if sentiment_score < self.sentiment_threshold:
            return self.buy_tomorrow()  # 注意：BuyPutMixin中buy_tomorrow实际是看跌操作
        
        return None