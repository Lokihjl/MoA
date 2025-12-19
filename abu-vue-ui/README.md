# ABU量化交易系统 - Vue前端

基于Vue 3 + TypeScript + Pinia + Vue Router + Axios + Vite构建的ABU量化交易系统前端界面。

## 技术栈

- **前端框架**：Vue 3
- **类型系统**：TypeScript
- **状态管理**：Pinia
- **路由管理**：Vue Router
- **HTTP客户端**：Axios
- **构建工具**：Vite
- **后端模拟**：Express

## 功能模块

- **历史回测**：策略回测和绩效评估
- **阻力位支撑位分析**：识别价格阻力位和支撑位
- **跳空缺口分析**：分析和筛选跳空缺口
- **趋势敏感速度对比**：对比不同股票的趋势速度
- **位移路程比分析**：分析价格位移和路程比
- **线性拟合分析**：线性回归分析
- **黄金分割分析**：黄金分割比例分析
- **价格通道分析**：价格通道识别
- **相关性分析**：股票相关性分析
- **涨跌幅分析**：涨跌幅统计分析
- **股票信息查询**：股票基本信息查询

## 安装和运行

### 1. 安装依赖

```bash
npm install
```

### 2. 启动后端模拟服务器

```bash
# 开发模式
node server/index.js
```

### 3. 启动前端开发服务器

```bash
# 开发模式
npm run dev
```

### 4. 构建生产版本

```bash
npm run build
```

### 5. 预览生产版本

```bash
npm run preview
```

## 项目结构

```
├── src/
│   ├── assets/          # 静态资源
│   ├── components/      # 组件
│   ├── router/          # 路由配置
│   ├── stores/          # 状态管理
│   ├── utils/           # 工具函数
│   ├── views/           # 页面组件
│   ├── App.vue          # 根组件
│   ├── main.ts          # 入口文件
│   └── style.css        # 全局样式
├── server/              # 后端模拟服务器
├── public/              # 公共资源
├── index.html           # HTML模板
├── package.json         # 项目配置
├── tsconfig.json        # TypeScript配置
└── vite.config.ts       # Vite配置
```

## API代理配置

在 `vite.config.ts` 中配置了API代理，将 `/api` 请求转发到 `http://localhost:3001`。

## 开发说明

1. 所有组件使用TypeScript编写
2. 使用Composition API
3. 状态管理使用Pinia
4. 路由使用Vue Router 4
5. HTTP请求使用Axios

## 许可证

MIT
