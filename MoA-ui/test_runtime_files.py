#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试运行时文件结构的脚本
"""
import os
import sys
import traceback

def main():
    print("=== 运行时文件结构检查 ===")
    
    # 当前工作目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # Python路径
    print("\nPython路径:")
    for i, path in enumerate(sys.path):
        print(f"  {i}: {path}")
    
    # 检查应用相关目录
    print("\n检查关键目录:")
    
    # 检查是否有static目录
    static_dirs = ['static', '../static', '../../static', 'server/static']
    for static_dir in static_dirs:
        abs_path = os.path.abspath(static_dir)
        exists = os.path.exists(abs_path)
        print(f"  {static_dir} -> {abs_path}: {'存在' if exists else '不存在'}")
        if exists and os.path.isdir(abs_path):
            files = os.listdir(abs_path)
            print(f"    包含文件: {files[:5]}...")  # 只显示前5个文件
    
    # 检查app.py是否存在
    app_files = ['app.py', '../app.py', '../../app.py', 'server/app.py']
    for app_file in app_files:
        abs_path = os.path.abspath(app_file)
        exists = os.path.exists(abs_path)
        print(f"  {app_file} -> {abs_path}: {'存在' if exists else '不存在'}")
    
    # 检查可执行文件目录
    exe_dir = os.path.dirname(sys.executable)
    print(f"\n可执行文件目录: {exe_dir}")
    print(f"可执行文件: {sys.executable}")
    
    # 查找是否有dist目录或其他相关目录
    for item in os.listdir('.'):
        print(f"  当前目录项: {item}")
        if os.path.isdir(item):
            try:
                sub_files = os.listdir(item)
                print(f"    包含: {sub_files[:3]}...")
            except:
                pass
    
    print("\n=== 检查完成 ===")
    input("按回车键继续...")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"错误: {e}")
        traceback.print_exc()
        input("按回车键退出...")