# -*- encoding:utf-8 -*-
"""
使用ABU框架获取股票数据并测试ATR计算功能
"""

import sys
import os

# 添加ABU框架路径
sys.path.append(os.path.abspath('./abupy'))

# 初始化ABU框架配置
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketDataFetchMode

# 设置数据源为腾讯财经
ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
# 设置数据获取模式为正常模式（先本地，后网络）
ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL

from abupy.MarketBu import ABuSymbolPd
from abupy.IndicatorBu import ABuNDAtr as Atr


def test_atr_with_abu():
    """使用ABU框架获取股票数据并测试ATR计算"""
    print("开始使用ABU框架测试ATR计算功能...")
    
    try:
        # 获取股票数据
        print("正在获取股票数据...")
        # 使用小市值股票进行测试，数据量较小，下载更快
        symbol = "sz300750"  # 宁德时代
        kl_pd = ABuSymbolPd.make_kl_df(symbol, n_folds=1)
        
        if kl_pd is None or kl_pd.empty:
            print(f"❌ 获取股票{symbol}数据失败")
            return False
        
        print(f"\n成功获取股票{symbol}数据")
        print(f"数据长度: {len(kl_pd)}")
        print(kl_pd.head())
        print(kl_pd.tail())
        
        # 确保数据包含必要的列
        required_columns = ['high', 'low', 'close']
        for col in required_columns:
            if col not in kl_pd.columns:
                print(f"❌ 数据缺少必要的列: {col}")
                return False
        
        # 添加pre_close列
        if 'pre_close' not in kl_pd.columns:
            kl_pd['pre_close'] = kl_pd['close'].shift(1)
            kl_pd.loc[0, 'pre_close'] = kl_pd.loc[0, 'close']
            print(f"\n已添加pre_close列")
        
        # 测试atr14计算
        print(f"\n正在计算atr14...")
        atr14_result = Atr.atr14(kl_pd['high'], kl_pd['low'], kl_pd['close'])
        print(f"✅ atr14计算成功")
        print(f"atr14结果长度: {len(atr14_result)}")
        print(f"atr14前5个值: {atr14_result[:5]}")
        print(f"atr14后5个值: {atr14_result[-5:]}")
        
        # 测试atr21计算
        print(f"\n正在计算atr21...")
        atr21_result = Atr.atr21(kl_pd['high'], kl_pd['low'], kl_pd['close'])
        print(f"✅ atr21计算成功")
        print(f"atr21结果长度: {len(atr21_result)}")
        print(f"atr21前5个值: {atr21_result[:5]}")
        print(f"atr21后5个值: {atr21_result[-5:]}")
        
        # 直接调用calc_atr函数
        print(f"\n正在直接调用calc_atr...")
        atr_result = Atr.calc_atr(kl_pd['high'], kl_pd['low'], kl_pd['close'], time_period=14)
        print(f"✅ 直接调用calc_atr计算成功")
        print(f"calc_atr结果长度: {len(atr_result)}")
        print(f"calc_atr前5个值: {atr_result[:5]}")
        print(f"calc_atr后5个值: {atr_result[-5:]}")
        
        # 测试calc_atr函数（ABuSymbolPd中的函数）
        print(f"\n正在测试ABuSymbolPd.calc_atr...")
        from abupy.MarketBu.ABuSymbolPd import calc_atr as abu_calc_atr
        abu_calc_atr(kl_pd)
        
        if 'atr14' in kl_pd.columns and 'atr21' in kl_pd.columns:
            print(f"✅ ABuSymbolPd.calc_atr计算成功")
            print(f"添加的atr14列前5个值: {kl_pd['atr14'].head().values}")
            print(f"添加的atr21列前5个值: {kl_pd['atr21'].head().values}")
            print(f"添加的atr14列后5个值: {kl_pd['atr14'].tail().values}")
            print(f"添加的atr21列后5个值: {kl_pd['atr21'].tail().values}")
        else:
            print(f"❌ ABuSymbolPd.calc_atr计算失败，未添加atr14或atr21列")
            return False
        
        print(f"\n✅ 所有ATR计算测试通过！")
        return True
        
    except Exception as e:
        print(f"\n❌ ATR计算测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_atr_with_abu()
