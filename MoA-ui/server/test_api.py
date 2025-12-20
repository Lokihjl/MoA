# 测试回测API返回的交易记录
import requests
import json

# API URL
api_url = 'http://localhost:3001/api/moA/loopback'

# 请求参数
payload = {
    "initialCash": 1000000,
    "nFolds": 2,
    "symbols": ["sh601118"]
}

# 发送请求
response = requests.post(api_url, json=payload)

if response.status_code == 200:
    result = response.json()
    print('API返回成功')
    print(f'数据源: {result["dataSource"]}')
    print(f'总收益: {result["totalProfit"]:.4f}')
    print(f'年化收益: {result["annualProfit"]:.4f}')
    print(f'交易次数: {result["tradesCount"]}')
    
    # 显示交易记录
    print('\n交易记录:')
    for record in result['tradeRecords']:
        print(f'ID: {record["id"]}, 股票: {record["symbol"]}')
        print(f'买入: {record["buy_date"]} - {record["buy_price"]:.2f}元')
        print(f'卖出: {record["sell_date"]} - {record["sell_price"]:.2f}元')
        print(f'持有: {record["hold_days"]}天, 利润: {record["profit"]:.2f}元, 利润率: {record["profit_rate"]:.2f}%')
        print('-' * 50)
else:
    print(f'API请求失败: {response.status_code}')
    print(response.text)
