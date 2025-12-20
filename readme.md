# 魔A量化交易系统 (MoA)

[![GitHub Stars](https://img.shields.io/github/stars/Lokihjl/MoA.svg)](https://github.com/Lokihjl/MoA/stargazers)
[![GitHub Issues](https://img.shields.io/github/issues/Lokihjl/MoA.svg)](https://github.com/Lokihjl/MoA/issues)
[![GitHub License](https://img.shields.io/github/license/Lokihjl/MoA.svg)](https://github.com/Lokihjl/MoA/blob/master/LICENSE)

## 📖 项目简介

魔A (MoA) 是一个基于 abupy 量化交易库开发的现代化量化交易系统，提供完整的数据下载、查询、分析和回测功能。系统采用前后端分离架构，前端使用 Vue 3 + TypeScript，后端使用 Flask，支持多种市场数据和策略分析。

## ✨ 主要功能

### 数据功能
- 📊 **数据下载**：从新浪财经 API 获取真实历史数据
- 🔍 **数据查询**：支持多条件查询和列排序
- 💾 **数据存储**：SQLite 数据库存储，高效可靠
- 📈 **数据可视化**：直观的数据展示和分析

### 策略功能
- 🚀 **Alpha 策略**：基于 abupy 核心模块实现 Alpha 因子策略
- 🔄 **策略回测**：支持多种策略的历史回测
- 📋 **策略报告**：生成详细的策略回测报告

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

## 📁 项目结构

```
MoA-ui/
├── server/                  # 后端代码
│   ├── blueprints/          # Flask 蓝图
│   │   ├── alpha_strategy.py    # Alpha 策略
│   │   ├── data.py              # 数据下载和查询
│   │   ├── stock.py             # 股票信息
│   │   └── loopback.py           # 回测功能
│   ├── config/              # 配置文件
│   ├── models/              # 数据库模型
│   ├── utils/               # 工具函数
│   └── app.py               # 应用入口
├── src/                     # 前端代码
│   ├── views/               # 页面组件
│   │   ├── DataDownloadView.vue  # 数据下载
│   │   ├── DataQueryView.vue     # 数据查询
│   │   ├── AlphaStrategyView.vue  # Alpha 策略
│   │   └── StockInfoView.vue      # 股票信息
│   ├── components/          # 通用组件
│   ├── stores/              # 状态管理
│   ├── router/              # 路由配置
│   └── main.ts              # 应用入口
└── package.json             # 前端依赖
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