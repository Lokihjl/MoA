<template>
  <div class="stock-info-container">
    <h2>股票信息查询</h2>
    <div class="stock-search">
      <div class="search-form">
        <div class="form-group">
          <label for="stockSymbol">股票代码</label>
          <input 
            type="text" 
            id="stockSymbol" 
            v-model="stockSymbol" 
            placeholder="例如：sh600000, sz000001, hk00700"
            @keyup.enter="searchStock"
          />
        </div>
        <div class="buttons-group">
          <button class="btn-primary" @click="searchStock" :disabled="isSearching">
            <span v-if="isSearching" class="loading-spinner"></span>
            {{ isSearching ? '查询中...' : '查询股票信息' }}
          </button>
        </div>
      </div>
      
      <!-- 示例股票代码，放在搜索框下方 -->
      <div class="examples-container">
        <div class="examples">
          <span class="example-label">示例：</span>
          <span 
            class="example-code"
            v-for="example in examples" 
            :key="example"
            @click="selectExample(example)"
          >
            {{ example }}
          </span>
        </div>
      </div>
      
      <!-- 错误信息显示 -->
      <div class="error-message" v-if="errorMessage">
        {{ errorMessage }}
      </div>
    </div>

    <div class="stock-results" v-if="stockInfo">
      <div class="stock-basic-info">
        <h3>{{ stockInfo.name }} ({{ stockInfo.symbol }})</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">当前价格:</span>
            <span class="value">{{ stockInfo.price.toFixed(2) }}</span>
          </div>
          <div class="info-item">
            <span class="label">涨跌幅:</span>
            <span class="value" :class="stockInfo.change >= 0 ? 'positive' : 'negative'">
              {{ stockInfo.change.toFixed(2) }} ({{ stockInfo.changePercent.toFixed(2) }}%)
            </span>
          </div>
          <div class="info-item">
            <span class="label">成交量:</span>
            <span class="value">{{ formatNumber(stockInfo.volume) }}</span>
          </div>
          <div class="info-item">
            <span class="label">市值:</span>
            <span class="value">{{ formatNumber(stockInfo.marketCap) }}</span>
          </div>
        </div>
      </div>

      <div class="stock-history">
        <h3>历史数据</h3>
        <div class="history-chart" ref="chartContainer"></div>
      </div>
    </div>

    <div class="no-results" v-else-if="!isSearching && searchAttempted">
      <p>未查询到股票信息，请尝试其他股票代码。</p>
    </div>
    
    <!-- 非模态加载提示 -->
    <div class="loading-toast" v-if="isSearching">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>正在查询股票信息，请稍候...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

interface StockInfo {
  symbol: string
  name: string
  price: number
  change: number
  changePercent: number
  volume: number
  marketCap: number
}

interface StockHistoryData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface StockHistory {
  symbol: string
  start_date: string | null
  end_date: string | null
  data: StockHistoryData[]
}

// 股票代码输入
const stockSymbol = ref('sh600000')
// 加载状态
const isSearching = ref(false)
// 是否尝试过搜索
const searchAttempted = ref(false)
// 股票基本信息
const stockInfo = ref<StockInfo | null>(null)
// 股票历史数据
const stockHistory = ref<StockHistory | null>(null)
// 图表容器
const chartContainer = ref<HTMLElement | null>(null)
// 图表实例
let chartInstance: any = null
// 错误信息
const errorMessage = ref('')
// 示例股票代码
const examples = ref(['sh600000', 'sh601398', 'sz000001', 'hk00700'])

// 格式化数字
const formatNumber = (num: number): string => {
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(2) + 'B'
  } else if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M'
  } else if (num >= 1000) {
    return (num / 1000).toFixed(2) + 'K'
  }
  return num.toString()
}

// 选择示例股票代码
const selectExample = (example: string) => {
  stockSymbol.value = example
  searchStock()
}

// 查询股票信息
const searchStock = async () => {
  if (!stockSymbol.value.trim()) {
    errorMessage.value = '请输入股票代码'
    return
  }

  isSearching.value = true
  searchAttempted.value = true
  errorMessage.value = ''

  try {
      // 获取股票基本信息
      const infoResponse = await axios.get(`/api/moA/stock/${stockSymbol.value.trim()}`)
      stockInfo.value = infoResponse.data

      // 获取股票历史数据
      const historyResponse = await axios.get(`/api/moA/stock/${stockSymbol.value.trim()}/history`)
      stockHistory.value = historyResponse.data

    // 绘制图表
    drawChart()
  } catch (error: any) {
    console.error('查询股票信息失败:', error)
    errorMessage.value = error.response?.data?.error || error.message || '查询股票信息失败，请稍后重试'
    stockInfo.value = null
    stockHistory.value = null
  } finally {
    isSearching.value = false
  }
}

// 绘制图表
const drawChart = () => {
  if (!stockHistory.value || !chartContainer.value) return

  // 简单的历史数据表格展示（实际项目中可使用ECharts等图表库）
  let chartHtml = `
    <table class="history-table">
      <thead>
        <tr>
          <th>日期</th>
          <th>开盘价</th>
          <th>最高价</th>
          <th>最低价</th>
          <th>收盘价</th>
          <th>成交量</th>
        </tr>
      </thead>
      <tbody>
  `

  stockHistory.value.data.forEach(item => {
    chartHtml += `
      <tr>
        <td>${item.date}</td>
        <td>${item.open.toFixed(2)}</td>
        <td>${item.high.toFixed(2)}</td>
        <td>${item.low.toFixed(2)}</td>
        <td>${item.close.toFixed(2)}</td>
        <td>${formatNumber(item.volume)}</td>
      </tr>
    `
  })

  chartHtml += `
      </tbody>
    </table>
  `

  chartContainer.value.innerHTML = chartHtml
}

// 组件挂载时不自动查询，等待用户手动触发
onMounted(() => {
  // 不自动调用searchStock，等待用户手动查询
})
</script>

<style scoped>
.stock-info-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 0;
}

.stock-search {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.search-form {
  display: flex;
  gap: 1rem;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
  max-width: 300px;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.buttons-group {
  display: flex;
  gap: 1rem;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  background-color: #3498db;
  color: white;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.stock-results {
  display: grid;
  gap: 2rem;
}

.stock-basic-info {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stock-basic-info h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.info-item .label {
  font-weight: 600;
  color: #666;
}

.info-item .value {
  font-weight: 600;
  color: #333;
}

.info-item .value.positive {
  color: #e74c3c;
}

.info-item .value.negative {
  color: #27ae60;
}

.stock-history {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stock-history h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
}

.history-chart {
  width: 100%;
  overflow-x: auto;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 0.75rem;
  text-align: right;
  border-bottom: 1px solid #eee;
}

.history-table th:first-child,
.history-table td:first-child {
  text-align: left;
}

.history-table th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #666;
}

.no-results {
  background-color: white;
  padding: 3rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
  color: #666;
}

/* 示例股票代码样式 */
.examples {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #666;
  flex-wrap: wrap;
}

.example-label {
  font-weight: 600;
  white-space: nowrap;
}

.example-code {
  padding: 0.25rem 0.5rem;
  background-color: #f0f2f5;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e0e0e0;
  white-space: nowrap;
}

.example-code:hover {
  background-color: #e6f7ff;
  border-color: #91d5ff;
  color: #1890ff;
}

/* 错误信息样式 */
.error-message {
  margin-top: 1rem;
  padding: 0.75rem;
  background-color: #fff1f0;
  color: #f5222d;
  border: 1px solid #ffccc7;
  border-radius: 4px;
  font-size: 0.875rem;
}

/* 加载状态样式 */
.loading-spinner {
  display: inline-block;
  width: 1rem;
  height: 1rem;
  margin-right: 0.5rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s ease-in-out infinite;
  vertical-align: middle;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 非模态加载提示 */
.loading-toast {
  position: fixed;
  top: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  max-width: 90%;
  backdrop-filter: blur(10px);
}

.loading-toast .loading-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  padding: 0;
  box-shadow: none;
  max-width: none;
  width: auto;
}

.loading-toast .loading-spinner {
  width: 1rem;
  height: 1rem;
  margin: 0;
  border-width: 2px;
  border-top-color: white;
  border-bottom-color: white;
  border-left-color: transparent;
  border-right-color: transparent;
}

.loading-toast .loading-content p {
  margin: 0;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
}

/* 按钮中加载状态 */
.btn-primary .loading-spinner {
  border-color: rgba(255, 255, 255, 0.3);
  border-top-color: white;
}

@media (max-width: 768px) {
  .search-form {
    flex-direction: column;
    align-items: stretch;
  }

  .form-group {
    max-width: none;
  }

  .buttons-group {
    justify-content: center;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .history-table {
    font-size: 0.875rem;
  }

  .history-table th,
  .history-table td {
    padding: 0.5rem;
  }
  
  .examples {
    flex-wrap: wrap;
  }
  
  .example-code {
    margin-bottom: 0.25rem;
  }
}
</style>
