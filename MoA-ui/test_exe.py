#!/usr/bin/env python3
"""
测试exe文件是否正常运行
"""

import socket
import requests
import time
import sys

def test_exe_running():
    """测试exe文件是否正在运行"""
    print("🔍 检查exe文件运行状态...")
    
    # 测试端口3001是否开放
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    result = sock.connect_ex(('localhost', 3001))
    sock.close()
    
    if result == 0:
        print("✅ exe文件正在运行，端口3001已开放")
        
        # 测试HTTP访问
        try:
            print("🔍 测试前端页面访问...")
            response = requests.get('http://localhost:3001/', timeout=5)
            print(f"✅ 前端页面可访问，HTTP状态码: {response.status_code}")
            print(f"✅ 内容长度: {len(response.text)} 字符")
            
            # 检查是否包含Vue应用标识
            has_vue_app = 'id="app"' in response.text
            if has_vue_app:
                print("✅ HTML包含Vue应用标识")
            else:
                print("⚠️ HTML不包含Vue应用标识")
                
            # 检查关键元素
            if '魔A量化交易系统' in response.text:
                print("✅ 页面包含应用标题")
            else:
                print("⚠️ 页面不包含应用标题")
                
            return True
            
        except Exception as e:
            print(f"❌ 前端页面访问失败: {e}")
            return False
    else:
        print("❌ exe文件可能未正常启动")
        return False

if __name__ == "__main__":
    success = test_exe_running()
    if success:
        print("\n🎉 exe文件测试通过！")
        sys.exit(0)
    else:
        print("\n💥 exe文件测试失败！")
        sys.exit(1)