# -*- encoding:utf-8 -*-
"""
    市场状态识别与适应模块
    包含HMM市场状态识别、波动率聚类和自适应策略
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from hmmlearn import hmm
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

__author__ = '量化策略师'


class AbuHMMMarketState(object):
    """使用隐马尔可夫模型（HMM）识别市场状态"""
    
    def __init__(self, n_states=3, n_iter=1000, random_state=42):
        """
        初始化HMM模型
        :param n_states: 市场状态数量
        :param n_iter: 迭代次数
        :param random_state: 随机种子
        """
        self.n_states = n_states
        self.model = hmm.GaussianHMM(n_components=n_states, n_iter=n_iter, random_state=random_state)
        self.market_states = None
        self.state_probabilities = None
    
    def fit(self, returns):
        """
        训练HMM模型
        :param returns: 收益率序列
        :return: 训练好的模型
        """
        # 准备特征数据
        X = returns.values.reshape(-1, 1)
        
        # 训练模型
        self.model.fit(X)
        
        # 预测市场状态
        self.market_states = self.model.predict(X)
        self.state_probabilities = self.model.predict_proba(X)
        
        return self
    
    def predict(self, returns):
        """
        预测市场状态
        :param returns: 收益率序列
        :return: 市场状态和状态概率
        """
        X = returns.values.reshape(-1, 1)
        states = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        return states, probabilities
    
    def get_state_description(self):
        """
        获取市场状态描述
        :return: 状态描述字典
        """
        # 计算每个状态的平均收益率和波动率
        state_means = self.model.means_.flatten()
        state_covars = self.model.covars_.flatten()
        state_volatility = np.sqrt(state_covars)
        
        # 根据收益率和波动率为状态命名
        state_descriptions = {}
        for i in range(self.n_states):
            if state_means[i] > 0 and state_volatility[i] < np.mean(state_volatility):
                state_descriptions[i] = '牛市（低波动）'
            elif state_means[i] > 0 and state_volatility[i] >= np.mean(state_volatility):
                state_descriptions[i] = '牛市（高波动）'
            elif state_means[i] <= 0 and state_volatility[i] < np.mean(state_volatility):
                state_descriptions[i] = '熊市（低波动）'
            else:
                state_descriptions[i] = '熊市（高波动）'
        
        return state_descriptions
    
    def plot_states(self, index, figsize=(12, 8)):
        """
        绘制市场状态变化
        :param index: 时间索引
        :param figsize: 图表尺寸
        """
        plt.figure(figsize=figsize)
        
        # 绘制状态概率
        ax1 = plt.subplot(2, 1, 1)
        for i in range(self.n_states):
            ax1.plot(index, self.state_probabilities[:, i], label=f'State {i}')
        ax1.set_ylabel('State Probability')
        ax1.set_title('Market State Probabilities')
        ax1.legend()
        
        # 绘制市场状态
        ax2 = plt.subplot(2, 1, 2, sharex=ax1)
        ax2.plot(index, self.market_states, 'o-', markersize=3)
        ax2.set_ylabel('Market State')
        ax2.set_xlabel('Date')
        ax2.set_title('Identified Market States')
        
        plt.tight_layout()
        plt.show()


class AbuVolatilityClustering(object):
    """基于波动率聚类的市场状态识别"""
    
    def __init__(self, n_clusters=3, clustering_method='kmeans', window=20):
        """
        初始化波动率聚类模型
        :param n_clusters: 聚类数量
        :param clustering_method: 聚类方法 ('kmeans' 或 'gmm')
        :param window: 计算波动率的窗口大小
        """
        self.n_clusters = n_clusters
        self.clustering_method = clustering_method
        self.window = window
        self.model = None
        self.market_states = None
        self.volatility = None
    
    def fit(self, prices):
        """
        训练波动率聚类模型
        :param prices: 价格序列
        :return: 训练好的模型
        """
        # 计算滚动波动率
        returns = prices.pct_change().dropna()
        self.volatility = returns.rolling(window=self.window).std() * np.sqrt(252)
        self.volatility = self.volatility.dropna()
        
        # 准备特征数据
        X = self.volatility.values.reshape(-1, 1)
        
        # 创建并训练聚类模型
        if self.clustering_method == 'kmeans':
            self.model = KMeans(n_clusters=self.n_clusters, random_state=42)
        elif self.clustering_method == 'gmm':
            self.model = GaussianMixture(n_components=self.n_clusters, random_state=42)
        else:
            raise ValueError(f"不支持的聚类方法: {self.clustering_method}")
        
        self.model.fit(X)
        
        # 预测市场状态
        if self.clustering_method == 'kmeans':
            self.market_states = self.model.predict(X)
        elif self.clustering_method == 'gmm':
            self.market_states = self.model.predict(X)
        
        return self
    
    def predict(self, prices):
        """
        预测市场状态
        :param prices: 价格序列
        :return: 市场状态
        """
        # 计算滚动波动率
        returns = prices.pct_change().dropna()
        volatility = returns.rolling(window=self.window).std() * np.sqrt(252)
        volatility = volatility.dropna()
        
        # 准备特征数据
        X = volatility.values.reshape(-1, 1)
        
        # 预测市场状态
        if self.clustering_method == 'kmeans':
            states = self.model.predict(X)
        elif self.clustering_method == 'gmm':
            states = self.model.predict(X)
        
        return states
    
    def get_state_description(self):
        """
        获取市场状态描述
        :return: 状态描述字典
        """
        # 根据波动率为状态命名
        if self.clustering_method == 'kmeans':
            cluster_centers = self.model.cluster_centers_.flatten()
        elif self.clustering_method == 'gmm':
            cluster_centers = self.model.means_.flatten()
        
        # 按波动率从小到大排序
        sorted_indices = np.argsort(cluster_centers)
        
        state_descriptions = {}
        for i, idx in enumerate(sorted_indices):
            if i == 0:
                state_descriptions[idx] = '低波动'
            elif i == 1:
                state_descriptions[idx] = '中波动'
            else:
                state_descriptions[idx] = '高波动'
        
        return state_descriptions
    
    def plot_volatility_states(self, prices, figsize=(12, 8)):
        """
        绘制波动率和市场状态
        :param prices: 价格序列
        :param figsize: 图表尺寸
        """
        plt.figure(figsize=figsize)
        
        # 绘制价格
        ax1 = plt.subplot(3, 1, 1)
        ax1.plot(prices, label='Price')
        ax1.set_ylabel('Price')
        ax1.set_title('Price, Volatility and Market States')
        ax1.legend()
        
        # 绘制波动率
        ax2 = plt.subplot(3, 1, 2, sharex=ax1)
        ax2.plot(self.volatility, label='Volatility', color='orange')
        ax2.set_ylabel('Volatility')
        ax2.legend()
        
        # 绘制市场状态
        ax3 = plt.subplot(3, 1, 3, sharex=ax1)
        ax3.plot(self.volatility.index, self.market_states, 'o-', markersize=3, label='Market State')
        ax3.set_ylabel('Market State')
        ax3.set_xlabel('Date')
        ax3.legend()
        
        plt.tight_layout()
        plt.show()


class AbuMarketCycle(object):
    """市场周期识别"""
    
    def __init__(self, short_window=20, medium_window=60, long_window=120):
        """
        初始化市场周期识别模型
        :param short_window: 短期移动平均线窗口
        :param medium_window: 中期移动平均线窗口
        :param long_window: 长期移动平均线窗口
        """
        self.short_window = short_window
        self.medium_window = medium_window
        self.long_window = long_window
        self.moving_averages = None
        self.market_cycle = None
    
    def fit(self, prices):
        """
        识别市场周期
        :param prices: 价格序列
        :return: 市场周期
        """
        # 计算移动平均线
        self.moving_averages = pd.DataFrame({
            'short_ma': prices.rolling(window=self.short_window).mean(),
            'medium_ma': prices.rolling(window=self.medium_window).mean(),
            'long_ma': prices.rolling(window=self.long_window).mean()
        })
        
        # 计算移动平均线的斜率
        short_ma_diff = self.moving_averages['short_ma'].diff()
        medium_ma_diff = self.moving_averages['medium_ma'].diff()
        long_ma_diff = self.moving_averages['long_ma'].diff()
        
        # 识别市场周期
        self.market_cycle = pd.Series(index=prices.index)
        
        for i in range(len(prices)):
            if pd.isna(self.moving_averages.iloc[i].any()):
                self.market_cycle.iloc[i] = -1  # 数据不足
                continue
            
            # 短期上升趋势
            if short_ma_diff.iloc[i] > 0 and medium_ma_diff.iloc[i] > 0 and long_ma_diff.iloc[i] > 0:
                if self.moving_averages['short_ma'].iloc[i] > self.moving_averages['medium_ma'].iloc[i] > self.moving_averages['long_ma'].iloc[i]:
                    self.market_cycle.iloc[i] = 2  # 牛市（强）
                else:
                    self.market_cycle.iloc[i] = 1  # 牛市（弱）
            # 短期下降趋势
            elif short_ma_diff.iloc[i] < 0 and medium_ma_diff.iloc[i] < 0 and long_ma_diff.iloc[i] < 0:
                if self.moving_averages['short_ma'].iloc[i] < self.moving_averages['medium_ma'].iloc[i] < self.moving_averages['long_ma'].iloc[i]:
                    self.market_cycle.iloc[i] = -2  # 熊市（强）
                else:
                    self.market_cycle.iloc[i] = -1  # 熊市（弱）
            # 震荡市
            else:
                self.market_cycle.iloc[i] = 0  # 震荡市
        
        return self
    
    def get_cycle_description(self):
        """
        获取市场周期描述
        :return: 周期描述字典
        """
        return {
            -2: '熊市（强）',
            -1: '熊市（弱）',
            0: '震荡市',
            1: '牛市（弱）',
            2: '牛市（强）'
        }
    
    def plot_cycle(self, prices, figsize=(12, 8)):
        """
        绘制市场周期
        :param prices: 价格序列
        :param figsize: 图表尺寸
        """
        plt.figure(figsize=figsize)
        
        # 绘制价格和移动平均线
        ax1 = plt.subplot(2, 1, 1)
        ax1.plot(prices, label='Price', alpha=0.7)
        ax1.plot(self.moving_averages['short_ma'], label=f'Short MA ({self.short_window})', alpha=0.7)
        ax1.plot(self.moving_averages['medium_ma'], label=f'Medium MA ({self.medium_window})', alpha=0.7)
        ax1.plot(self.moving_averages['long_ma'], label=f'Long MA ({self.long_window})', alpha=0.7)
        ax1.set_ylabel('Price')
        ax1.set_title('Price, Moving Averages and Market Cycle')
        ax1.legend()
        
        # 绘制市场周期
        ax2 = plt.subplot(2, 1, 2, sharex=ax1)
        ax2.plot(self.market_cycle, 'o-', markersize=3, label='Market Cycle')
        ax2.set_ylabel('Market Cycle')
        ax2.set_xlabel('Date')
        ax2.set_yticks([-2, -1, 0, 1, 2])
        ax2.set_yticklabels(['熊市（强）', '熊市（弱）', '震荡市', '牛市（弱）', '牛市（强）'])
        ax2.legend()
        
        plt.tight_layout()
        plt.show()


class AbuAdaptiveStrategy(object):
    """基于市场状态的自适应策略"""
    
    def __init__(self, strategies, state_identifier):
        """
        初始化自适应策略
        :param strategies: 策略字典 {策略名称: 策略对象}
        :param state_identifier: 市场状态识别器
        """
        self.strategies = strategies
        self.state_identifier = state_identifier
        self.strategy_allocations = None
    
    def fit(self, prices, returns):
        """
        训练自适应策略
        :param prices: 价格序列
        :param returns: 收益率序列
        :return: 自适应策略
        """
        # 识别市场状态
        if isinstance(self.state_identifier, AbuHMMMarketState):
            self.state_identifier.fit(returns)
            market_states = self.state_identifier.market_states
        elif isinstance(self.state_identifier, AbuVolatilityClustering):
            self.state_identifier.fit(prices)
            market_states = self.state_identifier.market_states
        elif isinstance(self.state_identifier, AbuMarketCycle):
            self.state_identifier.fit(prices)
            market_states = self.state_identifier.market_cycle
        else:
            raise ValueError(f"不支持的状态识别器类型: {type(self.state_identifier)}")
        
        # 计算每个策略在不同市场状态下的表现
        unique_states = np.unique(market_states)
        state_performance = {}
        
        for state in unique_states:
            if state == -1:  # 数据不足的状态
                continue
            
            # 获取该状态下的索引
            state_indices = np.where(market_states == state)[0]
            state_returns = returns.iloc[state_indices]
            
            # 计算每个策略在该状态下的表现
            state_performance[state] = {}
            for name, strategy in self.strategies.items():
                # 假设策略对象有predict方法返回信号
                signals = strategy.predict(prices.iloc[state_indices])
                strategy_returns = state_returns * signals
                
                # 使用夏普比率作为策略表现指标
                sharpe_ratio = np.mean(strategy_returns) / np.std(strategy_returns) if np.std(strategy_returns) > 0 else 0
                state_performance[state][name] = sharpe_ratio
        
        # 为每个状态选择表现最好的策略
        self.strategy_allocations = {}
        for state in state_performance:
            best_strategy = max(state_performance[state], key=state_performance[state].get)
            self.strategy_allocations[state] = best_strategy
        
        return self
    
    def generate_signals(self, prices, returns):
        """
        生成自适应策略信号
        :param prices: 价格序列
        :param returns: 收益率序列
        :return: 自适应策略信号
        """
        # 预测市场状态
        if isinstance(self.state_identifier, AbuHMMMarketState):
            states, _ = self.state_identifier.predict(returns)
        elif isinstance(self.state_identifier, AbuVolatilityClustering):
            states = self.state_identifier.predict(prices)
        elif isinstance(self.state_identifier, AbuMarketCycle):
            # 对于MarketCycle，我们需要重新计算
            self.state_identifier.fit(prices)
            states = self.state_identifier.market_cycle
        else:
            raise ValueError(f"不支持的状态识别器类型: {type(self.state_identifier)}")
        
        # 生成信号
        signals = pd.Series(index=returns.index)
        
        for i, state in enumerate(states):
            if state not in self.strategy_allocations:
                signals.iloc[i] = 0  # 默认不交易
                continue
            
            # 获取当前状态下的最优策略
            best_strategy_name = self.strategy_allocations[state]
            best_strategy = self.strategies[best_strategy_name]
            
            # 生成策略信号
            signal = best_strategy.predict(prices.iloc[[i]])
            signals.iloc[i] = signal
        
        return signals


def demo_market_state_analysis():
    """市场状态分析演示函数"""
    # 生成模拟价格数据
    np.random.seed(42)
    n_samples = 1000
    time = np.arange(n_samples)
    
    # 创建具有不同市场状态的价格序列
    prices = np.zeros(n_samples)
    prices[0] = 100
    
    # 阶段1: 牛市（低波动）
    for i in range(1, 200):
        prices[i] = prices[i-1] * (1 + np.random.normal(0.001, 0.005))
    
    # 阶段2: 牛市（高波动）
    for i in range(200, 400):
        prices[i] = prices[i-1] * (1 + np.random.normal(0.001, 0.02))
    
    # 阶段3: 熊市（低波动）
    for i in range(400, 600):
        prices[i] = prices[i-1] * (1 + np.random.normal(-0.001, 0.005))
    
    # 阶段4: 熊市（高波动）
    for i in range(600, 800):
        prices[i] = prices[i-1] * (1 + np.random.normal(-0.001, 0.02))
    
    # 阶段5: 震荡市
    for i in range(800, 1000):
        prices[i] = prices[i-1] * (1 + np.random.normal(0, 0.01))
    
    prices = pd.Series(prices, index=pd.date_range(start='2020-01-01', periods=n_samples, freq='D'))
    returns = prices.pct_change().dropna()
    
    print("=== 隐马尔可夫模型（HMM）市场状态识别 ===")
    hmm_model = AbuHMMMarketState(n_states=4)
    hmm_model.fit(returns)
    state_descriptions = hmm_model.get_state_description()
    print(f"市场状态描述: {state_descriptions}")
    
    print("\n=== 波动率聚类市场状态识别 ===")
    volatility_model = AbuVolatilityClustering(n_clusters=3, clustering_method='gmm', window=20)
    volatility_model.fit(prices)
    state_descriptions = volatility_model.get_state_description()
    print(f"市场状态描述: {state_descriptions}")
    
    print("\n=== 市场周期识别 ===")
    cycle_model = AbuMarketCycle(short_window=20, medium_window=60, long_window=120)
    cycle_model.fit(prices)
    cycle_descriptions = cycle_model.get_cycle_description()
    print(f"市场周期描述: {cycle_descriptions}")
    
    print("\n市场状态分析演示完成！")


if __name__ == '__main__':
    demo_market_state_analysis()
