# -*- encoding:utf-8 -*-
"""
    CNN价格形态特征提取模块
    实现CNN模型用于识别K线形态和提取价格特征
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import os

__author__ = '量化策略师'


class AbuCNNPricePattern(object):
    """CNN价格形态识别模型"""
    
    def __init__(self, pattern_length=20, n_features=4, n_patterns=10, model_path=None):
        """
        初始化CNN价格形态识别模型
        :param pattern_length: K线形态长度
        :param n_features: 特征数量（如OHLC）
        :param n_patterns: 要识别的形态数量
        :param model_path: 预训练模型路径
        """
        self.pattern_length = pattern_length
        self.n_features = n_features
        self.n_patterns = n_patterns
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.label_encoder = LabelEncoder()
        self.model = self.build_cnn_model()
        
        if model_path and os.path.exists(model_path):
            self.model.load_weights(model_path)
            print(f"Loaded pre-trained model from {model_path}")
    
    def build_cnn_model(self):
        """
        构建CNN模型
        :return: CNN模型
        """
        model = models.Sequential()
        
        # 第一层卷积
        model.add(layers.Conv2D(32, (3, 3), activation='relu', 
                               input_shape=(self.pattern_length, self.n_features, 1)))
        model.add(layers.MaxPooling2D((2, 2)))
        
        # 第二层卷积
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        model.add(layers.MaxPooling2D((2, 2)))
        
        # 第三层卷积
        model.add(layers.Conv2D(64, (3, 3), activation='relu'))
        
        # 展平层
        model.add(layers.Flatten())
        
        # 全连接层
        model.add(layers.Dense(64, activation='relu'))
        model.add(layers.Dropout(0.5))
        
        # 输出层
        model.add(layers.Dense(self.n_patterns, activation='softmax'))
        
        # 编译模型
        model.compile(optimizer=optimizers.Adam(learning_rate=0.001),
                     loss='sparse_categorical_crossentropy',
                     metrics=['accuracy'])
        
        return model
    
    def preprocess_data(self, data, labels=None):
        """
        预处理数据
        :param data: 输入数据 (n_samples, pattern_length, n_features)
        :param labels: 标签数据
        :return: 预处理后的数据和标签
        """
        # 归一化特征
        n_samples, pattern_length, n_features = data.shape
        data_reshaped = data.reshape(-1, n_features)
        data_scaled = self.scaler.fit_transform(data_reshaped)
        data_processed = data_scaled.reshape(n_samples, pattern_length, n_features, 1)
        
        if labels is not None:
            # 编码标签
            labels_encoded = self.label_encoder.fit_transform(labels)
            return data_processed, labels_encoded
        
        return data_processed
    
    def fit(self, data, labels, epochs=50, batch_size=32, validation_split=0.2, save_path=None):
        """
        训练CNN模型
        :param data: 训练数据 (n_samples, pattern_length, n_features)
        :param labels: 训练标签
        :param epochs: 训练轮数
        :param batch_size: 批次大小
        :param validation_split: 验证集比例
        :param save_path: 模型保存路径
        :return: 训练历史
        """
        # 预处理数据
        X, y = self.preprocess_data(data, labels)
        
        # 数据增强
        datagen = ImageDataGenerator(
            rotation_range=10,
            width_shift_range=0.1,
            height_shift_range=0.1,
            zoom_range=0.1,
            horizontal_flip=True
        )
        
        # 训练模型
        history = self.model.fit(datagen.flow(X, y, batch_size=batch_size),
                               epochs=epochs,
                               validation_data=(X[int(len(X)*(1-validation_split)):], 
                                               y[int(len(y)*(1-validation_split)):]))
        
        if save_path:
            self.model.save_weights(save_path)
            print(f"Model saved to {save_path}")
        
        return history
    
    def predict(self, data):
        """
        预测价格形态
        :param data: 输入数据 (n_samples, pattern_length, n_features)
        :return: 预测结果
        """
        # 预处理数据
        X = self.preprocess_data(data)
        
        # 预测
        predictions = self.model.predict(X)
        
        # 返回概率和预测类别
        return predictions, np.argmax(predictions, axis=1)
    
    def extract_features(self, data):
        """
        提取价格形态特征
        :param data: 输入数据 (n_samples, pattern_length, n_features)
        :return: 特征向量
        """
        # 创建特征提取模型（去掉输出层）
        feature_extractor = models.Model(inputs=self.model.input,
                                        outputs=self.model.layers[-3].output)  # 取倒数第三层的输出
        
        # 预处理数据
        X = self.preprocess_data(data)
        
        # 提取特征
        features = feature_extractor.predict(X)
        
        return features
    
    def plot_training_history(self, history):
        """
        绘制训练历史
        :param history: 训练历史对象
        """
        plt.figure(figsize=(12, 4))
        
        # 绘制准确率
        plt.subplot(1, 2, 1)
        plt.plot(history.history['accuracy'], label='Training Accuracy')
        plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
        plt.xlabel('Epoch')
        plt.ylabel('Accuracy')
        plt.legend()
        plt.title('Model Accuracy')
        
        # 绘制损失
        plt.subplot(1, 2, 2)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.title('Model Loss')
        
        plt.tight_layout()
        plt.show()


class AbuCNNFactorExtractor(object):
    """CNN因子提取器，与现有因子系统集成"""
    
    def __init__(self, pattern_length=20, model_path=None):
        """
        初始化CNN因子提取器
        :param pattern_length: K线形态长度
        :param model_path: 预训练模型路径
        """
        self.pattern_length = pattern_length
        self.cnn_model = AbuCNNPricePattern(pattern_length=pattern_length, model_path=model_path)
    
    def generate_pattern_features(self, kl_pd, n_future_days=5):
        """
        从K线数据生成形态特征
        :param kl_pd: K线数据
        :param n_future_days: 未来预测天数
        :return: 形态特征和价格预测
        """
        # 准备OHLC数据
        ohlc_data = kl_pd[['high', 'low', 'open', 'close']].values
        
        # 生成滑动窗口的形态数据
        patterns = []
        for i in range(len(ohlc_data) - self.pattern_length):
            pattern = ohlc_data[i:i+self.pattern_length]
            patterns.append(pattern)
        
        patterns = np.array(patterns)
        
        # 提取特征
        features = self.cnn_model.extract_features(patterns)
        
        # 预测价格形态
        predictions, classes = self.cnn_model.predict(patterns)
        
        # 创建结果DataFrame
        result = pd.DataFrame(index=kl_pd.index[self.pattern_length:])
        
        # 添加特征
        for i in range(features.shape[1]):
            result[f'cnn_feature_{i+1}'] = features[:, i]
        
        # 添加形态预测
        result['pattern_class'] = classes
        result['pattern_prob'] = np.max(predictions, axis=1)
        
        return result
    
    def generate_momentum_features(self, kl_pd):
        """
        生成动量相关的CNN特征
        :param kl_pd: K线数据
        :return: 动量特征
        """
        # 计算收益率和动量指标
        kl_pd['return'] = kl_pd['close'].pct_change()
        kl_pd['momentum_5'] = kl_pd['return'].rolling(window=5).sum()
        kl_pd['momentum_10'] = kl_pd['return'].rolling(window=10).sum()
        kl_pd['volatility'] = kl_pd['return'].rolling(window=10).std()
        
        # 准备动量数据
        momentum_data = kl_pd[['momentum_5', 'momentum_10', 'volatility', 'return']].dropna().values
        
        # 生成滑动窗口的动量模式
        patterns = []
        for i in range(len(momentum_data) - self.pattern_length):
            pattern = momentum_data[i:i+self.pattern_length]
            patterns.append(pattern)
        
        patterns = np.array(patterns)
        
        # 提取动量特征
        features = self.cnn_model.extract_features(patterns)
        
        # 创建结果DataFrame
        result = pd.DataFrame(index=kl_pd.index[self.pattern_length+10:])  # 考虑rolling窗口
        
        # 添加动量特征
        for i in range(features.shape[1]):
            result[f'cnn_momentum_feature_{i+1}'] = features[:, i]
        
        return result


class AbuKLinePatternRecognizer(object):
    """K线形态识别器"""
    
    def __init__(self, model_path=None):
        """
        初始化K线形态识别器
        :param model_path: 预训练模型路径
        """
        # 定义常见K线形态
        self.patterns = {
            'bullish_engulfing': 0,
            'bearish_engulfing': 1,
            'hammer': 2,
            'hanging_man': 3,
            'morning_star': 4,
            'evening_star': 5,
            'three_white_soldiers': 6,
            'three_black_crows': 7,
            'bullish_harami': 8,
            'bearish_harami': 9
        }
        
        self.reverse_patterns = {v: k for k, v in self.patterns.items()}
        
        # 初始化CNN模型
        self.cnn_model = AbuCNNPricePattern(n_patterns=len(self.patterns), model_path=model_path)
    
    def detect_candlestick_patterns(self, kl_pd):
        """
        检测K线形态
        :param kl_pd: K线数据
        :return: 包含检测到的形态的DataFrame
        """
        # 准备OHLC数据
        ohlc_data = kl_pd[['high', 'low', 'open', 'close']].values
        
        # 生成滑动窗口的K线数据
        patterns = []
        for i in range(len(ohlc_data) - self.cnn_model.pattern_length):
            pattern = ohlc_data[i:i+self.cnn_model.pattern_length]
            patterns.append(pattern)
        
        patterns = np.array(patterns)
        
        # 预测K线形态
        predictions, classes = self.cnn_model.predict(patterns)
        
        # 创建结果DataFrame
        result = pd.DataFrame(index=kl_pd.index[self.cnn_model.pattern_length:])
        result['detected_pattern'] = [self.reverse_patterns[c] for c in classes]
        result['pattern_confidence'] = np.max(predictions, axis=1)
        
        # 计算形态出现后的收益率
        for i in range(len(result)):
            idx = result.index[i]
            if i < len(result) - 5:
                future_returns = kl_pd.loc[idx:, 'close'].pct_change().iloc[1:6].sum()
                result.loc[idx, 'future_return_5d'] = future_returns
        
        return result
    
    def create_pattern_dataset(self, kl_pd, pattern_labels):
        """
        创建用于训练的模式数据集
        :param kl_pd: K线数据
        :param pattern_labels: 模式标签
        :return: 数据集和标签
        """
        ohlc_data = kl_pd[['high', 'low', 'open', 'close']].values
        
        patterns = []
        labels = []
        
        for i in range(len(ohlc_data) - self.cnn_model.pattern_length):
            if i + self.cnn_model.pattern_length < len(pattern_labels):
                pattern = ohlc_data[i:i+self.cnn_model.pattern_length]
                patterns.append(pattern)
                labels.append(pattern_labels[i + self.cnn_model.pattern_length])
        
        return np.array(patterns), np.array(labels)


class AbuCNNPriceForecast(object):
    """基于CNN的价格预测模型"""
    
    def __init__(self, lookback=20, n_features=4, n_future=1, model_path=None):
        """
        初始化CNN价格预测模型
        :param lookback: 回溯窗口大小
        :param n_features: 特征数量
        :param n_future: 预测未来天数
        :param model_path: 预训练模型路径
        """
        self.lookback = lookback
        self.n_features = n_features
        self.n_future = n_future
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.model = self.build_forecast_model()
        
        if model_path and os.path.exists(model_path):
            self.model.load_weights(model_path)
            print(f"Loaded pre-trained forecast model from {model_path}")
    
    def build_forecast_model(self):
        """
        构建价格预测CNN模型
        :return: 预测模型
        """
        model = models.Sequential()
        
        # 卷积层
        model.add(layers.Conv1D(filters=64, kernel_size=3, activation='relu', 
                               input_shape=(self.lookback, self.n_features)))
        model.add(layers.MaxPooling1D(pool_size=2))
        
        model.add(layers.Conv1D(filters=128, kernel_size=3, activation='relu'))
        model.add(layers.MaxPooling1D(pool_size=2))
        
        # LSTM层
        model.add(layers.LSTM(100, return_sequences=True))
        model.add(layers.LSTM(50))
        
        # 输出层
        model.add(layers.Dense(self.n_future))
        
        # 编译模型
        model.compile(optimizer=optimizers.Adam(learning_rate=0.001),
                     loss='mean_squared_error')
        
        return model
    
    def prepare_data(self, kl_pd, feature_cols=['high', 'low', 'open', 'close']):
        """
        准备预测数据
        :param kl_pd: K线数据
        :param feature_cols: 特征列
        :return: 输入数据和目标数据
        """
        # 选择特征
        data = kl_pd[feature_cols].values
        
        # 归一化
        data_scaled = self.scaler.fit_transform(data)
        
        X, y = [], []
        for i in range(self.lookback, len(data_scaled) - self.n_future + 1):
            X.append(data_scaled[i-self.lookback:i])
            y.append(data_scaled[i:i+self.n_future, 3])  # 预测收盘价
        
        return np.array(X), np.array(y)
    
    def fit(self, X, y, epochs=50, batch_size=32, save_path=None):
        """
        训练预测模型
        :param X: 输入数据
        :param y: 目标数据
        :param epochs: 训练轮数
        :param batch_size: 批次大小
        :param save_path: 模型保存路径
        :return: 训练历史
        """
        history = self.model.fit(X, y, epochs=epochs, batch_size=batch_size,
                               validation_split=0.2, verbose=1)
        
        if save_path:
            self.model.save_weights(save_path)
            print(f"Forecast model saved to {save_path}")
        
        return history
    
    def predict(self, X):
        """
        预测价格
        :param X: 输入数据
        :return: 预测结果
        """
        predictions = self.model.predict(X)
        
        # 反归一化
        dummy = np.zeros((predictions.shape[0], self.n_features))
        dummy[:, 3] = predictions[:, 0]  # 假设预测的是收盘价
        predictions_rescaled = self.scaler.inverse_transform(dummy)[:, 3]
        
        return predictions_rescaled
    
    def forecast_prices(self, kl_pd, feature_cols=['high', 'low', 'open', 'close']):
        """
        预测未来价格
        :param kl_pd: K线数据
        :param feature_cols: 特征列
        :return: 预测结果
        """
        # 准备数据
        X, y = self.prepare_data(kl_pd, feature_cols)
        
        # 预测
        predictions = self.predict(X)
        
        # 创建结果DataFrame
        result = pd.DataFrame(index=kl_pd.index[self.lookback:-self.n_future+1])
        result['actual_close'] = kl_pd['close'].iloc[self.lookback:-self.n_future+1]
        result['predicted_close'] = predictions
        result['prediction_error'] = result['predicted_close'] - result['actual_close']
        result['prediction_return'] = result['predicted_close'].pct_change()
        
        return result


def demo_cnn_pattern_recognition():
    """CNN形态识别演示函数"""
    import matplotlib.pyplot as plt
    from abupy import ABuSymbolPd
    
    # 获取数据
    kl_pd = ABuSymbolPd.make_kl_df('600519', n_folds=2)
    
    # 创建K线形态识别器
    recognizer = AbuKLinePatternRecognizer()
    
    # 生成形态特征
    pattern_features = recognizer.detect_candlestick_patterns(kl_pd)
    
    print("检测到的K线形态:")
    print(pattern_features.head())
    
    # 可视化形态分布
    plt.figure(figsize=(10, 6))
    pattern_features['detected_pattern'].value_counts().plot(kind='bar')
    plt.title('Detected Candlestick Patterns')
    plt.xlabel('Pattern Type')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


def demo_cnn_price_forecast():
    """CNN价格预测演示函数"""
    import matplotlib.pyplot as plt
    from abupy import ABuSymbolPd
    
    # 获取数据
    kl_pd = ABuSymbolPd.make_kl_df('000001', n_folds=2)
    
    # 创建价格预测模型
    forecaster = AbuCNNPriceForecast(lookback=20, n_future=1)
    
    # 准备数据
    X, y = forecaster.prepare_data(kl_pd)
    
    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # 训练模型
    history = forecaster.fit(X_train, y_train, epochs=20, batch_size=32)
    
    # 预测
    predictions = forecaster.predict(X_test)
    
    # 可视化预测结果
    plt.figure(figsize=(12, 6))
    plt.plot(y_test, label='Actual')
    plt.plot(predictions, label='Predicted')
    plt.title('Price Prediction with CNN')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    demo_cnn_pattern_recognition()
    demo_cnn_price_forecast()