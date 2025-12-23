# -*- encoding:utf-8 -*-
"""
    查找moa.db文件的实际位置
"""

import os
import sys

def find_moa_db():
    """
    查找moa.db文件的实际位置
    """
    print("=== 查找moa.db文件 ===")
    
    # 从项目根目录开始搜索
    project_root = os.path.abspath(os.path.dirname(__file__))
    print(f"搜索开始目录: {project_root}")
    
    # 遍历所有目录，查找moa.db文件
    for root, dirs, files in os.walk(project_root):
        if 'moa.db' in files:
            moa_db_path = os.path.join(root, 'moa.db')
            print(f"✅ 找到moa.db文件: {moa_db_path}")
            print(f"文件大小: {os.path.getsize(moa_db_path)} 字节")
            return moa_db_path
    
    print("❌ 未找到moa.db文件")
    return None

if __name__ == "__main__":
    find_moa_db()
