import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

# 导入Flask应用
from server.app import app
from server.models import db

# 在应用上下文中获取数据库连接信息
with app.app_context():
    # 获取SQLAlchemy的数据库URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"应用配置的DATABASE_URI: {db_uri}")
    
    # 获取数据库文件的实际路径
    # SQLite的URI格式为sqlite:///path/to/db.db
    if db_uri.startswith('sqlite:///'):
        # 相对路径，在Flask中会解析到instance目录
        relative_path = db_uri[10:]
        
        # 获取instance目录的路径
        instance_path = app.instance_path
        print(f"Flask应用的instance路径: {instance_path}")
        
        # 构建完整的数据库文件路径
        db_path = os.path.join(instance_path, relative_path)
        print(f"实际使用的数据库文件路径: {db_path}")
        
        # 检查文件是否存在
        if os.path.exists(db_path):
            print(f"数据库文件存在，大小: {os.path.getsize(db_path)} bytes")
        else:
            print("数据库文件不存在")
    else:
        print("不是SQLite数据库")

# 检查两个数据库文件的情况
moa_db_path = "e:\source\abu\abu-master\MoA-ui\server\moa.db"
abu_quant_db_path = "e:\source\abu\abu-master\MoA-ui\server\instance\abu_quant.db"

print(f"\n检查用户提到的两个数据库文件:")
if os.path.exists(moa_db_path):
    print(f"moa.db存在，大小: {os.path.getsize(moa_db_path)} bytes")
else:
    print("moa.db不存在")
    
if os.path.exists(abu_quant_db_path):
    print(f"abu_quant.db存在，大小: {os.path.getsize(abu_quant_db_path)} bytes")
else:
    print("abu_quant.db不存在")
