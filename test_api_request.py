# -*- encoding:utf-8 -*-
import requests
import json

# 构造回测请求
url = 'http://localhost:3001/api/moA/alpha/backtest'
headers = {'Content-Type': 'application/json'}
data = {
    "params": {
        "symbol": "sh000003",
        "startDate": "2020-01-01",
        "endDate": "2020-12-31",
        "capital": 1000000
    },
    "buyFactors": [
        {
            "name": "AbuFactorBuyBreak",
            "params": '{"xd":20}'
        }
    ],
    "sellFactors": [
        {
            "name": "AbuFactorAtrNStop",
            "params": '{"stop_loss_n":1.0}'
        }
    ]
}

# 发送请求
try:
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print(f"状态码: {response.status_code}")
    print(f"响应内容: {response.text}")
except Exception as e:
    print(f"请求失败: {e}")
    import traceback
    traceback.print_exc()