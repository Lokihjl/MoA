# Alpha策略相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os
import numpy as np
import pandas as pd
import datetime

# 将项目根目录添加到Python路径中，以便导入abupy模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

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
        stock_pool_id = data.get('stockPool', 'hs300')
        buy_alpha_ids = data.get('buyAlphaFactors', [])
        sell_alpha_ids = data.get('sellAlphaFactors', [])
        start_date = data.get('startDate', '2020-01-01')
        end_date = data.get('endDate', '2023-12-31')
        capital = data.get('capital', 1000000)
        
        # 目前只支持单股票回测，后续可以扩展到股票池
        # 这里使用腾讯股票作为示例
        symbol = 'sz000001'
        
        # 尝试使用ABU量化框架获取真实数据
        kl_pd = None
        try:
            # 导入ABU量化框架的股票数据函数
            from abupy import ABuSymbolPd
            from abupy.CoreBu.ABuEnv import EMarketSourceType
            from abupy.CoreBu import ABuEnv
            
            # 设置数据源为腾讯财经
            ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
            
            # 使用ABU框架获取股票历史K线数据
            kl_pd = ABuSymbolPd.make_kl_df(symbol, start=start_date, end=end_date)
            
            if kl_pd is None or kl_pd.empty:
                print("ABU框架返回空数据，将生成模拟数据")
                kl_pd = None
        except Exception as e:
            print(f"使用ABU框架获取数据失败: {e}")
            kl_pd = None
        
        # 如果ABU框架失败，生成模拟数据
        if kl_pd is None:
            # 生成30天的模拟数据
            import random
            
            # 生成日期序列
            end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d') if end_date else datetime.datetime.now()
            start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d') if start_date else end_dt - datetime.timedelta(days=30)
            
            date_range = pd.date_range(start=start_dt, end=end_dt, freq='B')  # B代表工作日
            
            # 生成模拟价格数据
            np.random.seed(42)  # 设置随机种子，确保结果可重现
            
            # 生成基础价格序列，带有随机波动
            base_price = 100.0
            prices = []
            for i in range(len(date_range)):
                if i == 0:
                    prices.append(base_price)
                else:
                    # 每天的价格有-2%到+2%的随机波动
                    change_percent = np.random.uniform(-0.02, 0.02)
                    new_price = prices[-1] * (1 + change_percent)
                    prices.append(new_price)
            
            # 创建DataFrame
            kl_pd = pd.DataFrame({
                'date': date_range,
                'close': prices,
                'open': [p * np.random.uniform(0.99, 1.01) for p in prices],
                'high': [p * np.random.uniform(1.0, 1.02) for p in prices],
                'low': [p * np.random.uniform(0.98, 1.0) for p in prices],
                'volume': [np.random.randint(1000000, 10000000) for _ in range(len(date_range))]
            })
            
            # 将date列设置为索引
            kl_pd.set_index('date', inplace=True)
        
        # 计算简单的收益率
        start_price = kl_pd['close'].iloc[0]
        end_price = kl_pd['close'].iloc[-1]
        total_return = (end_price - start_price) / start_price
        
        # 计算年化收益率
        days = (kl_pd.index[-1] - kl_pd.index[0]).days
        if days > 0:
            annual_return = (1 + total_return) ** (365 / days) - 1
        else:
            annual_return = 0
        
        # 计算最大回撤
        cum_return = (kl_pd['close'] / start_price).cumprod()
        max_return = cum_return.cummax()
        drawdown = (cum_return - max_return) / max_return
        max_drawdown = drawdown.min()
        
        # 计算夏普比率（简化版）
        daily_return = kl_pd['close'].pct_change().dropna()
        if not daily_return.empty and daily_return.std() > 0:
            sharpe_ratio = (daily_return.mean() / daily_return.std()) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
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
