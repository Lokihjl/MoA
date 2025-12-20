# 跳空缺口分析相关蓝图
from flask import request, jsonify
from . import moA_bp
import pandas as pd
import numpy as np

# =================== 跳空缺口分析相关接口 ===================

# 获取股票跳空缺口数据
@moA_bp.route('/stock/<symbol>/gaps', methods=['GET'])
def get_stock_gaps(symbol):
    """
    获取指定股票的跳空缺口数据
    :param symbol: 股票代码
    :return: 跳空缺口数据列表
    """
    try:
        import requests
        import datetime
        
        # 验证symbol参数
        if not symbol or symbol.strip() == '':
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 获取查询参数
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        gap_threshold = float(request.args.get('threshold', 0.005))  # 缺口阈值，默认为0.5%
        
        print(f'获取股票跳空缺口数据: symbol={symbol}, start_date={start_date}, end_date={end_date}, threshold={gap_threshold}')
        
        # 1. 尝试使用ABU量化框架获取真实数据
        try:
            from abupy import ABuSymbolPd
            from abupy.CoreBu.ABuEnv import EMarketSourceType
            from abupy.CoreBu import ABuEnv
            
            # 设置数据源为腾讯财经
            ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
            
            # 使用ABU框架获取股票历史K线数据
            kl_df = ABuSymbolPd.make_kl_df(symbol)
            
            if kl_df is not None and not kl_df.empty:
                # 根据start_date和end_date过滤数据
                if start_date is not None:
                    kl_df = kl_df[kl_df.index >= pd.to_datetime(start_date)]
                if end_date is not None:
                    kl_df = kl_df[kl_df.index <= pd.to_datetime(end_date)]
                
                if not kl_df.empty:
                    # 计算跳空缺口
                    gaps = calculate_gaps(kl_df, gap_threshold)
                    return jsonify({'symbol': symbol, 'start_date': str(kl_df.index.min().date()), 'end_date': str(kl_df.index.max().date()), 'gaps': gaps}), 200
        except Exception as e:
            print('使用ABU框架获取数据失败:', str(e))
        
        # 2. 如果ABU框架失败，尝试使用新浪财经API获取真实历史数据
        try:
            print('尝试使用新浪财经API获取真实历史数据')
            
            # 新浪财经API获取股票历史数据
            scale = 240  # 日K线
            datalen = 252  # 获取252天的数据
            
            sina_symbol = symbol
            sina_url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_symbol}&scale={scale}&ma=no&datalen={datalen}'
            
            response = requests.get(sina_url, timeout=10)
            response.raise_for_status()
            
            # 解析新浪财经返回的JSON数据
            sina_data = response.json()
            
            if sina_data and len(sina_data) > 0:
                # 转换为DataFrame
                kl_df = pd.DataFrame(sina_data)
                kl_df['date'] = pd.to_datetime(kl_df['day'])
                kl_df.set_index('date', inplace=True)
                
                # 转换数据类型
                kl_df[['open', 'high', 'low', 'close', 'volume']] = kl_df[['open', 'high', 'low', 'close', 'volume']].astype(float)
                
                # 根据start_date和end_date过滤数据
                if start_date is not None:
                    kl_df = kl_df[kl_df.index >= pd.to_datetime(start_date)]
                if end_date is not None:
                    kl_df = kl_df[kl_df.index <= pd.to_datetime(end_date)]
                
                if not kl_df.empty:
                    # 计算跳空缺口
                    gaps = calculate_gaps(kl_df, gap_threshold)
                    return jsonify({'symbol': symbol, 'start_date': str(kl_df.index.min().date()), 'end_date': str(kl_df.index.max().date()), 'gaps': gaps}), 200
        except Exception as e:
            print('使用新浪财经API获取数据失败:', str(e))
        
        # 3. 如果所有真实数据获取方法都失败，返回空数据
        print(f'所有获取真实历史数据的方法都失败了，返回空数据')
        return jsonify({'symbol': symbol, 'start_date': start_date, 'end_date': end_date, 'gaps': []}), 200
    except Exception as e:
        print(f'获取股票跳空缺口数据失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取股票跳空缺口数据失败: {str(e)}'}), 500


def calculate_gaps(kl_df, threshold=0.005):
    """
    使用ABU框架的跳空缺口计算逻辑
    :param kl_df: K线数据DataFrame，包含open, high, low, close列
    :param threshold: 缺口阈值，默认为0.5%
    :return: 跳空缺口列表
    """
    gaps = []
    
    try:
        # 尝试使用ABU框架的跳空缺口计算功能
        from abupy import AbuGapFinder
        
        # 使用ABU框架的AbuGapFinder类计算跳空缺口
        gap_finder = AbuGapFinder(kl_df)
        gap_result = gap_finder.find_gap()
        
        # 处理ABU框架返回的缺口结果
        if gap_result is not None and hasattr(gap_result, 'gap_list'):
            for gap_item in gap_result.gap_list:
                # 过滤掉小于阈值的缺口
                gap_percent = abs(gap_item.gap) / gap_item.prev_close * 100
                if gap_percent >= threshold * 100:
                    # 确定缺口类型
                    gap_type = 'up' if gap_item.gap > 0 else 'down'
                    
                    # 检查缺口是否被回补
                    is_filled = hasattr(gap_item, 'filled') and gap_item.filled
                    
                    gaps.append({
                        'date': str(gap_item.date.date()),
                        'type': gap_type,
                        'prev_date': str(gap_item.prev_date.date()),
                        'prev_close': float(gap_item.prev_close),
                        'curr_open': float(gap_item.curr_open),
                        'gap_size': float(abs(gap_item.gap)),
                        'gap_percent': float(gap_percent),
                        'is_filled': is_filled,
                        'fill_date': str(gap_item.fill_date.date()) if is_filled else None
                    })
            
            return gaps
    except Exception as e:
        print('使用ABU框架的跳空缺口计算功能失败:', str(e))
    
    # 如果ABU框架的跳空缺口计算功能不可用，使用自定义实现作为备选
    # 确保数据按日期排序
    kl_df = kl_df.sort_index()
    
    # 遍历每一行数据，识别跳空缺口
    for i in range(1, len(kl_df)):
        date = kl_df.index[i]
        prev_date = kl_df.index[i-1]
        
        # 获取当前行和前一行的数据
        curr_data = kl_df.iloc[i]
        prev_data = kl_df.iloc[i-1]
        
        # 计算缺口
        prev_close_val = prev_data['close']
        curr_open_val = curr_data['open']
        
        # 计算缺口百分比
        gap_percent = abs(curr_open_val - prev_close_val) / prev_close_val
        
        # 向上跳空缺口：当前开盘价 > 前一天收盘价，且缺口大于阈值
        if curr_open_val > prev_close_val and gap_percent > threshold:
            # 检查缺口是否被回补
            fill_date = None
            is_filled = False
            for j in range(i+1, len(kl_df)):
                if kl_df.iloc[j]['low'] <= prev_close_val and kl_df.iloc[j]['high'] >= curr_open_val:
                    is_filled = True
                    fill_date = kl_df.index[j]
                    break
            
            gaps.append({
                'date': str(date.date()),
                'type': 'up',  # 向上跳空
                'prev_date': str(prev_date.date()),
                'prev_close': float(prev_close_val),
                'curr_open': float(curr_open_val),
                'gap_size': float(curr_open_val - prev_close_val),
                'gap_percent': float(gap_percent * 100),
                'is_filled': is_filled,
                'fill_date': str(fill_date.date()) if is_filled else None
            })
        # 向下跳空缺口：当前开盘价 < 前一天收盘价，且缺口大于阈值
        elif curr_open_val < prev_close_val and gap_percent > threshold:
            # 检查缺口是否被回补
            fill_date = None
            is_filled = False
            for j in range(i+1, len(kl_df)):
                if kl_df.iloc[j]['high'] >= prev_close_val and kl_df.iloc[j]['low'] <= curr_open_val:
                    is_filled = True
                    fill_date = kl_df.index[j]
                    break
            
            gaps.append({
                'date': str(date.date()),
                'type': 'down',  # 向下跳空
                'prev_date': str(prev_date.date()),
                'prev_close': float(prev_close_val),
                'curr_open': float(curr_open_val),
                'gap_size': float(prev_close_val - curr_open_val),
                'gap_percent': float(gap_percent * 100),
                'is_filled': is_filled,
                'fill_date': str(fill_date.date()) if is_filled else None
            })
    
    return gaps


# 获取跳空缺口统计信息
@moA_bp.route('/stock/<symbol>/gaps/stats', methods=['GET'])
def get_gap_stats(symbol):
    """
    获取指定股票的跳空缺口统计信息
    :param symbol: 股票代码
    :return: 跳空缺口统计信息
    """
    try:
        # 验证symbol参数
        if not symbol or symbol.strip() == '':
            return jsonify({'error': '股票代码不能为空'}), 400
        
        # 获取查询参数
        start_date = request.args.get('start_date', None)
        end_date = request.args.get('end_date', None)
        gap_threshold = float(request.args.get('threshold', 0.005))  # 缺口阈值，默认为0.5%
        
        # 直接调用calculate_gaps函数获取缺口数据，而不是通过API调用
        # 1. 尝试使用ABU量化框架获取真实数据
        gaps = []
        kl_df = None
        
        # 尝试使用ABU框架获取数据
        try:
            from abupy import ABuSymbolPd
            from abupy.CoreBu.ABuEnv import EMarketSourceType
            from abupy.CoreBu import ABuEnv
            
            # 设置数据源为腾讯财经
            ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
            
            # 使用ABU框架获取股票历史K线数据
            kl_df = ABuSymbolPd.make_kl_df(symbol)
        except Exception as e:
            print('使用ABU框架获取数据失败:', str(e))
        
        # 如果ABU框架失败，尝试使用新浪财经API获取数据
        if kl_df is None or kl_df.empty:
            try:
                import requests
                
                # 新浪财经API获取股票历史数据
                scale = 240  # 日K线
                datalen = 252  # 获取252天的数据
                
                sina_symbol = symbol
                sina_url = f'http://money.finance.sina.com.cn/quotes_service/api/json_v2.php/CN_MarketData.getKLineData?symbol={sina_symbol}&scale={scale}&ma=no&datalen={datalen}'
                
                response = requests.get(sina_url, timeout=10)
                response.raise_for_status()
                
                # 解析新浪财经返回的JSON数据
                sina_data = response.json()
                
                if sina_data and len(sina_data) > 0:
                    # 转换为DataFrame
                    kl_df = pd.DataFrame(sina_data)
                    kl_df['date'] = pd.to_datetime(kl_df['day'])
                    kl_df.set_index('date', inplace=True)
                    
                    # 转换数据类型
                    kl_df[['open', 'high', 'low', 'close', 'volume']] = kl_df[['open', 'high', 'low', 'close', 'volume']].astype(float)
            except Exception as e:
                print('使用新浪财经API获取数据失败:', str(e))
        
        # 如果获取到了K线数据，计算跳空缺口
        if kl_df is not None and not kl_df.empty:
            # 根据start_date和end_date过滤数据
            if start_date is not None:
                kl_df = kl_df[kl_df.index >= pd.to_datetime(start_date)]
            if end_date is not None:
                kl_df = kl_df[kl_df.index <= pd.to_datetime(end_date)]
            
            if not kl_df.empty:
                # 计算跳空缺口
                gaps = calculate_gaps(kl_df, gap_threshold)
        
        # 计算统计信息
        stats = {
            'total_gaps': len(gaps),
            'up_gaps': len([g for g in gaps if g['type'] == 'up']),
            'down_gaps': len([g for g in gaps if g['type'] == 'down']),
            'filled_gaps': len([g for g in gaps if g['is_filled']]),
            'unfilled_gaps': len([g for g in gaps if not g['is_filled']]),
            'avg_gap_size': np.mean([g['gap_size'] for g in gaps]) if gaps else 0,
            'avg_gap_percent': np.mean([g['gap_percent'] for g in gaps]) if gaps else 0,
            'max_gap_size': np.max([g['gap_size'] for g in gaps]) if gaps else 0,
            'max_gap_percent': np.max([g['gap_percent'] for g in gaps]) if gaps else 0
        }
        
        return jsonify({'symbol': symbol, 'start_date': start_date, 'end_date': end_date, 'stats': stats}), 200
    except Exception as e:
        print(f'获取跳空缺口统计信息失败: {e}')
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取跳空缺口统计信息失败: {str(e)}'}), 500
