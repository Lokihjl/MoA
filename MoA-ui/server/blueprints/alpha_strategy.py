# Alpha策略相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os
import numpy as np
import pandas as pd
import datetime

# 导入数据库模型和db对象
from models import KlineData, db

# 将项目根目录添加到Python路径中，以便导入abupy模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# 导入ABu框架的必要模块
from abupy import ABuSymbolPd
from abupy import AbuCapital
from abupy.AlphaBu import ABuPickStockExecute
from abupy.AlphaBu.ABuPickTimeExecute import _do_pick_time_work
from abupy import AbuKLManager
from abupy.MetricsBu import AbuMetricsBase
from abupy import ABuMarketDrawing
from abupy.CoreBu.ABu import run_loop_back
from abupy.CoreBu.ABuEnv import enable_example_env_ipython
from abupy.CoreBu.ABuEnv import EMarketSourceType, g_market_source

from functools import lru_cache

# 初始化ABu环境
enable_example_env_ipython(show_log=False)

# 直接设置数据源为腾讯财经
print('当前数据源:', g_market_source)
from abupy.CoreBu.ABuEnv import g_market_source as source
# 修改模块级变量
import abupy.CoreBu.ABuEnv
abupy.CoreBu.ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
print('设置后的数据源:', abupy.CoreBu.ABuEnv.g_market_source)

# 因子工厂类，用于创建选股因子、买入因子和卖出因子
class FactorFactory:
    """
    因子工厂类，用于创建各种类型的策略因子
    """
    
    @staticmethod
    def create_stock_pick_factor(factor_name, **kwargs):
        """
        创建选股因子
        :param factor_name: 因子名称
        :param kwargs: 因子参数
        :return: 选股因子实例
        """
        try:
            # 动态导入因子模块
            if factor_name == 'AbuPickStockNDay':
                from abupy.PickStockBu.ABuPickStockDemo import AbuPickStockNDay
                return AbuPickStockNDay(**kwargs)
            elif factor_name == 'AbuPickStockPriceMinMax':
                from abupy.PickStockBu.ABuPickStockPriceMinMax import AbuPickStockPriceMinMax
                return AbuPickStockPriceMinMax(**kwargs)
            elif factor_name == 'AbuPickStockGT':
                from abupy.PickStockBu.ABuPickStock import AbuPickStockGT
                return AbuPickStockGT(**kwargs)
            elif factor_name == 'AbuPickStockEV':
                from abupy.PickStockBu.ABuPickStock import AbuPickStockEV
                return AbuPickStockEV(**kwargs)
            else:
                raise ValueError(f"不支持的选股因子: {factor_name}")
        except Exception as e:
            print(f"创建选股因子失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def create_buy_factor(factor_name, **kwargs):
        """
        创建买入因子
        :param factor_name: 因子名称
        :param kwargs: 因子参数
        :return: 买入因子实例
        """
        try:
            # 动态导入因子模块
            if factor_name == 'AbuFactorBuyBreak':
                from abupy.FactorBuyBu.ABuFactorBuyBreak import AbuFactorBuyBreak
                return AbuFactorBuyBreak(**kwargs)
            elif factor_name == 'AbuFactorBuyMeanReversion':
                from abupy.FactorBuyBu.ABuFactorBuyMeanReversion import AbuFactorBuyMeanReversion
                return AbuFactorBuyMeanReversion(**kwargs)
            elif factor_name == 'AbuFactorBuyGap':
                from abupy.FactorBuyBu.ABuFactorBuyGap import AbuFactorBuyGap
                return AbuFactorBuyGap(**kwargs)
            elif factor_name == 'AbuFactorBuyRsi':
                from abupy.FactorBuyBu.ABuFactorBuyRsi import AbuFactorBuyRsi
                return AbuFactorBuyRsi(**kwargs)
            else:
                raise ValueError(f"不支持的买入因子: {factor_name}")
        except Exception as e:
            print(f"创建买入因子失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def create_sell_factor(factor_name, **kwargs):
        """
        创建卖出因子
        :param factor_name: 因子名称
        :param kwargs: 因子参数
        :return: 卖出因子实例
        """
        try:
            # 动态导入因子模块
            if factor_name == 'AbuFactorSellBreak':
                from abupy.FactorSellBu.ABuFactorSellBreak import AbuFactorSellBreak
                return AbuFactorSellBreak(**kwargs)
            elif factor_name == 'AbuFactorSellMeanReversion':
                from abupy.FactorSellBu.ABuFactorSellMeanReversion import AbuFactorSellMeanReversion
                return AbuFactorSellMeanReversion(**kwargs)
            elif factor_name == 'AbuFactorSellPreAtrN':
                from abupy.FactorSellBu.ABuFactorAtrNStop import AbuFactorAtrNStop
                return AbuFactorAtrNStop(**kwargs)
            elif factor_name == 'AbuFactorSellRsi':
                from abupy.FactorSellBu.ABuFactorSellRsi import AbuFactorSellRsi
                return AbuFactorSellRsi(**kwargs)
            elif factor_name == 'AbuFactorSellTrailingStop':
                from abupy.FactorSellBu.ABuFactorSellTrailingStop import AbuFactorSellTrailingStop
                return AbuFactorSellTrailingStop(**kwargs)
            else:
                raise ValueError(f"不支持的卖出因子: {factor_name}")
        except Exception as e:
            print(f"创建卖出因子失败: {e}")
            import traceback
            traceback.print_exc()
            return None

# 获取所有股票列表
def get_all_stocks():
    """
    获取数据库中所有可用的股票代码
    :return: 股票代码列表
    """
    try:
        from models import KlineData, db
        
        # 从数据库获取所有唯一的股票代码
        stocks = KlineData.query.with_entities(KlineData.symbol).distinct().all()
        
        # 转换为列表
        stock_list = [stock.symbol for stock in stocks]
        
        return stock_list
    except Exception as e:
        print(f"Error getting all stocks: {e}")
        import traceback
        traceback.print_exc()
        return []

# 获取股票数据
# @lru_cache(maxsize=128)
def get_symbol_data(symbol, start_date, end_date):
    """
    获取股票历史数据
    :param symbol: 股票代码
    :param start_date: 开始日期
    :param end_date: 结束日期
    :return: 股票历史数据DataFrame
    """
    try:
        from models import KlineData, db
        from abupy.MarketBu.ABuSymbolPd import ABuSymbolPd
        from abupy.UtilBu import ABuDateUtil
        from abupy.IndicatorBu.ABuNDAtr import atr21, atr14
        
        # 从数据库获取K线数据
        kline_data = KlineData.query.filter(
            KlineData.symbol == symbol,
            KlineData.date >= start_date,
            KlineData.date <= end_date,
            KlineData.data_type == 'day'
        ).order_by(KlineData.date).all()
        
        if not kline_data:
            print(f"No data found for {symbol} from {start_date} to {end_date}")
            return None
        
        # 转换为DataFrame
        df = pd.DataFrame([{
            'date': pd.to_datetime(data.date),
            'open': data.open,
            'high': data.high,
            'low': data.low,
            'close': data.close,
            'volume': data.volume
        } for data in kline_data])
        
        # 设置日期索引
        df.set_index('date', inplace=True)
        
        # 计算pre_close和p_change
        df['pre_close'] = df['close'].shift(1)
        df['pre_close'].fillna(method='bfill', inplace=True)
        df['p_change'] = (df['close'] - df['pre_close']) / df['pre_close'] * 100
        
        # 计算date_week列
        df['date_week'] = df.index.to_series().apply(lambda x: ABuDateUtil.week_of_date(x.strftime('%Y%m%d'), '%Y%m%d'))
        
        # 计算ATR指标
        print(f"正在计算ATR指标...")
        try:
            # 直接调用atr21和atr14函数
            df['atr21'] = atr21(df['high'].values, df['low'].values, df['pre_close'].values)
            df['atr14'] = atr14(df['high'].values, df['low'].values, df['pre_close'].values)
            
            # 填充缺失值
            df['atr21'].fillna(method='bfill', inplace=True)
            df['atr14'].fillna(method='bfill', inplace=True)
            print(f"ATR指标计算完成")
        except Exception as atr_error:
            print(f"ATR指标计算失败: {atr_error}")
            # 如果ATR计算失败，添加空列
            df['atr21'] = 0.0
            df['atr14'] = 0.0
        
        # 只保留需要的列
        df = df[['open', 'high', 'low', 'close', 'volume', 'pre_close', 'p_change', 'date_week', 'atr21', 'atr14']]
        
        # 设置DataFrame的name属性
        df.name = symbol
        
        print(f"Fetched real data for {symbol} from {start_date} to {end_date}")
        print(f"Data shape: {df.shape}")
        print(f"Data columns: {df.columns.tolist()}")
        return df
    except Exception as e:
        print(f"Error getting symbol data from SQLite: {e}")
        import traceback
        traceback.print_exc()
        return None

# =================== Alpha策略相关接口 ===================

# 获取支持的Alpha因子列表
@moA_bp.route('/alpha/factors', methods=['GET'])
def get_alpha_factors():
    """
    获取支持的Alpha因子列表
    """
    try:
        # 这里可以动态获取所有继承自AbuAlphaBase的类
        # 目前先返回一些示例因子
        alpha_factors = [
            {
                "id": "alpha_001",
                "name": "Alpha001 - 动量策略",
                "description": "基于价格动量的Alpha因子，买入近期上涨的股票",
                "type": "buy"
            },
            {
                "id": "alpha_002",
                "name": "Alpha002 - 反转策略",
                "description": "基于价格反转的Alpha因子，买入近期下跌的股票",
                "type": "buy"
            },
            {
                "id": "alpha_003",
                "name": "Alpha003 - 成交量策略",
                "description": "基于成交量变化的Alpha因子，买入成交量放大的股票",
                "type": "buy"
            },
            {
                "id": "alpha_004",
                "name": "Alpha004 - 波动率策略",
                "description": "基于波动率的Alpha因子，买入波动率下降的股票",
                "type": "buy"
            },
            {
                "id": "alpha_005",
                "name": "Alpha005 - MACD策略",
                "description": "基于MACD指标的Alpha因子，买入MACD金叉的股票",
                "type": "buy"
            },
            {
                "id": "alpha_sell_001",
                "name": "AlphaSell001 - 止盈策略",
                "description": "基于止盈的卖出因子，达到目标收益率后卖出",
                "type": "sell"
            },
            {
                "id": "alpha_sell_002",
                "name": "AlphaSell002 - 止损策略",
                "description": "基于止损的卖出因子，亏损达到一定比例后卖出",
                "type": "sell"
            }
        ]
        
        return jsonify({
            "success": True,
            "data": alpha_factors,
            "message": "获取Alpha因子列表成功"
        })
    except Exception as e:
        print(f"获取Alpha因子列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"获取Alpha因子列表失败: {str(e)}"}), 500

# 获取股票池列表
@moA_bp.route('/alpha/stock-pool', methods=['GET'])
def get_stock_pool():
    """
    获取股票池列表
    """
    try:
        # 这里可以从数据库或配置文件中获取股票池
        # 目前先返回一些示例股票池
        stock_pools = [
            {
                "id": "hs300",
                "name": "沪深300",
                "description": "沪深300指数成分股",
                "symbol_count": 300
            },
            {
                "id": "zz500",
                "name": "中证500",
                "description": "中证500指数成分股",
                "symbol_count": 500
            },
            {
                "id": "szzs",
                "name": "上证指数",
                "description": "上证指数成分股",
                "symbol_count": 1500
            },
            {
                "id": "cyb",
                "name": "创业板",
                "description": "创业板指数成分股",
                "symbol_count": 1000
            }
        ]
        
        return jsonify({
            "success": True,
            "data": stock_pools,
            "message": "获取股票池列表成功"
        })
    except Exception as e:
        print(f"获取股票池列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"获取股票池列表失败: {str(e)}"}), 500



# 运行Alpha策略回测
@moA_bp.route('/alpha/backtest', methods=['POST'])
def run_backtest():
    """
    运行Alpha策略回测
    """
    try:
        # 获取请求参数
        data = request.get_json()
        print(f"收到回测请求参数: {data}")
        
        # 解析请求参数
        if 'params' in data:
            params = data['params']
            requested_start_date = params.get('startDate', params.get('start_date', '2020-01-01'))
            requested_end_date = params.get('endDate', params.get('end_date', '2023-12-31'))
            capital = params.get('initialCash', params.get('capital', 1000000))
            n_folds = params.get('nFolds', 2)
            symbol = params.get('symbol', 'sz000001')
            
            # 获取因子参数
            stock_factors = data.get('stockFactors', data.get('pick_stock_factors', []))
            # 支持前端发送的buyAlphaFactors参数
            buy_factors = data.get('buyFactors', data.get('buy_factors', data.get('buyAlphaFactors', [])))
            # 支持前端发送的sellAlphaFactors参数
            sell_factors = data.get('sellFactors', data.get('sell_factors', data.get('sellAlphaFactors', [])))
            
            # 处理可能包含在params中的因子参数
            if not stock_factors and 'stockFactors' in params:
                stock_factors = params['stockFactors']
            if not stock_factors and 'pick_stock_factors' in params:
                stock_factors = params['pick_stock_factors']
            if not buy_factors and 'buyFactors' in params:
                buy_factors = params['buyFactors']
            if not buy_factors and 'buy_factors' in params:
                buy_factors = params['buy_factors']
            if not buy_factors and 'buyAlphaFactors' in params:
                buy_factors = params['buyAlphaFactors']
            if not sell_factors and 'sellFactors' in params:
                sell_factors = params['sellFactors']
            if not sell_factors and 'sell_factors' in params:
                sell_factors = params['sell_factors']
            if not sell_factors and 'sellAlphaFactors' in params:
                sell_factors = params['sellAlphaFactors']
        else:
            # 兼容旧格式
            requested_start_date = data.get('startDate', data.get('start_date', '2020-01-01'))
            requested_end_date = data.get('endDate', data.get('end_date', '2023-12-31'))
            capital = data.get('capital', data.get('initialCash', 1000000))
            n_folds = data.get('nFolds', 2)
            symbol = data.get('symbol', 'sz000001')
            
            # 获取因子参数
            stock_factors = data.get('stockFactors', data.get('pick_stock_factors', []))
            # 支持前端发送的buyAlphaFactors参数
            buy_factors = data.get('buyFactors', data.get('buy_factors', data.get('buyAlphaFactors', [])))
            # 支持前端发送的sellAlphaFactors参数
            sell_factors = data.get('sellFactors', data.get('sell_factors', data.get('sellAlphaFactors', [])))
        
        # 打印因子信息
        print(f"选股因子: {stock_factors}")
        print(f"买入因子: {buy_factors}")
        print(f"卖出因子: {sell_factors}")
        
        # 获取股票数据的实际日期范围
        date_range = KlineData.query.with_entities(
            db.func.min(KlineData.date).label('min_date'),
            db.func.max(KlineData.date).label('max_date')
        ).filter_by(symbol=symbol).first()
        
        if date_range and date_range.min_date and date_range.max_date:
            actual_start_date = date_range.min_date.strftime('%Y-%m-%d')
            actual_end_date = date_range.max_date.strftime('%Y-%m-%d')
            print(f"股票{symbol}的实际日期范围: {actual_start_date} 到 {actual_end_date}")
            
            # 计算交集日期范围
            start_date = max(requested_start_date, actual_start_date)
            end_date = min(requested_end_date, actual_end_date)
            
            # 检查日期范围是否有效
            if start_date > end_date:
                # 如果没有重叠的日期范围，使用实际的日期范围
                start_date = actual_start_date
                end_date = actual_end_date
                print(f"请求范围与实际数据范围无重叠，使用实际日期范围: {start_date} 到 {end_date}")
            else:
                print(f"使用的日期范围: {start_date} 到 {end_date}")
        else:
            # 如果没有数据或日期为None，使用默认范围
            start_date = requested_start_date
            end_date = requested_end_date
            print(f"使用默认日期范围: {start_date} 到 {end_date}")
        
        # 使用缓存函数获取股票数据
        kl_pd = get_symbol_data(symbol, start_date, end_date)
        
        # 调试信息：检查从数据库获取的kl_pd
        print(f"从数据库获取股票数据后 - kl_pd类型: {type(kl_pd)}")
        print(f"从数据库获取股票数据后 - kl_pd是否为None: {kl_pd is None}")
        if kl_pd is not None:
            print(f"从数据库获取股票数据后 - kl_pd是否为空: {kl_pd.empty}")
            if not kl_pd.empty:
                print(f"从数据库获取股票数据后 - kl_pd形状: {kl_pd.shape}")
                print(f"从数据库获取股票数据后 - kl_pd列名: {kl_pd.columns.tolist()}")
        else:
            print("从数据库获取股票数据失败，kl_pd为None")
        
        if kl_pd is None or kl_pd.empty:
            print("数据库中没有找到数据，尝试从网络获取...")
            try:
                # 为股票代码添加交易所前缀（ABu框架要求）
                if not (symbol.startswith('sh') or symbol.startswith('sz')):
                    # 假设A股默认使用sh前缀，如果获取失败再尝试sz前缀
                    test_symbol = 'sh' + symbol
                    kl_pd = ABuSymbolPd.make_kl_df(test_symbol, start=start_date, end=end_date)
                    
                    if kl_pd is None or kl_pd.empty:
                        test_symbol = 'sz' + symbol
                        kl_pd = ABuSymbolPd.make_kl_df(test_symbol, start=start_date, end=end_date)
                else:
                    kl_pd = ABuSymbolPd.make_kl_df(symbol, start=start_date, end=end_date)
                
                # 调试信息：检查从网络获取的kl_pd
                print(f"从网络获取股票数据后 - kl_pd类型: {type(kl_pd)}")
                print(f"从网络获取股票数据后 - kl_pd是否为None: {kl_pd is None}")
                if kl_pd is not None:
                    print(f"从网络获取股票数据后 - kl_pd是否为空: {kl_pd.empty}")
                    if not kl_pd.empty:
                        print(f"从网络获取股票数据后 - kl_pd形状: {kl_pd.shape}")
                        print(f"从网络获取股票数据后 - kl_pd列名: {kl_pd.columns.tolist()}")
                else:
                    print("从网络获取股票数据失败，kl_pd为None")
                    
                if kl_pd is None or kl_pd.empty:
                    return jsonify({
                        "success": False,
                        "message": "获取股票数据失败"
                    })
            except Exception as e:
                print(f"从网络获取数据失败: {e}")
                return jsonify({
                    "success": False,
                    "message": "获取股票数据失败"
                })
        
        # 创建因子配置字典（ABu框架期望的格式）
        # 处理买入因子
        buy_factors_list = []
        for factor in buy_factors:
            try:
                # 处理因子是字符串的情况
                if isinstance(factor, str):
                    factor_name = factor
                    params_dict = {}
                # 处理因子是字典的情况
                else:
                    factor_name = factor.get('name')
                    factor_params = factor.get('params', '{}')
                    
                    # 解析参数JSON
                    import json
                    params_dict = json.loads(factor_params)
                
                # 创建因子配置字典（包含class键和参数）
                if factor_name == 'AbuFactorBuyBreak':
                    from abupy.FactorBuyBu.ABuFactorBuyBreak import AbuFactorBuyBreak
                    # 提供默认xd参数（突破天数）
                    if 'xd' not in params_dict:
                        params_dict['xd'] = 20
                    buy_factors_list.append({'class': AbuFactorBuyBreak, **params_dict})
                elif factor_name == 'AbuFactorBuyMeanReversion':
                    from abupy.FactorBuyBu.ABuFactorBuyMeanReversion import AbuFactorBuyMeanReversion
                    buy_factors_list.append({'class': AbuFactorBuyMeanReversion, **params_dict})
                elif factor_name == 'AbuFactorBuyGap':
                    from abupy.FactorBuyBu.ABuFactorBuyGap import AbuFactorBuyGap
                    buy_factors_list.append({'class': AbuFactorBuyGap, **params_dict})
                elif factor_name == 'AbuFactorBuyRsi':
                    from abupy.FactorBuyBu.ABuFactorBuyRsi import AbuFactorBuyRsi
                    buy_factors_list.append({'class': AbuFactorBuyRsi, **params_dict})
                else:
                    print(f"不支持的买入因子: {factor_name}")
            except Exception as e:
                print(f"处理买入因子失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 处理卖出因子
        sell_factors_list = []
        for factor in sell_factors:
            try:
                # 处理因子是字符串的情况
                if isinstance(factor, str):
                    factor_name = factor
                    params_dict = {}
                # 处理因子是字典的情况
                else:
                    factor_name = factor.get('name')
                    factor_params = factor.get('params', '{}')
                    
                    # 解析参数JSON
                    import json
                    params_dict = json.loads(factor_params)
                
                # 创建因子配置字典（包含class键和参数）
                if factor_name == 'AbuFactorSellBreak':
                    from abupy.FactorSellBu.ABuFactorSellBreak import AbuFactorSellBreak
                    # 提供默认参数
                    if 'xd' not in params_dict:
                        params_dict['xd'] = 20
                    sell_factors_list.append({'class': AbuFactorSellBreak, **params_dict})
                elif factor_name == 'AbuFactorSellMeanReversion':
                    from abupy.FactorSellBu.ABuFactorSellMeanReversion import AbuFactorSellMeanReversion
                    sell_factors_list.append({'class': AbuFactorSellMeanReversion, **params_dict})
                elif factor_name == 'AbuFactorAtrNStop':
                    from abupy.FactorSellBu.ABuFactorAtrNStop import AbuFactorAtrNStop
                    # 提供默认参数
                    if 'stop_loss_n' not in params_dict:
                        params_dict['stop_loss_n'] = 0.5
                    sell_factors_list.append({'class': AbuFactorAtrNStop, **params_dict})
                elif factor_name == 'AbuFactorSellPreAtrN' or factor_name == 'AbuFactorSellPreAtrNStop':
                    from abupy.FactorSellBu.ABuFactorPreAtrNStop import AbuFactorPreAtrNStop
                    sell_factors_list.append({'class': AbuFactorPreAtrNStop, **params_dict})
                else:
                    print(f"不支持的卖出因子: {factor_name}")
            except Exception as e:
                print(f"处理卖出因子失败: {e}")
                import traceback
                traceback.print_exc()
        
        # 如果没有选择任何因子，使用默认因子配置
        if not buy_factors_list:
            # 默认使用突破买入因子
            from abupy.FactorBuyBu.ABuFactorBuyBreak import AbuFactorBuyBreak
            buy_factors_list.append({'class': AbuFactorBuyBreak, 'xd': 20})
        
        if not sell_factors_list:
            # 默认使用ATR止损卖出因子
            from abupy.FactorSellBu.ABuFactorAtrNStop import AbuFactorAtrNStop
            sell_factors_list.append({'class': AbuFactorAtrNStop, 'stop_loss_n': 1.5})
        
        print(f"创建的因子配置:")
        print(f"买入因子配置: {[f['class'].__name__ for f in buy_factors_list]}")
        print(f"卖出因子配置: {[f['class'].__name__ for f in sell_factors_list]}")
        
        # 执行回测
        print("开始执行ABu回测...")
        
        # 调试信息：检查kl_pd是否为None
        print(f"kl_pd类型: {type(kl_pd)}")
        print(f"kl_pd是否为None: {kl_pd is None}")
        if kl_pd is not None:
            print(f"kl_pd形状: {kl_pd.shape}")
            print(f"kl_pd列名: {kl_pd.columns.tolist()}")
        
        # 确保kl_pd包含必要的列
        if kl_pd is not None and not kl_pd.empty:
            from abupy.UtilBu import ABuDateUtil
            from abupy.IndicatorBu.ABuNDAtr import atr21, atr14
            
            # 检查并添加pre_close列
            if 'pre_close' not in kl_pd.columns:
                kl_pd['pre_close'] = kl_pd['close'].shift(1)
                kl_pd['pre_close'].fillna(method='bfill', inplace=True)
            
            # 检查并添加p_change列
            if 'p_change' not in kl_pd.columns:
                kl_pd['p_change'] = (kl_pd['close'] - kl_pd['pre_close']) / kl_pd['pre_close'] * 100
            
            # 检查并添加date_week列
            if 'date_week' not in kl_pd.columns:
                kl_pd['date_week'] = kl_pd.index.to_series().apply(lambda x: ABuDateUtil.week_of_date(x.strftime('%Y%m%d'), '%Y%m%d'))
            
            # 检查并添加atr21和atr14列
            if 'atr21' not in kl_pd.columns:
                kl_pd['atr21'] = atr21(kl_pd['high'].values, kl_pd['low'].values, kl_pd['pre_close'].values)
                kl_pd['atr21'].fillna(method='bfill', inplace=True)
            
            if 'atr14' not in kl_pd.columns:
                kl_pd['atr14'] = atr14(kl_pd['high'].values, kl_pd['low'].values, kl_pd['pre_close'].values)
                kl_pd['atr14'].fillna(method='bfill', inplace=True)
            
            # 再次检查kl_pd列名
            print(f"处理后kl_pd列名: {kl_pd.columns.tolist()}")
        
        # 直接创建一个简单的基准对象，避免AbuBenchmark内部复杂的初始化逻辑
        class SimpleBenchmark:
            def __init__(self, kl_pd):
                self.kl_pd = kl_pd
                self.benchmark = kl_pd.name
                self.start = kl_pd.index[0].strftime('%Y-%m-%d') if hasattr(kl_pd.index[0], 'strftime') else kl_pd.index[0]
                self.end = kl_pd.index[-1].strftime('%Y-%m-%d') if hasattr(kl_pd.index[-1], 'strftime') else kl_pd.index[-1]
                self.n_folds = 2
        
        # 使用简单的基准对象
        benchmark = SimpleBenchmark(kl_pd)
        
        # 调试信息：检查benchmark的kl_pd属性
        print(f"benchmark.kl_pd类型: {type(benchmark.kl_pd)}")
        print(f"benchmark.kl_pd是否为None: {benchmark.kl_pd is None}")
        
        # 导入AbuCapital类
        from abupy.TradeBu.ABuCapital import AbuCapital
        
        # 创建资金对象
        capital_obj = AbuCapital(init_cash=capital, benchmark=benchmark)
        
        # 导入_do_pick_time_work函数
        from abupy.AlphaBu.ABuPickTimeExecute import _do_pick_time_work
        
        # 调试信息：检查买入因子配置
        print(f"买入因子配置: {buy_factors_list}")
        for i, factor in enumerate(buy_factors_list):
            print(f"买入因子 {i+1} 类型: {type(factor['class'])}")
            print(f"买入因子 {i+1} 参数: {dict(factor.items())}")
        
        # 调试信息：检查kl_pd数据
        print(f"kl_pd数据类型: {type(kl_pd)}")
        print(f"kl_pd是否为空: {kl_pd.empty}")
        print(f"kl_pd形状: {kl_pd.shape}")
        print(f"kl_pd列名: {kl_pd.columns.tolist()}")
        print(f"kl_pd索引类型: {type(kl_pd.index)}")
        print(f"kl_pd前几行:")
        print(kl_pd.head())
        
        # 执行回测
        abu_result_tuple, error_code = _do_pick_time_work(
            capital=capital_obj,  # 初始资金对象
            kl_pd=kl_pd,  # 股票数据
            benchmark=benchmark,
            buy_factors=buy_factors_list,  # 买入因子
            sell_factors=sell_factors_list  # 卖出因子
        )
        if abu_result_tuple is None:
            raise Exception(f"回测执行失败，错误码: {error_code}")
        
        print(f"ABu回测执行完成，结果: {abu_result_tuple}")
        
        # 解析回测结果
        if abu_result_tuple:
            orders_pd, action_pd = abu_result_tuple
            
            # 手动调用apply_action_to_capital函数来更新capital_pd并添加capital_blance列
            from abupy.TradeBu.ABuTradeExecute import apply_action_to_capital
            from abupy import AbuKLManager
            
            # 创建AbuKLManager实例
            kl_pd_manager = AbuKLManager(benchmark, capital_obj)
            # 直接添加择时时间序列到字典中
            kl_pd_manager.pick_kl_pd_dict['pick_time'][symbol] = kl_pd
            
            # 调用apply_action_to_capital函数
            apply_action_to_capital(capital_obj, action_pd, kl_pd_manager, show_progress=False)
            trade_records = []
            trade_id = 0
            
            # 从orders_pd中提取交易记录
            if orders_pd is not None and not orders_pd.empty:
                for _, order in orders_pd.iterrows():
                    try:
                        trade_id += 1
                        
                        # 计算交易指标
                        buy_price = order['buy_price']
                        sell_price = order['sell_price']
                        quantity = order['buy_cnt']
                        profit = order['profit']
                        # 获取sell_type
                        sell_type = order['sell_type']
                        
                        # 标记是否为未卖出订单
                        is_unsold = (sell_type == 'keep')
                        
                        # 处理回测结束时未卖出的订单
                        if is_unsold:
                            # 未卖出订单不计算收益
                            profit = 0.0
                        else:
                            # 处理NaN值
                            if pd.isna(profit):
                                profit = 0.0
                        
                        # 处理日期计算 - 将整数日期转换为datetime对象
                        from datetime import datetime
                        try:
                            # 处理日期：先转换为字符串，再转换为datetime对象
                            buy_date_str = str(order['buy_date'])
                            sell_date_str = str(order['sell_date'])
                            
                            # 确保日期字符串长度为8（YYYYMMDD格式）
                            if len(buy_date_str) == 8:
                                buy_date = datetime.strptime(buy_date_str, '%Y%m%d')
                                buy_date_formatted = buy_date.strftime('%Y-%m-%d')
                            else:
                                buy_date = datetime.now()
                                buy_date_formatted = buy_date.strftime('%Y-%m-%d')
                            
                            if len(sell_date_str) == 8:
                                sell_date = datetime.strptime(sell_date_str, '%Y%m%d')
                                sell_date_formatted = sell_date.strftime('%Y-%m-%d')
                            else:
                                sell_date = datetime.now()
                                sell_date_formatted = sell_date.strftime('%Y-%m-%d')
                                
                            hold_days = (sell_date - buy_date).days
                        except Exception as date_e:
                            print(f"日期转换失败: {date_e}")
                            # 如果日期转换失败，使用默认值
                            buy_date = datetime.now()
                            sell_date = datetime.now()
                            buy_date_formatted = buy_date.strftime('%Y-%m-%d')
                            sell_date_formatted = sell_date.strftime('%Y-%m-%d')
                            hold_days = 0
                        
                        # 计算收益率，避免除以零
                        if is_unsold:
                            profit_rate = "-"
                        else:
                            try:
                                profit_rate = (profit / (buy_price * quantity)) * 100
                                if pd.isna(profit_rate):
                                    profit_rate = 0.0
                            except (ZeroDivisionError, ValueError):
                                profit_rate = 0.0
                        
                        trade_record = {
                            "id": trade_id,
                            "symbol": symbol,
                            "buy_date": buy_date_formatted,
                            "sell_date": sell_date_formatted,
                            "buy_price": round(buy_price, 2) if not pd.isna(buy_price) else 0.0,
                            "sell_price": "-" if is_unsold else (round(sell_price, 2) if not pd.isna(sell_price) else 0.0),
                            "quantity": quantity if not pd.isna(quantity) else 0,
                            "profit": round(profit, 2),
                            "hold_days": hold_days,
                            "profit_rate": profit_rate if is_unsold else round(profit_rate, 2)
                        }
                        trade_records.append(trade_record)
                        print(f"添加交易记录: {trade_record}")
                    except Exception as e:
                        print(f"解析订单失败: {e}")
                        import traceback
                        traceback.print_exc()
            
            # 使用AbuMetricsBase计算回测指标
            metrics = AbuMetricsBase(orders_pd, action_pd, capital_obj, benchmark)
            
            # 添加调试信息
            print(f"AbuMetricsBase valid: {metrics.valid}")
            print(f"capital_pd columns: {capital_obj.capital_pd.columns.tolist()}")
            print(f"orders_pd shape: {orders_pd.shape if orders_pd is not None else 'None'}")
            
            # 检查capital_blance列是否存在，如果不存在则手动添加
            if 'capital_blance' not in capital_obj.capital_pd.columns:
                print("capital_blance列不存在，手动添加")
                capital_obj.capital_pd['capital_blance'] = capital_obj.capital_pd['cash_blance'] + capital_obj.capital_pd['stocks_blance']
                # 更新metrics.valid属性
                metrics.valid = True
            
            metrics.fit_metrics()  # 需要先调用fit_metrics计算指标
            
            # 打印所有可用的metrics属性
            print(f"metrics属性列表: {[attr for attr in dir(metrics) if not attr.startswith('_')]}")
            
            # 获取回测指标
            total_return = metrics.algorithm_period_returns if hasattr(metrics, 'algorithm_period_returns') and not pd.isna(metrics.algorithm_period_returns) else 0
            annual_return = metrics.algorithm_annualized_returns if hasattr(metrics, 'algorithm_annualized_returns') and not pd.isna(metrics.algorithm_annualized_returns) else 0
            max_drawdown = metrics.max_drawdown if hasattr(metrics, 'max_drawdown') and not pd.isna(metrics.max_drawdown) else 0
            sharpe_ratio = metrics.algorithm_sharpe if hasattr(metrics, 'algorithm_sharpe') and not pd.isna(metrics.algorithm_sharpe) else 0
            trade_count = len(trade_records)
            
            # 计算胜率等指标
            if trade_count > 0:
                win_trades = [trade for trade in trade_records if trade['profit'] > 0]
                loss_trades = [trade for trade in trade_records if trade['profit'] <= 0]
                
                win_rate = len(win_trades) / trade_count * 100
                avg_profit = sum(trade['profit'] for trade in win_trades) / len(win_trades) if len(win_trades) > 0 else 0
                avg_loss = sum(trade['profit'] for trade in loss_trades) / len(loss_trades) if len(loss_trades) > 0 else 0
                
                # 计算盈利因子，避免除以零
                total_win_profit = sum(trade['profit'] for trade in win_trades)
                total_loss_profit = abs(sum(trade['profit'] for trade in loss_trades))
                profit_factor = total_win_profit / total_loss_profit if total_loss_profit > 0 else 0
                
                # 确保所有指标都不是NaN
                win_rate = 0 if pd.isna(win_rate) else win_rate
                avg_profit = 0 if pd.isna(avg_profit) else avg_profit
                avg_loss = 0 if pd.isna(avg_loss) else avg_loss
                profit_factor = 0 if pd.isna(profit_factor) else profit_factor
            else:
                win_rate = 0
                avg_profit = 0
                avg_loss = 0
                profit_factor = 0
            
            # 准备回测结果
            backtest_result = {
                "symbol": symbol,
                "stockPool": "custom",
                "startDate": start_date,
                "endDate": end_date,
                "capital": capital,
                "totalReturn": round(total_return * 100, 2),
                "annualReturn": round(annual_return * 100, 2),
                "maxDrawdown": round(max_drawdown * 100, 2),
                "sharpeRatio": round(sharpe_ratio, 2),
                "tradeCount": trade_count,
                "winRate": round(win_rate, 2),
                "avgProfit": round(avg_profit, 2),
                "avgLoss": round(avg_loss, 2),
                "profitFactor": round(profit_factor, 2)
            }
            
            # 准备图表数据
            # 价格走势
            price = []
            for idx, row in kl_pd.iterrows():
                try:
                    price.append({
                        "date": idx.strftime('%Y-%m-%d'),
                        "close": round(row['close'], 2),
                        "open": round(row['open'], 2),
                        "high": round(row['high'], 2),
                        "low": round(row['low'], 2),
                        "volume": int(row['volume'])
                    })
                except Exception as e:
                    print(f"处理价格数据失败: {e}")
            
            # 收益率曲线
            cumReturn = []
            try:
                # 从capital_pd中获取累计收益率数据
                if hasattr(capital_obj, 'capital_pd') and not capital_obj.capital_pd.empty:
                    # 计算基准资金（初始资金）
                    base_capital = capital_obj.capital_pd['capital_blance'].iloc[0]
                    
                    for idx, row in capital_obj.capital_pd.iterrows():
                        try:
                            # 计算累计收益率
                            capital_blance = row['capital_blance']
                            if pd.isna(capital_blance):
                                return_value = 0.0
                            else:
                                # 计算相对于初始资金的收益率
                                return_value = round(((capital_blance / base_capital) - 1) * 100, 2)
                            
                            cumReturn.append({
                                "date": idx.strftime('%Y-%m-%d'),
                                "return": return_value
                            })
                        except Exception as e:
                            print(f"处理收益率曲线数据失败: {e}")
            except Exception as e:
                print(f"获取收益率曲线数据失败: {e}")
            
            # 回撤曲线
            drawdown_data = []
            try:
                # 从metrics中获取回撤数据，如果metrics对象有drawdown属性
                if hasattr(metrics, 'drawdown') and metrics.drawdown is not None:
                    drawdown = metrics.drawdown
                    for idx, value in drawdown.iterrows():
                        try:
                            # 检查值是否为NaN
                            if pd.isna(value):
                                drawdown_value = 0.0
                            else:
                                drawdown_value = round(value * 100, 2)
                            
                            drawdown_data.append({
                                "date": idx.strftime('%Y-%m-%d'),
                                "drawdown": drawdown_value
                            })
                        except Exception as e:
                            print(f"处理回撤曲线数据失败: {e}")
                else:
                    # 备选方案：从capital_pd中计算回撤
                    if hasattr(capital_obj, 'capital_pd') and not capital_obj.capital_pd.empty:
                        capital_blance = capital_obj.capital_pd['capital_blance']
                        if not capital_blance.empty:
                            # 计算滚动最大资金
                            rolling_max = capital_blance.expanding().max()
                            # 计算每日回撤
                            daily_drawdown = (capital_blance / rolling_max - 1) * 100
                            
                            for idx, value in daily_drawdown.items():
                                try:
                                    drawdown_value = round(value, 2) if not pd.isna(value) else 0.0
                                    drawdown_data.append({
                                        "date": idx.strftime('%Y-%m-%d'),
                                        "drawdown": drawdown_value
                                    })
                                except Exception as e:
                                    print(f"处理回撤曲线数据失败: {e}")
            except Exception as e:
                print(f"获取回撤曲线数据失败: {e}")
            
            chart_data = {
                "price": price,
                "cumReturn": cumReturn,
                "drawdown": drawdown_data
            }
            
            print(f"回测结果准备完成，交易记录数量: {len(trade_records)}")
            
            return jsonify({
                "success": True,
                "data": {
                    "backtestResult": backtest_result,
                    "chartData": chart_data,
                    "tradeRecords": trade_records
                },
                "message": "回测成功"
            })
        else:
            # 如果ABu回测失败，使用传统的移动平均线策略作为备选
            print("ABu回测失败，使用备选策略...")
            
            # 使用简单的移动平均线策略生成真实的交易记录
            # 计算10日均线
            kl_pd['ma10'] = kl_pd['close'].rolling(window=10).mean()
            
            # 初始化交易变量
            is_holding = False
            buy_date = None
            buy_price = None
            cash = capital
            shares = 0
            trade_records = []
            trade_id = 0
            
            # 遍历每一天的K线数据
            for idx, row in kl_pd.iterrows():
                # 确保已经有足够的数据计算均线
                if pd.isna(row['ma10']):
                    continue
                
                # 如果当前没有持仓，且收盘价突破10日均线，买入
                if not is_holding and row['close'] > row['ma10']:
                    # 计算可以买入的股票数量（不考虑手续费）
                    shares = int(cash // row['close'])
                    if shares > 0:
                        try:
                            # 更新持仓状态
                            is_holding = True
                            buy_date = idx
                            buy_price = row['close']
                            cash -= shares * buy_price
                            buy_date_formatted = idx.strftime('%Y-%m-%d')
                            print(f"买入: {buy_date_formatted}, 价格: {buy_price}, 数量: {shares}, 剩余资金: {cash}")
                        except Exception as e:
                            print(f"处理买入交易失败: {e}")
                            import traceback
                            traceback.print_exc()
                
                # 如果当前有持仓，且收盘价跌破10日均线，卖出
                elif is_holding and row['close'] < row['ma10']:
                    try:
                        # 计算卖出收益
                        sell_price = row['close']
                        profit = shares * (sell_price - buy_price)
                        hold_days = (idx - buy_date).days
                        profit_rate = (profit / (buy_price * shares)) * 100
                        
                        # 格式化日期
                        buy_date_formatted = buy_date.strftime('%Y-%m-%d')
                        sell_date_formatted = idx.strftime('%Y-%m-%d')
                        
                        # 记录交易
                        trade_id += 1
                        trade_record = {
                            "id": trade_id,
                            "symbol": symbol,
                            "buy_date": buy_date_formatted,
                            "sell_date": sell_date_formatted,
                            "buy_price": round(buy_price, 2),
                            "sell_price": round(sell_price, 2),
                            "quantity": shares,
                            "profit": round(profit, 2),
                            "hold_days": hold_days,
                            "profit_rate": round(profit_rate, 2)
                        }
                        trade_records.append(trade_record)
                        print(f"添加交易记录: {trade_record}")
                        
                        # 更新持仓状态
                        cash += shares * sell_price
                        is_holding = False
                        shares = 0
                        print(f"卖出: {sell_date_formatted}, 价格: {sell_price}, 收益: {profit}, 总资金: {cash}")
                    except Exception as e:
                        print(f"处理卖出交易失败: {e}")
                        import traceback
                        traceback.print_exc()
            
            # 如果在回测结束时仍然持有股票，强制卖出
            if is_holding:
                try:
                    # 计算卖出收益
                    sell_price = kl_pd['close'].iloc[-1]
                    profit = shares * (sell_price - buy_price)
                    hold_days = (kl_pd.index[-1] - buy_date).days
                    profit_rate = (profit / (buy_price * shares)) * 100
                    
                    # 格式化日期
                    buy_date_formatted = buy_date.strftime('%Y-%m-%d')
                    sell_date_formatted = kl_pd.index[-1].strftime('%Y-%m-%d')
                    
                    # 记录交易
                    trade_id += 1
                    trade_record = {
                        "id": trade_id,
                        "symbol": symbol,
                        "buy_date": buy_date_formatted,
                        "sell_date": sell_date_formatted,
                        "buy_price": round(buy_price, 2),
                        "sell_price": round(sell_price, 2),
                        "quantity": shares,
                        "profit": round(profit, 2),
                        "hold_days": hold_days,
                        "profit_rate": round(profit_rate, 2)
                    }
                    trade_records.append(trade_record)
                    print(f"添加强制卖出交易记录: {trade_record}")
                    
                    # 更新持仓状态
                    cash += shares * sell_price
                    is_holding = False
                    shares = 0
                    print(f"强制卖出: {sell_date_formatted}, 价格: {sell_price}, 收益: {profit}, 总资金: {cash}")
                except Exception as e:
                    print(f"处理强制卖出失败: {e}")
                    import traceback
                    traceback.print_exc()
            
            # 计算回测结果指标
            total_return = (cash - capital) / capital * 100
            
            # 计算年化收益率
            days = (kl_pd.index[-1] - kl_pd.index[0]).days
            if days > 0:
                annual_return = (1 + total_return / 100) ** (365 / days) - 1
                annual_return = annual_return * 100
            else:
                annual_return = 0
            
            # 计算最大回撤
            cum_return = (kl_pd['close'] / kl_pd['close'].iloc[0]).cumprod()
            max_return = cum_return.cummax()
            drawdown = (cum_return - max_return) / max_return
            max_drawdown = drawdown.min() * 100
            
            # 计算夏普比率（简化版）
            daily_return = kl_pd['close'].pct_change().dropna()
            if not daily_return.empty and daily_return.std() > 0:
                sharpe_ratio = (daily_return.mean() / daily_return.std()) * np.sqrt(252)
            else:
                sharpe_ratio = 0
            
            # 计算交易相关指标
            trade_count = len(trade_records)
            if trade_count > 0:
                win_trades = [trade for trade in trade_records if trade['profit'] > 0]
                loss_trades = [trade for trade in trade_records if trade['profit'] <= 0]
                
                win_rate = len(win_trades) / trade_count * 100
                avg_profit = sum(trade['profit'] for trade in win_trades) / len(win_trades) if len(win_trades) > 0 else 0
                avg_loss = sum(trade['profit'] for trade in loss_trades) / len(loss_trades) if len(loss_trades) > 0 else 0
                profit_factor = sum(trade['profit'] for trade in win_trades) / abs(sum(trade['profit'] for trade in loss_trades)) if len(loss_trades) > 0 else 0
            else:
                win_rate = 0
                avg_profit = 0
                avg_loss = 0
                profit_factor = 0
            
            # 准备回测结果
            backtest_result = {
                "symbol": symbol,
                "stockPool": "custom",
                "startDate": start_date,
                "endDate": end_date,
                "capital": capital,
                "totalReturn": round(total_return, 2),
                "annualReturn": round(annual_return, 2),
                "maxDrawdown": round(max_drawdown, 2),
                "sharpeRatio": round(sharpe_ratio, 2),
                "tradeCount": trade_count,
                "winRate": round(win_rate, 2),
                "avgProfit": round(avg_profit, 2),
                "avgLoss": round(avg_loss, 2),
                "profitFactor": round(profit_factor, 2)
            }
            
            # 准备图表数据
            # 价格走势
            price = []
            for idx, row in kl_pd.iterrows():
                try:
                    price.append({
                        "date": idx.strftime('%Y-%m-%d'),
                        "close": round(row['close'], 2),
                        "open": round(row['open'], 2),
                        "high": round(row['high'], 2),
                        "low": round(row['low'], 2),
                        "volume": int(row['volume'])
                    })
                except Exception as e:
                    print(f"处理价格数据失败: {e}")
            
            # 收益率曲线
            cumReturn = []
            for idx, value in cum_return.items():
                try:
                    # 检查值是否为NaN
                    if pd.isna(value):
                        return_value = 0.0
                    else:
                        return_value = round((value - 1) * 100, 2)
                    
                    cumReturn.append({
                        "date": idx.strftime('%Y-%m-%d'),
                        "return": return_value
                    })
                except Exception as e:
                    print(f"处理收益率曲线数据失败: {e}")
            
            # 回撤曲线
            drawdown_data = []
            for idx, value in drawdown.items():
                try:
                    # 检查值是否为NaN
                    if pd.isna(value):
                        drawdown_value = 0.0
                    else:
                        drawdown_value = round(value * 100, 2)
                    
                    drawdown_data.append({
                        "date": idx.strftime('%Y-%m-%d'),
                        "drawdown": drawdown_value
                    })
                except Exception as e:
                    print(f"处理回撤曲线数据失败: {e}")
            
            chart_data = {
                "price": price,
                "cumReturn": cumReturn,
                "drawdown": drawdown_data
            }
            
            print(f"回测结果准备完成，交易记录数量: {len(trade_records)}")
            
            return jsonify({
                "success": True,
                "data": {
                    "backtestResult": backtest_result,
                    "chartData": chart_data,
                    "tradeRecords": trade_records
                },
                "message": "回测成功（使用备选策略）"
            })
        
    except Exception as e:
        print(f"回测失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"回测失败: {str(e)}"}), 500

# 获取策略报告
@moA_bp.route('/alpha/strategy-report/<report_id>', methods=['GET'])
def get_strategy_report(report_id):
    """
    获取策略报告
    """
    try:
        # 这里可以从数据库或文件中获取策略报告
        # 目前先返回模拟数据
        report = {
            "reportId": report_id,
            "strategyName": "Alpha动量策略",
            "createTime": "2024-01-15 14:30:00",
            "backtestResult": {
                "totalReturn": 45.2,
                "annualReturn": 12.8,
                "maxDrawdown": -18.5,
                "sharpeRatio": 1.5,
                "tradeCount": 120,
                "winRate": 68,
                "avgProfit": 6.1,
                "avgLoss": 2.8,
                "profitFactor": 2.1
            },
            "alphaFactors": [
                {
                    "id": "alpha_001",
                    "name": "Alpha001 - 动量策略",
                    "type": "buy"
                },
                {
                    "id": "alpha_sell_001",
                    "name": "AlphaSell001 - 止盈策略",
                    "type": "sell"
                },
                {
                    "id": "alpha_sell_002",
                    "name": "AlphaSell002 - 止损策略",
                    "type": "sell"
                }
            ],
            "stockPool": {
                "id": "hs300",
                "name": "沪深300"
            },
            "backtestPeriod": {
                "startDate": "2020-01-01",
                "endDate": "2023-12-31"
            },
            "capital": 1000000,
            "performanceMetrics": {
                "alpha": 0.08,
                "beta": 0.85,
                "sortinoRatio": 1.8,
                "calmarRatio": 0.7
            }
        }
        
        return jsonify({
            "success": True,
            "data": report,
            "message": "获取策略报告成功"
        })
    except Exception as e:
        print(f"获取策略报告失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"获取策略报告失败: {str(e)}"}), 500

# 获取策略报告列表
@moA_bp.route('/alpha/strategy-reports', methods=['GET'])
def get_strategy_reports():
    """
    获取策略报告列表
    """
    try:
        # 这里可以从数据库中获取策略报告列表
        # 目前先返回模拟数据
        reports = [
            {
                "reportId": "report_001",
                "strategyName": "Alpha动量策略",
                "createTime": "2024-01-15 14:30:00",
                "totalReturn": 45.2,
                "annualReturn": 12.8,
                "maxDrawdown": -18.5,
                "sharpeRatio": 1.5
            },
            {
                "reportId": "report_002",
                "strategyName": "Alpha反转策略",
                "createTime": "2024-01-14 10:20:00",
                "totalReturn": 38.5,
                "annualReturn": 10.2,
                "maxDrawdown": -15.3,
                "sharpeRatio": 1.3
            },
            {
                "reportId": "report_003",
                "strategyName": "Alpha成交量策略",
                "createTime": "2024-01-13 16:45:00",
                "totalReturn": 52.8,
                "annualReturn": 14.1,
                "maxDrawdown": -22.1,
                "sharpeRatio": 1.4
            }
        ]
        
        return jsonify({
            "success": True,
            "data": reports,
            "message": "获取策略报告列表成功"
        })
    except Exception as e:
        print(f"获取策略报告列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": f"获取策略报告列表失败: {str(e)}"}), 500

