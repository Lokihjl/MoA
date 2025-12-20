<template>
  <div class="resistance-support-container">
    <h2>阻力位支撑位分析</h2>
    <div class="resistance-support-content">
      <div class="query-form">
        <h3>分析参数</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="symbol">股票代码</label>
            <div class="searchable-select">
              <div class="select-header" @click="toggleSelect($event)">
                <input 
                  type="text" 
                  class="search-input" 
                  v-model="symbolSearchText" 
                  placeholder="搜索股票代码或名称..."
                  @focus="openSelect"
                  @click="$event.stopPropagation(); openSelect()"
                />
                <span 
                  class="select-arrow" 
                  :class="{ 'active': isSelectOpen }"
                  @click="toggleSelect($event)"
                >▼</span>
              </div>
              <div 
                class="select-dropdown" 
                :class="{ 'open': isSelectOpen }"
              >
                <div class="select-options">
                  <div 
                    v-for="item in filteredSymbols" 
                    :key="item.symbol"
                    class="select-option"
                    :class="{ 'selected': queryParams.symbol === item.symbol }"
                    @click="selectSymbol(item.symbol)"
                  >
                    {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                  </div>
                </div>
              </div>
              <!-- 隐藏的select元素，用于表单提交 -->
              <select 
                id="symbol" 
                v-model="queryParams.symbol"
                class="hidden-select"
              >
                <option value="">请选择股票代码</option>
                <option 
                  v-for="item in symbolsList" 
                  :key="item.symbol" 
                  :value="item.symbol"
                >
                  {{ item.symbol }}
                </option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label for="market">市场类型</label>
            <select id="market" v-model="queryParams.market" disabled>
              <option value="cn">A股</option>
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
          <button class="btn-primary" @click="analyzeResistanceSupport" :disabled="isAnalyzing">
            {{ isAnalyzing ? '分析中...' : '分析阻力位支撑位' }}
          </button>
          <button class="btn-secondary" @click="clearQuery">
            清除条件
          </button>
        </div>
      </div>
      
      <div class="analysis-results">
        <h3>分析结果</h3>
        <!-- K线图容器 -->
        <div class="kline-chart-container">
          <div class="chart-title">K线图与阻力位支撑位</div>
          <div ref="klineChartRef" class="chart-content"></div>
        </div>
        
        <!-- 阻力位支撑位列表 -->
        <div class="levels-list">
          <h4>阻力位与支撑位</h4>
          <div class="levels-grid">
            <div class="level-card resistance">
              <h5>阻力位</h5>
              <ul>
                <li v-for="(level, index) in resistanceLevels" :key="'resistance-' + index">
                  <span class="level-price">{{ level.toFixed(2) }}</span>
                </li>
                <li v-if="resistanceLevels.length === 0" class="no-data">
                  暂无阻力位数据
                </li>
              </ul>
            </div>
            <div class="level-card support">
              <h5>支撑位</h5>
              <ul>
                <li v-for="(level, index) in supportLevels" :key="'support-' + index">
                  <span class="level-price">{{ level.toFixed(2) }}</span>
                </li>
                <li v-if="supportLevels.length === 0" class="no-data">
                  暂无支撑位数据
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- 数据表格 -->
        <div class="data-table">
          <h4>K线数据</h4>
          <div class="table-container">
            <table>
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
                <tr v-for="(item, index) in klineData" :key="index">
                  <td>{{ formatDate(item.date) }}</td>
                  <td>{{ item.open.toFixed(2) }}</td>
                  <td>{{ item.high.toFixed(2) }}</td>
                  <td>{{ item.low.toFixed(2) }}</td>
                  <td>{{ item.close.toFixed(2) }}</td>
                  <td>{{ formatVolume(item.volume) }}</td>
                </tr>
                <tr v-if="klineData.length === 0 && !isAnalyzing" class="no-data">
                  <td colspan="6">暂无数据，请调整分析参数</td>
                </tr>
                <tr v-if="isAnalyzing" class="loading">
                  <td colspan="6">正在分析数据...</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

// 查询参数
const queryParams = ref({
  symbol: '',
  market: 'cn',
  start_date: '',
  end_date: ''
})

// 已下载的股票列表
const symbolsList = ref<any[]>([])

// K线数据
const klineData = ref<any[]>([])

// 阻力位和支撑位
const resistanceLevels = ref<number[]>([])
const supportLevels = ref<number[]>([])

// 股票代码搜索文本
const symbolSearchText = ref('')

// 股票名称映射表
const stockNameMap = ref<Record<string, string>>({
  'sh600000': '浦发银行',
  'sh600036': '招商银行',
  'sh600519': '贵州茅台',
  'sh601398': '工商银行',
  'sh601857': '中国石油',
  'sh601118': '海南橡胶',
  'sz000001': '平安银行',
  'sz000002': '万科A',
  'sz000858': '五粮液',
  'sz002415': '海康威视',
  'sz300750': '宁德时代'
})

// 过滤后的股票列表
const filteredSymbols = computed(() => {
  if (!symbolSearchText.value) {
    return symbolsList.value
  }
  
  const searchText = symbolSearchText.value.toLowerCase()
  return symbolsList.value.filter(item => {
    // 搜索股票代码
    if (item.symbol.toLowerCase().includes(searchText)) {
      return true
    }
    
    // 搜索股票名称
    const stockName = stockNameMap.value[item.symbol]?.toLowerCase() || ''
    if (stockName.includes(searchText)) {
      return true
    }
    
    return false
  })
})

// 下拉框显示状态
const isSelectOpen = ref(false)

// 打开下拉框
const openSelect = () => {
  isSelectOpen.value = true
}

// 切换下拉框显示状态
const toggleSelect = (event?: MouseEvent) => {
  if (event) {
    event.stopPropagation()
  }
  isSelectOpen.value = !isSelectOpen.value
}

// 选择股票
const selectSymbol = (symbol: string) => {
  queryParams.value.symbol = symbol
  isSelectOpen.value = false
}

// 分析状态
const isAnalyzing = ref(false)

// K线图相关
const klineChartRef = ref<HTMLElement | null>(null)
let klineChart: echarts.ECharts | null = null

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  const selectElement = document.querySelector('.searchable-select')
  const target = event.target as HTMLElement
  
  // 检查点击目标是否在搜索选择框内部，或者是箭头元素
  if (selectElement && !selectElement.contains(target)) {
    isSelectOpen.value = false
  }
}

// 监听点击外部事件
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  initDateRange()
  fetchSymbolsList()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  // 销毁图表实例
  if (klineChart) {
    klineChart.dispose()
    klineChart = null
  }
})

// 初始化日期范围
const initDateRange = () => {
  // 设置默认日期范围：过去3个月
  const endDate = new Date()
  const startDate = new Date()
  startDate.setMonth(startDate.getMonth() - 3)
  
  // 格式化日期为YYYY-MM-DD
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  queryParams.value.start_date = formatDate(startDate)
  queryParams.value.end_date = formatDate(endDate)
}

// 获取已下载的股票列表
const fetchSymbolsList = async () => {
  try {
    const response = await axios.get('/api/moA/data/download/symbols')
    symbolsList.value = response.data
  } catch (error) {
    console.error('获取已下载股票列表失败:', error)
    // 如果获取失败，使用默认股票列表
    symbolsList.value = [
      { symbol: 'sh600000', market: 'cn' },
      { symbol: 'sh600036', market: 'cn' },
      { symbol: 'sh600519', market: 'cn' },
      { symbol: 'sz000001', market: 'cn' },
      { symbol: 'sz000858', market: 'cn' }
    ]
  }
}

// 清除查询条件
const clearQuery = () => {
  queryParams.value = {
    symbol: '',
    market: 'cn',
    start_date: '',
    end_date: ''
  }
  klineData.value = []
  resistanceLevels.value = []
  supportLevels.value = []
  initDateRange()
}

// 分析阻力位和支撑位
const analyzeResistanceSupport = async () => {
  if (!queryParams.value.symbol) {
    alert('请选择股票代码')
    return
  }
  
  isAnalyzing.value = true
  
  try {
    // 调用阻力位支撑位API获取数据
    const response = await axios.get('/api/moA/data/resistance-support', {
      params: {
        symbol: queryParams.value.symbol,
        market: queryParams.value.market,
        data_type: 'day',
        start_date: queryParams.value.start_date,
        end_date: queryParams.value.end_date
      }
    })
    
    klineData.value = response.data.kline_data
    resistanceLevels.value = response.data.resistance_levels
    supportLevels.value = response.data.support_levels
    
    // 绘制K线图
    initKlineChart()
  } catch (error) {
    console.error('分析阻力位支撑位失败:', error)
    alert('分析失败，请检查网络连接或参数设置')
  } finally {
    isAnalyzing.value = false
  }
}

// 初始化K线图
const initKlineChart = () => {
  if (!klineChartRef.value || klineData.value.length === 0) {
    return
  }
  
  // 确保容器有正确的尺寸
  klineChartRef.value.style.width = '100%'
  klineChartRef.value.style.height = '400px'
  
  // 销毁现有图表实例
  if (klineChart) {
    klineChart.dispose()
  }
  
  // 创建新的图表实例
  klineChart = echarts.init(klineChartRef.value)
  
  // 准备K线图数据
  const sortedData = [...klineData.value].sort((a, b) => {
    return new Date(a.date).getTime() - new Date(b.date).getTime()
  })
  
  const dates = sortedData.map(item => item.date)
  const candlestickData = sortedData.map(item => [
    parseFloat(item.open.toFixed(2)),
    parseFloat(item.close.toFixed(2)),
    parseFloat(item.low.toFixed(2)),
    parseFloat(item.high.toFixed(2))
  ])
  
  // 准备图表配置
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', '阻力位', '支撑位']
    },
    grid: [
      {
        left: '3%',
        right: '4%',
        height: '60%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: dates,
        axisPointer: {
          type: 'shadow'
        },
        axisLabel: {
          formatter: (value: string) => {
            // 格式化日期显示
            const date = new Date(value)
            return `${date.getMonth() + 1}/${date.getDate()}`
          }
        }
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: {
          show: true
        }
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: candlestickData,
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: '阻力位',
        type: 'line',
        data: resistanceLevels.value.map(level => [dates[0], dates[dates.length - 1]].map(date => [date, level])).flat(),
        lineStyle: {
          color: '#27ae60',
          width: 2,
          type: 'dashed'
        },
        symbol: 'none',
        z: 10
      },
      {
        name: '支撑位',
        type: 'line',
        data: supportLevels.value.map(level => [dates[0], dates[dates.length - 1]].map(date => [date, level])).flat(),
        lineStyle: {
          color: '#e74c3c',
          width: 2,
          type: 'dashed'
        },
        symbol: 'none',
        z: 10
      }
    ]
  }
  
  // 设置图表配置
  klineChart.setOption(option)
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    klineChart?.resize()
  })
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
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
</script>

<style scoped>
.resistance-support-container {
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.resistance-support-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.query-form, .analysis-results {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr;
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
.btn-secondary {
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

/* 搜索下拉框样式 */
.searchable-select {
  position: relative;
  width: 100%;
}

.select-header {
  display: flex;
  align-items: center;
  position: relative;
}

.search-input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.select-arrow {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
  transition: transform 0.2s;
}

.select-arrow.active {
  transform: translateY(-50%) rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  display: none;
  overflow-y: auto;
  max-height: 300px;
}

.select-dropdown.open {
  display: block;
}

.select-options {
  padding: 0.5rem 0;
}

.select-option {
  padding: 0.75rem 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.select-option:hover {
  background-color: #f0f8ff;
}

.select-option.selected {
  background-color: #e3f2fd;
  color: #1976d2;
  font-weight: 600;
}

.hidden-select {
  display: none;
}

/* K线图容器样式 */
.kline-chart-container {
  margin-bottom: 2rem;
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.chart-title {
  font-weight: 600;
  margin-bottom: 1rem;
  color: #333;
  text-align: center;
}

.chart-content {
  height: 400px;
  width: 100%;
  background-color: white;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

/* 阻力位支撑位列表样式 */
.levels-list {
  margin-bottom: 2rem;
}

.levels-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.level-card {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.level-card h5 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
  text-align: center;
}

.level-card.resistance h5 {
  color: #27ae60;
}

.level-card.support h5 {
  color: #e74c3c;
}

.level-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.level-card li {
  background-color: white;
  padding: 0.75rem;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.level-price {
  font-weight: 600;
  font-size: 1.1rem;
}

.level-card.resistance .level-price {
  color: #27ae60;
}

.level-card.support .level-price {
  color: #e74c3c;
}

.no-data {
  color: #95a5a6;
  font-style: italic;
}

.loading {
  text-align: center;
  color: #3498db;
  font-style: italic;
}

/* 数据表格样式 */
.data-table {
  margin-top: 2rem;
}

.table-container {
  overflow-x: auto;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.75rem;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
  text-align: right;
}

td {
  text-align: right;
}

/* 日期列左对齐 */
th:first-child, td:first-child {
  text-align: left;
}

tr:hover {
  background-color: #f5f7fa;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .levels-grid {
    grid-template-columns: 1fr;
  }
  
  .buttons-group {
    flex-direction: column;
  }
  
  .chart-content {
    height: 300px;
  }
}
</style>
