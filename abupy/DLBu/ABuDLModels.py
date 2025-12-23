# -*- encoding:utf-8 -*-
"""
    深度学习模型模块
    包含LSTM、Transformer、CNN等模型用于金融时间序列分析
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential, Model
from tensorflow.keras.layers import (
    LSTM, GRU, Dense, Dropout, Input, Conv1D, MaxPooling1D, Flatten,
    BatchNormalization, Activation, MultiHeadAttention, LayerNormalization,
    TimeDistributed, GlobalAveragePooling1D
)
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

__author__ = '量化策略师'


class AbuDLModelBase(object):
    """深度学习模型基类"""
    
    def __init__(self, model_type='regression', input_shape=None):
        """
        初始化深度学习模型基类
        :param model_type: 模型类型，'regression'或'classification'
        :param input_shape: 输入形状 (时间步长, 特征数量)
        """
        self.model_type = model_type
        self.input_shape = input_shape
        self.model = None
        self.scaler = None
        
    def build_model(self, **kwargs):
        """
        构建模型结构（需要子类实现）
        :param kwargs: 模型参数
        """
        raise NotImplementedError("Subclasses must implement build_model method")
    
    def prepare_data(self, data, time_steps=30, forecast_horizon=1, train_size=0.8):
        """
        准备时间序列数据
        :param data: 原始数据（numpy数组或DataFrame）
        :param time_steps: 时间步长
        :param forecast_horizon: 预测 horizon
        :param train_size: 训练集比例
        :return: 训练集和测试集 (X_train, y_train, X_test, y_test)
        """
        if isinstance(data, pd.DataFrame):
            data = data.values
        
        # 数据标准化
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        scaled_data = self.scaler.fit_transform(data)
        
        # 创建时间步数据
        X, y = [], []
        for i in range(len(scaled_data) - time_steps - forecast_horizon + 1):
            X.append(scaled_data[i:(i + time_steps), :])
            y.append(scaled_data[i + time_steps + forecast_horizon - 1, 0])  # 假设第一列为目标变量
        
        X, y = np.array(X), np.array(y)
        
        # 划分训练集和测试集
        split_index = int(len(X) * train_size)
        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]
        
        return X_train, y_train, X_test, y_test
    
    def train(self, X_train, y_train, epochs=100, batch_size=32, validation_split=0.2):
        """
        训练模型
        :param X_train: 训练特征
        :param y_train: 训练标签
        :param epochs: 训练轮数
        :param batch_size: 批次大小
        :param validation_split: 验证集比例
        :return: 训练历史
        """
        if self.model is None:
            raise ValueError("Model not built yet. Call build_model() first.")
        
        # 回调函数
        callbacks = [
            EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-6)
        ]
        
        # 训练模型
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=callbacks,
            verbose=1
        )
        
        return history
    
    def predict(self, X):
        """
        模型预测
        :param X: 输入数据
        :return: 预测结果
        """
        if self.model is None:
            raise ValueError("Model not built yet. Call build_model() first.")
        
        return self.model.predict(X)
    
    def inverse_transform(self, data):
        """
        逆标准化数据
        :param data: 标准化后的数据
        :return: 原始尺度数据
        """
        if self.scaler is None:
            raise ValueError("Scaler not initialized. Call prepare_data() first.")
        
        # 扩展维度以匹配标准化器的输入形状
        if len(data.shape) == 1:
            data = data.reshape(-1, 1)
        
        # 创建与原始数据相同特征数量的数组
        dummy_array = np.zeros((data.shape[0], self.scaler.n_features_in_))
        dummy_array[:, 0] = data.flatten()
        
        return self.scaler.inverse_transform(dummy_array)[:, 0]
    
    def plot_training_history(self, history):
        """
        绘制训练历史
        :param history: 训练历史对象
        """
        plt.figure(figsize=(12, 6))
        
        # 损失曲线
        plt.subplot(1, 2, 1)
        plt.plot(history.history['loss'], label='Training Loss')
        plt.plot(history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 准确率曲线（如果是分类模型）
        if self.model_type == 'classification' and 'accuracy' in history.history:
            plt.subplot(1, 2, 2)
            plt.plot(history.history['accuracy'], label='Training Accuracy')
            plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
            plt.title('Model Accuracy')
            plt.xlabel('Epoch')
            plt.ylabel('Accuracy')
            plt.legend()
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def evaluate(self, X_test, y_test):
        """
        评估模型性能
        :param X_test: 测试特征
        :param y_test: 测试标签
        :return: 评估指标
        """
        if self.model is None:
            raise ValueError("Model not built yet. Call build_model() first.")
        
        return self.model.evaluate(X_test, y_test, verbose=1)


class AbuLSTMModel(AbuDLModelBase):
    """LSTM模型类"""
    
    def build_model(self, units=[50, 50], dropout_rate=0.2, learning_rate=0.001):
        """
        构建LSTM模型
        :param units: LSTM层单元数列表
        :param dropout_rate: Dropout率
        :param learning_rate: 学习率
        """
        self.model = Sequential()
        
        # 输入层和第一个LSTM层
        self.model.add(LSTM(units=units[0], return_sequences=True, input_shape=self.input_shape))
        self.model.add(Dropout(dropout_rate))
        self.model.add(BatchNormalization())
        
        # 中间LSTM层
        for u in units[1:-1]:
            self.model.add(LSTM(units=u, return_sequences=True))
            self.model.add(Dropout(dropout_rate))
            self.model.add(BatchNormalization())
        
        # 最后一个LSTM层
        self.model.add(LSTM(units=units[-1], return_sequences=False))
        self.model.add(Dropout(dropout_rate))
        self.model.add(BatchNormalization())
        
        # 输出层
        if self.model_type == 'regression':
            self.model.add(Dense(1, activation='linear'))
            loss = 'mean_squared_error'
        else:  # classification
            self.model.add(Dense(2, activation='softmax'))
            loss = 'sparse_categorical_crossentropy'
        
        # 编译模型
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'] if self.model_type == 'classification' else None)
        
        return self.model


class AbuGRUModel(AbuDLModelBase):
    """GRU模型类"""
    
    def build_model(self, units=[50, 50], dropout_rate=0.2, learning_rate=0.001):
        """
        构建GRU模型
        :param units: GRU层单元数列表
        :param dropout_rate: Dropout率
        :param learning_rate: 学习率
        """
        self.model = Sequential()
        
        # 输入层和第一个GRU层
        self.model.add(GRU(units=units[0], return_sequences=True, input_shape=self.input_shape))
        self.model.add(Dropout(dropout_rate))
        self.model.add(BatchNormalization())
        
        # 中间GRU层
        for u in units[1:-1]:
            self.model.add(GRU(units=u, return_sequences=True))
            self.model.add(Dropout(dropout_rate))
            self.model.add(BatchNormalization())
        
        # 最后一个GRU层
        self.model.add(GRU(units=units[-1], return_sequences=False))
        self.model.add(Dropout(dropout_rate))
        self.model.add(BatchNormalization())
        
        # 输出层
        if self.model_type == 'regression':
            self.model.add(Dense(1, activation='linear'))
            loss = 'mean_squared_error'
        else:  # classification
            self.model.add(Dense(2, activation='softmax'))
            loss = 'sparse_categorical_crossentropy'
        
        # 编译模型
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'] if self.model_type == 'classification' else None)
        
        return self.model


class AbuCNNModel(AbuDLModelBase):
    """CNN模型类，用于提取价格形态特征"""
    
    def build_model(self, filters=[64, 32], kernel_sizes=[3, 3], pool_sizes=[2, 2], 
                   dense_units=[128, 64], dropout_rate=0.2, learning_rate=0.001):
        """
        构建CNN模型
        :param filters: 卷积层过滤器数量列表
        :param kernel_sizes: 卷积核大小列表
        :param pool_sizes: 池化层大小列表
        :param dense_units: 全连接层单元数列表
        :param dropout_rate: Dropout率
        :param learning_rate: 学习率
        """
        self.model = Sequential()
        
        # 输入层和第一个卷积层
        self.model.add(Conv1D(filters=filters[0], kernel_size=kernel_sizes[0], 
                             activation='relu', input_shape=self.input_shape))
        self.model.add(MaxPooling1D(pool_size=pool_sizes[0]))
        self.model.add(BatchNormalization())
        
        # 中间卷积层
        for i in range(1, len(filters)):
            self.model.add(Conv1D(filters=filters[i], kernel_size=kernel_sizes[i], activation='relu'))
            self.model.add(MaxPooling1D(pool_size=pool_sizes[i]))
            self.model.add(BatchNormalization())
        
        # 展平层
        self.model.add(Flatten())
        
        # 全连接层
        for u in dense_units:
            self.model.add(Dense(units=u, activation='relu'))
            self.model.add(Dropout(dropout_rate))
            self.model.add(BatchNormalization())
        
        # 输出层
        if self.model_type == 'regression':
            self.model.add(Dense(1, activation='linear'))
            loss = 'mean_squared_error'
        else:  # classification
            self.model.add(Dense(2, activation='softmax'))
            loss = 'sparse_categorical_crossentropy'
        
        # 编译模型
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'] if self.model_type == 'classification' else None)
        
        return self.model


class TransformerBlock(tf.keras.layers.Layer):
    """Transformer模块"""
    
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        """
        初始化Transformer模块
        :param embed_dim: 嵌入维度
        :param num_heads: 注意力头数量
        :param ff_dim: 前馈网络维度
        :param rate: Dropout率
        """
        super(TransformerBlock, self).__init__()
        self.att = MultiHeadAttention(num_heads=num_heads, key_dim=embed_dim)
        self.ffn = Sequential([
            Dense(ff_dim, activation="relu"),
            Dense(embed_dim)
        ])
        self.layernorm1 = LayerNormalization(epsilon=1e-6)
        self.layernorm2 = LayerNormalization(epsilon=1e-6)
        self.dropout1 = Dropout(rate)
        self.dropout2 = Dropout(rate)
    
    def call(self, inputs, training=False):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class TokenAndPositionEmbedding(tf.keras.layers.Layer):
    """Token和位置嵌入层"""
    
    def __init__(self, maxlen, vocab_size, embed_dim):
        """
        初始化Token和位置嵌入层
        :param maxlen: 最大长度
        :param vocab_size: 词汇表大小
        :param embed_dim: 嵌入维度
        """
        super(TokenAndPositionEmbedding, self).__init__()
        self.token_emb = tf.keras.layers.Embedding(input_dim=vocab_size, output_dim=embed_dim)
        self.pos_emb = tf.keras.layers.Embedding(input_dim=maxlen, output_dim=embed_dim)
    
    def call(self, x):
        maxlen = tf.shape(x)[-1]
        positions = tf.range(start=0, limit=maxlen, delta=1)
        positions = self.pos_emb(positions)
        x = self.token_emb(x)
        return x + positions


class AbuTransformerModel(AbuDLModelBase):
    """Transformer模型类"""
    
    def build_model(self, embed_dim=64, num_heads=2, ff_dim=64, num_transformer_blocks=2,
                   dense_units=[64, 32], dropout_rate=0.2, learning_rate=0.001):
        """
        构建Transformer模型
        :param embed_dim: 嵌入维度
        :param num_heads: 注意力头数量
        :param ff_dim: 前馈网络维度
        :param num_transformer_blocks: Transformer模块数量
        :param dense_units: 全连接层单元数列表
        :param dropout_rate: Dropout率
        :param learning_rate: 学习率
        """
        inputs = Input(shape=self.input_shape)
        
        # 重塑输入以适应Transformer
        x = TimeDistributed(Dense(embed_dim))(inputs)
        
        # Transformer模块
        for _ in range(num_transformer_blocks):
            x = TransformerBlock(embed_dim, num_heads, ff_dim, dropout_rate)(x)
        
        # 全局平均池化
        x = GlobalAveragePooling1D()(x)
        
        # 全连接层
        for u in dense_units:
            x = Dense(u, activation="relu")(x)
            x = Dropout(dropout_rate)(x)
            x = BatchNormalization()(x)
        
        # 输出层
        if self.model_type == 'regression':
            outputs = Dense(1, activation="linear")(x)
            loss = 'mean_squared_error'
        else:  # classification
            outputs = Dense(2, activation="softmax")(x)
            loss = 'sparse_categorical_crossentropy'
        
        # 创建模型
        self.model = Model(inputs=inputs, outputs=outputs)
        
        # 编译模型
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'] if self.model_type == 'classification' else None)
        
        return self.model


class AbuCNN_LSTM_Model(AbuDLModelBase):
    """CNN-LSTM混合模型类"""
    
    def build_model(self, cnn_filters=[64, 32], cnn_kernel_sizes=[3, 3], cnn_pool_sizes=[2, 2],
                   lstm_units=[50, 50], dense_units=[64], dropout_rate=0.2, learning_rate=0.001):
        """
        构建CNN-LSTM混合模型
        :param cnn_filters: CNN层过滤器数量列表
        :param cnn_kernel_sizes: CNN卷积核大小列表
        :param cnn_pool_sizes: CNN池化层大小列表
        :param lstm_units: LSTM层单元数列表
        :param dense_units: 全连接层单元数列表
        :param dropout_rate: Dropout率
        :param learning_rate: 学习率
        """
        self.model = Sequential()
        
        # CNN部分 - 提取空间特征
        for i in range(len(cnn_filters)):
            if i == 0:
                self.model.add(Conv1D(filters=cnn_filters[i], kernel_size=cnn_kernel_sizes[i], 
                                     activation='relu', input_shape=self.input_shape))
            else:
                self.model.add(Conv1D(filters=cnn_filters[i], kernel_size=cnn_kernel_sizes[i], activation='relu'))
            self.model.add(MaxPooling1D(pool_size=cnn_pool_sizes[i]))
            self.model.add(BatchNormalization())
            self.model.add(Dropout(dropout_rate))
        
        # LSTM部分 - 提取时间特征
        for i in range(len(lstm_units)):
            if i == len(lstm_units) - 1:
                self.model.add(LSTM(units=lstm_units[i], return_sequences=False))
            else:
                self.model.add(LSTM(units=lstm_units[i], return_sequences=True))
            self.model.add(BatchNormalization())
            self.model.add(Dropout(dropout_rate))
        
        # 全连接层
        for u in dense_units:
            self.model.add(Dense(units=u, activation='relu'))
            self.model.add(Dropout(dropout_rate))
            self.model.add(BatchNormalization())
        
        # 输出层
        if self.model_type == 'regression':
            self.model.add(Dense(1, activation='linear'))
            loss = 'mean_squared_error'
        else:  # classification
            self.model.add(Dense(2, activation='softmax'))
            loss = 'sparse_categorical_crossentropy'
        
        # 编译模型
        optimizer = Adam(learning_rate=learning_rate)
        self.model.compile(optimizer=optimizer, loss=loss, metrics=['accuracy'] if self.model_type == 'classification' else None)
        
        return self.model


def demo_lstm_model():
    """LSTM模型演示函数"""
    # 创建模拟时间序列数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2023-12-31', freq='B')
    n_dates = len(dates)
    
    # 创建带有趋势和季节性的时间序列
    trend = np.linspace(0, 100, n_dates)
    seasonality = 10 * np.sin(np.linspace(0, 10 * np.pi, n_dates))
    noise = np.random.randn(n_dates) * 5
    prices = 100 + trend + seasonality + noise
    
    # 创建多特征数据
    volume = np.random.randint(1000000, 10000000, n_dates)
    volatility = np.random.randn(n_dates) * 2 + 5
    
    data_df = pd.DataFrame({
        'Price': prices,
        'Volume': volume,
        'Volatility': volatility
    }, index=dates)
    
    # 准备数据
    time_steps = 30
    forecast_horizon = 1
    
    # 创建模型
    lstm_model = AbuLSTMModel(model_type='regression', input_shape=(time_steps, data_df.shape[1]))
    
    # 准备数据
    X_train, y_train, X_test, y_test = lstm_model.prepare_data(
        data_df, time_steps=time_steps, forecast_horizon=forecast_horizon
    )
    
    # 构建模型
    lstm_model.build_model(units=[50, 50], dropout_rate=0.2, learning_rate=0.001)
    
    # 训练模型
    history = lstm_model.train(X_train, y_train, epochs=50, batch_size=32)
    
    # 绘制训练历史
    lstm_model.plot_training_history(history)
    
    # 预测
    y_pred = lstm_model.predict(X_test)
    
    # 逆标准化
    y_test_original = lstm_model.inverse_transform(y_test)
    y_pred_original = lstm_model.inverse_transform(y_pred)
    
    # 绘制预测结果
    plt.figure(figsize=(12, 6))
    plt.plot(data_df.index[-len(y_test_original):], y_test_original, label='True Prices')
    plt.plot(data_df.index[-len(y_pred_original):], y_pred_original, label='Predicted Prices')
    plt.title('LSTM Model Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # 计算MSE
    mse = np.mean((y_test_original - y_pred_original) ** 2)
    print(f"Mean Squared Error: {mse:.2f}")


if __name__ == '__main__':
    demo_lstm_model()