# 线性拟合分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSymbol import code_to_symbol
from abupy.UtilBu.ABuRegUtil import (
    regress_xy,
    regress_y,
    calc_regress_deg,
    regress_xy_polynomial,
    regress_y_polynomial,
    valid_poly,
    least_valid_poly,
    search_best_poly,
    metrics_rmse, metrics_mae, metrics_mse
)


# 获取股票线性拟合分析
@moA_bp.route('/linear-fit/single', methods=['GET'])
def get_single_linear_fit():
    try:
        symbol = request.args.get('symbol')
        poly = int(request.args.get('poly', 1))  # 多项式次数，1为线性
        metric = request.args.get('metric', 'rmse')  # rmse, mae, mse
        n_folds = int(request.args.get('n_folds', 2))
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        
        # 获取股票数据
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
        if kl_df is None or kl_df.empty:
            return jsonify({'error': f'获取股票{symbol}数据失败'}), 404
        
        # 准备数据
        y = kl_df['close'].values
        x = kl_df.index.values.astype(float)
        
        # 选择评估指标
        metrics_func = metrics_rmse
        if metric == 'mae':
            metrics_func = metrics_mae
        elif metric == 'mse':
            metrics_func = metrics_mse
        
        # 进行线性/多项式拟合
        if poly == 1:
            # 线性拟合
            slope, intercept, r2, predicted, metrics_result = regress_xy(x, y, mode=True, zoom=False, show=False)
        else:
            # 多项式拟合
            slope, intercept, r2, predicted, metrics_result = regress_xy_polynomial(x, y, poly=poly, zoom=False, show=False)
        
        # 计算拟合直线角度
        deg = calc_regress_deg(y)
        
        # 验证拟合效果
        is_valid = valid_poly(y, poly=poly, zoom=False, show=False, metrics_func=metrics_func)
        
        # 组织结果
        result = {
            'symbol': symbol,
            'poly': poly,
            'metric': metric,
            'slope': float(slope),
            'intercept': float(intercept),
            'r2': float(r2),
            'metrics_value': float(metrics_result),
            'deg': float(deg),
            'is_valid': bool(is_valid),
            'data_points': len(y),
            'x': x.tolist(),
            'y': y.tolist(),
            'predicted': predicted.tolist()
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取股票线性拟合分析失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取股票线性拟合分析失败: {str(e)}'}), 500


# 寻找最佳多项式拟合次数
@moA_bp.route('/linear-fit/best-poly', methods=['GET'])
def get_best_poly():
    try:
        symbol = request.args.get('symbol')
        poly_min = int(request.args.get('poly_min', 1))
        poly_max = int(request.args.get('poly_max', 10))
        metric = request.args.get('metric', 'rmse')
        n_folds = int(request.args.get('n_folds', 2))
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        
        # 获取股票数据
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
        if kl_df is None or kl_df.empty:
            return jsonify({'error': f'获取股票{symbol}数据失败'}), 404
        
        # 准备数据
        y = kl_df['close'].values
        
        # 选择评估指标
        metrics_func = metrics_rmse
        if metric == 'mae':
            metrics_func = metrics_mae
        elif metric == 'mse':
            metrics_func = metrics_mse
        
        # 寻找最佳拟合次数
        best_poly = search_best_poly(
            y, 
            poly_min=poly_min, 
            poly_max=poly_max, 
            zoom=False, 
            show=False, 
            metrics_func=metrics_func
        )
        
        # 计算最小有效拟合次数
        least_valid = least_valid_poly(y, zoom=False, show=False, metrics_func=metrics_func)
        
        # 组织结果
        result = {
            'symbol': symbol,
            'metric': metric,
            'best_poly': int(best_poly),
            'least_valid_poly': int(least_valid),
            'poly_min': poly_min,
            'poly_max': poly_max
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('寻找最佳多项式拟合次数失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'寻找最佳多项式拟合次数失败: {str(e)}'}), 500


# 获取多只股票线性拟合比较
@moA_bp.route('/linear-fit/compare', methods=['POST'])
def get_linear_fit_compare():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        poly = int(data.get('poly', 1))
        metric = data.get('metric', 'rmse')
        n_folds = int(data.get('n_folds', 2))
        
        if not symbols or not isinstance(symbols, list) or len(symbols) < 2:
            return jsonify({'error': '股票代码列表不能为空且至少需要两只股票'}), 400
        
        # 选择评估指标
        metrics_func = metrics_rmse
        if metric == 'mae':
            metrics_func = metrics_mae
        elif metric == 'mse':
            metrics_func = metrics_mse
        
        results = []
        for symbol in symbols:
            try:
                # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
                symbol_obj = code_to_symbol(symbol)
                
                # 获取股票数据
                kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
                if kl_df is None or kl_df.empty:
                    continue
                
                # 准备数据
                y = kl_df['close'].values
                x = kl_df.index.values.astype(float)
                
                # 进行拟合
                if poly == 1:
                    # 线性拟合
                    slope, intercept, r2, predicted, metrics_result = regress_xy(x, y, mode=True, zoom=False, show=False)
                else:
                    # 多项式拟合
                    slope, intercept, r2, predicted, metrics_result = regress_xy_polynomial(x, y, poly=poly, zoom=False, show=False)
                
                # 计算拟合直线角度
                deg = calc_regress_deg(y)
                
                # 验证拟合效果
                is_valid = valid_poly(y, poly=poly, zoom=False, show=False, metrics_func=metrics_func)
                
                # 组织单只股票结果
                stock_result = {
                    'symbol': symbol,
                    'slope': float(slope),
                    'intercept': float(intercept),
                    'r2': float(r2),
                    'metrics_value': float(metrics_result),
                    'deg': float(deg),
                    'is_valid': bool(is_valid),
                    'data_points': len(y)
                }
                results.append(stock_result)
            except Exception as e:
                print(f'获取股票{symbol}线性拟合分析失败:', str(e))
                continue
        
        # 组织结果
        result = {
            'symbols': symbols,
            'poly': poly,
            'metric': metric,
            'results': results
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取多只股票线性拟合比较失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取多只股票线性拟合比较失败: {str(e)}'}), 500
