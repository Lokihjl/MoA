# K线数据模型
from . import db

class KlineData(db.Model):
    """K线数据模型"""
    __tablename__ = 'kline_data'
    
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False)  # 股票代码
    market = db.Column(db.String(50), nullable=False)  # 市场类型：us, hk, cn等
    data_type = db.Column(db.String(50), nullable=False)  # 数据类型：day, week, month等
    date = db.Column(db.Date, nullable=False)  # K线日期
    open = db.Column(db.Float, nullable=False)  # 开盘价
    high = db.Column(db.Float, nullable=False)  # 最高价
    low = db.Column(db.Float, nullable=False)  # 最低价
    close = db.Column(db.Float, nullable=False)  # 收盘价
    volume = db.Column(db.Float, nullable=False)  # 成交量
    amount = db.Column(db.Float, nullable=True)  # 成交额
    adjust = db.Column(db.Float, nullable=True)  # 复权因子
    atr21 = db.Column(db.Float, nullable=True)  # 21日ATR
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())  # 创建时间
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())  # 更新时间
    
    # 复合唯一索引，确保同一股票同一日期的数据不会重复
    __table_args__ = (
        db.UniqueConstraint('symbol', 'market', 'data_type', 'date', name='_symbol_date_uc'),
    )
    
    def __repr__(self):
        return f'<KlineData {self.symbol} {self.date} {self.close}>'
