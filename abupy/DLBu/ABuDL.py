from __future__ import absolute_import

# noinspection PyUnresolvedReferences
from .ABuDLImgStd import *
# noinspection PyUnresolvedReferences
from .ABuDLTVSplit import *

import numpy as np
import pandas as pd
import os

__author__ = '量化策略师'


class AbuDL(object):
    """深度学习基础类，提供通用的深度学习功能"""
    
    def __init__(self, model_path=None, **kwargs):
        """
        初始化AbuDL类
        :param model_path: 预训练模型路径
        :param kwargs: 其他参数
        """
        self.model_path = model_path
        self.model = None
        self.scaler = None
        
    def build_model(self, **kwargs):
        """
        构建深度学习模型
        :param kwargs: 模型构建参数
        :return: 构建好的模型
        """
        raise NotImplementedError("子类必须实现build_model方法")
    
    def fit(self, X, y, **kwargs):
        """
        训练模型
        :param X: 输入数据
        :param y: 目标数据
        :param kwargs: 训练参数
        :return: 训练历史
        """
        raise NotImplementedError("子类必须实现fit方法")
    
    def predict(self, X):
        """
        预测数据
        :param X: 输入数据
        :return: 预测结果
        """
        raise NotImplementedError("子类必须实现predict方法")
    
    def save_model(self, path=None):
        """
        保存模型
        :param path: 保存路径
        """
        if path is None:
            path = self.model_path
        
        if path is None:
            raise ValueError("保存路径不能为空")
        
        if self.model is None:
            raise ValueError("模型未构建")
        
        # 保存模型
        if hasattr(self.model, 'save_weights'):
            self.model.save_weights(path)
            print(f"模型权重已保存到 {path}")
        elif hasattr(self.model, 'save'):
            self.model.save(path)
            print(f"模型已保存到 {path}")
        else:
            raise NotImplementedError("模型保存方法未实现")
    
    def load_model(self, path=None):
        """
        加载模型
        :param path: 模型路径
        """
        if path is None:
            path = self.model_path
        
        if path is None:
            raise ValueError("模型路径不能为空")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"模型文件不存在: {path}")
        
        if self.model is None:
            raise ValueError("模型未构建，请先调用build_model方法")
        
        # 加载模型
        if hasattr(self.model, 'load_weights'):
            self.model.load_weights(path)
            print(f"模型权重已从 {path} 加载")
        elif hasattr(self.model, 'load'):
            self.model = self.model.load(path)
            print(f"模型已从 {path} 加载")
        else:
            raise NotImplementedError("模型加载方法未实现")
    
    def preprocess_data(self, data, **kwargs):
        """
        预处理数据
        :param data: 输入数据
        :param kwargs: 预处理参数
        :return: 预处理后的数据
        """
        raise NotImplementedError("子类必须实现preprocess_data方法")
    
    def evaluate(self, X, y, **kwargs):
        """
        评估模型
        :param X: 输入数据
        :param y: 目标数据
        :param kwargs: 评估参数
        :return: 评估结果
        """
        if self.model is None:
            raise ValueError("模型未构建")
        
        return self.model.evaluate(X, y, **kwargs)
    
    @staticmethod
    def create_data_generator(X, y, batch_size=32, shuffle=True, **kwargs):
        """
        创建数据生成器
        :param X: 输入数据
        :param y: 目标数据
        :param batch_size: 批次大小
        :param shuffle: 是否打乱数据
        :param kwargs: 其他参数
        :return: 数据生成器
        """
        # 简单的数据生成器实现
        while True:
            indices = np.arange(len(X))
            if shuffle:
                np.random.shuffle(indices)
            
            for i in range(0, len(X), batch_size):
                batch_indices = indices[i:i+batch_size]
                yield X[batch_indices], y[batch_indices]
