# -*- coding: utf-8 -*-
"""
Alpha策略模块，用于实现各种Alpha因子的计算和策略回测
"""

from flask import Blueprint, request, jsonify
from abupy.AlphaBu.ABuAlphaModel import AbuAlphaBase
from abupy.AlphaBu.ABuAlphaBuyBase import AbuAlphaBuyBase
from abupy.AlphaBu.ABuAlphaSellBase import AbuAlphaSellBase
from abupy.AlphaBu import ABuPickStockExecute
from abupy import ABuSymbolPd, AbuCapital, AbuKLManager
import numpy as np
import pandas as pd
from functools import lru_cache

# 创建蓝图
alpha_strategy_bp = Blueprint('alpha_strategy', __name__)

@alpha_strategy_bp.route('/alpha-factors', methods=['GET'])
def get_alpha_factors():
    """
    获取支持的Alpha因子列表
    """
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

@alpha_strategy_bp.route('/stock-pool', methods=['GET'])
def get_stock_pool():
    """
    获取股票池列表
    """
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

@lru_cache(maxsize=128)
def get_symbol_data(symbol, n_folds=2):
    """
    获取股票数据，带缓存
    """
    try:
        # 使用ABuSymbolPd获取股票数据
        kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=n_folds)
        return kl_pd
    except Exception as e:
        print(f"获取股票数据失败: {e}")
        return None

@alpha_strategy_bp.route('/backtest', methods=['POST'])
def run_backtest():
    """
    运行Alpha策略回测
    """
    try:
        # 获取请求参数
        data = request.get_json()
        stock_pool_id = data.get('stockPool', 'hs300')
        buy_alpha_ids = data.get('buyAlphaFactors', [])
        sell_alpha_ids = data.get('sellAlphaFactors', [])
        start_date = data.get('startDate', '2020-01-01')
        end_date = data.get('endDate', '2023-12-31')
        capital = data.get('capital', 1000000)
        n_folds = data.get('nFolds', 2)
        
        # 目前只支持单股票回测，后续可以扩展到股票池
        # 这里使用腾讯股票作为示例
        symbol = 'sz000001'
        
        # 获取股票数据
        kl_pd = get_symbol_data(symbol, n_folds=n_folds)
        
        if kl_pd is None or kl_pd.empty:
            return jsonify({
                "success": False,
                "message": "获取股票数据失败"
            })
        
        # 简单的回测逻辑，实际应该使用ABu的回测框架
        # 这里只返回模拟数据，后续可以扩展为真实回测
        
        # 计算简单的收益率
        start_price = kl_pd['close'].iloc[0]
        end_price = kl_pd['close'].iloc[-1]
        total_return = (end_price - start_price) / start_price
        
        # 计算年化收益率
        days = (kl_pd.index[-1] - kl_pd.index[0]).days
        annual_return = (1 + total_return) ** (365 / days) - 1
        
        # 计算最大回撤
        cum_return = (kl_pd['close'] / start_price).cumprod()
        max_return = cum_return.cummax()
        drawdown = (cum_return - max_return) / max_return
        max_drawdown = drawdown.min()
        
        # 计算夏普比率（简化版）
        daily_return = kl_pd['close'].pct_change().dropna()
        sharpe_ratio = (daily_return.mean() / daily_return.std()) * np.sqrt(252)
        
        # 准备回测结果
        backtest_result = {
            "symbol": symbol,
            "stockPool": stock_pool_id,
            "startDate": start_date,
            "endDate": end_date,
            "capital": capital,
            "totalReturn": round(total_return * 100, 2),
            "annualReturn": round(annual_return * 100, 2),
            "maxDrawdown": round(max_drawdown * 100, 2),
            "sharpeRatio": round(sharpe_ratio, 2),
            "tradeCount": 100,  # 模拟数据
            "winRate": 65,  # 模拟数据
            "avgProfit": 5.2,  # 模拟数据
            "avgLoss": 3.1,  # 模拟数据
            "profitFactor": 1.8  # 模拟数据
        }
        
        # 准备图表数据
        # 价格走势
        price_data = []
        for idx, row in kl_pd.iterrows():
            price_data.append({
                "date": idx.strftime('%Y-%m-%d'),
                "close": round(row['close'], 2),
                "open": round(row['open'], 2),
                "high": round(row['high'], 2),
                "low": round(row['low'], 2),
                "volume": int(row['volume'])
            })
        
        # 收益率曲线
        cum_return_data = []
        for idx, value in cum_return.items():
            cum_return_data.append({
                "date": idx.strftime('%Y-%m-%d'),
                "return": round((value - 1) * 100, 2)
            })
        
        # 回撤曲线
        drawdown_data = []
        for idx, value in drawdown.items():
            drawdown_data.append({
                "date": idx.strftime('%Y-%m-%d'),
                "drawdown": round(value * 100, 2)
            })
        
        chart_data = {
            "price": price_data,
            "cumReturn": cum_return_data,
            "drawdown": drawdown_data
        }
        
        return jsonify({
            "success": True,
            "data": {
                "backtestResult": backtest_result,
                "chartData": chart_data
            },
            "message": "回测成功"
        })
        
    except Exception as e:
        print(f"回测失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "success": False,
            "message": f"回测失败: {str(e)}"
        })

@alpha_strategy_bp.route('/strategy-report/<report_id>', methods=['GET'])
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
        return jsonify({
            "success": False,
            "message": f"获取策略报告失败: {str(e)}"
        })

@alpha_strategy_bp.route('/strategy-reports', methods=['GET'])
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
        return jsonify({
            "success": False,
            "message": f"获取策略报告列表失败: {str(e)}"
        })
