# 趋势敏感速度对比相关蓝图
from flask import request, jsonify
from . import moA_bp
import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('../../../abupy'))

from abupy.TLineBu.ABuTLExecute import calc_kl_speed, calc_pair_speed
from abupy.MarketBu import ABuSymbolPd
from abupy.TradeBu import AbuBenchmark
from abupy.CoreBu.ABuEnv import EMarketDataSplitMode


# 获取单个股票的趋势敏感速度
@moA_bp.route('/trend-speed/single', methods=['GET'])
def get_single_trend_speed():
    try:
        symbol = request.args.get('symbol')
        if not symbol:
            return jsonify({'error': '股票代码不能为空'}), 400
        speed_key = request.args.get('speed_key', 'close')
        resample = int(request.args.get('resample', 5))
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        from abupy.MarketBu.ABuSymbol import code_to_symbol
        
        kl_df = None
        
        # 处理股票代码，确保code_to_symbol函数能够正确识别
        processed_symbol = symbol
        
        # 打印原始股票代码信息
        print(f"原始股票代码: {symbol}, 长度: {len(symbol)}, 前缀: {symbol[:2] if len(symbol) >= 2 else ''}")
        
        try:
            # 尝试1: 直接使用原始代码
            print(f"尝试1: 直接使用原始代码 {symbol}")
            symbol_obj = code_to_symbol(symbol)
            kl_df = ABuSymbolPd.make_kl_df(symbol_obj)
            
            if kl_df is not None and not kl_df.empty:
                print(f"使用ABU框架成功获取{symbol}数据，形状：{kl_df.shape}")
            else:
                # 尝试2: 如果原始代码失败，尝试去掉前缀
                print(f"尝试2: 去掉前缀处理")
                if len(processed_symbol) == 8 and (processed_symbol.startswith('sh') or processed_symbol.startswith('sz')):
                    # 对于带有sh或sz前缀的代码，尝试去掉前缀
                    core_symbol = processed_symbol[2:]
                    print(f"去掉前缀后: {core_symbol}")
                    symbol_obj = code_to_symbol(core_symbol)
                    kl_df = ABuSymbolPd.make_kl_df(symbol_obj)
                    
                    if kl_df is not None and not kl_df.empty:
                        print(f"使用ABU框架成功获取{core_symbol}数据，形状：{kl_df.shape}")
                    else:
                        # 尝试3: 如果去掉前缀失败，尝试添加不同的前缀
                        print(f"尝试3: 添加不同前缀处理")
                        if processed_symbol.startswith('sh'):
                            # 尝试sz前缀
                            test_symbol = f"sz{core_symbol}"
                            print(f"尝试sz前缀: {test_symbol}")
                            symbol_obj = code_to_symbol(test_symbol)
                            kl_df = ABuSymbolPd.make_kl_df(symbol_obj)
                        elif processed_symbol.startswith('sz'):
                            # 尝试sh前缀
                            test_symbol = f"sh{core_symbol}"
                            print(f"尝试sh前缀: {test_symbol}")
                            symbol_obj = code_to_symbol(test_symbol)
                            kl_df = ABuSymbolPd.make_kl_df(symbol_obj)
        except Exception as e:
            print(f"使用ABU框架获取{symbol}数据失败: {e}")
            # 打印详细的错误信息，包括堆栈跟踪
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'获取股票{symbol}数据失败: {str(e)}'}), 404
        
        if kl_df is None or kl_df.empty:
            # 对于无法获取数据的股票，返回友好的错误信息
            error_msg = f'获取股票{symbol}数据失败。可能原因：\n'
            error_msg += '1. 该股票代码可能不存在\n'
            error_msg += '2. ABU框架的数据源可能无法提供该股票数据\n'
            error_msg += '3. 请尝试使用其他股票代码，如000001（平安银行）、600519（贵州茅台）等'
            return jsonify({'error': error_msg}), 404
        
        # 计算趋势敏感速度
        speed = calc_kl_speed(kl_df[speed_key], resample)
        
        return jsonify({
            'symbol': symbol,
            'speed_key': speed_key,
            'resample': resample,
            'speed': float(speed)
        }), 200
    except Exception as e:
        print('获取单个股票趋势敏感速度失败:', str(e))
        return jsonify({'error': f'获取单个股票趋势敏感速度失败: {str(e)}'}), 500


# 获取两只股票的趋势敏感速度对比
@moA_bp.route('/trend-speed/pair', methods=['GET'])
def get_pair_trend_speed():
    try:
        symbol = request.args.get('symbol')
        benchmark_symbol = request.args.get('benchmark_symbol')
        if not symbol or not benchmark_symbol:
            return jsonify({'error': '股票代码和基准股票代码不能为空'}), 400
        speed_key = request.args.get('speed_key', 'close')
        resample = int(request.args.get('resample', 5))
        
        # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
        from abupy.MarketBu.ABuSymbol import code_to_symbol
        from abupy.SimilarBu.ABuCorrcoef import corr_xy
        from abupy.SimilarBu.ABuCorrcoef import ECoreCorrType
        
        try:
            # 使用code_to_symbol函数将两只股票代码转换为ABU框架可识别的Symbol对象
            symbol_obj = code_to_symbol(symbol)
            benchmark_symbol_obj = code_to_symbol(benchmark_symbol)
            
            # 使用Symbol对象获取真实数据
            kl_df1 = ABuSymbolPd.make_kl_df(symbol_obj)
            kl_df2 = ABuSymbolPd.make_kl_df(benchmark_symbol_obj)
            
            if kl_df1 is None or kl_df1.empty or kl_df2 is None or kl_df2.empty:
                return jsonify({'error': '获取股票数据失败'}), 404
            
            print(f"使用ABU框架成功获取{symbol}数据，形状：{kl_df1.shape}")
            print(f"使用ABU框架成功获取{benchmark_symbol}数据，形状：{kl_df2.shape}")
            
            # 计算两只股票的趋势敏感速度
            kl_speed = calc_kl_speed(kl_df1[speed_key], resample)
            benchmark_kl_speed = calc_kl_speed(kl_df2[speed_key], resample)
            
            # 使用ABU框架的corr_xy函数计算真实相关系数
            corr = corr_xy(kl_df1.close, kl_df2.close, ECoreCorrType.E_CORE_TYPE_SPERM)
            
            print(f"使用ABU框架真实数据，kl_speed={kl_speed}, benchmark_kl_speed={benchmark_kl_speed}, corr={corr}")
        except Exception as e:
            print(f"使用ABU框架获取数据失败: {e}")
            return jsonify({'error': f'获取股票数据失败: {str(e)}'}), 404
        
        return jsonify({
            'symbol': symbol,
            'benchmark_symbol': benchmark_symbol,
            'speed_key': speed_key,
            'resample': resample,
            'kl_speed': float(kl_speed),
            'benchmark_kl_speed': float(benchmark_kl_speed),
            'corr': float(corr) if corr is not None else None
        }), 200
    except Exception as e:
        print('获取股票趋势敏感速度对比失败:', str(e))
        return jsonify({'error': f'获取股票趋势敏感速度对比失败: {str(e)}'}), 500


# 获取多只股票的趋势敏感速度对比
@moA_bp.route('/trend-speed/multi', methods=['POST'])
def get_multi_trend_speed():
    try:
        data = request.get_json()
        symbols = data.get('symbols', [])
        speed_key = data.get('speed_key', 'close')
        resample = int(data.get('resample', 5))
        
        if not symbols:
            return jsonify({'error': '股票列表不能为空'}), 400
        
        results = []
        for symbol in symbols:
            try:
                # 使用ABU框架的code_to_symbol函数正确处理股票代码格式
                from abupy.MarketBu.ABuSymbol import code_to_symbol
                
                # 使用code_to_symbol函数将股票代码转换为ABU框架可识别的Symbol对象
                symbol_obj = code_to_symbol(symbol)
                # 使用Symbol对象获取真实数据
                kl_df = ABuSymbolPd.make_kl_df(symbol_obj)
                
                if kl_df is not None and not kl_df.empty:
                    # 计算趋势敏感速度
                    speed = calc_kl_speed(kl_df[speed_key], resample)
                    results.append({
                        'symbol': symbol,
                        'speed': float(speed)
                    })
                    print(f"使用ABU框架真实数据，股票{symbol}的趋势敏感速度为{speed}")
            except Exception as e:
                print(f'计算股票{symbol}趋势敏感速度失败:', str(e))
                continue
        
        return jsonify({
            'speed_key': speed_key,
            'resample': resample,
            'results': results
        }), 200
    except Exception as e:
        print('获取多只股票趋势敏感速度对比失败:', str(e))
        return jsonify({'error': f'获取多只股票趋势敏感速度对比失败: {str(e)}'}), 500
