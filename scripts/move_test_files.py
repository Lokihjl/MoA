# coding=utf-8
"""
将所有测试文件移动到统一的tests目录
"""

import os
import shutil

# 项目根目录
root_dir = os.path.abspath(os.path.dirname(__file__))

# 目标测试目录
tests_dir = os.path.join(root_dir, 'tests')

# 确保tests目录存在
if not os.path.exists(tests_dir):
    os.makedirs(tests_dir)
    print(f"创建测试目录: {tests_dir}")

# 移动MoA-ui/server中的测试文件
moa_server_dir = os.path.join(root_dir, 'MoA-ui', 'server')
moa_server_tests_dir = os.path.join(tests_dir, 'moa_server')

if not os.path.exists(moa_server_tests_dir):
    os.makedirs(moa_server_tests_dir)
    print(f"创建MoA服务器测试目录: {moa_server_tests_dir}")

# 移动项目根目录下的测试文件
test_files = [
    'test_abu.py',
    'test_abu_fix.py',
    'test_abu_symbol.py',
    'test_atr.py',
    'test_atr_with_abu.py',
    'test_backtest.py',
    'test_data_download.py',
    'test_data_fetch.py',
    'test_data_source.py',
    'test_db.py',
    'test_get_all_stocks.py',
    'test_ml_strategy.py',
    'test_modified_abu.py',
    'test_price_change_api.py',
    'test_simple.py',
    'test_sqlite.py',
    'test_train_model.py',
    'test_tx_api.py'
]

for test_file in test_files:
    src_path = os.path.join(root_dir, test_file)
    if os.path.exists(src_path):
        dst_path = os.path.join(tests_dir, test_file)
        shutil.move(src_path, dst_path)
        print(f"移动文件: {src_path} -> {dst_path}")
    else:
        print(f"文件不存在: {src_path}")

# 移动MoA-ui/server中的测试文件
moa_test_files = [
    'test_api.py',
    'test_finance_apis.py',
    'test_tx_api.py'
]

for test_file in moa_test_files:
    src_path = os.path.join(moa_server_dir, test_file)
    if os.path.exists(src_path):
        dst_path = os.path.join(moa_server_tests_dir, test_file)
        shutil.move(src_path, dst_path)
        print(f"移动MoA服务器测试文件: {src_path} -> {dst_path}")
    else:
        print(f"MoA服务器测试文件不存在: {src_path}")

print("\n所有测试文件移动完成！")
