# 配置文件

# Swagger UI配置
SWAGGER_URL = '/api/docs'  # Swagger UI访问地址
API_URL = '/api/swagger.json'  # Swagger JSON文档地址

# 数据库配置
DATABASE_URI = 'sqlite:///abu_quant.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 应用配置
DEBUG = False  # 打包时关闭调试模式
PORT = 3001
STANDALONE_MODE = True  # 独立模式：启用静态文件托管

# 打包配置
PACKAGE_BUILD = True  # 是否为打包构建
STATIC_FOLDER = 'static'  # 静态文件目录
