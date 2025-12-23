# 股票基本信息模型
from . import db

class StockBasic(db.Model):
    """股票基本信息模型，用于存储股票代码、名称等基本信息"""
    __tablename__ = 'stock_basic'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)  # 股票代码，如sh600000
    name = db.Column(db.String(50), nullable=False)  # 股票名称
    market = db.Column(db.String(50), nullable=False)  # 市场类型：us, hk, cn等
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间
    
    def __repr__(self):
        return f'<StockBasic {self.symbol} {self.name}>'