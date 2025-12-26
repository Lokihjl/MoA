#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
魔A量化交易系统打包脚本
一键打包为独立exe文件
"""

import os
import sys
import subprocess
import shutil
import time
from pathlib import Path

class PackageBuilder:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.frontend_dir = self.project_root  # 前端文件就在当前目录
        self.server_dir = self.project_root / "server"  # server在当前目录下的server文件夹
        
    def log(self, message, level="INFO"):
        """输出日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_environment(self):
        """检查打包环境"""
        self.log("检查打包环境...")
        
        # 检查Python版本
        python_version = sys.version_info
        if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
            self.log("错误：需要Python 3.8或更高版本", "ERROR")
            return False
        
        # 检查必要文件
        required_files = [
            self.project_root / "build_exe.spec",
            self.server_dir / "app.py",
            self.frontend_dir / "package.json",
            self.frontend_dir / "vite.config.ts"
        ]
        
        for file_path in required_files:
            if not file_path.exists():
                self.log(f"错误：缺少必要文件 {file_path}", "ERROR")
                return False
        
        self.log("环境检查通过")
        return True
    
    def install_dependencies(self):
        """安装Python依赖"""
        self.log("安装Python依赖...")
        
        # 安装PyInstaller
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                         check=True, capture_output=True)
            self.log("PyInstaller安装完成")
        except subprocess.CalledProcessError as e:
            self.log(f"PyInstaller安装失败: {e}", "ERROR")
            return False
        
        # 安装Flask依赖
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", 
                          str(self.server_dir / "requirements.txt")], 
                         check=True, capture_output=True)
            self.log("Flask依赖安装完成")
        except subprocess.CalledProcessError:
            # 如果没有requirements.txt，尝试安装pyproject.toml中的依赖
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", 
                              "Flask==3.0.3", "Flask-SQLAlchemy==3.1.1", 
                              "SQLAlchemy==2.0.35"], check=True, capture_output=True)
                self.log("Flask依赖安装完成")
            except subprocess.CalledProcessError as e:
                self.log(f"Flask依赖安装失败: {e}", "ERROR")
                return False
        
        return True
    
    def build_frontend(self):
        """构建前端"""
        self.log("检查前端构建文件...")
        
        # 检查server/static/frontend目录下是否有构建好的前端文件
        frontend_static_dir = self.server_dir / "static" / "frontend"
        if frontend_static_dir.exists():
            html_files = list(frontend_static_dir.glob("*.html"))
            js_files = list(frontend_static_dir.glob("**/*.js"))
            css_files = list(frontend_static_dir.glob("**/*.css"))
            
            if html_files and js_files and css_files:
                self.log("发现前端构建文件，跳过重新构建")
                return True
            else:
                self.log("前端构建文件不完整，将重新构建", "WARNING")
        else:
            self.log("前端静态目录不存在，将重新构建", "WARNING")
        
        self.log("开始构建前端...")
        
        try:
            # 运行前端构建脚本
            build_script = self.frontend_dir / "build_frontend.py"
            if build_script.exists():
                result = subprocess.run([sys.executable, str(build_script)], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("前端构建完成")
                    return True
                else:
                    self.log("前端构建失败，跳过前端构建（将只提供API服务）", "WARNING")
                    self.log(f"错误信息: {result.stderr}", "WARNING")
                    return True  # 不因前端构建失败而终止整个打包过程
            else:
                self.log("前端构建脚本不存在，跳过前端构建", "WARNING")
                return True
            
        except Exception as e:
            self.log(f"前端构建过程异常，跳过前端构建: {e}", "WARNING")
            return True  # 不因前端构建异常而终止整个打包过程
    
    def clean_build(self):
        """清理之前的构建"""
        self.log("清理之前的构建...")
        
        # 清理PyInstaller构建文件
        for dir_name in ["build", "dist", "__pycache__"]:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                self.log(f"已清理 {dir_name} 目录")
        
        # 清理server目录下的缓存（但不清理static目录）
        server_cache_dirs = ["__pycache__", ".pytest_cache"]
        for cache_dir in server_cache_dirs:
            cache_path = self.server_dir / cache_dir
            if cache_path.exists():
                shutil.rmtree(cache_path)
                self.log(f"已清理 {cache_dir}")
        
        self.log("清理完成")
    
    def build_exe(self):
        """使用PyInstaller打包"""
        self.log("开始打包exe...")
        
        try:
            # 切换到项目根目录
            os.chdir(self.project_root)
            
            # 执行PyInstaller
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--clean",  # 清理临时文件
                "--noconfirm",  # 不询问覆盖
                "build_exe.spec"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            if result.returncode == 0:
                self.log("exe打包成功")
                return True
            else:
                self.log(f"exe打包失败: {result.stderr}", "ERROR")
                return False
                
        except subprocess.CalledProcessError as e:
            self.log(f"exe打包异常: {e}", "ERROR")
            return False
    
    def create_launcher(self):
        """创建启动器"""
        self.log("创建启动器...")
        
        # Windows批处理启动器
        batch_content = f'''@echo off
chcp 65001 >nul
echo ================================================
echo     魔A量化交易系统
echo ================================================
echo.

cd /d "{self.project_root}"

echo 正在启动系统...
echo 请稍候，系统正在初始化...

if exist "dist\\魔A量化交易系统.exe" (
    start "" "dist\\魔A量化交易系统.exe"
    echo 系统已启动！
    echo.
    echo 系统访问地址: http://localhost:3001
    echo.
    echo 按任意键退出...
    pause >nul
) else (
    echo 错误：找不到可执行文件！
    echo 请确保打包过程已完成。
    echo.
    pause
)
'''
        
        batch_file = self.project_root / "启动系统.bat"
        with open(batch_file, 'w', encoding='gbk') as f:
            f.write(batch_content)
        
        # 创建便携版启动脚本
        portable_content = f'''@echo off
chcp 65001 >nul
echo ================================================
echo     魔A量化交易系统 - 便携版
echo ================================================
echo.

cd /d "{self.project_root}"

echo 正在启动系统（开发模式）...
echo.

REM 启动后端服务
start "魔A量化交易系统-后端" cmd /k "cd server && python app.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端开发服务器
start "魔A量化交易系统-前端" cmd /k "npm run dev"

echo.
echo 系统已启动！
echo 后端地址: http://localhost:3001
echo 前端地址: http://localhost:5173
echo.
echo 按任意键退出...
pause >nul
'''
        
        portable_file = self.project_root / "便携版启动.bat"
        with open(portable_file, 'w', encoding='gbk') as f:
            f.write(portable_content)
        
        # 创建README文件
        readme_content = f'''# 魔A量化交易系统 - 打包版本

## 打包说明

本版本为魔A量化交易系统的独立可执行文件版本，无需安装Python环境即可运行。

## 文件说明

- `魔A量化交易系统.exe` - 主程序文件
- `启动系统.bat` - 启动脚本（推荐使用）
- `便携版启动.bat` - 便携版启动脚本（开发模式）

## 使用方法

### 方法一：使用启动脚本（推荐）
1. 双击 `启动系统.bat`
2. 等待系统启动完成
3. 在浏览器中访问 http://localhost:3001

### 方法二：直接运行
1. 双击 `魔A量化交易系统.exe`
2. 在浏览器中访问 http://localhost:3001

## 系统要求

- Windows 7/8/10/11 (64位)
- 至少 2GB 可用内存
- 至少 500MB 磁盘空间

## 功能特性

- ✅ 量化交易回测
- ✅ 股票数据分析
- ✅ 策略因子研究
- ✅ 风险管理
- ✅ 数据可视化
- ✅ Web界面操作

## 技术栈

- 后端：Python 3.8+ + Flask + SQLAlchemy
- 前端：Vue.js 3 + TypeScript + Vite
- 数据库：SQLite
- 量化框架：ABU量化框架

## 注意事项

1. 首次运行可能需要较长时间进行初始化
2. 如果端口3001被占用，请关闭其他程序后重试
3. 数据文件会保存在程序同目录下
4. 如遇到问题，请检查系统日志

## 版本信息

- 版本：v1.0.0
- 构建时间：{time.strftime("%Y-%m-%d %H:%M:%S")}
- Python版本：{sys.version}
- 打包工具：PyInstaller

## 技术支持

如有问题，请检查：
1. 系统是否满足最低要求
2. 是否有足够的磁盘空间
3. 端口是否被其他程序占用
4. 防火墙是否阻止了程序运行

---
魔A量化交易系统 © 2024
'''
        
        readme_file = self.project_root / "README_打包版本.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.log("启动器创建完成")
    
    def test_build(self):
        """测试打包结果"""
        self.log("测试打包结果...")
        
        exe_file = self.dist_dir / "魔A量化交易系统.exe"
        if exe_file.exists():
            file_size = exe_file.stat().st_size / (1024 * 1024)  # MB
            self.log(f"✅ exe文件创建成功: {exe_file}")
            self.log(f"文件大小: {file_size:.1f} MB")
            return True
        else:
            self.log("❌ exe文件创建失败", "ERROR")
            return False
    
    def build(self):
        """执行完整打包流程"""
        self.log("🚀 开始打包魔A量化交易系统...")
        
        # 检查环境
        if not self.check_environment():
            return False
        
        # 安装依赖
        if not self.install_dependencies():
            return False
        
        # 构建前端
        if not self.build_frontend():
            return False
        
        # 清理之前的构建
        self.clean_build()
        
        # 打包exe
        if not self.build_exe():
            return False
        
        # 测试打包结果
        if not self.test_build():
            return False
        
        # 创建启动器
        self.create_launcher()
        
        self.log("🎉 打包完成！")
        self.log("📁 输出目录: dist/")
        self.log("🚀 启动方式: 双击 启动系统.bat")
        
        return True

def main():
    """主函数"""
    builder = PackageBuilder()
    success = builder.build()
    
    if success:
        print("\n" + "="*50)
        print("🎊 打包成功完成！")
        print("="*50)
        print("📦 打包文件位置:", builder.dist_dir)
        print("🚀 启动方式: 双击 启动系统.bat")
        print("🌐 访问地址: http://localhost:3001")
        print("="*50)
    else:
        print("\n" + "="*50)
        print("❌ 打包失败！")
        print("="*50)
        print("请检查错误信息并重试")
        print("="*50)
    
    input("\n按回车键退出...")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())