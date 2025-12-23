# 测试save_kl_data_to_db函数中股票名称存储功能

import os
import sys
import pandas as pd
from datetime import date

# 将server目录添加到系统路径
server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'server')
sys.path.insert(0, server_path)

# 切换到server目录
os.chdir(server_path)

# 导入必要的模块
from models import db, StockBasic, KlineData
from app import app

# 创建测试数据
def create_test_kl_data(symbol, market):
    """创建测试用的K线数据"""
    dates = pd.date_range(start='2023-01-01', end='2023-01-10')
    kl_data = {
        'date': dates,
        'open': [10.0, 10.2, 10.3, 10.5, 10.4, 10.6, 10.7, 10.8, 10.9, 11.0],
        'close': [10.1, 10.3, 10.4, 10.6, 10.5, 10.7, 10.8, 10.9, 11.0, 11.1],
        'high': [10.2, 10.4, 10.5, 10.7, 10.6, 10.8, 10.9, 11.0, 11.1, 11.2],
        'low': [9.9, 10.1, 10.2, 10.4, 10.3, 10.5, 10.6, 10.7, 10.8, 10.9],
        'volume': [1000000, 1200000, 1300000, 1500000, 1400000, 1600000, 1700000, 1800000, 1900000, 2000000]
    }
    
    kl_df = pd.DataFrame(kl_data)
    kl_df.set_index('date', inplace=True)
    
    return kl_df

def test_save_kl_data_with_name_storage():
    """测试保存K线数据时是否同时存储股票名称"""
    print("开始测试save_kl_data_to_db函数的股票名称存储功能...")
    
    # 测试用的股票代码和市场
    test_symbol = 'sh601118'
    test_market = 'SH'
    test_data_type = 'daily'
    
    with app.app_context():
        # 先删除可能存在的测试数据
        StockBasic.query.filter_by(symbol=test_symbol).delete()
        KlineData.query.filter_by(symbol=test_symbol).delete()
        db.session.commit()
        
        print(f"已清除股票{test_symbol}的现有数据")
        
        # 创建测试K线数据
        kl_df = create_test_kl_data(test_symbol, test_market)
        print(f"已创建测试K线数据，共{len(kl_df)}条记录")
        
        # 导入save_kl_data_to_db函数
        from blueprints.data import save_kl_data_to_db
        
        # 测试保存K线数据
        print("开始保存K线数据...")
        result = save_kl_data_to_db(kl_df, test_symbol, test_market, test_data_type)
        
        if result:
            print("K线数据保存成功！")
            
            # 检查股票名称是否已存储
            stock_basic = StockBasic.query.filter_by(symbol=test_symbol).first()
            if stock_basic:
                print(f"✓ 股票名称已成功存储：{stock_basic.symbol} - {stock_basic.name} ({stock_basic.market})")
                
                # 检查K线数据是否已存储
                kline_count = KlineData.query.filter_by(symbol=test_symbol).count()
                print(f"✓ K线数据已成功存储：共{kline_count}条记录")
                
                return True
            else:
                print("✗ 股票名称未存储到StockBasic表")
                return False
        else:
            print("✗ K线数据保存失败")
            return False

if __name__ == "__main__":
    success = test_save_kl_data_with_name_storage()
    if success:
        print("\n测试成功！save_kl_data_to_db函数能正确地在保存K线数据时存储股票名称")
        sys.exit(0)
    else:
        print("\n测试失败！")
        sys.exit(1)