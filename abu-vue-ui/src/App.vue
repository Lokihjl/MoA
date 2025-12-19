<template>
  <div class="app-container">
    <header class="app-header">
      <h1>魔A</h1>
    </header>
    <nav class="app-nav">
      <ul>
        <li>
          <router-link to="/">首页</router-link>
        </li>
        <li>
          <router-link to="/loopback">历史回测</router-link>
        </li>
        <li>
          <router-link to="/resistance-support">阻力位支撑位</router-link>
        </li>
        <li>
          <router-link to="/gap-analysis">跳空缺口分析</router-link>
        </li>
        <li>
          <router-link to="/trend-speed">趋势敏感速度</router-link>
        </li>
        <li>
          <router-link to="/distance-ratio">位移路程比</router-link>
        </li>
        <li>
          <router-link to="/linear-fit">线性拟合分析</router-link>
        </li>
        <li>
          <router-link to="/golden-section">黄金分割分析</router-link>
        </li>
        <li>
          <router-link to="/price-channel">价格通道分析</router-link>
        </li>
        <li>
          <router-link to="/correlation">相关性分析</router-link>
        </li>
        <li>
          <router-link to="/change-analysis">涨跌幅分析</router-link>
        </li>
        <li>
          <router-link to="/stock-info">股票信息查询</router-link>
        </li>
        <li>
          <router-link to="/data-download">数据下载</router-link>
        </li>
        <li>
          <router-link to="/finance-api-test">财经API测试</router-link>
        </li>
        <li>
          <router-link to="/alpha-strategy">Alpha策略</router-link>
        </li>
      </ul>
    </nav>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>魔A © 2025</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: Arial, sans-serif;
}

.app-header {
  background-color: #2c3e50;
  color: white;
  padding: 1rem;
  text-align: center;
}

.app-nav {
  background-color: #34495e;
  padding: 0.5rem;
}

.app-nav ul {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0;
  padding: 0;
}

.app-nav li {
  margin: 0;
}

.app-nav a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.app-nav a:hover {
  background-color: #3498db;
}

.app-nav a.router-link-active {
  background-color: #2980b9;
}

.app-main {
  flex: 1;
  padding: 2rem;
  background-color: #ecf0f1;
}

.app-footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem;
  text-align: center;
  margin-top: auto;
}
</style>
