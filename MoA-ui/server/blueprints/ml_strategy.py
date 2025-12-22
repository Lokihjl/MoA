# -*- encoding:utf-8 -*-
"""
    机器学习策略蓝图
    提供智能选股和动态止盈止损功能
"""

from flask import Blueprint, request, jsonify
from abupy.MLBu.ABuML import EMLFitType
from abupy.MLBu.ABuMLCreater import AbuMLCreater
from abupy.PickStockBu.ABuPickStockBase import AbuPickStockBase
from abupy import ABuSymbolPd, AbuFactorBuyBase, AbuFactorSellBase
from abupy import AbuKLManager
import numpy as np
import pandas as pd

# 创建蓝图
ml_strategy_bp = Blueprint('ml_strategy', __name__)

# 注册到主蓝图moA_bp
from . import moA_bp
moA_bp.register_blueprint(ml_strategy_bp, url_prefix='/ml_strategy')

# 机器学习模型封装类
class MLModelWrapper:
    """
    封装多种机器学习模型，提供统一的接口
    """
    def __init__(self, model_type='random_forest', fit_type='clf'):
        """
        初始化机器学习模型
        :param model_type: 模型类型，支持random_forest, xgb, svc, knn, decision_tree
        :param fit_type: 拟合类型，clf(分类), reg(回归)
        """
        self.model_type = model_type
        self.fit_type = fit_type
        self.estimator = AbuMLCreater()
        self.model = None
        self.lookback_days = 20  # 默认回溯天数
        self._init_model()
    
    def _init_model(self):
        """
        初始化具体的机器学习模型
        """
        if self.fit_type == 'clf':
            if self.model_type == 'random_forest':
                self.model = self.estimator.random_forest_classifier()
            elif self.model_type == 'xgb':
                self.model = self.estimator.xgb_classifier()
            elif self.model_type == 'svc':
                self.model = self.estimator.svc(probability=True)
            elif self.model_type == 'knn':
                self.model = self.estimator.knn_classifier()
            elif self.model_type == 'decision_tree':
                self.model = self.estimator.decision_tree_classifier()
            else:
                raise ValueError(f"不支持的分类模型类型: {self.model_type}")
        elif self.fit_type == 'reg':
            if self.model_type == 'random_forest':
                self.model = self.estimator.random_forest_regressor()
            elif self.model_type == 'xgb':
                self.model = self.estimator.xgb_regressor()
            elif self.model_type == 'svr':
                self.model = self.estimator.svr()
            elif self.model_type == 'linear':
                self.model = self.estimator.linear_regressor()
            else:
                raise ValueError(f"不支持的回归模型类型: {self.model_type}")
        else:
            raise ValueError(f"不支持的拟合类型: {self.fit_type}")
    
    def fit(self, x, y):
        """
        训练模型
        :param x: 特征数据
        :param y: 标签数据
        :return: 训练后的模型
        """
        return self.model.fit(x, y)
    
    def predict(self, x):
        """
        预测结果
        :param x: 特征数据
        :return: 预测结果
        """
        return self.model.predict(x)
    
    def predict_proba(self, x):
        """
        预测概率（仅分类模型支持）
        :param x: 特征数据
        :return: 预测概率
        """
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(x)
        else:
            raise NotImplementedError("该模型不支持概率预测")

# 智能选股因子类
class MLPickStock(AbuPickStockBase):
    """
    基于机器学习的智能选股因子
    """
    def _init_self(self, **kwargs):
        """
        初始化选股因子
        :param kwargs: 配置参数
        """
        self.model_wrapper = kwargs.get('model_wrapper')
        self.feature_cols = kwargs.get('feature_cols', ['close', 'volume', 'high', 'low', 'open'])
        self.lookback_days = kwargs.get('lookback_days', 20)
        self.future_days = kwargs.get('future_days', 5)
    
    def _generate_features(self, kl_pd):
        """
        生成特征数据
        :param kl_pd: 股票K线数据
        :return: 特征数据
        """
        # 生成基础特征
        features = []
        for col in self.feature_cols:
            if col in kl_pd.columns:
                features.append(kl_pd[col].values[-self.lookback_days:])
        
        # 生成衍生特征
        # 收益率特征
        returns = kl_pd['close'].pct_change().values[-self.lookback_days:]
        features.append(returns)
        
        # 波动率特征
        volatility = kl_pd['close'].pct_change().rolling(window=5).std().values[-self.lookback_days:]
        features.append(volatility)
        
        return np.concatenate(features).reshape(1, -1)
    
    def _generate_label(self, kl_pd):
        """
        生成标签数据
        :param kl_pd: 股票K线数据
        :return: 标签数据
        """
        # 未来几天的收益率
        future_return = kl_pd['close'].pct_change(periods=self.future_days).values[-1]
        # 上涨为1，下跌为0
        return 1 if future_return > 0 else 0
    
    def fit_pick(self, kl_pd, target_symbol):
        """
        选股操作接口
        :param kl_pd: 股票K线数据
        :param target_symbol: 目标股票代码
        :return: 选股结果，True表示选中，False表示不选中
        """
        if kl_pd.shape[0] < self.lookback_days + self.future_days:
            return False
        
        # 生成特征
        features = self._generate_features(kl_pd)
        
        # 预测结果
        try:
            prediction = self.model_wrapper.predict(features)
            return bool(prediction[0])
        except Exception as e:
            print(f"选股预测失败: {e}")
            return False
    
    def fit_first_choice(self, pick_worker, choice_symbols, *args, **kwargs):
        """
        因子首选批量选股接口
        :param pick_worker: 选股工作者
        :param choice_symbols: 备选股票列表
        :return: 选中的股票列表
        """
        selected_symbols = []
        
        for symbol in choice_symbols:
            kl_pd = pick_worker.kl_pd_manager.get_pick_stock_kl_pd(symbol)
            if kl_pd is not None and self.fit_pick(kl_pd, symbol):
                selected_symbols.append(symbol)
        
        return selected_symbols

# 动态止盈止损因子基类
class MLDynamicStopBase:
    """
    基于机器学习的动态止盈止损基类
    """
    def __init__(self, model_wrapper, lookback_days=20):
        """
        初始化动态止盈止损因子
        :param model_wrapper: 机器学习模型封装对象
        :param lookback_days: 回溯天数
        """
        self.model_wrapper = model_wrapper
        self.lookback_days = lookback_days
    
    def _generate_features(self, kl_pd):
        """
        生成特征数据
        :param kl_pd: 股票K线数据
        :return: 特征数据
        """
        # 生成基础特征
        features = []
        for col in ['close', 'volume', 'high', 'low', 'open']:
            if col in kl_pd.columns:
                features.append(kl_pd[col].values[-self.lookback_days:])
        
        # 生成衍生特征
        returns = kl_pd['close'].pct_change().values[-self.lookback_days:]
        volatility = kl_pd['close'].pct_change().rolling(window=5).std().values[-self.lookback_days:]
        
        features.append(returns)
        features.append(volatility)
        
        return np.concatenate(features).reshape(1, -1)
    
    def adjust_stop_params(self, kl_pd, current_params):
        """
        调整止盈止损参数
        :param kl_pd: 股票K线数据
        :param current_params: 当前止盈止损参数
        :return: 调整后的止盈止损参数
        """
        if kl_pd.shape[0] < self.lookback_days:
            return current_params
        
        # 生成特征
        features = self._generate_features(kl_pd)
        
        try:
            # 预测未来走势
            prediction = self.model_wrapper.predict(features)
            prediction_proba = self.model_wrapper.predict_proba(features) if hasattr(self.model_wrapper, 'predict_proba') else None
            
            # 根据预测结果调整参数
            if prediction[0] == 1:  # 预测上涨
                # 放宽止损，收紧止盈
                adjusted_params = {
                    'stop_loss': current_params.get('stop_loss', 0.05) * 1.2,  # 放宽止损
                    'take_profit': current_params.get('take_profit', 0.1) * 0.8  # 收紧止盈
                }
            else:  # 预测下跌
                # 收紧止损，放宽止盈
                adjusted_params = {
                    'stop_loss': current_params.get('stop_loss', 0.05) * 0.8,  # 收紧止损
                    'take_profit': current_params.get('take_profit', 0.1) * 1.2  # 放宽止盈
                }
            
            return adjusted_params
        except Exception as e:
            print(f"调整止盈止损参数失败: {e}")
            return current_params

# 机器学习策略服务类
class MLStrategyService:
    """
    机器学习策略服务类
    提供智能选股和动态止盈止损功能
    """
    def __init__(self):
        """
        初始化服务
        """
        self.model_wrappers = {}
    
    def create_model(self, model_type='random_forest', fit_type='clf'):
        """
        创建机器学习模型
        :param model_type: 模型类型
        :param fit_type: 拟合类型
        :return: 模型ID
        """
        model_wrapper = MLModelWrapper(model_type=model_type, fit_type=fit_type)
        model_id = f"model_{len(self.model_wrappers) + 1}"
        self.model_wrappers[model_id] = model_wrapper
        return model_id
    
    def get_model(self, model_id):
        """
        获取机器学习模型
        :param model_id: 模型ID
        :return: 模型封装对象
        """
        return self.model_wrappers.get(model_id)
    
    def train_model(self, model_id, symbol, lookback_days=20):
        """
        训练模型
        :param model_id: 模型ID
        :param symbol: 股票代码
        :param lookback_days: 回溯天数，默认20，与预测时保持一致
        :return: 训练结果
        """
        model_wrapper = self.get_model(model_id)
        if not model_wrapper:
            return False, "模型不存在"
        
        try:
            # 保存lookback_days到模型对象中
            model_wrapper.lookback_days = lookback_days
            
            # 获取股票数据
            kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=lookback_days + 20)
            if kl_pd.shape[0] < lookback_days + 20:
                return False, "数据不足"
            
            # 生成训练数据
            x_train = []
            y_train = []
            
            # 处理缺失值，填充NaN
            kl_pd = kl_pd.fillna(method='ffill').fillna(method='bfill')
            
            for i in range(lookback_days, kl_pd.shape[0] - 5):
                # 生成特征
                features = []
                for col in ['close', 'volume', 'high', 'low', 'open']:
                    features.append(kl_pd[col].values[i-lookback_days:i])
                
                returns = kl_pd['close'].pct_change().values[i-lookback_days:i]
                volatility = kl_pd['close'].pct_change().rolling(window=5).std().values[i-lookback_days:i]
                
                # 处理特征中的NaN值，用0填充
                returns = np.nan_to_num(returns, nan=0.0)
                volatility = np.nan_to_num(volatility, nan=0.0)
                
                features.append(returns)
                features.append(volatility)
                
                x_train.append(np.concatenate(features))
                
                # 生成标签
                future_return = kl_pd['close'].pct_change(periods=5).values[i]
                # 处理标签中的NaN值
                future_return = 0.0 if np.isnan(future_return) else future_return
                y_train.append(1 if future_return > 0 else 0)
            
            x_train = np.array(x_train)
            y_train = np.array(y_train)
            
            # 训练模型
            model_wrapper.fit(x_train, y_train)
            
            return True, "模型训练成功"
        except Exception as e:
            return False, f"模型训练失败: {e}"
    
    def smart_pick_stocks(self, model_id, symbols, top_n=10):
        """
        智能选股
        :param model_id: 模型ID
        :param symbols: 备选股票列表
        :param top_n: 选中股票数量
        :return: 选中的股票列表
        """
        model_wrapper = self.get_model(model_id)
        if not model_wrapper:
            return [], "模型不存在"
        
        try:
            selected_stocks = []
            
            # 使用模型中保存的lookback_days参数
            lookback_days = model_wrapper.lookback_days
            
            for symbol in symbols:
                try:
                    # 获取股票数据，确保有足够的数据
                    kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=lookback_days + 20)
                    
                    # 检查kl_pd是否为None
                    if kl_pd is None:
                        print(f"获取{symbol}数据失败，跳过")
                        continue
                        
                    # 检查数据量是否足够
                    if kl_pd.shape[0] < lookback_days + 20:
                        print(f"{symbol}数据量不足，跳过")
                        continue
                    
                    # 处理缺失值，填充NaN
                    kl_pd = kl_pd.fillna(method='ffill').fillna(method='bfill')
                    
                    # 生成特征
                    features = []
                    required_cols = ['close', 'volume', 'high', 'low', 'open']
                    
                    # 检查所有必需的列是否都存在
                    if not all(col in kl_pd.columns for col in required_cols):
                        print(f"{symbol}缺少必需的列，跳过")
                        continue
                    
                    for col in required_cols:
                        features.append(kl_pd[col].values[-lookback_days:])
                    
                    returns = kl_pd['close'].pct_change().values[-lookback_days:]
                    volatility = kl_pd['close'].pct_change().rolling(window=5).std().values[-lookback_days:]
                    
                    # 处理特征中的NaN值，用0填充
                    returns = np.nan_to_num(returns, nan=0.0)
                    volatility = np.nan_to_num(volatility, nan=0.0)
                    
                    features.append(returns)
                    features.append(volatility)
                    
                    x = np.concatenate(features).reshape(1, -1)
                except Exception as e:
                    print(f"处理{symbol}时出错: {e}")
                    continue
                
                # 预测结果
                prediction = model_wrapper.predict(x)
                prediction_proba = model_wrapper.predict_proba(x) if hasattr(model_wrapper, 'predict_proba') else None
                
                if prediction[0] == 1:
                    stock_info = {
                        'symbol': symbol,
                        'prediction': int(prediction[0]),
                        'probability': float(prediction_proba[0][1]) if prediction_proba is not None else None,
                        'latest_price': float(kl_pd['close'].values[-1]),
                        'latest_date': kl_pd.index[-1].strftime('%Y-%m-%d')
                    }
                    selected_stocks.append(stock_info)
            
            # 按概率排序，返回top_n
            if selected_stocks:
                selected_stocks = sorted(selected_stocks, key=lambda x: x['probability'] if x['probability'] is not None else 0, reverse=True)
                selected_stocks = selected_stocks[:top_n]
            
            return selected_stocks, "选股成功"
        except Exception as e:
            return [], f"选股失败: {e}"
    
    def adjust_stop_loss_take_profit(self, model_id, symbol, current_params):
        """
        调整止盈止损参数
        :param model_id: 模型ID
        :param symbol: 股票代码
        :param current_params: 当前止盈止损参数
        :return: 调整后的止盈止损参数
        """
        model_wrapper = self.get_model(model_id)
        if not model_wrapper:
            return current_params, "模型不存在"
        
        try:
            # 使用模型中保存的lookback_days参数
            lookback_days = model_wrapper.lookback_days
            
            # 获取股票数据，确保有足够的数据
            kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=lookback_days + 20)
            if kl_pd.shape[0] < lookback_days + 20:
                return current_params, "数据不足"
            
            # 处理缺失值，填充NaN
            kl_pd = kl_pd.fillna(method='ffill').fillna(method='bfill')
            
            # 创建动态止盈止损调整器，使用模型的lookback_days
            dynamic_stop = MLDynamicStopBase(model_wrapper, lookback_days=lookback_days)
            
            # 调整参数
            adjusted_params = dynamic_stop.adjust_stop_params(kl_pd, current_params)
            
            return adjusted_params, "参数调整成功"
        except Exception as e:
            return current_params, f"参数调整失败: {e}"

# 初始化服务
ml_strategy_service = MLStrategyService()

# 路由定义

@ml_strategy_bp.route('/create_model', methods=['POST'])
def create_model():
    """
    创建机器学习模型
    POST /ml_strategy/create_model
    Body: {
        "model_type": "random_forest",  # 模型类型
        "fit_type": "clf"  # 拟合类型
    }
    """
    data = request.get_json()
    model_type = data.get('model_type', 'random_forest')
    fit_type = data.get('fit_type', 'clf')
    
    model_id = ml_strategy_service.create_model(model_type, fit_type)
    
    return jsonify({
        "success": True,
        "model_id": model_id,
        "message": "模型创建成功"
    })

@ml_strategy_bp.route('/train_model', methods=['POST'])
def train_model():
    """
    训练机器学习模型
    POST /ml_strategy/train_model
    Body: {
        "model_id": "model_1",  # 模型ID
        "symbol": "sz000002",  # 股票代码
        "lookback_days": 100  # 回溯天数
    }
    """
    data = request.get_json()
    model_id = data.get('model_id')
    symbol = data.get('symbol')
    lookback_days = data.get('lookback_days', 100)
    
    if not model_id or not symbol:
        return jsonify({
            "success": False,
            "message": "缺少必要参数"
        })
    
    success, message = ml_strategy_service.train_model(model_id, symbol, lookback_days)
    
    return jsonify({
        "success": success,
        "message": message
    })

@ml_strategy_bp.route('/smart_pick', methods=['POST'])
def smart_pick():
    """
    智能选股
    POST /ml_strategy/smart_pick
    Body: {
        "model_id": "model_1",  # 模型ID
        "symbols": ["sz000002", "sh600036"],  # 备选股票列表
        "top_n": 10  # 选中股票数量
    }
    """
    data = request.get_json()
    model_id = data.get('model_id')
    symbols = data.get('symbols', [])
    top_n = data.get('top_n', 10)
    
    if not model_id or not symbols:
        return jsonify({
            "success": False,
            "message": "缺少必要参数"
        })
    
    selected_stocks, message = ml_strategy_service.smart_pick_stocks(model_id, symbols, top_n)
    
    return jsonify({
        "success": True,
        "selected_stocks": selected_stocks,
        "message": message
    })

@ml_strategy_bp.route('/adjust_stop_params', methods=['POST'])
def adjust_stop_params():
    """
    调整止盈止损参数
    POST /ml_strategy/adjust_stop_params
    Body: {
        "model_id": "model_1",  # 模型ID
        "symbol": "sz000002",  # 股票代码
        "current_params": {
            "stop_loss": 0.05,
            "take_profit": 0.1
        }  # 当前止盈止损参数
    }
    """
    data = request.get_json()
    model_id = data.get('model_id')
    symbol = data.get('symbol')
    current_params = data.get('current_params', {})
    
    if not model_id or not symbol:
        return jsonify({
            "success": False,
            "message": "缺少必要参数"
        })
    
    adjusted_params, message = ml_strategy_service.adjust_stop_loss_take_profit(model_id, symbol, current_params)
    
    return jsonify({
        "success": True,
        "adjusted_params": adjusted_params,
        "message": message
    })

@ml_strategy_bp.route('/available_models', methods=['GET'])
def available_models():
    """
    获取可用模型列表
    GET /ml_strategy/available_models
    """
    models = list(ml_strategy_service.model_wrappers.keys())
    
    return jsonify({
        "success": True,
        "models": models
    })
