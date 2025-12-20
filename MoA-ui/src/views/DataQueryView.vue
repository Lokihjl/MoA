<template>
  <div class="data-query-container">
    <h2>数据查询</h2>
    <div class="data-query-content">
      <div class="query-form">
        <h3>查询条件</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="symbol">股票代码</label>
            <select id="symbol" v-model="queryParams.symbol">
              <option value="">请选择股票代码</option>
              <option v-for="item in symbolsList" :key="item.symbol" :value="item.symbol">
                {{ item.symbol }} ({{ item.market }})
              </option>
            </select>
          </div>
          <div class="form-group">
            <label for="market">市场类型</label>
            <select id="market" v-model="queryParams.market" disabled>
              <option value="cn">A股</option>
            </select>
          </div>
          <div class="form-group">
            <label for="data_type">数据类型</label>
            <select id="data_type" v-model="queryParams.data_type">
              <option value="day">日线</option>
              <option value="week">周线</option>
              <option value="month">月线</option>
            </select>
          </div>
          <div class="form-group">
            <label for="start_date">开始日期</label>
            <input 
              type="date" 
              id="start_date" 
              v-model="queryParams.start_date"
            />
          </div>
          <div class="form-group">
            <label for="end_date">结束日期</label>
            <input 
              type="date" 
              id="end_date" 
              v-model="queryParams.end_date"
            />
          </div>
        </div>
        <div class="buttons-group">
          <button class="btn-primary" @click="queryData" :disabled="isQuerying">
            {{ isQuerying ? '查询中...' : '查询数据' }}
          </button>
          <button class="btn-secondary" @click="clearQuery">
            清除条件
          </button>
        </div>
      </div>
      
      <div class="query-results">
        <h3>查询结果</h3>
        <div class="results-header">
          <div class="result-info">
            <span v-if="klineData.length > 0">
              共找到 {{ klineData.length }} 条记录
            </span>
            <span v-else-if="isQuerying">
              查询中...
            </span>
            <span v-else>
              暂无数据
            </span>
          </div>
          <div class="result-actions">
            <button class="btn-sm" @click="exportData" :disabled="klineData.length === 0">
              导出数据
            </button>
          </div>
        </div>
        <div class="results-table">
          <table v-if="klineData.length > 0">
            <thead>
              <tr>
                <th @click="sortData('date')" class="sortable">
                  日期
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'date' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'date' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
                <th @click="sortData('open')" class="sortable">
                  开盘价
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'open' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'open' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
                <th @click="sortData('high')" class="sortable">
                  最高价
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'high' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'high' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
                <th @click="sortData('low')" class="sortable">
                  最低价
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'low' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'low' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
                <th @click="sortData('close')" class="sortable">
                  收盘价
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'close' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'close' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
                <th @click="sortData('volume')" class="sortable">
                  成交量
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'volume' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'volume' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
                <th @click="sortData('amount')" class="sortable">
                  成交额
                  <span class="sort-indicator">
                    <span v-if="sortConfig.key === 'amount' && sortConfig.direction === 'asc'" class="sort-asc">↑</span>
                    <span v-else-if="sortConfig.key === 'amount' && sortConfig.direction === 'desc'" class="sort-desc">↓</span>
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in klineData" :key="index">
                <td>{{ formatDate(item.date) }}</td>
                <td>{{ item.open.toFixed(2) }}</td>
                <td>{{ item.high.toFixed(2) }}</td>
                <td>{{ item.low.toFixed(2) }}</td>
                <td>{{ item.close.toFixed(2) }}</td>
                <td>{{ formatVolume(item.volume) }}</td>
                <td>{{ item.amount ? item.amount.toFixed(2) : '-' }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else-if="isQuerying" class="loading">
            <p>正在查询数据...</p>
          </div>
          <div v-else class="empty-state">
            <p>暂无数据，请调整查询条件</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

// 查询参数
const queryParams = ref({
  symbol: '',
  market: 'cn',
  data_type: 'day',
  start_date: '',
  end_date: ''
})

// 已下载的股票列表
const symbolsList = ref<any[]>([])

// K线数据
const klineData = ref<any[]>([])
// 原始K线数据（用于排序）
const originalKlineData = ref<any[]>([])

// 加载状态
const isQuerying = ref(false)

// 排序状态
const sortConfig = ref({
  key: 'date',
  direction: 'desc' // asc: 升序, desc: 降序
})

// 格式化日期
const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

// 格式化成交量
const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  } else {
    return volume.toString()
  }
}

// 初始化日期范围
const initDateRange = () => {
  const endDate = new Date()
  const startDate = new Date()
  startDate.setMonth(endDate.getMonth() - 6) // 默认查询最近6个月的数据
  
  queryParams.value.start_date = startDate.toISOString().split('T')[0]
  queryParams.value.end_date = endDate.toISOString().split('T')[0]
}

// 获取已下载的股票列表
const fetchSymbolsList = async () => {
  try {
    const response = await axios.get('/api/moA/data/symbols')
    symbolsList.value = response.data
  } catch (error) {
    console.error('获取已下载股票列表失败:', error)
  }
}

// 排序数据
const sortData = (key: string) => {
  // 如果点击的是当前排序的列，切换排序方向
  if (sortConfig.value.key === key) {
    sortConfig.value.direction = sortConfig.value.direction === 'asc' ? 'desc' : 'asc'
  } else {
    // 否则，设置新的排序列和默认排序方向
    sortConfig.value.key = key
    sortConfig.value.direction = 'asc'
  }
  
  // 创建数据副本，避免修改原始数据
  const sortedData = [...originalKlineData.value]
  
  // 根据关键字排序
  sortedData.sort((a, b) => {
    let aVal = a[key]
    let bVal = b[key]
    
    // 处理日期类型
    if (key === 'date') {
      aVal = new Date(aVal)
      bVal = new Date(bVal)
    }
    
    // 处理数值类型
    if (typeof aVal === 'string' && typeof bVal === 'string' && !isNaN(Number(aVal)) && !isNaN(Number(bVal))) {
      aVal = Number(aVal)
      bVal = Number(bVal)
    }
    
    // 执行比较
    if (aVal < bVal) {
      return sortConfig.value.direction === 'asc' ? -1 : 1
    }
    if (aVal > bVal) {
      return sortConfig.value.direction === 'asc' ? 1 : -1
    }
    return 0
  })
  
  // 更新显示数据
  klineData.value = sortedData
}

// 查询数据
const queryData = async () => {
  isQuerying.value = true
  klineData.value = []
  
  try {
    // 构建查询参数
    const params: any = {
      data_type: queryParams.value.data_type
    }
    
    if (queryParams.value.symbol) {
      params.symbol = queryParams.value.symbol
    }
    
    if (queryParams.value.market) {
      params.market = queryParams.value.market
    }
    
    if (queryParams.value.start_date) {
      params.start_date = queryParams.value.start_date
    }
    
    if (queryParams.value.end_date) {
      params.end_date = queryParams.value.end_date
    }
    
    // 调用API查询数据
    const response = await axios.get('/api/moA/data/kline', { params })
    originalKlineData.value = response.data
    
    // 应用排序
    sortConfig.value.key = 'date'
    sortConfig.value.direction = 'desc'
    klineData.value = [...originalKlineData.value]
  } catch (error) {
    console.error('查询数据失败:', error)
    alert('查询数据失败')
  } finally {
    isQuerying.value = false
  }
}

// 清除查询条件
const clearQuery = () => {
  queryParams.value = {
    symbol: '',
    market: 'cn',
    data_type: 'day',
    start_date: '',
    end_date: ''
  }
  klineData.value = []
  initDateRange()
}

// 导出数据
const exportData = () => {
  if (klineData.value.length === 0) return
  
  // 转换为CSV格式
  const headers = ['日期', '开盘价', '最高价', '最低价', '收盘价', '成交量', '成交额']
  const csvContent = [
    headers.join(','),
    ...klineData.value.map(item => [
      item.date,
      item.open,
      item.high,
      item.low,
      item.close,
      item.volume,
      item.amount || ''
    ].join(','))
  ].join('\n')
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `kline_data_${queryParams.value.symbol}_${queryParams.value.start_date}_${queryParams.value.end_date}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 组件挂载时初始化
onMounted(async () => {
  initDateRange()
  await fetchSymbolsList()
})
</script>

<style scoped>
.data-query-container {
  max-width: 1200px;
  margin: 0 auto;
}

.data-query-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.query-form, .query-results {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.buttons-group {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary,
.btn-sm {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
}

.btn-primary:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  background-color: #3498db;
  color: white;
}

.btn-sm:hover {
  background-color: #2980b9;
}

.btn-sm:disabled {
  background-color: #bdc3c7;
  cursor: not-allowed;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.result-info {
  font-size: 0.9rem;
  color: #666;
}

.results-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
  cursor: pointer;
  position: relative;
}

th.sortable {
  user-select: none;
}

th.sortable:hover {
  background-color: #e9ecef;
}

.sort-indicator {
  margin-left: 0.5rem;
  font-size: 0.8rem;
  color: #666;
}

.sort-asc,
.sort-desc {
  font-weight: bold;
  color: #3498db;
}

td {
  color: #333;
}

.loading, .empty-state {
  text-align: center;
  padding: 2rem;
  color: #666;
}

@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .buttons-group {
    flex-direction: column;
  }
  
  .results-header {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>