#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔A量化交易系统 - 快速打包脚本
简化版打包工具
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """快速打包入口"""
    print("="*60)
    print("🚀 魔A量化交易系统 - 快速打包工具")
    print("="*60)
    
    # 检查当前目录
    current_dir = Path.cwd()
    if not (current_dir / "build_exe.spec").exists():
        print("❌ 错误：请在项目根目录下运行此脚本")
        print(f"当前目录: {current_dir}")
        print("请确保目录中包含 build_exe.spec 文件")
        input("按回车键退出...")
        return 1
    
    print(f"📁 项目目录: {current_dir}")
    print("📋 准备开始打包...")
    
    # 运行完整打包脚本
    build_script = current_dir / "build_exe.py"
    if build_script.exists():
        try:
            print("\n🔄 启动完整打包流程...")
            result = subprocess.run([sys.executable, str(build_script)])
            return result.returncode
        except Exception as e:
            print(f"❌ 运行失败: {e}")
            return 1
    else:
        print("❌ 找不到打包脚本 build_exe.py")
        return 1

if __name__ == "__main__":
    sys.exit(main())