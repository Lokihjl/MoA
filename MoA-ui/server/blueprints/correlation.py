# 相关性分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSymbol import code_to_symbol
from abupy.SimilarBu.ABuCorrcoef import corr_matrix, corr_xy, ECoreCorrType
from abupy.SimilarBu.ABuSimilar import find_similar_with_folds


# 获取两只股票的相关性分析
@moA_bp.route('/correlation/pair', methods=['GET'])
def get_pair_correlation():
    try:
        symbol = request.args.get('symbol')
        benchmark_symbol = request.args.get('benchmark_symbol')
        corr_type = request.args.get('corr_type', 'pears')  # pears, sperm, sign
        period = request.args.get('period', '1d')
        n_folds = int(request.args.get('n_folds', 2))
        
        if not symbol or not benchmark_symbol:
            return jsonify({'error': '两只股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        benchmark_symbol_obj = code_to_symbol(benchmark_symbol)
        
        # 获取两只股票数据
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
        benchmark_kl_df = ABuSymbolPd.make_kl_df(benchmark_symbol_obj, n_folds=n_folds)
        
        if kl_df is None or kl_df.empty or benchmark_kl_df is None or benchmark_kl_df.empty:
            return jsonify({'error': '获取股票数据失败'}), 404
        
        # 对齐数据日期
        merged_df = kl_df[['close']].join(benchmark_kl_df[['close']], lsuffix='_1', rsuffix='_2', how='inner')
        if merged_df.empty:
            return jsonify({'error': '两只股票数据日期不匹配'}), 400
        
        # 选择相关系数类型
        if corr_type == 'sperm':
            ctc_method = ECoreCorrType.E_CORE_TYPE_SPERM
        elif corr_type == 'sign':
            ctc_method = ECoreCorrType.E_CORE_TYPE_SIGN
        else:
            ctc_method = ECoreCorrType.E_CORE_TYPE_PEARS
        
        # 计算相关系数
        correlation = corr_xy(merged_df['close_1'], merged_df['close_2'], ctc_method)
        
        # 计算不同时间窗口的滚动相关系数
        rolling_windows = [20, 60, 120]
        rolling_corrs = {}
        for window in rolling_windows:
            if len(merged_df) >= window:
                rolling_corr = merged_df['close_1'].rolling(window).corr(merged_df['close_2'])
                rolling_corrs[f'window_{window}'] = float(rolling_corr.mean())
        
        # 组织结果
        result = {
            'symbol': symbol,
            'benchmark_symbol': benchmark_symbol,
            'period': period,
            'corr_type': corr_type,
            'correlation': float(correlation),
            'rolling_correlations': rolling_corrs,
            'data_points': len(merged_df)
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取两只股票相关性分析失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取两只股票相关性分析失败: {str(e)}'}), 500


# 获取多只股票的相关性矩阵
@moA_bp.route('/correlation/matrix', methods=['POST'])
def get_multi_correlation():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        corr_type = data.get('corr_type', 'pears')  # pears, sperm, sign
        period = data.get('period', '1d')
        n_folds = int(data.get('n_folds', 2))
        
        if not symbols or not isinstance(symbols, list) or len(symbols) < 2:
            return jsonify({'error': '股票代码列表不能为空且至少需要两只股票'}), 400
        
        # 获取所有股票数据
        kl_dfs = {}
        for symbol in symbols:
            try:
                symbol_obj = code_to_symbol(symbol)
                kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
                if kl_df is not None and not kl_df.empty:
                    kl_dfs[symbol] = kl_df[['close']].rename(columns={'close': symbol})
            except Exception as e:
                print(f'获取股票{symbol}数据失败:', str(e))
                continue
        
        if len(kl_dfs) < 2:
            return jsonify({'error': '有效股票数据不足两只'}), 404
        
        # 合并所有股票数据
        from functools import reduce
        merged_df = reduce(lambda x, y: x.join(y, how='inner'), kl_dfs.values())
        if merged_df.empty:
            return jsonify({'error': '股票数据日期不匹配'}), 400
        
        # 选择相关系数类型
        if corr_type == 'sperm':
            ctc_method = ECoreCorrType.E_CORE_TYPE_SPERM
        elif corr_type == 'sign':
            ctc_method = ECoreCorrType.E_CORE_TYPE_SIGN
        else:
            ctc_method = ECoreCorrType.E_CORE_TYPE_PEARS
        
        # 计算相关系数矩阵
        corr_mat = corr_matrix(merged_df, ctc_method)
        
        # 转换为字典格式
        corr_dict = {
            symbol: {
                benchmark: float(corr_mat.loc[symbol, benchmark]) 
                for benchmark in corr_mat.columns 
                if benchmark in symbols
            } 
            for symbol in corr_mat.index 
            if symbol in symbols
        }
        
        # 组织结果
        result = {
            'symbols': symbols,
            'period': period,
            'corr_type': corr_type,
            'correlation_matrix': corr_dict,
            'data_points': len(merged_df)
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取多只股票相关性矩阵失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取多只股票相关性矩阵失败: {str(e)}'}), 500


# 查找相似股票
@moA_bp.route('/correlation/similar', methods=['GET'])
def get_similar_stocks():
    try:
        symbol = request.args.get('symbol')
        top_n = int(request.args.get('top_n', 5))
        n_folds = int(request.args.get('n_folds', 2))
        
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        
        # 查找相似股票
        similar_stocks = find_similar_with_folds(symbol_obj, n_folds=n_folds)
        
        # 提取前N个相似股票
        top_similar = []
        for i, similar_info in enumerate(similar_stocks[:top_n]):
            top_similar.append({
                'rank': i + 1,
                'symbol': similar_info[0],
                'correlation': float(similar_info[1]),
                'name': similar_info[2] if len(similar_info) > 2 else ''
            })
        
        # 组织结果
        result = {
            'symbol': symbol,
            'n_folds': n_folds,
            'top_n': top_n,
            'similar_stocks': top_similar
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('查找相似股票失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'查找相似股票失败: {str(e)}'}), 500


# 获取单只股票与多个基准股票的相关性
@moA_bp.route('/correlation/multi-benchmark', methods=['POST'])
def get_multi_benchmark_correlation():
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        benchmark_symbols = data.get('benchmark_symbols', [])
        corr_type = data.get('corr_type', 'pears')
        n_folds = int(data.get('n_folds', 2))
        
        if not symbol or not benchmark_symbols or not isinstance(benchmark_symbols, list):
            return jsonify({'error': '股票代码和基准股票列表不能为空'}), 400
        
        # 获取目标股票数据
        symbol_obj = code_to_symbol(symbol)
        target_kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=n_folds)
        
        if target_kl_df is None or target_kl_df.empty:
            return jsonify({'error': '获取目标股票数据失败'}), 404
        
        # 选择相关系数类型
        if corr_type == 'sperm':
            ctc_method = ECoreCorrType.E_CORE_TYPE_SPERM
        elif corr_type == 'sign':
            ctc_method = ECoreCorrType.E_CORE_TYPE_SIGN
        else:
            ctc_method = ECoreCorrType.E_CORE_TYPE_PEARS
        
        correlations = []
        for benchmark_symbol in benchmark_symbols:
            try:
                benchmark_obj = code_to_symbol(benchmark_symbol)
                benchmark_kl_df = ABuSymbolPd.make_kl_df(benchmark_obj, n_folds=n_folds)
                
                if benchmark_kl_df is not None and not benchmark_kl_df.empty:
                    # 对齐数据日期
                    merged_df = target_kl_df[['close']].join(
                        benchmark_kl_df[['close']], 
                        lsuffix='_target', 
                        rsuffix='_benchmark', 
                        how='inner'
                    )
                    
                    if not merged_df.empty:
                        # 计算相关系数
                        correlation = corr_xy(
                            merged_df['close_target'], 
                            merged_df['close_benchmark'], 
                            ctc_method
                        )
                        
                        correlations.append({
                            'benchmark_symbol': benchmark_symbol,
                            'correlation': float(correlation),
                            'data_points': len(merged_df)
                        })
            except Exception as e:
                print(f'计算与基准股票{benchmark_symbol}相关性失败:', str(e))
                continue
        
        # 组织结果
        result = {
            'symbol': symbol,
            'corr_type': corr_type,
            'n_folds': n_folds,
            'correlations': correlations
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取单只股票与多个基准股票的相关性失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取单只股票与多个基准股票的相关性失败: {str(e)}'}), 500
