# 简单测试股票名称存储功能
import os
import sys
import requests

# 设置项目根目录和server目录
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'server'))

# 确保能够导入config模块
os.chdir(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'server'))

# 导入数据库模型
from models import db, StockBasic
from app import app

# 测试股票名称获取和存储功能
def test_stock_name_storage():
    with app.app_context():
        # 1. 测试股票代码
        test_symbol = 'sh601118'
        
        # 2. 删除测试股票的基本信息（如果存在）
        existing_stock = StockBasic.query.filter_by(symbol=test_symbol).first()
        if existing_stock:
            db.session.delete(existing_stock)
            db.session.commit()
            print(f'已删除{test_symbol}的基本信息')
        
        # 3. 模拟从ABuSymbolCN获取股票名称
        try:
            from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN
            
            abu_symbol_cn = AbuSymbolCN()
            
            # 打印数据框的列名，查看可用字段
            print(f'ABuSymbolCN数据框的列名: {list(abu_symbol_cn.df.columns)}')
            
            # 解析股票代码，去掉市场前缀
            stock_code = test_symbol[2:] if test_symbol.startswith('sh') or test_symbol.startswith('sz') else test_symbol
            
            print(f'从ABuSymbolCN获取股票{stock_code}的信息...')
            
            # 从本地数据中获取股票信息
            stock_info = abu_symbol_cn.df[abu_symbol_cn.df['symbol'] == stock_code]
            if not stock_info.empty:
                # 使用'co_name'列获取股票名称和'market'列获取市场代码
                if 'co_name' in abu_symbol_cn.df.columns and 'market' in abu_symbol_cn.df.columns:
                    stock_name = stock_info.iloc[0]['co_name']
                    market_code = stock_info.iloc[0]['market']
                else:
                    # 打印第一行数据，查看可用信息
                    print(f'股票{stock_code}的第一行数据: {stock_info.iloc[0].to_dict()}')
                    raise Exception(f'无法找到股票名称或市场代码字段')
                
                print(f'从ABuSymbolCN获取到股票名称: {stock_name}')
                print(f'从ABuSymbolCN获取到市场代码: {market_code}')
            else:
                print(f'无法从ABuSymbolCN获取股票{stock_code}的信息')
                # 打印前几行数据，查看数据格式
                print(f'ABuSymbolCN前几行数据: {abu_symbol_cn.df.head().to_dict()}')
                raise Exception(f'无法从ABuSymbolCN获取股票{stock_code}的信息')
            
            print(f'解析到股票名称: {stock_name}')
            
            # 4. 存储到数据库
            stock_basic = StockBasic(
                symbol=test_symbol,
                name=stock_name,
                market=market_code
            )
            db.session.add(stock_basic)
            db.session.commit()
            print(f'成功存储股票{test_symbol}的名称: {stock_name}')
            
            # 5. 验证存储结果
            saved_stock = StockBasic.query.filter_by(symbol=test_symbol).first()
            if saved_stock:
                print(f'验证成功: 股票{test_symbol}的名称已存储为: {saved_stock.name}')
            else:
                print(f'验证失败: 股票{test_symbol}的名称未存储到数据库中')
                
        except Exception as e:
            print(f'测试失败: {e}')
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_stock_name_storage()
