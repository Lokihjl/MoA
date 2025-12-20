# 黄金分割分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.TLineBu.ABuTLGolden import calc_golden
from abupy.MarketBu import ABuSymbolPd
from abupy.MarketBu.ABuSymbol import code_to_symbol


# 获取单个股票的黄金分割分析
@moA_bp.route('/golden-section/single', methods=['GET'])
def get_single_golden_section():
    try:
        symbol = request.args.get('symbol')
        resample = request.args.get('resample', 5, type=int)
        period = request.args.get('period', '1d')  # 新增：支持不同K线周期
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        symbol_obj = code_to_symbol(symbol)
        
        # 获取股票数据，支持不同周期
        kl_df = ABuSymbolPd.make_kl_df(symbol_obj, n_folds=2)
        if kl_df is None or kl_df.empty:
            return jsonify({'error': f'获取股票{symbol}数据失败'}), 404
        
        # 计算黄金分割及比例分割
        golden_result = calc_golden(kl_df, show=False)
        
        # 将namedtuple转换为字典，并按照前端需要的格式组织数据
        # 完整展示核心黄金比例和扩展黄金比例
        result = {
            'symbol': symbol,
            'resample': resample,
            'period': period,
            # 核心黄金比例
            'g382': float(golden_result.g382),
            'g500': float(golden_result.g500),
            'g618': float(golden_result.g618),
            'gex382': float(golden_result.gex382),
            'gex500': float(golden_result.gex500),
            'gex618': float(golden_result.gex618),
            # 扩展黄金比例带
            'above618': float(golden_result.above618),
            'below618': float(golden_result.below618),
            'above382': float(golden_result.above382),
            'below382': float(golden_result.below382),
            # 百分比关键点
            'above950': float(golden_result.above950),
            'above900': float(golden_result.above900),
            'above800': float(golden_result.above800),
            'above700': float(golden_result.above700),
            'below300': float(golden_result.below300),
            'below250': float(golden_result.below250),
            'below200': float(golden_result.below200),
            # 前端可视化需要的阻力位和支撑位
            'resistance_0_618': float(golden_result.g618),
            'resistance_1_0': float(golden_result.above382),
            'resistance_1_618': float(golden_result.above618),
            'support_0_618': float(golden_result.gex618),
            'support_0_0': float(golden_result.gex382),
            'support_neg_0_618': float(golden_result.below382)
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取单个股票黄金分割分析失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取单个股票黄金分割分析失败: {str(e)}'}), 500


# 获取两只股票的黄金分割分析对比
@moA_bp.route('/golden-section/pair', methods=['GET'])
def get_pair_golden_section():
    try:
        symbol = request.args.get('symbol')
        benchmark_symbol = request.args.get('benchmark_symbol')
        resample = request.args.get('resample', 5, type=int)
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
        
        # 计算两只股票的黄金分割及比例分割
        golden_result = calc_golden(kl_df, show=False)
        benchmark_golden_result = calc_golden(benchmark_kl_df, show=False)
        
        # 将namedtuple转换为字典，并按照前端需要的格式组织数据
        result = {
            'symbol': symbol,
            'benchmark_symbol': benchmark_symbol,
            'resample': resample,
            'period': period,
            # 第一只股票的完整黄金分割信息
            'symbol_golden': {
                'g382': float(golden_result.g382),
                'g500': float(golden_result.g500),
                'g618': float(golden_result.g618),
                'gex382': float(golden_result.gex382),
                'gex500': float(golden_result.gex500),
                'gex618': float(golden_result.gex618),
                'above618': float(golden_result.above618),
                'below618': float(golden_result.below618),
                'above382': float(golden_result.above382),
                'below382': float(golden_result.below382),
                'above950': float(golden_result.above950),
                'above900': float(golden_result.above900),
                'above800': float(golden_result.above800),
                'above700': float(golden_result.above700),
                'below300': float(golden_result.below300),
                'below250': float(golden_result.below250),
                'below200': float(golden_result.below200)
            },
            # 基准股票的完整黄金分割信息
            'benchmark_golden': {
                'g382': float(benchmark_golden_result.g382),
                'g500': float(benchmark_golden_result.g500),
                'g618': float(benchmark_golden_result.g618),
                'gex382': float(benchmark_golden_result.gex382),
                'gex500': float(benchmark_golden_result.gex500),
                'gex618': float(benchmark_golden_result.gex618),
                'above618': float(benchmark_golden_result.above618),
                'below618': float(benchmark_golden_result.below618),
                'above382': float(benchmark_golden_result.above382),
                'below382': float(benchmark_golden_result.below382),
                'above950': float(benchmark_golden_result.above950),
                'above900': float(benchmark_golden_result.above900),
                'above800': float(benchmark_golden_result.above800),
                'above700': float(benchmark_golden_result.above700),
                'below300': float(benchmark_golden_result.below300),
                'below250': float(benchmark_golden_result.below250),
                'below200': float(benchmark_golden_result.below200)
            },
            # 简化的阻力位和支撑位（保持向前兼容）
            'resistance_0_618': float(golden_result.g618),
            'resistance_1_0': float(golden_result.above382),
            'resistance_1_618': float(golden_result.above618),
            'support_0_618': float(golden_result.gex618),
            'support_0_0': float(golden_result.gex382),
            'support_neg_0_618': float(golden_result.below382),
            'benchmark_resistance_0_618': float(benchmark_golden_result.g618),
            'benchmark_resistance_1_0': float(benchmark_golden_result.above382),
            'benchmark_resistance_1_618': float(benchmark_golden_result.above618),
            'benchmark_support_0_618': float(benchmark_golden_result.gex618),
            'benchmark_support_0_0': float(benchmark_golden_result.gex382),
            'benchmark_support_neg_0_618': float(benchmark_golden_result.below382)
        }
        
        return jsonify(result), 200
    except Exception as e:
        print('获取两只股票黄金分割分析对比失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取两只股票黄金分割分析对比失败: {str(e)}'}), 500


# 获取多只股票的黄金分割分析对比
@moA_bp.route('/golden-section/multi', methods=['POST'])
def get_multi_golden_section():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        resample = data.get('resample', 5)
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
                
                # 计算黄金分割及比例分割
                golden_result = calc_golden(kl_df, show=False)
                
                # 将namedtuple转换为字典，并按照前端需要的格式组织数据
                # 每只股票都包含完整的黄金分割信息
                result = {
                    'symbol': symbol,
                    'resample': resample,
                    'period': period,
                    # 完整黄金分割信息
                    'g382': float(golden_result.g382),
                    'g500': float(golden_result.g500),
                    'g618': float(golden_result.g618),
                    'gex382': float(golden_result.gex382),
                    'gex500': float(golden_result.gex500),
                    'gex618': float(golden_result.gex618),
                    'above618': float(golden_result.above618),
                    'below618': float(golden_result.below618),
                    'above382': float(golden_result.above382),
                    'below382': float(golden_result.below382),
                    'above950': float(golden_result.above950),
                    'above900': float(golden_result.above900),
                    'above800': float(golden_result.above800),
                    'above700': float(golden_result.above700),
                    'below300': float(golden_result.below300),
                    'below250': float(golden_result.below250),
                    'below200': float(golden_result.below200),
                    # 简化的阻力位和支撑位（保持向前兼容）
                    'resistance_0_618': float(golden_result.g618),
                    'resistance_1_0': float(golden_result.above382),
                    'resistance_1_618': float(golden_result.above618),
                    'support_0_618': float(golden_result.gex618),
                    'support_0_0': float(golden_result.gex382),
                    'support_neg_0_618': float(golden_result.below382)
                }
                results.append(result)
            except Exception as e:
                print(f'获取股票{symbol}黄金分割分析失败:', str(e))
                continue
        
        return jsonify({'results': results, 'resample': resample, 'period': period}), 200
    except Exception as e:
        print('获取多只股票黄金分割分析对比失败:', str(e))
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取多只股票黄金分割分析对比失败: {str(e)}'}), 500
