# -*- encoding:utf-8 -*-
"""
测试涨跌幅分析API功能
"""

import requests
import json


def test_price_change_api():
    """测试涨跌幅分析API"""
    print("开始测试涨跌幅分析API...")
    
    # 测试单个股票涨跌幅分析
    print("\n1. 测试单个股票涨跌幅分析API")
    url = "http://127.0.0.1:3001/api/moA/price-change/single"
    params = {
        "symbol": "sh600000",
        "period": "1d"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 单个股票涨跌幅分析API调用成功")
            print(f"结果包含的键: {list(result.keys())}")
        else:
            print(f"❌ 单个股票涨跌幅分析API调用失败")
    except Exception as e:
        print(f"❌ 单个股票涨跌幅分析API调用失败: {e}")
    
    # 测试两只股票涨跌幅对比
    print("\n2. 测试两只股票涨跌幅对比API")
    url = "http://127.0.0.1:3001/api/moA/price-change/pair"
    params = {
        "symbol": "sh600000",
        "benchmark_symbol": "sh600036",
        "period": "1d"
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 两只股票涨跌幅对比API调用成功")
            print(f"结果包含的键: {list(result.keys())}")
        else:
            print(f"❌ 两只股票涨跌幅对比API调用失败")
    except Exception as e:
        print(f"❌ 两只股票涨跌幅对比API调用失败: {e}")
    
    # 测试多只股票涨跌幅对比
    print("\n3. 测试多只股票涨跌幅对比API")
    url = "http://127.0.0.1:3001/api/moA/price-change/multi"
    data = {
        "symbols": ["sh600000", "sh600036", "sz000001"],
        "period": "1d"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"请求URL: {response.url}")
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 多只股票涨跌幅对比API调用成功")
            print(f"结果包含的键: {list(result.keys())}")
        else:
            print(f"❌ 多只股票涨跌幅对比API调用失败")
    except Exception as e:
        print(f"❌ 多只股票涨跌幅对比API调用失败: {e}")
    
    print("\nAPI测试完成！")


if __name__ == '__main__':
    test_price_change_api()
