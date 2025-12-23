# Swagger配置
from flask_swagger_ui import get_swaggerui_blueprint
from ..config.config import SWAGGER_URL, API_URL
from flask import jsonify

# 创建Swagger UI Blueprint
def create_swagger_blueprint():
    return get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': '魔A量化交易系统API'
        }
    )

# Swagger JSON文档内容
def get_swagger_json():
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "魔A量化交易系统API",
            "version": "1.0.0",
            "description": "魔A量化交易系统的RESTful API文档"
        },
        "paths": {
            # Alpha策略相关接口
            "/api/moA/alpha/factors": {
                "get": {
                    "summary": "获取Alpha因子列表",
                    "responses": {
                        "200": {
                            "description": "Alpha因子列表"
                        }
                    }
                }
            },
            "/api/moA/alpha/stock-pool": {
                "get": {
                    "summary": "获取股票池列表",
                    "responses": {
                        "200": {
                            "description": "股票池列表"
                        }
                    }
                }
            },
            "/api/moA/alpha/backtest": {
                "post": {
                    "summary": "运行Alpha策略回测",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "stockPool": {"type": "string"},
                                        "buyAlphaFactors": {"type": "array", "items": {"type": "string"}},
                                        "sellAlphaFactors": {"type": "array", "items": {"type": "string"}},
                                        "startDate": {"type": "string", "format": "date"},
                                        "endDate": {"type": "string", "format": "date"},
                                        "capital": {"type": "number"},
                                        "nFolds": {"type": "number"}
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
            "/api/moA/alpha/strategy-reports": {
                "get": {
                    "summary": "获取策略报告列表",
                    "responses": {
                        "200": {
                            "description": "策略报告列表"
                        }
                    }
                }
            },
            "/api/moA/alpha/strategy-report/{report_id}": {
                "get": {
                    "summary": "获取策略报告",
                    "parameters": [
                        {
                            "name": "report_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "string"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "策略报告"
                        }
                    }
                }
            },
            
            # 数据下载相关接口
            "/api/moA/data/download": {
                "post": {
                    "summary": "创建数据下载任务",
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "market": {"type": "string"},
                                        "timeMode": {"type": "string"},
                                        "years": {"type": "number"},
                                        "startDate": {"type": "string"},
                                        "endDate": {"type": "string"},
                                        "dataSource": {"type": "string"},
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
            "/api/moA/data/download/records": {
                "get": {
                    "summary": "获取数据下载任务列表",
                    "responses": {
                        "200": {
                            "description": "下载任务列表"
                        }
                    }
                }
            },
            "/api/moA/data/download/records/{record_id}": {
                "get": {
                    "summary": "获取单个数据下载任务详情",
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "下载任务详情"
                        },
                        "404": {
                            "description": "下载记录不存在"
                        }
                    }
                }
            },
            "/api/moA/data/download/records/{record_id}/cancel": {
                "put": {
                    "summary": "取消数据下载任务",
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "下载任务已取消"
                        },
                        "404": {
                            "description": "下载记录不存在"
                        }
                    }
                }
            },
            "/api/moA/data/download/records/{record_id}/retry": {
                "post": {
                    "summary": "重新执行数据下载任务",
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            }
                        }
                    ],
                    "responses": {
                        "201": {
                            "description": "新的下载任务创建成功"
                        },
                        "404": {
                            "description": "下载记录不存在"
                        }
                    }
                }
            },
            "/api/moA/data/download/records/{record_id}": {
                "delete": {
                    "summary": "删除数据下载任务记录",
                    "parameters": [
                        {
                            "name": "record_id",
                            "in": "path",
                            "required": True,
                            "schema": {
                                "type": "integer"
                            }
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "下载记录已删除"
                        },
                        "404": {
                            "description": "下载记录不存在"
                        }
                    }
                }
            },
            "/api/moA/data/markets": {
                "get": {
                    "summary": "获取支持的市场列表",
                    "responses": {
                        "200": {
                            "description": "支持的市场列表"
                        }
                    }
                }
            },
            "/api/moA/data/types": {
                "get": {
                    "summary": "获取支持的数据类型",
                    "responses": {
                        "200": {
                            "description": "支持的数据类型列表"
                        }
                    }
                }
            },

        }
    }
