# 价格通道分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSymbol import code_to_symbol
from abupy.TLineBu.ABuTLine import AbuTLine
from abupy.TLineBu.ABuTLExecute import regress_trend_channel, support_resistance_pos, select_k_support_resistance


# 获取股票价格通道分析
@moA_bp.route('/price-channel/single', methods=['GET'])
def get_single_price_channel():
    try:
        symbol = request.args.get('symbol')
        channel_type = request.args.get('channel_type', 'regress')  # regress, skeleton, support
        period = request.args.get('period', '1d')
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
        close = kl_df['close'].values
        dates = kl_df.index.values.astype(float)
        
        result = {
            'symbol': symbol,
            'channel_type': channel_type,
            'period': period,
            'dates': dates.tolist(),
            'close': close.tolist()
        }
        
        if channel_type == 'regress':
            # 拟合通道
            lower, middle, upper = regress_trend_channel(close)
            result['channel'] = {
                'lower': lower.tolist(),
                'middle': middle.tolist(),
                'upper': upper.tolist()
            }
        elif channel_type == 'skeleton':
            # 骨架通道
            line = AbuTLine(close)
            line.show_skeleton_channel(show=False)
            # 提取骨架通道数据
            result['channel'] = {
                'lower': line.lower.tolist() if hasattr(line, 'lower') else [],
                'middle': line.middle.tolist() if hasattr(line, 'middle') else [],
                'upper': line.upper.tolist() if hasattr(line, 'upper') else []
            }
        elif channel_type == 'support':
            # 支撑阻力通道
            # 寻找支撑阻力位
            support_pos, resistance_pos = support_resistance_pos(close)
            # 对支撑阻力位进行聚类
            k_support, k_resistance = select_k_support_resistance(close, support_pos, resistance_pos)
            
            # 提取支撑阻力趋势线数据
            # 这里简化处理，直接返回支撑阻力位坐标
            result['support_pos'] = support_pos.tolist()
            result['resistance_pos'] = resistance_pos.tolist()
            result['k_support'] = k_support.tolist()
            result['k_resistance'] = k_resistance.tolist()
        
        return jsonify(result), 200
    except Exception as e:
        print('获取股票价格通道分析失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取股票价格通道分析失败: {str(e)}'}), 500


# 获取多只股票价格通道比较
@moA_bp.route('/price-channel/compare', methods=['POST'])
def get_multi_price_channel():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        channel_type = data.get('channel_type', 'regress')
        n_folds = int(data.get('n_folds', 2))
        
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
                
                # 计算通道宽度
                width = 0
                if channel_type == 'regress':
                    # 拟合通道
                    lower, middle, upper = regress_trend_channel(close)
                    # 计算通道平均宽度
                    avg_width = (upper - lower).mean()
                    # 计算通道相对宽度（相对于价格）
                    width = (avg_width / middle.mean()) * 100
                elif channel_type == 'skeleton':
                    # 骨架通道
                    line = AbuTLine(close)
                    line.show_skeleton_channel(show=False)
                    if hasattr(line, 'lower') and hasattr(line, 'upper'):
                        avg_width = (line.upper - line.lower).mean()
                        mid_price = (line.upper + line.lower).mean() / 2
                        width = (avg_width / mid_price) * 100
                
                # 组织单只股票结果
                stock_result = {
                    'symbol': symbol,
                    'channel_width': float(width),
                    'data_points': len(close)
                }
                results.append(stock_result)
            except Exception as e:
                print(f'获取股票{symbol}价格通道分析失败:', str(e))
                continue
        
        # 组织结果
        result = {
            'symbols': symbols,
            'channel_type': channel_type,
            'results': results
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取多只股票价格通道比较失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取多只股票价格通道比较失败: {str(e)}'}), 500
