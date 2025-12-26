# 主应用文件 - 独立版本（支持静态文件托管）
import sys
import os
from pathlib import Path

# 将项目根目录添加到Python路径中，以便导入abupy模块
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# 初始化ABU框架配置
from abupy.CoreBu import ABuEnv
from abupy.CoreBu.ABuEnv import EMarketSourceType, EMarketDataFetchMode

# 设置数据源为腾讯财经
ABuEnv.g_market_source = EMarketSourceType.E_MARKET_SOURCE_tx
# 设置数据获取模式为正常模式（先本地，后网络）
ABuEnv.g_data_fetch_mode = EMarketDataFetchMode.E_DATA_FETCH_NORMAL
# 设置使用SQLite缓存
ABuEnv.g_data_cache_type = ABuEnv.EDataCacheType.E_DATA_CACHE_SQLITE

from flask import Flask, jsonify, send_from_directory, render_template_string
from config.config import DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, DEBUG, PORT
from models import db
from blueprints import moA_bp
from utils.swagger import create_swagger_blueprint, get_swagger_json, API_URL
import logging

# 创建Flask应用
app = Flask(__name__, static_folder='static', static_url_path='/static')

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# 前端页面路由
@app.route('/')
def index():
    """主页面"""
    return send_from_directory(app.static_folder, 'frontend/index.html')

@app.route('/<path:path>')
def serve_frontend(path):
    """服务于前端路由"""
    # 首先尝试从静态文件服务
    try:
        return send_from_directory(app.static_folder, f'frontend/{path}')
    except:
        # 如果文件不存在，返回index.html（SPA路由支持）
        if path.startswith('api/') or path.startswith('static/'):
            # API路由和静态资源直接返回404
            return jsonify({'error': 'Not found'}), 404
        else:
            # 前端路由返回index.html
            return send_from_directory(app.static_folder, 'frontend/index.html')

# API健康检查路由
@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'ok', 
        'message': '魔A量化交易系统API运行正常',
        'version': '1.0.0',
        'static_files': 'enabled'
    })

# 系统信息路由
@app.route('/api/system/info')
def system_info():
    """系统信息"""
    import platform
    import sys
    
    return jsonify({
        'system': {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.architecture(),
            'processor': platform.processor()
        },
        'application': {
            'name': '魔A量化交易系统',
            'version': '1.0.0',
            'mode': 'standalone'
        }
    })

# 初始化数据库表
with app.app_context():
    try:
        db.create_all()
        logger.info("数据库表初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")

if __name__ == '__main__':
    logger.info("启动魔A量化交易系统...")
    logger.info(f"调试模式: {DEBUG}")
    logger.info(f"端口: {PORT}")
    
    # 检查静态文件是否存在
    static_frontend = Path(__file__).parent / 'static' / 'frontend' / 'index.html'
    if static_frontend.exists():
        logger.info("✅ 前端静态文件已就绪")
    else:
        logger.warning("⚠️ 前端静态文件未找到，请先运行 build_frontend.py")
    
    try:
        app.run(debug=DEBUG, host='0.0.0.0', port=PORT)
    except KeyboardInterrupt:
        logger.info("用户中断，程序退出")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        raise