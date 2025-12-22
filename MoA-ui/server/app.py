# 主应用文件
import sys
import os

# 将项目根目录添加到Python路径中，以便导入abupy模块
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# 初始化ABU框架配置
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketDataFetchMode

# 设置数据源为腾讯财经
ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
# 设置数据获取模式为正常模式（先本地，后网络）
ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
# 设置使用SQLite缓存
ABuEnv.g_data_cache_type = ABuEnv.EDataCacheType.E_DATA_CACHE_SQLITE

from flask import Flask, jsonify
from config.config import DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, DEBUG, PORT
from models import db
from blueprints import moA_bp
from utils.swagger import create_swagger_blueprint, get_swagger_json, API_URL

# 创建Flask应用
app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# 初始化数据库
db.init_app(app)

# CORS中间件
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

app.after_request(add_cors_headers)

# 注册蓝图
app.register_blueprint(moA_bp)

# 配置Swagger
swaggerui_blueprint = create_swagger_blueprint()
app.register_blueprint(swaggerui_blueprint)

# Swagger JSON文档路由
@app.route(API_URL)
def swagger_json():
    return jsonify(get_swagger_json())

# 根路由
@app.route('/')
def index():
    return jsonify({'message': '魔A量化交易系统API'})

# API健康检查路由
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'ok', 'message': '魔A量化交易系统API运行正常'})

# 初始化数据库表
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=DEBUG, port=PORT)
