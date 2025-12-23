# coding=utf-8
"""
将辅助脚本移动到统一的scripts目录
"""

import os
import shutil

# 项目根目录
root_dir = os.path.abspath(os.path.dirname(__file__))

# 目标脚本目录
scripts_dir = os.path.join(root_dir, 'scripts')

# 确保scripts目录存在
if not os.path.exists(scripts_dir):
    os.makedirs(scripts_dir)
    print(f"创建脚本目录: {scripts_dir}")

# 需要移动的脚本文件
script_files = [
    'batch_download_all_stocks.py',
    'find_moa_db.py',
    'find_emarket_target_type.py',
    'init_db.py',
    'move_test_files.py',
    'run_tests.py'
]

for script_file in script_files:
    src_path = os.path.join(root_dir, script_file)
    if os.path.exists(src_path):
        dst_path = os.path.join(scripts_dir, script_file)
        shutil.move(src_path, dst_path)
        print(f"移动脚本: {src_path} -> {dst_path}")
    else:
        print(f"脚本文件不存在: {src_path}")

print("\n所有辅助脚本移动完成！")
