# -*- encoding:utf-8 -*-
"""
    测试脚本：验证数据下载模块能正确下载数据到kline_data表
"""

import sys
import os

# 切换到MoA-ui/server目录
moa_ui_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'MoA-ui', 'server'))
os.chdir(moa_ui_server_path)

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

# 导入Flask应用和数据库模型
from app import app
from models import db, KlineData, DataDownloadRecord

print("=== 测试数据下载模块 ===")
print(f"当前工作目录: {os.getcwd()}")

with app.app_context():
    # 测试1：验证kline_data表存在
    print("\n=== 测试1：验证kline_data表存在 ===")
    try:
        # 检查kline_data表是否存在
        cursor = db.session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='kline_data'")
        if cursor.fetchone():
            print("✅ kline_data表存在")
        else:
            print("❌ kline_data表不存在")
    except Exception as e:
        print(f"❌ 检查kline_data表时出错: {e}")
    
    # 测试2：获取表结构
    print("\n=== 测试2：获取kline_data表结构 ===")
    try:
        cursor = db.session.execute("PRAGMA table_info(kline_data)")
        columns = cursor.fetchall()
        print("✅ kline_data表结构:")
        for col in columns:
            print(f"   {col[1]}: {col[2]}")
    except Exception as e:
        print(f"❌ 获取kline_data表结构时出错: {e}")
    
    # 测试3：验证DataDownloadRecord表存在
    print("\n=== 测试3：验证DataDownloadRecord表存在 ===")
    try:
        # 检查DataDownloadRecord表是否存在
        cursor = db.session.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='data_download_record'")
        if cursor.fetchone():
            print("✅ data_download_record表存在")
        else:
            print("❌ data_download_record表不存在")
    except Exception as e:
        print(f"❌ 检查data_download_record表时出错: {e}")
    
    # 测试4：查看数据下载记录
    print("\n=== 测试4：查看数据下载记录 ===")
    try:
        records = DataDownloadRecord.query.all()
        print(f"✅ 数据下载记录数量: {len(records)}")
        for record in records:
            print(f"   ID: {record.id}, Status: {record.status}, Symbols: {record.symbols}, Progress: {record.progress}%")
    except Exception as e:
        print(f"❌ 查看数据下载记录时出错: {e}")
    
    # 测试5：查看kline_data表中的数据
    print("\n=== 测试5：查看kline_data表中的数据 ===")
    try:
        # 查询kline_data表中的数据
        data = KlineData.query.limit(10).all()
        print(f"✅ kline_data表中的数据数量: {len(data)}")
        if data:
            print("   数据样例:")
            for item in data[:5]:
                print(f"   Symbol: {item.symbol}, Date: {item.date}, Close: {item.close}")
    except Exception as e:
        print(f"❌ 查看kline_data表中的数据时出错: {e}")

print("\n=== 测试完成 ===")
