# -*- encoding:utf-8 -*-
"""
    集成学习模块
    包含Stacking、Bagging等集成学习方法和基于信息论的策略权重分配算法
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
import pandas as pd
from sklearn.ensemble import (BaggingClassifier, BaggingRegressor, 
                              RandomForestClassifier, RandomForestRegressor,
                              AdaBoostClassifier, AdaBoostRegressor, 
                              GradientBoostingClassifier, GradientBoostingRegressor)
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.model_selection import KFold, StratifiedKFold, train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.base import BaseEstimator, ClassifierMixin, RegressorMixin, clone
from scipy.stats import entropy
import matplotlib.pyplot as plt

__author__ = '量化策略师'


class AbuStackingModel(BaseEstimator):
    """Stacking集成学习模型"""
    
    def __init__(self, base_models, meta_model, n_folds=5, stratified=True, regression=False):
        """
        初始化Stacking模型
        :param base_models: 基础模型列表
        :param meta_model: 元模型
        :param n_folds: K折交叉验证的折数
        :param stratified: 是否使用分层交叉验证
        :param regression: 是否为回归问题
        """
        self.base_models = base_models
        self.meta_model = meta_model
        self.n_folds = n_folds
        self.stratified = stratified
        self.regression = regression
        self.models = []
        
    def fit(self, X, y):
        """
        训练Stacking模型
        :param X: 训练特征
        :param y: 训练标签
        :return: 训练好的模型
        """
        self.models = []
        
        # 创建K折交叉验证
        if self.stratified and not self.regression:
            kf = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=42)
        else:
            kf = KFold(n_splits=self.n_folds, shuffle=True, random_state=42)
        
        # 为每个基础模型创建元特征
        meta_features = np.zeros((X.shape[0], len(self.base_models) * (1 if self.regression else self.base_models[0].classes_.shape[0])))
        
        for i, model in enumerate(self.base_models):
            self.models.append([])
            
            for train_idx, val_idx in kf.split(X, y):
                # 训练基础模型
                model_fold = clone(model)
                model_fold.fit(X[train_idx], y[train_idx])
                self.models[i].append(model_fold)
                
                # 生成元特征
                if self.regression:
                    meta_features[val_idx, i] = model_fold.predict(X[val_idx])
                else:
                    meta_features[val_idx, i * self.base_models[0].classes_.shape[0]:(i + 1) * self.base_models[0].classes_.shape[0]] = \
                        model_fold.predict_proba(X[val_idx])
        
        # 训练元模型
        self.meta_model.fit(meta_features, y)
        
        return self
    
    def predict(self, X):
        """
        预测
        :param X: 输入特征
        :return: 预测结果
        """
        # 为每个基础模型生成元特征
        meta_features = np.zeros((X.shape[0], len(self.base_models) * (1 if self.regression else self.base_models[0].classes_.shape[0])))
        
        for i, models in enumerate(self.models):
            fold_predictions = np.zeros((X.shape[0], 1 if self.regression else self.base_models[0].classes_.shape[0]))
            
            for model in models:
                if self.regression:
                    fold_predictions += model.predict(X).reshape(-1, 1)
                else:
                    fold_predictions += model.predict_proba(X)
            
            # 取平均
            fold_predictions /= len(models)
            
            if self.regression:
                meta_features[:, i] = fold_predictions.flatten()
            else:
                meta_features[:, i * self.base_models[0].classes_.shape[0]:(i + 1) * self.base_models[0].classes_.shape[0]] = fold_predictions
        
        # 使用元模型预测
        return self.meta_model.predict(meta_features)
    
    def predict_proba(self, X):
        """
        预测概率（分类问题）
        :param X: 输入特征
        :return: 预测概率
        """
        if self.regression:
            raise ValueError("predict_proba is only available for classification models")
        
        # 为每个基础模型生成元特征
        meta_features = np.zeros((X.shape[0], len(self.base_models) * self.base_models[0].classes_.shape[0]))
        
        for i, models in enumerate(self.models):
            fold_predictions = np.zeros((X.shape[0], self.base_models[0].classes_.shape[0]))
            
            for model in models:
                fold_predictions += model.predict_proba(X)
            
            # 取平均
            fold_predictions /= len(models)
            
            meta_features[:, i * self.base_models[0].classes_.shape[0]:(i + 1) * self.base_models[0].classes_.shape[0]] = fold_predictions
        
        # 使用元模型预测概率
        return self.meta_model.predict_proba(meta_features)


class AbuBaggingModel(BaseEstimator):
    """自定义Bagging模型"""
    
    def __init__(self, base_model, n_estimators=10, max_samples=1.0, max_features=1.0, regression=False):
        """
        初始化Bagging模型
        :param base_model: 基础模型
        :param n_estimators: 模型数量
        :param max_samples: 每棵树使用的样本比例
        :param max_features: 每棵树使用的特征比例
        :param regression: 是否为回归问题
        """
        self.base_model = base_model
        self.n_estimators = n_estimators
        self.max_samples = max_samples
        self.max_features = max_features
        self.regression = regression
        self.models = []
        self.features_indices = []
        
    def fit(self, X, y):
        """
        训练Bagging模型
        :param X: 训练特征
        :param y: 训练标签
        :return: 训练好的模型
        """
        self.models = []
        self.features_indices = []
        n_samples, n_features = X.shape
        
        for _ in range(self.n_estimators):
            # 随机采样样本
            sample_indices = np.random.choice(n_samples, size=int(n_samples * self.max_samples), replace=True)
            
            # 随机选择特征
            feature_indices = np.random.choice(n_features, size=int(n_features * self.max_features), replace=False)
            self.features_indices.append(feature_indices)
            
            # 训练基础模型
            model = clone(self.base_model)
            model.fit(X[sample_indices][:, feature_indices], y[sample_indices])
            self.models.append(model)
        
        return self
    
    def predict(self, X):
        """
        预测
        :param X: 输入特征
        :return: 预测结果
        """
        n_samples = X.shape[0]
        predictions = np.zeros((n_samples, len(self.models)))
        
        for i, (model, feature_indices) in enumerate(zip(self.models, self.features_indices)):
            predictions[:, i] = model.predict(X[:, feature_indices])
        
        if self.regression:
            # 回归问题取平均
            return np.mean(predictions, axis=1)
        else:
            # 分类问题投票
            return np.apply_along_axis(lambda x: np.bincount(x.astype(int)).argmax(), axis=1, arr=predictions)


class AbuInfoTheoryWeighting(object):
    """基于信息论的策略权重分配"""
    
    def __init__(self, strategies_returns):
        """
        初始化信息论权重分配
        :param strategies_returns: 策略收益矩阵（行：时间，列：策略）
        """
        self.strategies_returns = strategies_returns
        self.weights = None
    
    def calculate_mutual_information(self, x, y):
        """
        计算两个变量之间的互信息
        :param x: 第一个变量
        :param y: 第二个变量
        :return: 互信息值
        """
        # 离散化变量
        x_discrete = pd.cut(x, bins=10, labels=False)
        y_discrete = pd.cut(y, bins=10, labels=False)
        
        # 计算联合概率分布
        joint_prob, _, _ = np.histogram2d(x_discrete, y_discrete, bins=10, density=True)
        joint_prob = joint_prob.flatten()
        
        # 计算边缘概率分布
        x_prob, _ = np.histogram(x_discrete, bins=10, density=True)
        y_prob, _ = np.histogram(y_discrete, bins=10, density=True)
        
        # 计算互信息
        mi = 0.0
        for i in range(10):
            for j in range(10):
                idx = i * 10 + j
                if joint_prob[idx] > 0 and x_prob[i] > 0 and y_prob[j] > 0:
                    mi += joint_prob[idx] * np.log2(joint_prob[idx] / (x_prob[i] * y_prob[j]))
        
        return mi
    
    def calculate_entropy(self, x):
        """
        计算变量的熵
        :param x: 变量
        :return: 熵值
        """
        # 离散化变量
        x_discrete = pd.cut(x, bins=10, labels=False)
        
        # 计算概率分布
        prob, _ = np.histogram(x_discrete, bins=10, density=True)
        
        # 计算熵
        return entropy(prob, base=2)
    
    def maximum_diversity_weighting(self):
        """
        最大多样性权重分配
        :return: 策略权重
        """
        n_strategies = self.strategies_returns.shape[1]
        
        # 计算策略之间的互信息矩阵
        mi_matrix = np.zeros((n_strategies, n_strategies))
        for i in range(n_strategies):
            for j in range(n_strategies):
                if i != j:
                    mi_matrix[i, j] = self.calculate_mutual_information(
                        self.strategies_returns[:, i], self.strategies_returns[:, j]
                    )
        
        # 计算每个策略的平均互信息（与其他策略的平均相似度）
        avg_mi = np.mean(mi_matrix, axis=1)
        
        # 计算权重：互信息越低（多样性越高），权重越高
        self.weights = (1 - avg_mi) / np.sum(1 - avg_mi)
        
        return self.weights
    
    def entropy_weighting(self):
        """
        熵权法权重分配
        :return: 策略权重
        """
        n_strategies = self.strategies_returns.shape[1]
        
        # 计算每个策略的熵
        entropy_values = np.zeros(n_strategies)
        for i in range(n_strategies):
            entropy_values[i] = self.calculate_entropy(self.strategies_returns[:, i])
        
        # 计算权重：熵越高（不确定性越高，提供的信息越多），权重越高
        self.weights = entropy_values / np.sum(entropy_values)
        
        return self.weights
    
    def information_ratio_weighting(self):
        """
        信息比率权重分配
        :return: 策略权重
        """
        # 计算每个策略的信息比率
        mean_returns = np.mean(self.strategies_returns, axis=0)
        std_returns = np.std(self.strategies_returns, axis=0)
        
        # 避免除以零
        std_returns[std_returns == 0] = 1e-10
        
        information_ratios = mean_returns / std_returns
        
        # 计算权重：信息比率越高，权重越高
        self.weights = information_ratios / np.sum(information_ratios)
        
        return self.weights
    
    def combined_weighting(self, alpha=0.3, beta=0.3, gamma=0.4):
        """
        组合权重分配
        :param alpha: 最大多样性权重的权重
        :param beta: 熵权法的权重
        :param gamma: 信息比率权重的权重
        :return: 策略权重
        """
        # 计算各种权重
        w_md = self.maximum_diversity_weighting()
        w_ent = self.entropy_weighting()
        w_ir = self.information_ratio_weighting()
        
        # 组合权重
        self.weights = alpha * w_md + beta * w_ent + gamma * w_ir
        self.weights = self.weights / np.sum(self.weights)  # 归一化
        
        return self.weights
    
    def plot_weights(self, figsize=(10, 6)):
        """
        绘制策略权重
        :param figsize: 图表尺寸
        """
        if self.weights is None:
            raise ValueError("Weights not calculated yet. Call one of the weighting methods first.")
        
        plt.figure(figsize=figsize)
        strategies = [f'Strategy {i+1}' for i in range(len(self.weights))]
        plt.bar(strategies, self.weights)
        plt.xlabel('Strategies')
        plt.ylabel('Weights')
        plt.title('Strategy Weights Distribution')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()


class AbuDynamicPortfolio(object):
    """动态策略组合"""
    
    def __init__(self, strategies_returns, market_states):
        """
        初始化动态策略组合
        :param strategies_returns: 策略收益矩阵（行：时间，列：策略）
        :param market_states: 市场状态序列（与策略收益时间对应）
        """
        self.strategies_returns = strategies_returns
        self.market_states = market_states
        self.state_weights = None
    
    def calculate_state_weights(self):
        """
        计算不同市场状态下的策略权重
        :return: 状态权重字典
        """
        unique_states = np.unique(self.market_states)
        self.state_weights = {}
        
        for state in unique_states:
            # 获取该市场状态下的收益数据
            state_returns = self.strategies_returns[self.market_states == state]
            
            # 使用信息论权重分配
            info_weighting = AbuInfoTheoryWeighting(state_returns)
            weights = info_weighting.combined_weighting()
            self.state_weights[state] = weights
        
        return self.state_weights
    
    def generate_dynamic_returns(self):
        """
        生成动态策略组合的收益
        :return: 动态组合收益序列
        """
        if self.state_weights is None:
            self.calculate_state_weights()
        
        dynamic_returns = np.zeros(len(self.strategies_returns))
        
        for i in range(len(self.strategies_returns)):
            state = self.market_states[i]
            weights = self.state_weights[state]
            dynamic_returns[i] = np.dot(self.strategies_returns[i], weights)
        
        return dynamic_returns
    
    def plot_performance(self, figsize=(12, 8)):
        """
        绘制动态组合与静态组合的性能对比
        :param figsize: 图表尺寸
        """
        # 生成动态组合收益
        dynamic_returns = self.generate_dynamic_returns()
        
        # 生成等权重组合收益
        equal_weights = np.ones(self.strategies_returns.shape[1]) / self.strategies_returns.shape[1]
        equal_returns = np.dot(self.strategies_returns, equal_weights)
        
        # 计算累计收益
        dynamic_cumulative = np.cumprod(1 + dynamic_returns)
        equal_cumulative = np.cumprod(1 + equal_returns)
        
        plt.figure(figsize=figsize)
        plt.plot(dynamic_cumulative, label='Dynamic Portfolio')
        plt.plot(equal_cumulative, label='Equal Weighted Portfolio')
        plt.xlabel('Time')
        plt.ylabel('Cumulative Return')
        plt.title('Dynamic vs Static Portfolio Performance')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()


def demo_ensemble_learning():
    """集成学习演示函数"""
    from sklearn.datasets import make_classification
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.svm import SVC
    from sklearn.neighbors import KNeighborsClassifier
    
    # 创建分类数据集
    X, y = make_classification(n_samples=1000, n_features=20, n_informative=10, 
                               n_classes=2, random_state=42)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 定义基础模型
    base_models = [
        DecisionTreeClassifier(max_depth=5, random_state=42),
        SVC(probability=True, random_state=42),
        KNeighborsClassifier(n_neighbors=5)
    ]
    
    # 定义元模型
    meta_model = LogisticRegression(random_state=42)
    
    # 创建Stacking模型
    stacking_model = AbuStackingModel(base_models, meta_model, n_folds=5, stratified=True, regression=False)
    
    # 训练模型
    stacking_model.fit(X_train, y_train)
    
    # 预测
    y_pred = stacking_model.predict(X_test)
    
    # 评估模型
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Stacking Model Accuracy: {accuracy:.4f}")
    
    # 比较单个模型的性能
    for i, model in enumerate(base_models):
        model.fit(X_train, y_train)
        y_pred_single = model.predict(X_test)
        accuracy_single = accuracy_score(y_test, y_pred_single)
        print(f"Model {i+1} Accuracy: {accuracy_single:.4f}")


if __name__ == '__main__':
    demo_ensemble_learning()