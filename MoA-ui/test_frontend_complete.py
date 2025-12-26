#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
前端页面完整性测试脚本
测试Flask服务器启动和前端页面访问
"""

import requests
import socket
import time
import urllib.request
import json
import os
from pathlib import Path

def test_port_listening(port=3001, timeout=5):
    """测试端口是否在监听"""
    print(f"🔍 测试端口 {port} 是否在监听...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result == 0:
            print(f"✅ 端口 {port} 正在监听")
            return True
        else:
            print(f"❌ 端口 {port} 未响应")
            return False
    except Exception as e:
        print(f"❌ 端口测试出错: {e}")
        return False

def test_flask_endpoints():
    """测试Flask API端点"""
    base_url = "http://localhost:3001"
    results = {}
    
    print("\n🌐 测试Flask API端点...")
    
    # 测试根路径
    try:
        response = requests.get(base_url + "/", timeout=5)
        results['root'] = {
            'status_code': response.status_code,
            'content_length': len(response.text),
            'is_html': response.headers.get('content-type', '').startswith('text/html'),
            'has_vue_app': 'id="app"' in response.text
        }
        print(f"✅ 根路径: HTTP {response.status_code}, 内容长度: {len(response.text)}")
    except Exception as e:
        print(f"❌ 根路径测试失败: {e}")
        results['root'] = {'error': str(e)}
    
    # 测试API端点
    try:
        response = requests.get(base_url + "/api/health", timeout=5)
        results['health'] = {
            'status_code': response.status_code,
            'response': response.text
        }
        print(f"✅ 健康检查: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        results['health'] = {'error': str(e)}
    
    return results

def test_frontend_files():
    """测试前端静态文件"""
    print("\n📁 检查前端静态文件...")
    
    frontend_dir = Path("server/static/frontend")
    if not frontend_dir.exists():
        print("❌ 前端静态目录不存在")
        return False
    
    # 检查关键文件
    files_to_check = [
        "index.html",
        "moa.svg", 
        "assets/index-CzrVFP4C.js",
        "assets/index-DX1sx2xA.css"
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        full_path = frontend_dir / file_path
        if full_path.exists():
            size = full_path.stat().st_size
            print(f"✅ {file_path}: {size} bytes")
        else:
            print(f"❌ {file_path}: 文件不存在")
            all_files_exist = False
    
    return all_files_exist

def test_vue_app_content():
    """测试Vue应用内容"""
    print("\n🎯 测试Vue应用内容...")
    
    try:
        # 获取首页HTML
        response = requests.get("http://localhost:3001/", timeout=5)
        html_content = response.text
        
        # 检查Vue应用标识
        checks = {
            'has_app_div': 'id="app"' in html_content,
            'has_js_files': '.js' in html_content,
            'has_css_files': '.css' in html_content,
            'has_title': '<title>' in html_content,
            'has_meta_viewport': 'viewport' in html_content
        }
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}: {result}")
        
        # 检查JS和CSS文件是否可访问
        import re
        js_files = re.findall(r'src="([^"]*\.js)"', html_content)
        css_files = re.findall(r'href="([^"]*\.css)"', html_content)
        
        print(f"\n📄 发现 {len(js_files)} 个JS文件和 {len(css_files)} 个CSS文件")
        
        assets_accessible = True
        for js_file in js_files:
            try:
                resp = requests.get(f"http://localhost:3001{js_file}", timeout=3)
                if resp.status_code == 200:
                    print(f"✅ JS文件可访问: {js_file}")
                else:
                    print(f"❌ JS文件访问失败: {js_file} (HTTP {resp.status_code})")
                    assets_accessible = False
            except Exception as e:
                print(f"❌ JS文件访问出错: {js_file} ({e})")
                assets_accessible = False
        
        for css_file in css_files:
            try:
                resp = requests.get(f"http://localhost:3001{css_file}", timeout=3)
                if resp.status_code == 200:
                    print(f"✅ CSS文件可访问: {css_file}")
                else:
                    print(f"❌ CSS文件访问失败: {css_file} (HTTP {resp.status_code})")
                    assets_accessible = False
            except Exception as e:
                print(f"❌ CSS文件访问出错: {css_file} ({e})")
                assets_accessible = False
        
        return all(checks.values()) and assets_accessible
        
    except Exception as e:
        print(f"❌ Vue应用内容测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("🎊 魔A量化交易系统 - 前端页面完整性测试")
    print("=" * 60)
    
    # 检查当前目录
    if not Path("server/app.py").exists():
        print("❌ 请在MoA-ui目录下运行此脚本")
        return
    
    tests_passed = 0
    total_tests = 4
    
    # 测试1: 端口监听
    if test_port_listening():
        tests_passed += 1
    
    # 测试2: 前端文件
    if test_frontend_files():
        tests_passed += 1
    
    # 测试3: Flask API端点
    flask_results = test_flask_endpoints()
    if flask_results.get('root', {}).get('status_code') == 200:
        tests_passed += 1
    
    # 测试4: Vue应用内容
    if test_vue_app_content():
        tests_passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 测试结果: {tests_passed}/{total_tests} 通过")
    
    if tests_passed == total_tests:
        print("🎉 所有测试通过！前端页面功能正常！")
        print("🌐 访问地址: http://localhost:3001")
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息")
    
    print("=" * 60)
    
    return tests_passed == total_tests

if __name__ == "__main__":
    main()