<template>
  <div class="home-container">
    <h2>欢迎使用魔A量化交易系统</h2>
    <p>魔A量化是一个开源的量化交易框架，提供完整的策略开发、回测、评估和可视化解决方案。</p>
    
    <div class="features-grid">
      <div class="feature-card">
        <h3>策略开发</h3>
        <p>丰富的因子库，支持多种买入和卖出策略，灵活的参数配置。</p>
      </div>
      <div class="feature-card">
        <h3>历史回测</h3>
        <p>真实的交易模拟，全面的绩效评估指标，可视化回测结果。</p>
      </div>
      <div class="feature-card">
        <h3>技术分析</h3>
        <p>多种技术分析工具，包括阻力位支撑位、跳空缺口、趋势分析等。</p>
      </div>
      <div class="feature-card">
        <h3>机器学习</h3>
        <p>集成多种机器学习算法，支持智能选股和动态止盈止损。</p>
      </div>
    </div>
    
    <div class="quick-links">
      <h3>快速开始</h3>
      <ul>
        <li><router-link to="/loopback">运行历史回测</router-link></li>
        <li><router-link to="/stock-info">查询股票信息</router-link></li>
        <li><router-link to="/resistance-support">分析阻力位支撑位</router-link></li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.home-container {
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin: 2rem 0;
}

.feature-card {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s, box-shadow 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.feature-card h3 {
  color: #2c3e50;
  margin-top: 0;
}

.quick-links {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.quick-links ul {
  list-style: none;
  padding: 0;
}

.quick-links li {
  margin: 0.5rem 0;
}

.quick-links a {
  color: #3498db;
  text-decoration: none;
  font-size: 1.1rem;
  transition: color 0.3s;
}

.quick-links a:hover {
  color: #2980b9;
  text-decoration: underline;
}
</style>
