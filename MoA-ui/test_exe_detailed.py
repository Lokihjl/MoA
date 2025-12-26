#!/usr/bin/env python3
"""
详细测试exe文件运行状态
"""

import subprocess
import time
import socket
import sys
import os
from pathlib import Path

def test_exe_startup():
    """测试exe文件启动"""
    print("🔍 测试exe文件启动...")
    
    exe_path = Path("dist/魔A量化交易系统.exe")
    if not exe_path.exists():
        print(f"❌ exe文件不存在: {exe_path}")
        return False
    
    print(f"✅ exe文件存在: {exe_path}")
    print(f"文件大小: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    # 尝试启动exe文件
    print("🚀 启动exe文件...")
    try:
        # 使用subprocess启动exe文件
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=exe_path.parent
        )
        
        print(f"✅ exe进程已启动，PID: {process.pid}")
        
        # 等待几秒钟让exe文件启动
        print("⏳ 等待exe文件启动...")
        time.sleep(5)
        
        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ exe进程仍在运行")
            
            # 测试端口3001
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', 3001))
            sock.close()
            
            if result == 0:
                print("✅ 端口3001已开放")
                return True
            else:
                print("❌ 端口3001未开放")
                return False
        else:
            print("❌ exe进程已退出")
            stdout, stderr = process.communicate()
            print(f"标准输出: {stdout}")
            print(f"错误输出: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 启动exe文件失败: {e}")
        return False

def test_alternative_startup():
    """测试替代启动方式"""
    print("\n🔍 测试替代启动方式...")
    
    exe_path = Path("dist/魔A量化交易系统.exe")
    try:
        # 使用cmd启动exe文件
        cmd = f'start /B "{exe_path}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"✅ 替代启动命令已执行")
        
        # 等待并测试
        time.sleep(5)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', 3001))
        sock.close()
        
        if result == 0:
            print("✅ 端口3001已开放（替代方式）")
            return True
        else:
            print("❌ 端口3001未开放（替代方式）")
            return False
            
    except Exception as e:
        print(f"❌ 替代启动失败: {e}")
        return False

if __name__ == "__main__":
    # 切换到MoA-ui目录
    moa_dir = Path(__file__).parent
    os.chdir(moa_dir)
    print(f"工作目录: {os.getcwd()}")
    
    # 测试exe文件启动
    if test_exe_startup():
        print("\n🎉 exe文件测试通过！")
        sys.exit(0)
    else:
        print("\n💥 方式1失败，尝试方式2...")
        if test_alternative_startup():
            print("\n🎉 替代方式测试通过！")
            sys.exit(0)
        else:
            print("\n💥 所有启动方式都失败！")
            sys.exit(1)