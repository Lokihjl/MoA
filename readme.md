# 魔A量化交易系统 (MoA)

[![GitHub Stars](https://img.shields.io/github/stars/Lokihjl/MoA.svg)](https://github.com/Lokihjl/MoA/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Lokihjl/MoA.svg)](https://github.com/Lokihjl/MoA/issues)
[![GitHub License](https://img.shields.io/github/license/Lokihjl/MoA.svg)](https://github.com/Lokihjl/MoA/blob/master/LICENSE)

## 📖 项目简介

魔A (MoA) 是一个基于 abupy 量化交易库开发的现代化量化交易系统，提供完整的数据下载、查询、分析和回测功能。系统采用前后端分离架构，前端使用 Vue 3 + TypeScript，后端使用 Flask，支持多种市场数据和策略分析。

### 🔄 最新更新
- **2025-12-22**：
  - 将ABU框架的数据获取和存储从CSV/HDF5转换为SQLite作为唯一数据源
  - 创建了统一的`scripts/`目录，包含所有辅助脚本
  - 创建了统一的`tests/`目录，包含所有测试文件
  - 实现了批量下载所有A股股票数据的功能
  - 优化了项目结构，使项目更加合理和整洁

## 📁 项目结构

```
e:/source/abu/abu-master/
├── abupy/                 # ABU框架核心代码
├── MoA-ui/                # 魔A量化交易系统
│   ├── src/               # 前端代码
│   ├── server/            # 后端代码
│   └── ...
├── scripts/               # 辅助脚本目录
│   ├── batch_download_all_stocks.py
│   ├── find_moa_db.py
│   ├── init_db.py
│   ├── run_tests.py
│   └── ...
├── tests/                 # 测试文件目录
│   ├── test_data_source.py
│   ├── test_sqlite.py
│   └── ...
├── venv/                  # 虚拟环境
├── .gitignore
├── readme.md
└── ...
```

## ✨ 主要功能

### 数据功能
- 📊 **数据下载**：从新浪财经 API 获取真实历史数据，支持批量下载所有A股股票数据
- 🔍 **数据查询**：支持多条件查询和列排序
- 💾 **数据存储**：**SQLite 作为唯一数据源**，高效可靠，已将ABU框架的数据获取和存储从CSV/HDF5转换为SQLite
- 📈 **数据可视化**：直观的数据展示和分析
- 🚀 **批量下载**：实现了一键批量下载所有A股股票数据的功能

### 策略功能
- 🚀 **Alpha 策略**：基于 abupy 核心模块实现 Alpha 因子策略
- 🔄 **策略回测**：支持多种策略的历史回测
- 📋 **策略报告**：生成详细的策略回测报告
- 🤖 **机器学习策略**：集成多种机器学习算法，支持智能选股和动态止盈止损
  - 支持随机森林、XGBoost、SVC、KNN、决策树等多种算法
  - 智能选股：从多个备选股票中筛选出有潜力的股票
  - 动态止盈止损：根据模型预测结果调整止盈止损参数

### 分析功能
- 📊 **涨跌幅分析**：分析单个、多只或市场整体的涨跌幅情况
- 🔗 **相关性分析**：计算和可视化股票之间的相关性
- 📈 **线性拟合分析**：对股票价格进行线性和多项式拟合，预测未来趋势
- 📉 **价格通道分析**：分析股票价格的上下通道，识别支撑和阻力位
- 📐 **黄金分割分析**：基于黄金分割理论分析股票价格支撑位和阻力位
- ⚡ **趋势敏感速度**：分析股票价格趋势的变化速度
- 🎯 **位移路程比**：分析股票价格变化的效率，识别趋势的强度和持续性
- 📏 **跳空缺口分析**：识别和分析股票价格的跳空缺口

### 其他功能
- 📱 **响应式设计**：适配各种设备
- 📝 **Swagger 文档**：完整的 API 文档
- 🔒 **安全可靠**：完善的错误处理和日志记录
- 🔧 **易于扩展**：模块化设计，便于功能扩展

## 🛠️ 技术栈

### 后端
- **语言**：Python 3.8+
- **框架**：Flask 2.0+
- **数据库**：SQLite
- **ORM**：SQLAlchemy
- **API 文档**：Swagger
- **量化库**：abupy

### 前端
- **框架**：Vue 3
- **语言**：TypeScript
- **构建工具**：Vite
- **UI 组件**：原生 CSS
- **状态管理**：Pinia
- **路由**：Vue Router

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- npm 8+

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone https://github.com/Lokihjl/MoA.git
   cd MoA
   ```

2. **安装后端依赖**
   ```bash
   cd MoA-ui/server
   pip install -r requirements.txt
   ```

3. **安装前端依赖**
   ```bash
   cd ../
   npm install
   ```

4. **启动后端服务**
   ```bash
   cd server
   python app.py
   ```

5. **启动前端服务**
   ```bash
   cd ../
   npm run dev
   ```

6. **访问应用**
   - 前端：http://localhost:5173
   - 后端 API：http://localhost:3001
   - Swagger 文档：http://localhost:3001/swagger/

### 📦 高级功能使用

#### 批量下载所有A股股票数据
```bash
# 在项目根目录下运行
python scripts/batch_download_all_stocks.py
```

#### 运行测试
```bash
# 运行所有测试
python scripts/run_tests.py

# 运行特定测试
python scripts/run_tests.py tests.test_data_source

# 生成测试覆盖率报告
python scripts/run_tests.py --coverage
```

#### 初始化数据库
```bash
python scripts/init_db.py
```

#### 查找数据库文件
```bash
python scripts/find_moa_db.py
```

## 📖 使用说明

### 数据下载
1. 进入 "数据下载" 页面
2. 选择市场类型（默认 A 股）
3. 设置时间范围
4. 选择数据源
5. 输入股票代码（可选，留空则下载全市场）
6. 点击 "从数据源下载更新"
7. 在 "下载任务记录" 中查看进度

### 数据查询
1. 进入 "数据查询" 页面
2. 选择股票代码
3. 设置查询条件
4. 点击 "查询数据"
5. 查看查询结果
6. 支持点击表头排序
7. 可导出数据为 CSV 文件

### Alpha 策略
1. 进入 "Alpha 策略" 页面
2. 选择股票池
3. 选择买入和卖出因子
4. 设置回测参数
5. 点击 "运行回测"
6. 查看回测结果和报告

### 机器学习策略
1. 进入 "机器学习策略" 页面

#### 模型管理
1. 在 "模型管理" 选项卡下，选择模型类型和拟合类型
2. 点击 "创建模型" 生成机器学习模型
3. 在模型列表中选择一个模型，输入股票代码和回溯天数
4. 点击 "训练模型" 开始训练
5. 训练完成后，可以在可用模型列表中看到训练好的模型

#### 智能选股
1. 切换到 "智能选股" 选项卡
2. 选择一个训练好的模型
3. 输入备选股票代码（多个用逗号分隔）
4. 设置选中股票数量
5. 点击 "智能选股" 开始筛选
6. 查看选股结果，包括股票代码、概率、最新价格和预测结果

#### 动态止盈止损
1. 切换到 "动态止盈止损" 选项卡
2. 选择一个训练好的模型
3. 输入股票代码
4. 设置初始止盈止损比例
5. 点击 "调整参数" 生成动态调整后的参数
6. 查看调整后的止盈止损参数和变化情况

## 🤝 贡献指南

欢迎贡献代码或提出建议！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 GPL 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📞 联系方式

- **GitHub**：https://github.com/Lokihjl/MoA
- **Issues**：https://github.com/Lokihjl/MoA/issues

## 📌 注意事项

1. 本项目仅供学习和研究使用，不构成任何投资建议
2. 数据来源为新浪财经 API，使用时请遵守相关规定
3. 量化交易有风险，投资需谨慎
4. 建议在测试环境中使用，逐步熟悉功能后再考虑实盘应用

## 🙏 致谢

- 感谢 abupy 量化交易库的开发者
- 感谢所有为项目做出贡献的开发者
- 感谢社区的支持和反馈

---

**魔A量化交易系统** - 让量化交易更简单、更高效！ 🚀