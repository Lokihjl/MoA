# -*- encoding:utf-8 -*-
"""
    数据库初始化脚本：创建所有必需的表
"""

import sys
import os

# 切换到MoA-ui/server目录
os.chdir(os.path.abspath(os.path.join(os.path.dirname(__file__), 'MoA-ui', 'server')))

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

# 导入Flask应用和数据库模型
from app import app
from models import db

with app.app_context():
    # 初始化数据库表
    print("=== 初始化数据库表 ===")
    try:
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功")
        
        # 显示创建的表
        print("\n=== 创建的表列表 ===")
        for table in db.metadata.tables.keys():
            print(f"   {table}")
        
        print("\n=== 数据库初始化完成 ===")
    except Exception as e:
        print(f"❌ 数据库表创建失败: {e}")
        import traceback
        traceback.print_exc()
