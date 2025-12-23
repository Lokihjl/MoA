# 测试数据下载模块中股票名称存储功能

import os
import sys
import json
import time
import requests
from datetime import datetime

# 设置测试环境
MOA_UI_PATH = os.path.abspath('.')
sys.path.insert(0, MOA_UI_PATH)

# 定义测试服务器URL
BASE_URL = 'http://localhost:3001'
DATA_DOWNLOAD_URL = f'{BASE_URL}/api/moA/data/download'
DATA_RECORDS_URL = f'{BASE_URL}/api/moA/data/download/records'

# 测试用的股票代码
test_stock_symbol = 'sh601118'  # 上海橡胶 - 海南橡胶

def test_data_download_with_name_storage():
    """测试数据下载功能，确保股票名称能正确存储"""
    print("开始测试数据下载模块的股票名称存储功能...")
    print(f"测试股票代码: {test_stock_symbol}")
    
    # 检查服务器是否正在运行
    try:
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print(f"✗ 服务器未运行，状态码: {response.status_code}")
            print("请先启动服务器: python server/run.py")
            return False
    except requests.ConnectionError:
        print("✗ 无法连接到服务器")
        print("请先启动服务器: python server/run.py")
        return False
    
    print("✓ 服务器正在运行")
    
    # 创建数据下载请求
    download_data = {
        "market": "SH",
        "data_type": "day",
        "symbols": test_stock_symbol
    }
    
    print("\n发送数据下载请求...")
    try:
        response = requests.post(DATA_DOWNLOAD_URL, json=download_data)
        if response.status_code not in [200, 201]:
            print(f"✗ 请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
        result = response.json()
        # API直接返回下载记录信息，而不是包含'success'字段的对象
        download_id = result.get('id')
        if download_id:
            print(f"✓ 下载请求已提交，下载ID: {download_id}")
            
            # 等待下载完成
            print("\n等待下载完成...")
            max_wait = 60  # 最大等待时间（秒）
            wait_time = 0
            download_completed = False
            
            while wait_time < max_wait:
                time.sleep(5)
                wait_time += 5
                
                # 查询下载记录
                record_response = requests.get(f'{DATA_RECORDS_URL}/{download_id}')
                if record_response.status_code == 200:
                    record_data = record_response.json()
                    # API直接返回下载记录信息
                    status = record_data.get('status')
                    print(f"  当前状态: {status} (等待 {wait_time} 秒)")
                    
                    if status == 'completed':
                        download_completed = True
                        break
                    elif status == 'failed':
                        error_msg = record_data.get('error_msg', '')
                        print(f"  下载失败: {error_msg}")
                        return False
            
            if not download_completed:
                print(f"✗ 下载超时（{max_wait}秒）")
                return False
                
            # 检查股票名称是否已存储
            print("\n检查股票名称是否已存储...")
            
            # 这里我们需要直接查询数据库，因为API可能没有提供查询StockBasic的接口
            from server.models import db, StockBasic
            from server.app import app
            
            with app.app_context():
                stock_basic = StockBasic.query.filter_by(symbol=test_stock_symbol).first()
                if stock_basic:
                    print(f"✓ 股票名称已成功存储：{stock_basic.symbol} - {stock_basic.name} ({stock_basic.market})")
                    
                    # 检查K线数据是否已存储
                    from server.models import KlineData
                    kline_count = KlineData.query.filter_by(symbol=test_stock_symbol).count()
                    print(f"✓ K线数据已成功存储：共{kline_count}条记录")
                    
                    return True
                else:
                    print("✗ 股票名称未存储到StockBasic表")
                    return False
        else:
            print(f"✗ 无法获取下载ID")
            return False
            
    except Exception as e:
        print(f"✗ 请求过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=== MoA-UI 数据下载模块股票名称存储测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_data_download_with_name_storage()
    
    print()
    print("=== 测试结果 ===")
    if success:
        print("🎉 测试成功！数据下载模块能正确地存储股票名称")
        return 0
    else:
        print("❌ 测试失败！数据下载模块无法正确存储股票名称")
        return 1

if __name__ == "__main__":
    sys.exit(main())