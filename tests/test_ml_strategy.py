# -*- encoding:utf-8 -*-
"""
    测试机器学习策略模块
"""

import sys
import os
import requests
import json

# 将项目根目录添加到Python路径中
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

# 定义API地址
BASE_URL = 'http://localhost:3001/api/moA/ml_strategy'

def test_create_model():
    """
    测试创建机器学习模型
    """
    print("\n=== 测试创建机器学习模型 ===")
    url = f"{BASE_URL}/create_model"
    data = {
        "model_type": "random_forest",
        "fit_type": "clf"
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            return result.get("model_id")
        else:
            print("创建模型失败")
            return None
    except Exception as e:
        print(f"请求失败: {e}")
        return None

def test_train_model(model_id):
    """
    测试训练机器学习模型
    """
    if not model_id:
        print("跳过训练模型测试，因为模型创建失败")
        return False
    
    print(f"\n=== 测试训练机器学习模型 (model_id: {model_id}) ===")
    url = f"{BASE_URL}/train_model"
    data = {
        "model_id": model_id,
        "symbol": "sz000002",
        "lookback_days": 100
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result.get("success")
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_smart_pick(model_id):
    """
    测试智能选股
    """
    if not model_id:
        print("跳过智能选股测试，因为模型创建失败")
        return False
    
    print(f"\n=== 测试智能选股 (model_id: {model_id}) ===")
    url = f"{BASE_URL}/smart_pick"
    data = {
        "model_id": model_id,
        "symbols": ["sz000002", "sh600036", "sz000858", "sh601318", "sz000333"],
        "top_n": 3
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            selected_stocks = result.get("selected_stocks", [])
            print(f"选中的股票数量: {len(selected_stocks)}")
            for stock in selected_stocks:
                print(f"  - {stock['symbol']}: 概率={stock['probability']}, 最新价格={stock['latest_price']}, 最新日期={stock['latest_date']}")
        
        return result.get("success")
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_adjust_stop_params(model_id):
    """
    测试调整止盈止损参数
    """
    if not model_id:
        print("跳过调整止盈止损参数测试，因为模型创建失败")
        return False
    
    print(f"\n=== 测试调整止盈止损参数 (model_id: {model_id}) ===")
    url = f"{BASE_URL}/adjust_stop_params"
    data = {
        "model_id": model_id,
        "symbol": "sz000002",
        "current_params": {
            "stop_loss": 0.05,
            "take_profit": 0.1
        }
    }
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            adjusted_params = result.get("adjusted_params", {})
            print(f"调整后的止盈止损参数: {adjusted_params}")
        
        return result.get("success")
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def test_available_models():
    """
    测试获取可用模型列表
    """
    print("\n=== 测试获取可用模型列表 ===")
    url = f"{BASE_URL}/available_models"
    
    try:
        response = requests.get(url)
        result = response.json()
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("success"):
            models = result.get("models", [])
            print(f"可用模型数量: {len(models)}")
            for model in models:
                print(f"  - {model}")
        
        return result.get("success")
    except Exception as e:
        print(f"请求失败: {e}")
        return False

def main():
    """
    主测试函数
    """
    print("开始测试机器学习策略模块...")
    
    # 测试1: 创建模型
    model_id = test_create_model()
    
    # 测试2: 获取可用模型列表
    test_available_models()
    
    # 测试3: 训练模型
    train_success = test_train_model(model_id)
    
    # 测试4: 智能选股
    if train_success:
        test_smart_pick(model_id)
    
    # 测试5: 调整止盈止损参数
    if train_success:
        test_adjust_stop_params(model_id)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()
