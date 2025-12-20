<template>
  <div class="finance-api-test">
    <h1>财经API测试</h1>
    
    <div class="test-section">
      <h2>财经API测试</h2>
      <div class="input-group">
        <label for="apiType">API类型：</label>
        <select id="apiType" v-model="selectedApi" class="api-select">
          <option v-for="api in apiOptions" :key="api.value" :value="api.value">
            {{ api.label }}
          </option>
        </select>
      </div>
      
      <div class="input-group">
        <label for="stockSymbol">股票代码：</label>
        <input 
          type="text" 
          id="stockSymbol" 
          v-model="stockSymbol" 
          placeholder="如：sh600000"
        />
        <button @click="testApi" :disabled="loading">
          {{ loading ? '测试中...' : `测试${selectedApiLabel}API` }}
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        <p>正在请求数据...</p>
      </div>
      
      <div v-if="error" class="error">
        <p>{{ error }}</p>
      </div>
      
      <div v-if="stockData" class="result">
        <h3>返回结果：</h3>
        <div class="result-content">
          <h4>基本信息</h4>
          <div class="info-grid">
            <div class="info-item">
              <span class="label">股票名称：</span>
              <span class="value">{{ stockData.stock_name }}</span>
            </div>
            <div class="info-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ stockData.stock_code }}</span>
            </div>
            <div class="info-item">
              <span class="label">当前价格：</span>
              <span class="value">{{ stockData.current_price }} 元</span>
            </div>
            <div class="info-item">
              <span class="label">今日开盘：</span>
              <span class="value">{{ stockData.today_open }} 元</span>
            </div>
            <div class="info-item">
              <span class="label">昨日收盘：</span>
              <span class="value">{{ stockData.yesterday_close }} 元</span>
            </div>
            <div class="info-item">
              <span class="label">今日最高：</span>
              <span class="value">{{ stockData.today_high }} 元</span>
            </div>
            <div class="info-item">
              <span class="label">今日最低：</span>
              <span class="value">{{ stockData.today_low }} 元</span>
            </div>
            <div class="info-item">
              <span class="label">成交量：</span>
              <span class="value">{{ stockData.volume }} 手</span>
            </div>
            <div class="info-item">
              <span class="label">成交额：</span>
              <span class="value">{{ stockData.total_amount }} 万元</span>
            </div>
            <div class="info-item">
              <span class="label">价格变动：</span>
              <span class="value">{{ stockData.price_change }} 元</span>
            </div>
            <div class="info-item">
              <span class="label">涨跌幅：</span>
              <span class="value">{{ stockData.change_percent }}%</span>
            </div>
            <div class="info-item">
              <span class="label">换手率：</span>
              <span class="value">{{ stockData.turnover_rate }}%</span>
            </div>
          </div>
          
          <h4>买卖盘</h4>
          <div class="order-grid">
            <div class="order-header">
              <span>价格 (元)</span>
              <span>买盘 (手)</span>
              <span>卖盘 (手)</span>
              <span>价格 (元)</span>
            </div>
            <div class="order-row">
              <span class="price">{{ stockData.buy5_price }}</span>
              <span class="volume">{{ stockData.buy5_volume }}</span>
              <span class="volume">{{ stockData.sell5_volume }}</span>
              <span class="price">{{ stockData.sell5_price }}</span>
            </div>
            <div class="order-row">
              <span class="price">{{ stockData.buy4_price }}</span>
              <span class="volume">{{ stockData.buy4_volume }}</span>
              <span class="volume">{{ stockData.sell4_volume }}</span>
              <span class="price">{{ stockData.sell4_price }}</span>
            </div>
            <div class="order-row">
              <span class="price">{{ stockData.buy3_price }}</span>
              <span class="volume">{{ stockData.buy3_volume }}</span>
              <span class="volume">{{ stockData.sell3_volume }}</span>
              <span class="price">{{ stockData.sell3_price }}</span>
            </div>
            <div class="order-row">
              <span class="price">{{ stockData.buy2_price }}</span>
              <span class="volume">{{ stockData.buy2_volume }}</span>
              <span class="volume">{{ stockData.sell2_volume }}</span>
              <span class="price">{{ stockData.sell2_price }}</span>
            </div>
            <div class="order-row">
              <span class="price">{{ stockData.buy1_price }}</span>
              <span class="volume">{{ stockData.buy1_volume }}</span>
              <span class="volume">{{ stockData.sell1_volume }}</span>
              <span class="price">{{ stockData.sell1_price }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const stockSymbol = ref('sh600000')
const selectedApi = ref('tx')
const stockData = ref<any>(null)
const loading = ref(false)
const error = ref('')

// API选项配置
const apiOptions = [
  { value: 'tx', label: '腾讯财经' },
  { value: 'sina', label: '新浪财经' },
  { value: 'eastmoney', label: '东方财富' }
]

// 计算当前选中的API名称
const selectedApiLabel = computed(() => {
  const api = apiOptions.find(item => item.value === selectedApi.value)
  return api ? api.label : ''
})

const testApi = async () => {
  if (!stockSymbol.value) {
    error.value = '请输入股票代码'
    return
  }
  
  loading.value = true
  error.value = ''
  stockData.value = null
  
  try {
    // 调用后端API执行策略
    const response = await fetch(`/api/moA/stock/${selectedApi.value}/${stockSymbol.value}`, {
      timeout: 10000, // 设置前端超时，避免用户等待过长
    })
    
    if (!response.ok) {
      if (response.status === 500) {
        const errorData = await response.json()
        throw new Error(errorData.error || `服务器错误: ${response.status}`)
      } else if (response.status === 404) {
        throw new Error('请求的资源不存在')
      } else {
        throw new Error(`HTTP错误: ${response.status}`)
      }
    }
    
    const data = await response.json()
    if (data.error) {
      throw new Error(data.error)
    }
    
    stockData.value = data
  } catch (err) {
    const errorMessage = err instanceof Error ? err.message : String(err)
    // 根据错误类型显示更友好的提示
    if (errorMessage.includes('timeout') || errorMessage.includes('超时')) {
      error.value = `请求超时，请检查网络连接或稍后重试`
    } else if (errorMessage.includes('NetworkError') || errorMessage.includes('网络') || errorMessage.includes('connect')) {
      error.value = `网络连接失败，请检查您的网络设置`
    } else if (errorMessage.includes('Failed to fetch')) {
      error.value = `无法连接到服务器，请检查服务器是否正常运行`
    } else {
      error.value = `请求失败: ${errorMessage}`
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.finance-api-test {
  width: 100%;
  margin: 0 auto;
  padding: 20px;
  box-sizing: border-box;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

h2 {
  color: #555;
  margin-bottom: 20px;
}

h3 {
  color: #666;
  margin-bottom: 15px;
}

h4 {
  color: #777;
  margin: 20px 0 15px 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
}

.test-section {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.input-group {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  align-items: center;
}

.input-group label {
  font-weight: bold;
  margin-right: 5px;
}

.input-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  flex: 1;
  max-width: 300px;
}

.input-group button {
  padding: 8px 20px;
  background-color: #42b883;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

.input-group button:hover:not(:disabled) {
  background-color: #35495e;
}

.input-group button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.api-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  background-color: white;
  cursor: pointer;
  flex: 1;
  max-width: 200px;
}

.api-select:focus {
  outline: none;
  border-color: #42b883;
  box-shadow: 0 0 0 2px rgba(66, 184, 131, 0.2);
}

.loading {
  padding: 20px;
  background-color: #e8f4f8;
  border-radius: 4px;
  color: #0056b3;
}

.error {
  padding: 20px;
  background-color: #f8d7da;
  border-radius: 4px;
  color: #721c24;
}

.result {
  margin-top: 20px;
  padding: 20px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.result-content {
  margin-top: 15px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.info-item .label {
  font-weight: bold;
  color: #555;
}

.info-item .value {
  color: #333;
}

.order-grid {
  background-color: #f5f5f5;
  border-radius: 4px;
  overflow: hidden;
}

.order-header {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  padding: 10px;
  background-color: #e0e0e0;
  font-weight: bold;
  text-align: center;
}

.order-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
  padding: 8px 10px;
  border-bottom: 1px solid #ddd;
  text-align: center;
}

.order-row:last-child {
  border-bottom: none;
}

.order-row .price {
  font-weight: bold;
  color: #333;
}

.order-row .volume {
  color: #666;
}
</style>
