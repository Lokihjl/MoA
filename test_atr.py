# -*- encoding:utf-8 -*-
"""
测试ATR计算功能是否正常
"""

import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('./abupy'))

from abupy.IndicatorBu.ABuNDAtr import calc_atr, atr14, atr21
import pandas as pd
import numpy as np

def test_atr_calculation():
    """测试ATR计算功能"""
    print("开始测试ATR计算功能...")
    
    # 创建测试数据
    dates = pd.date_range('2023-01-01', periods=30)
    high = np.random.rand(30) * 100 + 100
    low = high - np.random.rand(30) * 10
    close = (high + low) / 2 + np.random.rand(30) * 5 - 2.5
    
    # 创建DataFrame
    kl_pd = pd.DataFrame({
        'date': dates,
        'high': high,
        'low': low,
        'close': close,
        'pre_close': np.roll(close, 1)  # 前收盘价
    })
    
    kl_pd.loc[0, 'pre_close'] = kl_pd.loc[0, 'close']  # 第一天的前收盘价等于当天收盘价
    
    print("测试数据创建成功")
    print(kl_pd.head())
    
    try:
        # 测试atr14计算
        atr14_result = atr14(kl_pd['high'], kl_pd['low'], kl_pd['close'])
        print(f"\natr14计算成功")
        print(f"atr14结果长度: {len(atr14_result)}")
        print(f"atr14前5个值: {atr14_result[:5]}")
        print(f"atr14后5个值: {atr14_result[-5:]}")
        
        # 测试atr21计算
        atr21_result = atr21(kl_pd['high'], kl_pd['low'], kl_pd['close'])
        print(f"\natr21计算成功")
        print(f"atr21结果长度: {len(atr21_result)}")
        print(f"atr21前5个值: {atr21_result[:5]}")
        print(f"atr21后5个值: {atr21_result[-5:]}")
        
        # 测试直接调用calc_atr函数
        atr_result = calc_atr(kl_pd['high'], kl_pd['low'], kl_pd['close'], time_period=14)
        print(f"\n直接调用calc_atr计算成功")
        print(f"calc_atr结果长度: {len(atr_result)}")
        print(f"calc_atr前5个值: {atr_result[:5]}")
        print(f"calc_atr后5个值: {atr_result[-5:]}")
        
        print("\n✅ 所有ATR计算测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ ATR计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    test_atr_calculation()
