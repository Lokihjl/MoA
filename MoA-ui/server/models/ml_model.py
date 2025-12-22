# 机器学习模型存储模型
from datetime import datetime
from . import db
import pickle
import base64

class MLModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.String(100), unique=True, nullable=False)  # 模型ID
    model_name = db.Column(db.String(200), nullable=False)  # 模型名称
    model_type = db.Column(db.String(100), nullable=False)  # 模型类型
    fit_type = db.Column(db.String(50), nullable=False)  # 拟合类型
    lookback_days = db.Column(db.Integer, nullable=False, default=20)  # 回溯天数
    # 由于模型可能较大，这里存储模型的序列化数据
    model_data = db.Column(db.LargeBinary, nullable=True)  # 序列化的模型数据
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # 创建时间
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间
    
    def __repr__(self):
        return f'<MLModel {self.model_id}: {self.model_name}>'
    
    def serialize_model(self, model):
        """
        将模型序列化为二进制数据
        :param model: 要序列化的模型对象
        :return: 序列化后的二进制数据
        """
        try:
            # 使用pickle序列化模型
            model_bytes = pickle.dumps(model)
            # 使用base64编码，确保可以安全存储到数据库
            return base64.b64encode(model_bytes)
        except Exception as e:
            print(f"模型序列化失败: {e}")
            return None
    
    def deserialize_model(self, model_bytes):
        """
        将二进制数据反序列化为模型对象
        :param model_bytes: 序列化的模型二进制数据
        :return: 反序列化后的模型对象
        """
        try:
            # 先base64解码，再pickle反序列化
            if model_bytes:
                return pickle.loads(base64.b64decode(model_bytes))
            return None
        except Exception as e:
            print(f"模型反序列化失败: {e}")
            return None
