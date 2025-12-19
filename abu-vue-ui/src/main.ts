import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import pinia from './stores'
import './style.css'

const app = createApp(App)

// 使用Pinia状态管理
app.use(pinia)

// 使用Vue Router
app.use(router)

// 挂载应用
app.mount('#app')
