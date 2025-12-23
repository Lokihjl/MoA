<script setup lang="ts">
// App.vue - 应用根组件
import { ref, onMounted } from 'vue';

// 菜单折叠状态
const isMenuCollapsed = ref(false);
// 菜单动画状态
const menuAnimation = ref('');

// 切换菜单折叠状态
const toggleMenu = () => {
  menuAnimation.value = isMenuCollapsed.value ? 'expand' : 'collapse';
  setTimeout(() => {
    isMenuCollapsed.value = !isMenuCollapsed.value;
  }, 100);
};

// 页面加载完成后添加动画
onMounted(() => {
  // 先设置菜单为可见状态，再添加加载动画
  menuAnimation.value = 'loaded';
});
</script>

<template>
  <div class="app-container">
    <!-- 顶部导航栏 -->
    <header class="app-header fade-in-down">
      <button class="menu-toggle" @click="toggleMenu">
        <span class="menu-icon" :class="{ 'rotate': !isMenuCollapsed }"></span>
      </button>
      <h1 class="app-title gradient-text">
        <span>魔A</span>
      </h1>
      <!-- 顶部装饰 -->
      <div class="header-decoration"></div>
    </header>

    <!-- 菜单头部 
        <div class="sidebar-header">
          <div class="logo">
            <svg width="40" height="40" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" :style="{ stopColor: 'var(--primary-color)', stopOpacity: 1 }" />
                  <stop offset="100%" :style="{ stopColor: 'var(--accent-color)', stopOpacity: 1 }" />
                </linearGradient>
              </defs>
              <circle cx="50" cy="50" r="45" fill="url(#logoGradient)" />
              <text x="50" y="60" font-family="Arial" font-size="30" font-weight="bold" fill="white" text-anchor="middle">
                魔A
              </text>
            </svg>
          </div>
        </div>-->

    <!-- 主内容区域 -->
    <div class="app-main">
      <!-- 侧边栏菜单 -->
      <aside 
        class="app-sidebar"
        :class="{
          'collapsed': isMenuCollapsed,
          'menu-expand': menuAnimation === 'expand',
          'menu-collapse': menuAnimation === 'collapse',
          'menu-loaded': menuAnimation === 'loaded'
        }"
      >


        <!-- 菜单内容 -->
        <nav class="sidebar-nav">
          <ul>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.1s' }">
              <router-link to="/" active-class="active">
                <span class="menu-icon">🏠</span>
                <span class="menu-text">首页</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.15s' }">
              <router-link to="/loopback" active-class="active">
                <span class="menu-icon">📊</span>
                <span class="menu-text">历史回测</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.2s' }">
              <router-link to="/resistance-support" active-class="active">
                <span class="menu-icon">�</span>
                <span class="menu-text">阻力位支撑位</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.25s' }">
              <router-link to="/gap-analysis" active-class="active">
                <span class="menu-icon">🔍</span>
                <span class="menu-text">跳空缺口分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.3s' }">
              <router-link to="/trend-speed" active-class="active">
                <span class="menu-icon">⚡</span>
                <span class="menu-text">趋势速度分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.35s' }">
              <router-link to="/linear-fit" active-class="active">
                <span class="menu-icon">📏</span>
                <span class="menu-text">线性拟合分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.4s' }">
              <router-link to="/golden-section" active-class="active">
                <span class="menu-icon">✨</span>
                <span class="menu-text">黄金分割分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.45s' }">
              <router-link to="/price-channel" active-class="active">
                <span class="menu-icon">📉</span>
                <span class="menu-text">价格通道分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.5s' }">
              <router-link to="/correlation" active-class="active">
                <span class="menu-icon">🔗</span>
                <span class="menu-text">相关性分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.55s' }">
              <router-link to="/change-analysis" active-class="active">
                <span class="menu-icon">📊</span>
                <span class="menu-text">涨跌分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.6s' }">
              <router-link to="/stock-info" active-class="active">
                <span class="menu-icon">�</span>
                <span class="menu-text">股票信息查询</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.65s' }">
              <router-link to="/data-download" active-class="active">
                <span class="menu-icon">⬇️</span>
                <span class="menu-text">数据下载</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.7s' }">
              <router-link to="/finance-api-test" active-class="active">
                <span class="menu-icon">�</span>
                <span class="menu-text">金融API测试</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.75s' }">
              <router-link to="/alpha-strategy" active-class="active">
                <span class="menu-icon">🎯</span>
                <span class="menu-text">Alpha策略</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.8s' }">
              <router-link to="/data-query" active-class="active">
                <span class="menu-icon">🔎</span>
                <span class="menu-text">数据查询</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.85s' }">
              <router-link to="/price-change" active-class="active">
                <span class="menu-icon">💰</span>
                <span class="menu-text">价格变动分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.9s' }">
              <router-link to="/ml-strategy" active-class="active">
                <span class="menu-icon">🤖</span>
                <span class="menu-text">机器学习策略</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '0.95s' }">
              <router-link to="/distance-ratio" active-class="active">
                <span class="menu-icon">📏</span>
                <span class="menu-text">位移比率分析</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '1.0s' }">
              <router-link to="/ai-quant-features" active-class="active">
                <span class="menu-icon">🧠</span>
                <span class="menu-text">AI量化功能</span>
              </router-link>
            </li>
            <li class="menu-item fade-in-up" :style="{ animationDelay: '1.05s' }">
              <router-link to="/ai-quant-workbench" active-class="active">
                <span class="menu-icon">💻</span>
                <span class="menu-text">AI量化工作台</span>
              </router-link>
            </li>
          </ul>
        </nav>

        <!-- 菜单底部装饰 -->
        <div class="sidebar-footer">
          <div class="footer-decoration"></div>
        </div>
      </aside>

      <!-- 路由视图，用于渲染当前路由对应的组件 -->
      <main class="app-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
  font-family: inherit;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

/* 顶部导航栏 */
.app-header {
  background: rgba(255, 255, 255, 0.98);
  backdrop-filter: blur(10px);
  color: var(--text-primary);
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
  z-index: 100;
  position: relative;
  overflow: hidden;
  border-bottom: 1px solid var(--border-color);
}

/* 菜单按钮 */
.menu-toggle {
  background: var(--gradient-primary);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  margin-right: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.menu-toggle:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-lg);
}

.menu-toggle:active {
  transform: scale(0.95);
}

/* 菜单图标 */
.menu-icon {
  display: block;
  width: 20px;
  height: 2px;
  background-color: white;
  position: relative;
  transition: all 0.3s ease;
}

.menu-icon::before,
.menu-icon::after {
  content: '';
  position: absolute;
  width: 20px;
  height: 2px;
  background-color: white;
  transition: all 0.3s ease;
}

.menu-icon::before {
  top: -6px;
}

.menu-icon::after {
  top: 6px;
}

/* 菜单图标旋转动画 */
.menu-icon.rotate {
  background-color: transparent;
}

.menu-icon.rotate::before {
  top: 0;
  transform: rotate(45deg);
}

.menu-icon.rotate::after {
  top: 0;
  transform: rotate(-45deg);
}

/* 应用标题 */
.app-title {
  font-size: 1.8rem;
  font-weight: 800;
  margin: 0;
  position: relative;
  z-index: 1;
  animation: titleGlow 3s ease-in-out infinite;
}

@keyframes titleGlow {
  0%, 100% {
    text-shadow: 0 0 10px rgba(64, 158, 255, 0.3);
  }
  50% {
    text-shadow: 0 0 20px rgba(64, 158, 255, 0.6), 0 0 30px rgba(64, 158, 255, 0.3);
  }
}

/* 头部装饰 */
.header-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 100%;
  background: var(--gradient-primary);
  opacity: 0.1;
  clip-path: polygon(100% 0, 0 0, 100% 100%);
  z-index: 0;
}

/* 主内容区域 */
.app-main {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

/* 侧边栏菜单 */
.app-sidebar {
  /* 增加背景色深度，提高对比度 */
  background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
  backdrop-filter: blur(10px);
  width: 280px;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  overflow-y: auto;
  box-shadow: 2px 0 20px rgba(0, 0, 0, 0.1);
  z-index: 50;
  border-right: 1px solid var(--border-color);
  position: relative;
}

.app-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--gradient-primary);
  opacity: 0.05;
  z-index: 0;
}

.app-sidebar.collapsed {
  width: 0;
  opacity: 0;
  visibility: hidden;
  transform: translateX(-20px);
}

/* 菜单动画 */
.menu-expand {
  animation: menuExpand 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.menu-collapse {
  animation: menuCollapse 0.4s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

.menu-loaded {
  animation: menuLoaded 0.6s ease-out forwards;
}

@keyframes menuExpand {
  0% {
    opacity: 0;
    transform: translateX(-20px);
  }
  100% {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes menuCollapse {
  0% {
    opacity: 1;
    transform: translateX(0);
  }
  100% {
    opacity: 0;
    transform: translateX(-20px);
  }
}

@keyframes menuLoaded {
  0% {
    opacity: 0;
    transform: translateY(-20px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 菜单头部 */
.sidebar-header {
  padding: 2rem 1rem;
  text-align: center;
  position: relative;
  z-index: 1;
  border-bottom: 1px solid var(--border-color);
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

/* 菜单内容 */
.sidebar-nav {
  padding: 1rem 0;
  position: relative;
  z-index: 1;
}

.sidebar-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

/* 菜单项 - 移除初始opacity: 0，改为由fade-in-up动画控制 */
.menu-item {
  /* 移除了opacity: 0和transform: translateY(10px)，改为使用fade-in-up动画 */
}

.menu-item a {
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  color: var(--text-primary);
  font-weight: 500;
  text-decoration: none;
  transition: all 0.3s ease;
  border-radius: 0 25px 25px 0;
  position: relative;
  overflow: hidden;
  z-index: 1;
  background: transparent;
  border-left: 3px solid transparent;
}

.menu-item a::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 3px;
  height: 100%;
  background: var(--gradient-primary);
  transform: scaleY(0);
  transition: transform 0.3s ease;
}

.menu-item a:hover::before {
  transform: scaleY(1);
}

.menu-item a:hover {
  /* 增强悬停效果 */
  background-color: rgba(64, 158, 255, 0.15);
  transform: translateX(5px);
  color: var(--primary-color);
  font-weight: 600;
  border-left-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}

.menu-item a.active {
    /* 增强激活状态 */
    background: linear-gradient(135deg, rgba(64, 158, 255, 0.2) 0%, rgba(64, 158, 255, 0.3) 100%);
    color: var(--primary-color);
    font-weight: 700;
    border-left-color: var(--primary-color);
    box-shadow: 0 2px 10px rgba(64, 158, 255, 0.2);
  }

  .menu-item a.active::before {
    transform: scaleY(1);
  }

/* 菜单图标 */
.menu-item .menu-icon {
  font-size: 1.3rem;
  margin-right: 1rem;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: rgba(64, 158, 255, 0.15);
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08);
}

.menu-item a:hover .menu-icon {
  background: var(--gradient-primary);
  color: white;
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.menu-item a.active .menu-icon {
  background: var(--gradient-primary);
  color: white;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.4);
}

/* 菜单文本 */
.menu-item .menu-text {
  font-size: 0.95rem;
  transition: all 0.3s ease;
  letter-spacing: 0.2px;
}

/* 菜单底部 */
.sidebar-footer {
  padding: 2rem 1rem;
  text-align: center;
  position: relative;
  z-index: 1;
  border-top: 1px solid var(--border-color);
  background: white;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.05);
}

/* 底部装饰 */
.footer-decoration {
  width: 100%;
  height: 4px;
  background: var(--gradient-primary);
  border-radius: 2px;
  opacity: 0.8;
  animation: pulse 2s infinite;
}

/* 内容区域 */
.app-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background: var(--bg-secondary);
  transition: all 0.3s ease;
  position: relative;
}

/* 添加滚动条样式 */
.app-sidebar::-webkit-scrollbar,
.app-content::-webkit-scrollbar {
  width: 8px;
}

.app-sidebar::-webkit-scrollbar-track,
.app-content::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.08);
  border-radius: 4px;
}

.app-sidebar::-webkit-scrollbar-thumb,
.app-content::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.3);
  border-radius: 4px;
  transition: background 0.3s ease;
}

.app-sidebar::-webkit-scrollbar-thumb:hover,
.app-content::-webkit-scrollbar-thumb:hover {
  background: rgba(0, 0, 0, 0.45);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app-header {
    padding: 1rem;
  }

  .app-title {
    font-size: 1.4rem;
  }

  .menu-toggle {
    width: 35px;
    height: 35px;
    margin-right: 1rem;
  }

  .app-content {
    padding: 1rem;
  }

  .app-sidebar {
    width: 260px;
  }
}
</style>
