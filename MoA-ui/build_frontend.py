#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端构建脚本
构建Vue.js前端并准备静态文件托管
"""

import os
import subprocess
import shutil
import sys
from pathlib import Path

class FrontendBuilder:
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent
        self.frontend_dir = self.project_root  # 前端文件就在当前目录
        self.backend_static_dir = self.project_root / "server" / "static"
        self.build_dir = self.project_root / "dist"
        
    def check_node_environment(self):
        """检查Node.js环境"""
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            print("✅ Node.js环境检查通过")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("未找到Node.js或npm，请先安装Node.js")
            return False
    
    def install_dependencies(self):
        """安装依赖包"""
        print("📦 安装前端依赖...")
        os.chdir(self.frontend_dir)
        
        try:
            # 检查是否有node_modules
            if not (self.frontend_dir / "node_modules").exists():
                subprocess.run(["npm", "install"], check=True)
                print("✅ 依赖安装完成")
            else:
                print("✅ 依赖已存在，跳过安装")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    
    def modify_vite_config(self):
        """修改Vite配置以支持构建到Flask静态目录"""
        vite_config_path = self.frontend_dir / "vite.config.ts"
        
        config_content = '''import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/',
  build: {
    outDir: '../server/static/dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['vue', 'vue-router', 'pinia'],
          echarts: ['echarts']
        }
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3001',
        changeOrigin: true,
        secure: false
      }
    }
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  }
})'''
        
        with open(vite_config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        print("✅ Vite配置文件已更新")
    
    def build_frontend(self):
        """构建前端"""
        print("🔨 开始构建前端...")
        os.chdir(self.frontend_dir)
        
        try:
            # 清理之前的构建
            if self.backend_static_dir.exists():
                shutil.rmtree(self.backend_static_dir)
            
            # 执行构建
            result = subprocess.run(["npm", "run", "build"], 
                                  capture_output=True, text=True, check=True)
            print("✅ 前端构建完成")
            print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 前端构建失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
    
    def setup_static_hosting(self):
        """设置静态文件托管"""
        static_dist_dir = self.backend_static_dir / "dist"
        
        if not static_dist_dir.exists():
            print("❌ 构建文件不存在，请先构建前端")
            return False
        
        # 移动文件到正确的位置
        final_static_dir = self.backend_static_dir / "frontend"
        if final_static_dir.exists():
            shutil.rmtree(final_static_dir)
        
        shutil.move(str(static_dist_dir), str(final_static_dir))
        print("✅ 静态文件托管设置完成")
        return True
    
    def create_startup_script(self):
        """创建启动脚本"""
        script_content = '''@echo off
echo 启动魔A量化交易系统...

cd /d "%~dp0"
python server/app.py

pause
'''
        script_path = self.frontend_dir / "启动系统.bat"
        with open(script_path, 'w', encoding='gbk') as f:
            f.write(script_content)
        print("✅ 启动脚本已创建")
    
    def build(self):
        """执行完整构建流程"""
        print("开始前端构建流程...")
        
        # 检查环境
        if not self.check_node_environment():
            return False
        
        # 安装依赖
        if not self.install_dependencies():
            return False
        
        # 修改配置
        self.modify_vite_config()
        
        # 构建前端
        if not self.build_frontend():
            return False
        
        # 设置静态托管
        if not self.setup_static_hosting():
            return False
        
        # 创建启动脚本
        self.create_startup_script()
        
        print("🎉 前端构建完成！")
        return True

if __name__ == "__main__":
    builder = FrontendBuilder()
    success = builder.build()
    sys.exit(0 if success else 1)