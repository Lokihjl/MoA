<template>
  <div class="app-container">
    <header class="app-header">
      <!-- <h1>MoA</h1> -->
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
          <router-link to="/data-query">数据查询</router-link>
        </li>
        <li>
          <router-link to="/finance-api-test">财经API测试</router-link>
        </li>
        <li>
          <router-link to="/alpha-strategy">Alpha策略</router-link>
        </li>
        <li>
          <router-link to="/ml-strategy">机器学习策略</router-link>
        </li>
      </ul>
    </nav>
    <main class="app-main">
      <router-view />
    </main>
    <footer class="app-footer">
      <p>MoA © 2025</p>
    </footer>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  width: 100%;
  box-sizing: border-box;
  background-color: var(--bg-secondary);
  position: relative;
  overflow-x: hidden;
}

/* 添加背景装饰元素 */
.app-container::before {
  content: '';
  position: fixed;
  top: -50%;
  right: -10%;
  width: 400px;
  height: 400px;
  background: var(--gradient-primary);
  opacity: 0.05;
  border-radius: 50%;
  animation: float 6s ease-in-out infinite alternate;
  z-index: -1;
}

.app-container::after {
  content: '';
  position: fixed;
  bottom: -30%;
  left: -15%;
  width: 500px;
  height: 500px;
  background: var(--gradient-secondary);
  opacity: 0.05;
  border-radius: 50%;
  animation: float 8s ease-in-out infinite alternate-reverse;
  z-index: -1;
}

@keyframes float {
  0% {
    transform: translateY(0px) rotate(0deg);
  }
  100% {
    transform: translateY(-20px) rotate(10deg);
  }
}

.app-header {
  background: var(--gradient-primary);
  color: white;
  padding: 1.5rem;
  text-align: center;
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.app-header h1 {
  margin: 0;
  font-size: 3rem;
  font-weight: 800;
  text-shadow: 0 3px 6px rgba(0, 0, 0, 0.2), 0 1px 2px rgba(0, 0, 0, 0.3);
  animation: fadeInDown 0.8s ease-out;
  letter-spacing: 0.1em;
  background: linear-gradient(135deg, #ffffff, #e0f7fa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

/* 导航栏样式 */
.app-nav {
  background-color: white;
  padding: 0.75rem;
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 1000;
  animation: fadeInDown 0.8s ease-out 0.2s both;
}

.app-nav ul {
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin: 0;
  padding: 0;
  justify-content: center;
}

.app-nav li {
  margin: 0;
}

.app-nav a {
  color: var(--text-secondary);
  text-decoration: none;
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  transition: all var(--transition-normal);
  font-weight: 500;
  font-size: 0.95rem;
  position: relative;
  overflow: hidden;
}

.app-nav a::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 0;
  height: 2px;
  background: var(--gradient-primary);
  transition: width var(--transition-normal);
}

.app-nav a:hover {
  color: var(--primary-color);
  background-color: var(--bg-tertiary);
  transform: translateY(-2px);
}

.app-nav a:hover::before {
  width: 100%;
}

.app-nav a.router-link-active {
  color: var(--primary-color);
  background-color: var(--bg-tertiary);
  font-weight: 600;
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.app-nav a.router-link-active::before {
  width: 100%;
}

/* 主内容区域 */
.app-main {
  flex: 1;
  padding: 2rem;
  width: 100%;
  box-sizing: border-box;
  max-width: 1400px;
  margin: 0 auto;
  animation: fadeInUp 0.8s ease-out 0.4s both;
}

/* 页脚样式 */
.app-footer {
  background: var(--gradient-primary);
  color: white;
  padding: 2rem;
  text-align: center;
  margin-top: auto;
  box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
  animation: fadeInUp 0.8s ease-out 0.6s both;
}

.app-footer p {
  margin: 0;
  font-size: 1rem;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header h1 {
    font-size: 2rem;
  }
  
  .app-nav ul {
    gap: 0.5rem;
  }
  
  .app-nav a {
    padding: 0.5rem 0.8rem;
    font-size: 0.85rem;
  }
  
  .app-main {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .app-header {
    padding: 1rem;
  }
  
  .app-header h1 {
    font-size: 1.5rem;
  }
  
  .app-nav {
    padding: 0.5rem;
  }
  
  .app-nav ul {
    gap: 0.25rem;
  }
  
  .app-nav a {
    padding: 0.4rem 0.6rem;
    font-size: 0.75rem;
  }
}
</style>
