# coding=utf-8
"""
ABU框架测试运行脚本

使用方法：
1. 运行所有测试：python run_tests.py
2. 运行特定测试模块：python run_tests.py tests.test_data_source
3. 运行特定测试类：python run_tests.py tests.test_data_source.TestDataSource
4. 运行特定测试方法：python run_tests.py tests.test_data_source.TestDataSource.test_load_data

依赖：
- pytest
- unittest
"""

import sys
import os
import argparse
import subprocess

# 项目根目录
root_dir = os.path.abspath(os.path.dirname(__file__))

# 将项目根目录添加到Python路径
sys.path.insert(0, root_dir)

def run_all_tests():
    """运行所有测试"""
    print("=== 运行所有测试 ===")
    
    # 检查pytest是否安装
    try:
        import pytest
        print("使用pytest运行所有测试...")
        result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], 
                               cwd=root_dir, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        return result.returncode
    except ImportError:
        print("pytest未安装，使用unittest运行所有测试...")
        import unittest
        
        # 发现所有测试
        test_loader = unittest.TestLoader()
        test_suite = test_loader.discover("tests")
        
        # 运行测试
        test_runner = unittest.TextTestRunner(verbosity=2)
        result = test_runner.run(test_suite)
        return 0 if result.wasSuccessful() else 1

def run_specific_test(test_name):
    """运行特定测试"""
    print(f"=== 运行测试: {test_name} ===")
    
    # 检查pytest是否安装
    try:
        import pytest
        print("使用pytest运行特定测试...")
        result = subprocess.run([sys.executable, "-m", "pytest", test_name, "-v"], 
                               cwd=root_dir, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        return result.returncode
    except ImportError:
        print("pytest未安装，使用unittest运行特定测试...")
        result = subprocess.run([sys.executable, "-m", "unittest", test_name, "-v"], 
                               cwd=root_dir, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        return result.returncode

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ABU框架测试运行脚本')
    parser.add_argument('test', nargs='?', help='要运行的测试名称，例如：tests.test_data_source')
    parser.add_argument('--coverage', action='store_true', help='生成测试覆盖率报告')
    
    args = parser.parse_args()
    
    if args.coverage:
        # 检查coverage是否安装
        try:
            import coverage
            print("生成测试覆盖率报告...")
            result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "--cov=abupy", "--cov-report=html"], 
                                  cwd=root_dir, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("错误信息:")
                print(result.stderr)
            return result.returncode
        except ImportError:
            print("coverage未安装，请先安装：pip install pytest-cov")
            return 1
    
    if args.test:
        return run_specific_test(args.test)
    else:
        return run_all_tests()

if __name__ == '__main__':
    sys.exit(main())
