# 魔A量化交易系统 (MoA)

基于Vue 3 + TypeScript + Flask构建的量化交易系统，提供策略回测、数据分析、股票信息查询、财经API测试和Alpha策略等功能。

## 项目概述

魔A量化交易系统是一个综合的量化交易平台，支持多种数据源、策略回测、技术分析和实时股票信息查询。系统采用前后端分离架构，前端使用Vue 3 + TypeScript，后端使用Flask。

## 技术栈

### 前端
- **框架**: Vue 3
- **类型系统**: TypeScript
- **状态管理**: Pinia
- **路由**: Vue Router
- **HTTP客户端**: Axios
- **构建工具**: Vite

### 后端
- **框架**: Flask
- **数据库**: SQLite
- **ORM**: SQLAlchemy
- **API文档**: Swagger

### 数据源
- 腾讯财经
- 新浪财经
- 东方财富
- 百度财经
- 网易财经

## 功能模块

### 1. 量化分析
- **历史回测**: 策略回测和绩效评估
- **阻力位支撑位分析**: 识别价格阻力位和支撑位
- **跳空缺口分析**: 分析和筛选跳空缺口
- **趋势敏感速度对比**: 对比不同股票的趋势速度
- **位移路程比分析**: 分析价格位移和路程比
- **线性拟合分析**: 线性回归分析
- **黄金分割分析**: 黄金分割比例分析
- **价格通道分析**: 价格通道识别
- **相关性分析**: 股票相关性分析
- **涨跌幅分析**: 涨跌幅统计分析

### 2. 股票信息
- **股票信息查询**: 实时股票基本信息查询
- **历史数据**: 股票历史K线数据
- **实时行情**: 实时股票行情数据

### 3. 数据管理
- **数据下载**: 支持从多种数据源下载股票数据
- **数据更新**: 定期更新股票数据
- **数据管理**: 管理本地股票数据

### 4. 财经API测试
- **多API支持**: 支持测试多种财经API
- **实时数据对比**: 对比不同API的实时数据
- **API可用性检测**: 检测API可用性

### 5. Alpha策略
- **策略配置**: 配置Alpha策略参数
- **因子选择**: 选择选股因子、买入因子和卖出因子
- **策略回测**: 回测Alpha策略
- **结果分析**: 分析策略回测结果

## 安装和运行

### 前置条件
- Node.js >= 18.0.0
- Python >= 3.8.0
- npm >= 9.0.0

### 1. 克隆项目

```bash
git clone https://github.com/Lokihjl/MoA.git
cd MoA/MoA-ui
```

### 2. 安装前端依赖

```bash
npm install
```

### 3. 安装后端依赖

```bash
# 进入server目录
cd server

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装Python依赖
pip install -r requirements.txt

# 返回项目根目录
cd ..
```

### 4. 运行项目

#### 方式一：分别启动前端和后端

```bash
# 终端1：启动后端服务器
npm run server

# 终端2：启动前端开发服务器
npm run dev
```

#### 方式二：同时启动前端和后端（推荐）

```bash
# 同时启动前端和后端开发服务器
npm run dev:all
```

#### 访问地址
- 前端：http://localhost:5173
- 后端API：http://localhost:3001/api
- Swagger文档：http://localhost:3001/api/docs

### 5. 构建生产版本

```bash
# 构建前端生产版本
npm run build

# 构建完成后，使用以下命令预览生产版本
npm run preview
```

## 项目结构

```
MoA-ui/
├── src/                  # 前端代码
│   ├── router/           # 路由配置
│   ├── stores/           # 状态管理
│   ├── views/            # 页面组件
│   │   ├── AlphaStrategyView.vue      # Alpha策略页面
│   │   ├── FinanceApiTestView.vue     # 财经API测试页面
│   │   ├── DataDownloadView.vue      # 数据下载页面
│   │   ├── StockInfoView.vue           # 股票信息页面
│   │   └── ...
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   └── vite-env.d.ts     # Vite环境类型声明
├── server/               # 后端代码
│   ├── app.py            # Flask应用入口
│   ├── blueprints/       # API蓝图
│   │   ├── alpha_strategy.py   # Alpha策略API
│   │   ├── stock.py            # 股票数据API
│   │   ├── data.py            # 数据下载API
│   │   └── ...
│   ├── config/           # 配置文件
│   ├── models/           # 数据模型
│   ├── utils/            # 工具函数
│   ├── requirements.txt  # Python依赖
│   └── test_tx_api.py    # 腾讯财经API测试
├── index.html            # HTML模板
├── package.json          # 前端项目配置
├── tsconfig.json         # TypeScript配置
├── vite.config.ts        # Vite配置
└── .gitignore            # Git忽略规则
```

## API文档

### 主要API端点

#### 1. 股票数据API
- `GET /api/moA/stock/<symbol>` - 获取股票基本信息
- `GET /api/moA/stock/<symbol>/history` - 获取股票历史数据
- `GET /api/moA/stock/<api_type>/<symbol>` - 从特定API获取股票数据

#### 2. 数据下载API
- `POST /api/moA/data/download` - 创建数据下载任务
- `GET /api/moA/data/download/records` - 获取下载任务记录
- `POST /api/moA/data/download/cloud` - 云盘下载6年数据

#### 3. Alpha策略API
- `GET /api/moA/alpha/factors` - 获取Alpha因子列表
- `GET /api/moA/alpha/stock-pool` - 获取股票池列表
- `POST /api/moA/alpha/backtest` - 运行Alpha策略回测
- `GET /api/moA/alpha/strategy-reports` - 获取策略报告列表

#### 4. 财经API测试API
- `GET /api/moA/stock/<api_type>/<symbol>` - 测试特定财经API

## 开发说明

### 1. 前端开发
- 使用Vue 3 Composition API
- TypeScript类型安全
- Pinia状态管理
- Vue Router路由管理

### 2. 后端开发
- Flask框架
- Blueprint模块化设计
- SQLAlchemy ORM
- Swagger API文档

### 3. 数据源配置
- 在 `server/config/config.py` 中配置数据源
- 支持多种财经API数据源

### 4. 测试
- 前端：使用Vue Test Utils和Jest
- 后端：使用pytest

## 数据说明

### 数据格式
- K线数据：OHLCV格式（开盘价、最高价、最低价、收盘价、成交量）
- 时间周期：支持日线、周线、月线
- 数据存储：SQLite数据库

### 数据更新
- 支持手动触发数据更新
- 支持自动定时更新
- 支持多数据源对比

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

- 项目地址：https://github.com/Lokihjl/MoA
- 开发者：Lokihjl

## 更新日志

### v1.0.0 (2025-12-19)
- 初始版本
- 实现基本量化分析功能
- 支持多种数据源
- 实现Alpha策略
- 实现财经API测试
- 实现数据下载功能

### v1.0.1 (2025-12-20)
- 更新README文档
- 优化项目结构
- 修复已知问题
- 增强API文档

## 鸣谢

感谢以下开源项目的支持：
- Vue 3
- TypeScript
- Flask
- SQLite
- Axios
- Vite
- Vue Router
- Pinia
- SQLAlchemy
