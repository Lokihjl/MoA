# 位移路程比分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os
import numpy as np

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSymbol import code_to_symbol


# 计算位移路程比
def calculate_displacement_ratio(close):
    """
    计算位移路程比(DDR, Displacement to Distance Ratio)
    DDR = 净位移 / 总路程
    净位移 = |终点价格 - 起点价格|
    总路程 = 所有相邻价格变化的绝对值之和
    
    参数:
    close: 收盘价数组
    
    返回:
    ddr: 位移路程比
    net_displacement: 净位移
    total_distance: 总路程
    """
    if len(close) < 2:
        return 0.0, 0.0, 0.0
    
    # 计算净位移
    net_displacement = abs(close[-1] - close[0])
    
    # 计算总路程
    total_distance = np.sum(np.abs(np.diff(close)))
    
    # 计算位移路程比
    if total_distance == 0:
        ddr = 1.0  # 价格没有变化，位移路程比为1
    else:
        ddr = net_displacement / total_distance
    
    return ddr, net_displacement, total_distance


# 获取单个股票位移路程比分析
@moA_bp.route('/displacement-ratio/single', methods=['GET'])
def get_single_displacement_ratio():
    try:
        symbol = request.args.get('symbol')
        period = request.args.get('period', '1d')
        n_folds = int(request.args.get('n_folds', 2))
        window = int(request.args.get('window', 20))  # 计算位移路程比的窗口大小
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        
        # 获取股票数据
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
        if kl_df is None or kl_df.empty:
            return jsonify({'error': f'获取股票{symbol}数据失败'}), 404
        
        # 准备数据
        close = kl_df['close'].values
        dates = kl_df.index.values.astype(float)
        
        # 计算不同窗口大小的位移路程比
        ddr_results = []
        for w in range(5, 61, 5):  # 测试不同窗口大小的DDR值
            ddr_list = []
            for i in range(len(close) - w + 1):
                window_close = close[i:i+w]
                ddr, _, _ = calculate_displacement_ratio(window_close)
                ddr_list.append(ddr)
            
            # 计算该窗口大小下的平均DDR和标准差
            avg_ddr = np.mean(ddr_list) if ddr_list else 0
            std_ddr = np.std(ddr_list) if ddr_list else 0
            max_ddr = np.max(ddr_list) if ddr_list else 0
            min_ddr = np.min(ddr_list) if ddr_list else 0
            
            ddr_results.append({
                'window_size': w,
                'avg_ddr': float(avg_ddr),
                'std_ddr': float(std_ddr),
                'max_ddr': float(max_ddr),
                'min_ddr': float(min_ddr)
            })
        
        # 计算指定窗口大小的位移路程比序列
        specified_ddr_list = []
        for i in range(len(close) - window + 1):
            window_close = close[i:i+window]
            ddr, net_displacement, total_distance = calculate_displacement_ratio(window_close)
            specified_ddr_list.append({
                'date': float(dates[i+window-1]),
                'ddr': float(ddr),
                'net_displacement': float(net_displacement),
                'total_distance': float(total_distance)
            })
        
        result = {
            'symbol': symbol,
            'period': period,
            'n_folds': n_folds,
            'window': window,
            'dates': dates.tolist(),
            'close': close.tolist(),
            'ddr_results': ddr_results,
            'specified_ddr_list': specified_ddr_list
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取单个股票位移路程比分析失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取单个股票位移路程比分析失败: {str(e)}'}), 500


# 获取多只股票位移路程比比较
@moA_bp.route('/displacement-ratio/compare', methods=['POST'])
def get_multi_displacement_ratio():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        n_folds = int(data.get('n_folds', 2))
        window = int(data.get('window', 20))
        
        if not symbols or not isinstance(symbols, list) or len(symbols) < 2:
            return jsonify({'error': '股票代码列表不能为空且至少需要两只股票'}), 400
        
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
                close = kl_df['close'].values
                
                # 计算不同时间周期的位移路程比
                short_term = close[-20:]  # 短期：20天
                medium_term = close[-60:]  # 中期：60天
                long_term = close[-120:]  # 长期：120天
                
                # 计算各周期的DDR
                short_ddr, _, _ = calculate_displacement_ratio(short_term)
                medium_ddr, _, _ = calculate_displacement_ratio(medium_term)
                long_ddr, _, _ = calculate_displacement_ratio(long_term)
                
                # 计算平均DDR
                avg_ddr = (short_ddr + medium_ddr + long_ddr) / 3
                
                # 组织单只股票结果
                stock_result = {
                    'symbol': symbol,
                    'short_term_ddr': float(short_ddr),
                    'medium_term_ddr': float(medium_ddr),
                    'long_term_ddr': float(long_ddr),
                    'avg_ddr': float(avg_ddr),
                    'data_points': len(close)
                }
                results.append(stock_result)
            except Exception as e:
                print(f'获取股票{symbol}位移路程比分析失败:', str(e))
                continue
        
        # 组织结果
        result = {
            'symbols': symbols,
            'window': window,
            'results': results
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取多只股票位移路程比比较失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取多只股票位移路程比比较失败: {str(e)}'}), 500
