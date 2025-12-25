import sys
import os
from flask import Flask

# 添加项目路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 导入应用和模型
from server.app import app, db
from server.models import KlineData, StockBasic

def check_db_data():
    with app.app_context():
        # 检查是否有股票基本信息
        stocks = StockBasic.query.all()
        print(f"StockBasic表中有 {len(stocks)} 条记录")
        for stock in stocks[:10]:  # 只显示前10条
            print(f"股票: {stock.symbol} - {stock.name}")
        
        # 检查是否有K线数据
        kline_data_count = KlineData.query.count()
        print(f"\nKlineData表中有 {kline_data_count} 条记录")
        
        # 检查sz000001的K线数据
        sz000001_data = KlineData.query.filter_by(symbol='sz000001').order_by(KlineData.date).all()
        print(f"\nsz000001的K线数据有 {len(sz000001_data)} 条记录")
        if sz000001_data:
            print(f"最早日期: {sz000001_data[0].date}")
            print(f"最新日期: {sz000001_data[-1].date}")
            print(f"数据类型: {set([data.data_type for data in sz000001_data])}")
        
        # 检查其他股票的K线数据
        symbols = db.session.query(KlineData.symbol).distinct().all()
        symbols = [s[0] for s in symbols]
        print(f"\n数据库中包含 {len(symbols)} 种股票的K线数据")
        print(f"股票代码列表: {symbols}")

if __name__ == '__main__':
    check_db_data()
