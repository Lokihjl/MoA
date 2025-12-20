# 检查数据库中sh601118的真实数据
from models import KlineData, db
from app import app

with app.app_context():
    # 查询sh601118的数据
    records = KlineData.query.filter_by(symbol='sh601118').all()
    print(f'找到 {len(records)} 条 sh601118 的数据')
    
    if records:
        # 计算价格范围
        prices = [r.close for r in records]
        min_price = min(prices)
        max_price = max(prices)
        print(f'价格范围: {min_price:.2f} - {max_price:.2f}')
        
        # 显示最近5条数据
        print('最近5条数据:')
        for r in records[-5:]:
            print(f'{r.date} - 开盘: {r.open:.2f}, 收盘: {r.close:.2f}')
    else:
        print('数据库中没有sh601118的数据')
        # 检查是否有其他股票的数据
        other_records = KlineData.query.limit(10).all()
        print(f'数据库中共有 {KlineData.query.count()} 条K线数据，前10条数据的股票代码:')
        for r in other_records:
            print(f'{r.symbol} - {r.date} - {r.close:.2f}')
