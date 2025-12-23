# -*- encoding:utf-8 -*-
"""
    因子正交化和处理模块
    包含因子正交化、相关性分析、生命周期管理等功能
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

__author__ = '量化策略师'


class AbuFactorOrthogonalization(object):
    """因子正交化处理类"""
    
    def __init__(self, factors_df, target_factor=None):
        """
        初始化因子正交化类
        :param factors_df: 因子数据DataFrame，行索引为时间，列索引为因子名称
        :param target_factor: 目标因子（如果只对特定因子进行正交化）
        """
        self.factors_df = factors_df.dropna()
        self.target_factor = target_factor
        self.orthogonalized_factors = None
        
    def calculate_correlation(self):
        """
        计算因子间的相关系数矩阵
        :return: 相关系数矩阵
        """
        return self.factors_df.corr()
    
    def plot_correlation_heatmap(self, figsize=(10, 8)):
        """
        绘制因子相关性热力图
        :param figsize: 图表尺寸
        """
        corr_matrix = self.calculate_correlation()
        plt.figure(figsize=figsize)
        plt.imshow(corr_matrix, cmap='coolwarm', interpolation='nearest')
        plt.colorbar()
        plt.xticks(np.arange(len(corr_matrix.columns)), corr_matrix.columns, rotation=45)
        plt.yticks(np.arange(len(corr_matrix.columns)), corr_matrix.columns)
        plt.title('Factor Correlation Heatmap')
        plt.tight_layout()
        plt.show()
    
    def orthogonalize(self, method='linear_regression'):
        """
        对因子进行正交化处理
        :param method: 正交化方法，可选'linear_regression'或'pca'
        :return: 正交化后的因子DataFrame
        """
        if method == 'linear_regression':
            return self._orthogonalize_linear_regression()
        elif method == 'pca':
            return self._orthogonalize_pca()
        else:
            raise ValueError("Invalid orthogonalization method. Choose 'linear_regression' or 'pca'.")
    
    def _orthogonalize_linear_regression(self):
        """
        使用线性回归方法进行因子正交化
        :return: 正交化后的因子DataFrame
        """
        factors = self.factors_df.copy()
        orthogonalized = pd.DataFrame(index=factors.index)
        
        if self.target_factor:
            # 只对目标因子进行正交化
            other_factors = factors.drop(columns=[self.target_factor])
            if other_factors.empty:
                return factors
                
            # 标准化因子
            scaler = StandardScaler()
            other_factors_scaled = scaler.fit_transform(other_factors)
            target_scaled = scaler.fit_transform(factors[[self.target_factor]])
            
            # 使用线性回归去除其他因子对目标因子的影响
            reg = LinearRegression()
            reg.fit(other_factors_scaled, target_scaled)
            target_orthogonalized = target_scaled - reg.predict(other_factors_scaled)
            
            orthogonalized[self.target_factor] = target_orthogonalized.flatten()
            orthogonalized = pd.concat([orthogonalized, other_factors], axis=1)
        else:
            # 对所有因子进行正交化
            for factor in factors.columns:
                other_factors = factors.drop(columns=[factor])
                if other_factors.empty:
                    orthogonalized[factor] = factors[factor]
                    continue
                    
                # 标准化因子
                scaler = StandardScaler()
                other_factors_scaled = scaler.fit_transform(other_factors)
                current_scaled = scaler.fit_transform(factors[[factor]])
                
                # 使用线性回归去除其他因子对当前因子的影响
                reg = LinearRegression()
                reg.fit(other_factors_scaled, current_scaled)
                current_orthogonalized = current_scaled - reg.predict(other_factors_scaled)
                
                orthogonalized[factor] = current_orthogonalized.flatten()
        
        self.orthogonalized_factors = orthogonalized
        return orthogonalized
    
    def _orthogonalize_pca(self):
        """
        使用PCA方法进行因子正交化
        :return: 正交化后的因子DataFrame
        """
        # 标准化因子
        scaler = StandardScaler()
        factors_scaled = scaler.fit_transform(self.factors_df)
        
        # 进行PCA分解
        pca = PCA(n_components=len(self.factors_df.columns))
        pca_result = pca.fit_transform(factors_scaled)
        
        # 将PCA结果转换为DataFrame
        orthogonalized = pd.DataFrame(
            pca_result,
            index=self.factors_df.index,
            columns=[f'PC{i+1}' for i in range(len(self.factors_df.columns))]
        )
        
        self.orthogonalized_factors = orthogonalized
        self.pca_explained_variance_ratio_ = pca.explained_variance_ratio_
        
        return orthogonalized
    
    def get_explained_variance_ratio(self):
        """
        获取PCA方法的解释方差比
        :return: 解释方差比数组
        """
        if hasattr(self, 'pca_explained_variance_ratio_'):
            return self.pca_explained_variance_ratio_
        else:
            raise AttributeError("Explained variance ratio is only available after PCA orthogonalization.")
    
    def plot_explained_variance(self):
        """
        绘制PCA解释方差图
        """
        if not hasattr(self, 'pca_explained_variance_ratio_'):
            # 如果还没有进行PCA，先执行
            self._orthogonalize_pca()
        
        explained_variance = self.pca_explained_variance_ratio_
        cumulative_variance = np.cumsum(explained_variance)
        
        plt.figure(figsize=(10, 6))
        plt.bar(range(1, len(explained_variance) + 1), explained_variance, alpha=0.8, align='center',
                label='Individual Explained Variance')
        plt.step(range(1, len(cumulative_variance) + 1), cumulative_variance, where='mid',
                 label='Cumulative Explained Variance')
        plt.ylabel('Explained Variance Ratio')
        plt.xlabel('Principal Components')
        plt.title('PCA Explained Variance')
        plt.legend(loc='best')
        plt.tight_layout()
        plt.show()


class AbuFactorLifecycleManager(object):
    """因子生命周期管理类"""
    
    def __init__(self, factors_df, returns_df):
        """
        初始化因子生命周期管理类
        :param factors_df: 因子数据DataFrame
        :param returns_df: 收益数据DataFrame，与因子数据对应
        """
        self.factors_df = factors_df.dropna()
        self.returns_df = returns_df.dropna()
        # 对齐因子和收益数据
        common_index = self.factors_df.index.intersection(self.returns_df.index)
        self.factors_df = self.factors_df.loc[common_index]
        self.returns_df = self.returns_df.loc[common_index]
    
    def calculate_ic(self, lookahead_period=1):
        """
        计算因子的信息系数(IC)
        :param lookahead_period: 前瞻期数
        :return: IC值序列
        """
        ic_series = []
        for i in range(len(self.factors_df) - lookahead_period):
            factor_values = self.factors_df.iloc[i]
            future_returns = self.returns_df.iloc[i + lookahead_period]
            ic = factor_values.corr(future_returns, method='spearman')
            ic_series.append(ic)
        
        ic_index = self.factors_df.index[lookahead_period:]
        return pd.Series(ic_series, index=ic_index, name='IC')
    
    def calculate_factor_return(self, factor_name, quantile=5):
        """
        计算因子的分层收益
        :param factor_name: 因子名称
        :param quantile: 分层数量
        :return: 分层收益DataFrame
        """
        factor_values = self.factors_df[factor_name]
        quantiles = pd.qcut(factor_values, quantile, labels=False)
        
        factor_returns = []
        for q in range(quantile):
            quantile_returns = self.returns_df[quantiles == q].mean(axis=1)
            factor_returns.append(quantile_returns)
        
        factor_returns_df = pd.concat(factor_returns, axis=1)
        factor_returns_df.columns = [f'Q{i+1}' for i in range(quantile)]
        
        # 计算多空收益
        factor_returns_df['Long_Short'] = factor_returns_df[f'Q{quantile}'] - factor_returns_df['Q1']
        
        return factor_returns_df
    
    def analyze_factor_lifecycle(self, factor_name, lookahead_period=1, rolling_window=20):
        """
        分析因子生命周期
        :param factor_name: 因子名称
        :param lookahead_period: 前瞻期数
        :param rolling_window: 滚动窗口大小
        :return: 因子生命周期分析结果
        """
        # 计算IC值
        ic_series = self.calculate_ic(lookahead_period)
        
        # 计算滚动IC均值和标准差
        rolling_ic_mean = ic_series.rolling(window=rolling_window).mean()
        rolling_ic_std = ic_series.rolling(window=rolling_window).std()
        
        # 计算因子收益
        factor_returns = self.calculate_factor_return(factor_name)
        rolling_factor_return = factor_returns['Long_Short'].rolling(window=rolling_window).mean()
        
        # 绘制因子生命周期图表
        plt.figure(figsize=(12, 8))
        
        # IC分析
        plt.subplot(2, 1, 1)
        plt.plot(ic_series.index, ic_series, label='IC')
        plt.plot(rolling_ic_mean.index, rolling_ic_mean, label=f'Rolling IC Mean ({rolling_window}D)')
        plt.axhline(y=0, color='r', linestyle='--')
        plt.title(f'Factor IC Analysis - {factor_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 因子收益分析
        plt.subplot(2, 1, 2)
        plt.plot(factor_returns.index, factor_returns['Long_Short'], label='Long-Short Return')
        plt.plot(rolling_factor_return.index, rolling_factor_return, 
                 label=f'Rolling Return Mean ({rolling_window}D)')
        plt.axhline(y=0, color='r', linestyle='--')
        plt.title(f'Factor Return Analysis - {factor_name}')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
        
        # 返回分析结果
        analysis_result = {
            'ic_series': ic_series,
            'rolling_ic_mean': rolling_ic_mean,
            'rolling_ic_std': rolling_ic_std,
            'factor_returns': factor_returns,
            'rolling_factor_return': rolling_factor_return
        }
        
        return analysis_result
    
    def check_factor_decay(self, factor_name, max_lookahead=20):
        """
        检查因子的衰减情况
        :param factor_name: 因子名称
        :param max_lookahead: 最大前瞻期数
        :return: 因子衰减结果
        """
        ic_values = []
        lookahead_periods = range(1, max_lookahead + 1)
        
        for period in lookahead_periods:
            ic_series = self.calculate_ic(period)
            ic_values.append(ic_series.mean())
        
        # 绘制因子衰减曲线
        plt.figure(figsize=(10, 6))
        plt.plot(lookahead_periods, ic_values, marker='o')
        plt.xlabel('Lookahead Periods')
        plt.ylabel('Average IC')
        plt.title(f'Factor Decay Analysis - {factor_name}')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()
        
        return pd.Series(ic_values, index=lookahead_periods, name='Average IC')


def demo_factor_orthogonalization():
    """因子正交化演示函数"""
    # 创建模拟因子数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    n_dates = len(dates)
    
    # 创建相关的因子数据
    factor1 = np.random.randn(n_dates)
    factor2 = factor1 * 0.7 + np.random.randn(n_dates) * 0.5  # 与factor1相关
    factor3 = np.random.randn(n_dates) * 0.8 + np.random.randn(n_dates) * 0.4  # 与其他因子弱相关
    
    factors_df = pd.DataFrame({
        'Factor1': factor1,
        'Factor2': factor2,
        'Factor3': factor3
    }, index=dates)
    
    # 创建因子正交化实例
    ortho = AbuFactorOrthogonalization(factors_df)
    
    # 计算原始相关性
    print("Original Correlation Matrix:")
    print(ortho.calculate_correlation())
    
    # 进行线性回归正交化
    ortho_factors_lr = ortho.orthogonalize(method='linear_regression')
    print("\nOrthogonalized Correlation Matrix (Linear Regression):")
    print(ortho_factors_lr.corr())
    
    # 进行PCA正交化
    ortho_factors_pca = ortho.orthogonalize(method='pca')
    print("\nOrthogonalized Correlation Matrix (PCA):")
    print(ortho_factors_pca.corr())
    
    print("\nPCA Explained Variance Ratio:")
    print(ortho.get_explained_variance_ratio())


if __name__ == '__main__':
    demo_factor_orthogonalization()