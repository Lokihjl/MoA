# 数据库模型初始化
from flask_sqlalchemy import SQLAlchemy

# 创建数据库实例
db = SQLAlchemy()

# 导入所有模型
from .loopback import LoopBackRecord
from .kline import KlineData
from .data_download import DataDownloadRecord
