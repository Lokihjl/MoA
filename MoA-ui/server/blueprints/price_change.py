# 涨跌幅分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSymbol import code_to_symbol


# 获取单个股票的涨跌幅分析
@moA_bp.route('/price-change/single', methods=['GET'])
def get_single_price_change():
    try:
        symbol = request.args.get('symbol')
        period = request.args.get('period', '1d')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        
        # 获取股票数据
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=2)
        if kl_df is None or kl_df.empty:
            return jsonify({'error': f'获取股票{symbol}数据失败'}), 404
        
        # 计算涨跌幅
        kl_df['p_change'] = kl_df['close'].pct_change() * 100
        kl_df['p_change_cum'] = kl_df['p_change'].cumsum()
        
        # 统计信息
        stats = {
            'total_days': len(kl_df),
            'avg_change': float(kl_df['p_change'].mean()),
            'max_change': float(kl_df['p_change'].max()),
            'min_change': float(kl_df['p_change'].min()),
            'positive_days': int((kl_df['p_change'] > 0).sum()),
            'negative_days': int((kl_df['p_change'] < 0).sum()),
            'zero_days': int((kl_df['p_change'] == 0).sum()),
            'total_return': float(kl_df['p_change_cum'].iloc[-1])
        }
        
        # 最近N天涨跌幅
        recent_days = {
            '5_days': float(kl_df['p_change'].tail(5).sum()),
            '10_days': float(kl_df['p_change'].tail(10).sum()),
            '30_days': float(kl_df['p_change'].tail(30).sum()),
            '60_days': float(kl_df['p_change'].tail(60).sum())
        }
        
        # 组织结果
        result = {
            'symbol': symbol,
            'period': period,
            'stats': stats,
            'recent_days': recent_days,
            'latest_price': float(kl_df['close'].iloc[-1]),
            'start_price': float(kl_df['close'].iloc[0])
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取单个股票涨跌幅分析失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取单个股票涨跌幅分析失败: {str(e)}'}), 500


# 获取两只股票的涨跌幅对比
@moA_bp.route('/price-change/pair', methods=['GET'])
def get_pair_price_change():
    try:
        symbol = request.args.get('symbol')
        benchmark_symbol = request.args.get('benchmark_symbol')
        period = request.args.get('period', '1d')
        
        if not symbol or not benchmark_symbol:
            return jsonify({'error': '两只股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        benchmark_symbol_obj = code_to_symbol(benchmark_symbol)
        
        # 获取两只股票数据
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=2)
        benchmark_kl_df = ABuSymbolPd.make_kl_df(benchmark_symbol_obj, n_folds=2)
        
        if kl_df is None or kl_df.empty or benchmark_kl_df is None or benchmark_kl_df.empty:
            return jsonify({'error': '获取股票数据失败'}), 404
        
        # 计算涨跌幅
        kl_df['p_change'] = kl_df['close'].pct_change() * 100
        kl_df['p_change_cum'] = kl_df['p_change'].cumsum()
        
        benchmark_kl_df['p_change'] = benchmark_kl_df['close'].pct_change() * 100
        benchmark_kl_df['p_change_cum'] = benchmark_kl_df['p_change'].cumsum()
        
        # 统计信息
        def calc_stats(df):
            return {
                'total_days': len(df),
                'avg_change': float(df['p_change'].mean()),
                'max_change': float(df['p_change'].max()),
                'min_change': float(df['p_change'].min()),
                'positive_days': int((df['p_change'] > 0).sum()),
                'negative_days': int((df['p_change'] < 0).sum()),
                'zero_days': int((df['p_change'] == 0).sum()),
                'total_return': float(df['p_change_cum'].iloc[-1])
            }
        
        def calc_recent_days(df):
            return {
                '5_days': float(df['p_change'].tail(5).sum()),
                '10_days': float(df['p_change'].tail(10).sum()),
                '30_days': float(df['p_change'].tail(30).sum()),
                '60_days': float(df['p_change'].tail(60).sum())
            }
        
        # 组织结果
        result = {
            'symbol': symbol,
            'benchmark_symbol': benchmark_symbol,
            'period': period,
            'symbol_change': {
                'stats': calc_stats(kl_df),
                'recent_days': calc_recent_days(kl_df),
                'latest_price': float(kl_df['close'].iloc[-1]),
                'start_price': float(kl_df['close'].iloc[0])
            },
            'benchmark_change': {
                'stats': calc_stats(benchmark_kl_df),
                'recent_days': calc_recent_days(benchmark_kl_df),
                'latest_price': float(benchmark_kl_df['close'].iloc[-1]),
                'start_price': float(benchmark_kl_df['close'].iloc[0])
            }
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取两只股票涨跌幅对比失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取两只股票涨跌幅对比失败: {str(e)}'}), 500


# 获取多只股票的涨跌幅对比
@moA_bp.route('/price-change/multi', methods=['POST'])
def get_multi_price_change():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        period = data.get('period', '1d')
        
        if not symbols or not isinstance(symbols, list):
            return jsonify({'error': '股票代码列表不能为空'}), 400
        
        results = []
        for symbol in symbols:
            try:
                # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
                symbol_obj = code_to_symbol(symbol)
                
                # 获取股票数据
                kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=2)
                if kl_df is None or kl_df.empty:
                    continue
                
                # 计算涨跌幅
                kl_df['p_change'] = kl_df['close'].pct_change() * 100
                kl_df['p_change_cum'] = kl_df['p_change'].cumsum()
                
                # 最近N天涨跌幅
                recent_days = {
                    '5_days': float(kl_df['p_change'].tail(5).sum()),
                    '10_days': float(kl_df['p_change'].tail(10).sum()),
                    '30_days': float(kl_df['p_change'].tail(30).sum()),
                    '60_days': float(kl_df['p_change'].tail(60).sum())
                }
                
                # 组织结果
                result = {
                    'symbol': symbol,
                    'period': period,
                    'total_return': float(kl_df['p_change_cum'].iloc[-1]),
                    'avg_change': float(kl_df['p_change'].mean()),
                    'max_change': float(kl_df['p_change'].max()),
                    'min_change': float(kl_df['p_change'].min()),
                    'latest_price': float(kl_df['close'].iloc[-1]),
                    'recent_days': recent_days
                }
                results.append(result)
            except Exception as e:
                print(f'获取股票{symbol}涨跌幅分析失败:', str(e))
                continue
        
        return jsonify({'results': results, 'period': period}), 200
    except Exception as e:
        print('获取多只股票涨跌幅对比失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取多只股票涨跌幅对比失败: {str(e)}'}), 500
