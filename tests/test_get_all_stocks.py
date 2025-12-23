# coding=utf-8
"""
测试获取所有A股股票代码的功能
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 测试从ABu框架获取所有A股股票代码
from abupy.MarketBu.ABuSymbolStock import AbuSymbolCN

print("=== 测试获取所有A股股票代码 ===")

# 初始化AbuSymbolCN对象
abu_symbol_cn = AbuSymbolCN()

# 获取所有A股股票代码
all_symbols = abu_symbol_cn.all_symbol()
print(f"1. 通过all_symbol()方法获取到 {len(all_symbols)} 个A股股票代码")
print(f"   前10个股票代码: {all_symbols[:10]}")
print(f"   后10个股票代码: {all_symbols[-10:]}")

# 直接从df中获取股票代码
sh_stocks = abu_symbol_cn.df[abu_symbol_cn.df['exchange'] == 'SH']['symbol'].tolist()
sz_stocks = abu_symbol_cn.df[abu_symbol_cn.df['exchange'] == 'SZ']['symbol'].tolist()

all_stocks = [f'sh{code}' for code in sh_stocks] + [f'sz{code}' for code in sz_stocks]
print(f"\n2. 通过df获取到 {len(all_stocks)} 个A股股票代码")
print(f"   上海A股数量: {len(sh_stocks)}")
print(f"   深圳A股数量: {len(sz_stocks)}")
print(f"   前10个股票代码: {all_stocks[:10]}")
print(f"   后10个股票代码: {all_stocks[-10:]}")

# 测试从新浪财经API获取股票代码
print("\n=== 测试从新浪财经API获取股票代码 ===")

def get_a_share_stocks_from_sina():
    """
    从新浪财经API获取A股股票列表
    """
    try:
        import requests
        
        # 配置请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
        }
        
        # 获取上海A股
        print("正在获取上海A股列表...")
        sh_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=10000&sort=symbol&asc=1&node=sh_a&symbol=&_s_r_a=page'
        sh_response = requests.get(sh_url, timeout=20, headers=headers)
        sh_response.raise_for_status()
        sh_data = sh_response.json()
        print(f"上海A股API返回数据长度: {len(sh_data)}")
        
        # 获取深圳A股
        print("正在获取深圳A股列表...")
        sz_url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=10000&sort=symbol&asc=1&node=sz_a&symbol=&_s_r_a=page'
        sz_response = requests.get(sz_url, timeout=20, headers=headers)
        sz_response.raise_for_status()
        sz_data = sz_response.json()
        print(f"深圳A股API返回数据长度: {len(sz_data)}")
        
        # 合并股票列表
        stocks = []
        for stock in sh_data:
            stocks.append(f'sh{stock["symbol"]}')
        for stock in sz_data:
            stocks.append(f'sz{stock["symbol"]}')
        
        return stocks
    except Exception as e:
        print(f"从新浪财经API获取股票代码失败: {e}")
        return []

# 调用测试函数
sina_stocks = get_a_share_stocks_from_sina()
if sina_stocks:
    print(f"3. 从新浪财经API获取到 {len(sina_stocks)} 个A股股票代码")
    print(f"   前10个股票代码: {sina_stocks[:10]}")
    print(f"   后10个股票代码: {sina_stocks[-10:]}")
else:
    print("3. 从新浪财经API获取股票代码失败")

print("\n=== 测试完成 ===")
