# 回测记录模型
from datetime import datetime
from . import db

class LoopBackRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    params = db.Column(db.Text, nullable=False)  # 回测参数，JSON格式存储
    result = db.Column(db.Text, nullable=False)  # 回测结果，JSON格式存储
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    
    def __repr__(self):
        return f'<LoopBackRecord {self.id}>'