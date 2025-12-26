import requests
import json

# 设置请求URL
url = "http://localhost:3001/api/moA/alpha/backtest"

# 设置请求头
headers = {
    "Content-Type": "application/json"
}

# 设置请求体
data = {
    "initialCash": 1000000,
    "nFolds": 2,
    "symbol": "sz000001",
    "startDate": "2022-01-01",
    "endDate": "2023-12-31",
    "stockFactors": {"AbuPickStockNDay": '{"n": 20}'},
    "buyFactors": {"AbuFactorBuyBreak": '{"xd": 10}'},
    "sellFactors": {"AbuFactorSellPreAtrN": '{"pre_atr_n": 1.5}'}
}

# 发送POST请求
try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    
    # 检查响应状态码
    print(f"Status Code: {response.status_code}")
    
    # 解析并打印响应内容
    response_data = response.json()
    print("Response Content:")
    print(json.dumps(response_data, indent=2, ensure_ascii=False))
    
    # 专门打印交易记录
    if "tradeRecords" in response_data.get("data", {}):
        print("\n=== 交易记录详情 ===")
        for trade in response_data["data"]["tradeRecords"]:
            print(f"交易ID: {trade.get('id', 'N/A')}")
            print(f"股票代码: {trade.get('symbol', 'N/A')}")
            print(f"买入日期: {trade.get('buy_date', 'N/A')}")
            print(f"卖出日期: {trade.get('sell_date', 'N/A')}")
            print(f"买入价格: {trade.get('buy_price', 'N/A')}")
            print(f"卖出价格: {trade.get('sell_price', 'N/A')}")
            print(f"成交数量: {trade.get('quantity', 'N/A')}")
            print(f"盈利金额: {trade.get('profit', 'N/A')}")
            print(f"持仓天数: {trade.get('hold_days', 'N/A')}")
            print(f"收益率: {trade.get('profit_rate', 'N/A')}%")
            print("-" * 50)
    else:
        print("\n没有找到交易记录")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
