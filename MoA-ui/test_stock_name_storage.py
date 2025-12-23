# 测试股票名称存储功能
import os
import sys
import json
import requests

# 设置项目根目录和server目录
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'server'))

# 确保能够导入config模块
os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'server'))

# 导入数据库模型
from models import db, StockBasic, KlineData
from app import app

# 测试股票名称存储功能
def test_stock_name_storage():
    with app.app_context():
        # 1. 检查数据库中是否已经存在测试股票的信息
        test_symbol = 'sh601118'
        existing_stock = StockBasic.query.filter_by(symbol=test_symbol).first()
        if existing_stock:
            print(f'测试股票{test_symbol}已存在于数据库中，名称为: {existing_stock.name}')
        else:
            print(f'测试股票{test_symbol}不存在于数据库中')
        
        # 2. 删除测试股票的K线数据（如果存在）
        kline_data_count = KlineData.query.filter_by(symbol=test_symbol).delete()
        db.session.commit()
        print(f'已删除{test_symbol}的{kline_data_count}条K线数据')
        
        # 3. 删除测试股票的基本信息（如果存在）
        if existing_stock:
            db.session.delete(existing_stock)
            db.session.commit()
            print(f'已删除{test_symbol}的基本信息')
        
        # 4. 模拟调用save_kl_data_to_db函数
        print('\n测试调用save_kl_data_to_db函数...')
        
        # 创建测试K线数据
        import pandas as pd
        from datetime import datetime, timedelta
        
        # 创建一个简单的DataFrame
        dates = [datetime.now() - timedelta(days=i) for i in range(5)]
        kl_df = pd.DataFrame({
            'open': [10.0, 10.5, 11.0, 10.8, 11.2],
            'high': [11.0, 11.5, 12.0, 11.8, 12.2],
            'low': [9.0, 9.5, 10.0, 9.8, 10.2],
            'close': [10.5, 11.0, 11.5, 11.2, 11.8],
            'volume': [1000000, 2000000, 3000000, 2500000, 3500000]
        }, index=dates)
        
        # 导入save_kl_data_to_db函数
        from server.blueprints.data import save_kl_data_to_db
        
        # 调用函数保存K线数据
        records_saved = save_kl_data_to_db(kl_df, test_symbol, 'sh', 'day')
        print(f'已保存{records_saved}条K线数据')
        
        # 5. 检查股票名称是否已存储
        saved_stock = StockBasic.query.filter_by(symbol=test_symbol).first()
        if saved_stock:
            print(f'测试成功！股票{test_symbol}的名称已存储到数据库中: {saved_stock.name}')
        else:
            print(f'测试失败！股票{test_symbol}的名称未存储到数据库中')
        
        # 6. 检查K线数据是否已存储
        saved_kline_data = KlineData.query.filter_by(symbol=test_symbol).count()
        print(f'已存储{saved_kline_data}条K线数据')

if __name__ == '__main__':
    test_stock_name_storage()
