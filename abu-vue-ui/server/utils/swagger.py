# Swagger配置
from flask_swagger_ui import get_swaggerui_blueprint
from config.config import SWAGGER_URL, API_URL
from flask import jsonify

# 创建Swagger UI Blueprint
def create_swagger_blueprint():
    return get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': 'ABU量化交易系统API'
        }
    )

# Swagger JSON文档内容
def get_swagger_json():
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "ABU量化交易系统API",
            "version": "1.0.0",
            "description": "ABU量化交易系统的RESTful API文档"
        },
        "paths": {
            "/api/abu/loopback": {
                "post": {
                    "summary": "运行策略回测",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "initialCash": {"type": "number"},
                                        "nFolds": {"type": "number"},
                                        "symbols": {"type": "array", "items": {"type": "string"}},
                                        "buyFactors": {"type": "array"},
                                        "sellFactors": {"type": "array"}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "回测结果"
                        }
                    }
                }
            },
            "/api/abu/stock/{symbol}": {
                "get": {
                    "summary": "获取股票基本信息",
                    "parameters": [
                        {
                            "name": "symbol",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "股票基本信息"
                        }
                    }
                }
            },
            "/api/abu/data/download": {
                "post": {
                    "summary": "创建数据下载任务",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "market": {"type": "string"},
                                        "data_type": {"type": "string"},
                                        "symbols": {"type": "array", "items": {"type": "string"}}
                                    }
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "下载任务创建成功"
                        }
                    }
                }
            },
            "/api/abu/strategies": {
                "get": {
                    "summary": "获取可用策略列表",
                    "responses": {
                        "200": {
                            "description": "策略列表"
                        }
                    }
                }
            }
        }
    }
