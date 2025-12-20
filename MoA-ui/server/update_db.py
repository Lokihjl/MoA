# 更新数据库表结构脚本
from app import app
from models import db

with app.app_context():
    # 更新数据库表结构
    db.create_all()
    print("数据库表结构更新完成")
