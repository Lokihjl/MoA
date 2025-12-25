import requests
import json

# 设置请求URL和参数
url = 'http://localhost:3001/api/moA/alpha/backtest'
headers = {'Content-Type': 'application/json'}
params = {
    "stockPool": "hs300",
    "buyAlphaFactors": ["alpha_001", "alpha_002"],
    "sellAlphaFactors": ["alpha_003"],
    "startDate": "2024-06-26",
    "endDate": "2025-12-24",
    "capital": 1000000,
    "nFolds": 2
}

# 发送请求
response = requests.post(url, headers=headers, data=json.dumps(params))

# 打印响应状态码和内容
print(f"Response Status: {response.status_code}")
print(f"Response Content: {response.text}")