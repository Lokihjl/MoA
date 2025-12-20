# 数据下载记录模型
from datetime import datetime
from . import db

class DataDownloadRecord(db.Model):
    """数据下载记录模型"""
    __tablename__ = 'data_download_record'
    
    id = db.Column(db.Integer, primary_key=True)
    market = db.Column(db.String(50), nullable=False)  # 市场类型：us, hk, cn等
    data_type = db.Column(db.String(50), nullable=False)  # 数据类型：day, week, month等
    symbols = db.Column(db.Text, nullable=False)  # 股票代码，逗号分隔
    status = db.Column(db.String(20), nullable=False, default='pending')  # 状态：pending, running, completed, failed
    progress = db.Column(db.Integer, nullable=False, default=0)  # 进度：0-100
    start_time = db.Column(db.DateTime, nullable=True)  # 开始时间
    end_time = db.Column(db.DateTime, nullable=True)  # 结束时间
    error_message = db.Column(db.Text, nullable=True)  # 错误信息
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    total_downloaded = db.Column(db.Integer, nullable=False, default=0)  # 下载的条数
    total_symbols = db.Column(db.Integer, nullable=False, default=0)  # 处理的股票数量
    success_symbols = db.Column(db.Integer, nullable=False, default=0)  # 成功获取数据的股票数量
    
    def __repr__(self):
        return f'<DataDownloadRecord {self.id} - {self.market} - {self.status}>'
