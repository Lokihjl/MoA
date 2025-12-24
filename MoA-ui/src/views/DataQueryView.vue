<template>
  <div class="data-query-container">
    <h2>数据查询</h2>
    <div class="data-query-content">
      <div class="query-form">
        <h3>查询条件</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="symbol">股票代码</label>
            <div class="searchable-select">
              <div class="select-header">
                <input
                  type="text"
                  class="search-input"
                  v-model="symbolSearchText"
                  placeholder="搜索股票代码或名称..."
                  @focus="openSelect"
                  @click="openSelect"
                />
                <span
                  class="select-arrow"
                  :class="{ 'active': isSelectOpen }"
                  @click="toggleSelect"
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
            </div>
          </div>
          <div class="form-group">
            <label for="start-date">开始日期</label>
            <input
              type="date"
              id="start-date"
              v-model="queryParams.startDate"
            />
          </div>
          <div class="form-group">
            <label for="end-date">结束日期</label>
            <input
              type="date"
              id="end-date"
              v-model="queryParams.endDate"
            />
          </div>
          <div class="form-group">
            <label for="period">周期</label>
            <select id="period" v-model="queryParams.period">
              <option value="day">日线</option>
              <option value="week">周线</option>
              <option value="month">月线</option>
            </select>
          </div>
          <div class="form-group full-width">
            <button class="query-btn" @click="handleQuery">查询</button>
            <button class="export-btn" @click="handleExport" :disabled="!klineData.length">导出数据</button>
          </div>
        </div>
      </div>

      <!-- 股票基本信息 -->
      <div class="stock-info" v-if="stockBasicInfo.symbol">
        <h3>基本信息</h3>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">股票代码</span>
            <span class="info-value">{{ stockBasicInfo.symbol }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">股票名称</span>
            <span class="info-value">{{ stockBasicInfo.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">当前价格</span>
            <span class="info-value">¥{{ stockBasicInfo.currentPrice?.toFixed(2) || '-' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">涨跌幅</span>
            <span class="info-value" :class="{ 'rise': stockBasicInfo.changePercent > 0, 'fall': stockBasicInfo.changePercent < 0 }">
              {{ stockBasicInfo.changePercent > 0 ? '+' : '' }}{{ stockBasicInfo.changePercent?.toFixed(2) || 0 }}%
            </span>
          </div>
          <div class="info-item">
            <span class="info-label">成交量</span>
            <span class="info-value">{{ formatVolume(stockBasicInfo.volume || 0) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">成交额</span>
            <span class="info-value">{{ formatAmount(stockBasicInfo.amount || 0) }}</span>
          </div>
        </div>
      </div>

      <!-- K线图 -->
      <div class="kline-section">
        <h3>K线图</h3>
        <div class="kline-controls">
          <div class="ma-settings">
            <label>均线设置:</label>
            <div class="ma-inputs">
              <input type="number" v-model.number="maParams.ma5" min="1" max="100" placeholder="MA5">
              <input type="number" v-model.number="maParams.ma10" min="1" max="100" placeholder="MA10">
              <input type="number" v-model.number="maParams.ma20" min="1" max="100" placeholder="MA20">
              <input type="number" v-model.number="maParams.ma60" min="1" max="200" placeholder="MA60">
              <input type="number" v-model.number="maParams.ma120" min="1" max="200" placeholder="MA120">
            </div>
          </div>
          <button class="apply-ma-btn" @click="updateKlineChart">应用均线</button>
        </div>
        <div id="kline-chart" ref="klineChartRef"></div>
      </div>

      <!-- 原理查询 -->
      <div class="theory-query" v-if="klineData.length">
        <h3>原理查询</h3>
        <div class="theory-form">
          <div class="theory-inputs">
            <input type="text" v-model="theoryQuery" placeholder="输入查询条件..." />
            <button @click="handleTheoryQuery">查询</button>
          </div>
          <div class="theory-result" v-if="theoryResult">
            <h4>查询结果</h4>
            <pre>{{ theoryResult }}</pre>
          </div>
        </div>
      </div>

      <!-- 查询结果表格 -->
      <div class="result-table-container" v-if="klineData.length">
        <h3>查询结果</h3>
        <div class="table-wrapper">
          <table class="result-table">
            <thead>
              <tr>
                <th>日期</th>
                <th>开盘</th>
                <th>最高</th>
                <th>最低</th>
                <th>收盘</th>
                <th>成交量</th>
                <th>成交额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in klineData" :key="index">
                <td>{{ formatDate(item.date) }}</td>
                <td>¥{{ item.open.toFixed(2) }}</td>
                <td>¥{{ item.high.toFixed(2) }}</td>
                <td>¥{{ item.low.toFixed(2) }}</td>
                <td>¥{{ item.close.toFixed(2) }}</td>
                <td>{{ formatVolume(item.volume) }}</td>
                <td>{{ formatAmount(item.amount) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import { apiService } from '../services/api'
import * as echarts from 'echarts'

// 查询参数
interface QueryParams {
  symbol: string
  startDate: string
  endDate: string
  period: 'day' | 'week' | 'month'
}

// 股票数据接口
interface KlineData {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
  amount: number
}

// 股票基本信息接口
interface StockBasicInfo {
  symbol: string
  name: string
  currentPrice: number
  changePercent: number
  volume: number
  amount: number
}

// 均线参数
interface MaParams {
  ma5: number
  ma10: number
  ma20: number
  ma60: number
  ma120: number
}

// 响应式数据
const queryParams = ref<QueryParams>({
  symbol: '',
  startDate: '',
  endDate: '',
  period: 'day'
})

const symbolSearchText = ref('')
const isSelectOpen = ref(false)
const klineData = ref<KlineData[]>([])
const stockBasicInfo = ref<StockBasicInfo>({ symbol: '', name: '', currentPrice: 0, changePercent: 0, volume: 0, amount: 0 })
const stockNameMap = ref<Record<string, string>>({})
const availableSymbols = ref<{ symbol: string; market: string }[]>([])
const theoryQuery = ref('')
const theoryResult = ref('')
const maParams = ref<MaParams>({ ma5: 5, ma10: 10, ma20: 20, ma60: 60, ma120: 120 })

// K线图相关
const klineChartRef = ref<HTMLElement | null>(null)
let klineChart: echarts.ECharts | null = null

// 计算属性：过滤后的股票列表
const filteredSymbols = computed(() => {
  if (!symbolSearchText.value) {
    return availableSymbols.value.slice(0, 20)
  }
  const searchText = symbolSearchText.value.toLowerCase()
  return availableSymbols.value.filter(item => 
    item.symbol.toLowerCase().includes(searchText) ||
    (stockNameMap.value[item.symbol] && stockNameMap.value[item.symbol].toLowerCase().includes(searchText))
  ).slice(0, 20)
})

// 方法：打开选择框
const openSelect = () => {
  isSelectOpen.value = true
}

// 方法：关闭选择框
const closeSelect = () => {
  isSelectOpen.value = false
}

// 方法：切换选择框
const toggleSelect = () => {
  isSelectOpen.value = !isSelectOpen.value
}

// 方法：选择股票
const selectSymbol = (symbol: string) => {
  queryParams.value.symbol = symbol
  symbolSearchText.value = symbol
  closeSelect()
}

// 方法：格式化日期
const formatDate = (dateStr: string) => {
  return dateStr.replace(/-/g, '/')
}

// 方法：格式化成交量
const formatVolume = (volume: number) => {
  if (volume >= 100000000) {
    return (volume / 100000000).toFixed(2) + '亿'
  } else if (volume >= 10000) {
    return (volume / 10000).toFixed(2) + '万'
  }
  return volume.toString()
}

// 方法：格式化成交额
const formatAmount = (amount: number) => {
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  }
  return amount.toFixed(2)
}

// 方法：处理查询
const handleQuery = async () => {
  if (!queryParams.value.symbol) {
    alert('请选择股票代码')
    return
  }
  
  try {
    console.log('开始查询K线数据，参数：', {
      symbol: queryParams.value.symbol,
      start_date: queryParams.value.startDate,
      end_date: queryParams.value.endDate,
      data_type: queryParams.value.period
    })
    
    // 查询K线数据
    const data = await apiService.get<KlineData[]>('/data/kline', {
      symbol: queryParams.value.symbol,
      start_date: queryParams.value.startDate,
      end_date: queryParams.value.endDate,
      data_type: queryParams.value.period
    })
    
    console.log('K线数据查询结果：', data)
    console.log('K线数据长度：', data.length)
    klineData.value = data
    
    // 查询股票基本信息
    await fetchStockBasicInfo()
    
    // 更新K线图
    updateKlineChart()
    
    console.log('查询完成，数据已更新到图表')
  } catch (error) {
    console.error('查询失败:', error)
    alert('查询失败，请检查输入参数')
  }
}

// 方法：获取股票基本信息
const fetchStockBasicInfo = async () => {
  if (!queryParams.value.symbol) return
  
  try {
    console.log('开始查询股票基本信息，参数：', {
      symbol: queryParams.value.symbol
    })
    
    const data = await apiService.get<StockBasicInfo>('/data/stock_basic', {
      symbol: queryParams.value.symbol
    })
    
    console.log('股票基本信息查询结果：', data)
    stockBasicInfo.value = data
  } catch (error) {
    console.error('获取股票信息失败:', error)
    // 即使获取股票基本信息失败，也继续执行后续操作
  }
}

// 方法：初始化K线图
const initKlineChart = () => {
  if (klineChartRef.value) {
    klineChart = echarts.init(klineChartRef.value)
    window.addEventListener('resize', () => {
      klineChart?.resize()
    })
  }
}

// 方法：更新K线图
const updateKlineChart = () => {
  if (!klineData.value.length || !klineChart) return
  
  // 准备K线数据并按日期升序排序（确保最新数据在最右边）
  const chartData = [...klineData.value]
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
    .map(item => [
      item.date,
      item.open,
      item.close,
      item.low,
      item.high,
      item.volume
    ])
  
  // 计算均线
  const ma5Data = calculateMA(chartData, maParams.value.ma5)
  const ma10Data = calculateMA(chartData, maParams.value.ma10)
  const ma20Data = calculateMA(chartData, maParams.value.ma20)
  const ma60Data = calculateMA(chartData, maParams.value.ma60)
  const ma120Data = calculateMA(chartData, maParams.value.ma120)
  
  // 调试信息：查看数据长度和部分均线数据
  console.log('K线数据长度:', chartData.length)
  console.log('MA5数据:', ma5Data.slice(-5))
  console.log('MA10数据:', ma10Data.slice(-5))
  console.log('MA20数据:', ma20Data.slice(-5))
  console.log('MA60数据:', ma60Data.slice(-5))
  console.log('MA120数据:', ma120Data.slice(-5))
  console.log('均线参数:', maParams.value)
  
  // 配置K线图
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: ['K线', `MA${maParams.value.ma5}`, `MA${maParams.value.ma10}`, `MA${maParams.value.ma20}`, `MA${maParams.value.ma60}`, `MA${maParams.value.ma120}`]
    },
    grid: [
      {
        left: '10%',
        right: '10%',
        height: '60%'
      },
      {
        left: '10%',
        right: '10%',
        top: '75%',
        height: '15%'
      }
    ],
    xAxis: [
      {
        type: 'category',
        data: chartData.map(item => item[0]),
        boundaryGap: false,
        axisLine: { onZero: false },
        splitLine: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      },
      {
        type: 'category',
        gridIndex: 1,
        data: chartData.map(item => item[0]),
        boundaryGap: false,
        axisLine: { onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        min: 'dataMin',
        max: 'dataMax'
      }
    ],
    yAxis: [
      {
        scale: true,
        splitArea: { show: true }
      },
      {
        scale: true,
        gridIndex: 1,
        splitNumber: 2,
        axisLabel: { show: false },
        axisLine: { show: false },
        axisTick: { show: false },
        splitLine: { show: false }
      }
    ],
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: [0, 1],
        start: 50,
        end: 100
      },
      {
        show: true,
        xAxisIndex: [0, 1],
        type: 'slider',
        bottom: '5%',
        start: 50,
        end: 100
      }
    ],
    series: [
      {
        name: 'K线',
        type: 'candlestick',
        data: chartData.map(item => [item[1], item[2], item[3], item[4]]),
        itemStyle: {
          color: '#ef5350',
          color0: '#26a69a',
          borderColor: '#ef5350',
          borderColor0: '#26a69a'
        }
      },
      {
        name: `MA${maParams.value.ma5}`,
        type: 'line',
        data: ma5Data,
        smooth: true,
        lineStyle: { opacity: 0.5 },
        symbol: 'none'
      },
      {
        name: `MA${maParams.value.ma10}`,
        type: 'line',
        data: ma10Data,
        smooth: true,
        lineStyle: { opacity: 0.5 },
        symbol: 'none'
      },
      {
        name: `MA${maParams.value.ma20}`,
        type: 'line',
        data: ma20Data,
        smooth: true,
        lineStyle: { opacity: 0.5 },
        symbol: 'none'
      },
      {
        name: `MA${maParams.value.ma60}`,
        type: 'line',
        data: ma60Data,
        smooth: true,
        lineStyle: { opacity: 0.5 },
        symbol: 'none'
      },
      {
        name: `MA${maParams.value.ma120}`,
        type: 'line',
        data: ma120Data,
        smooth: true,
        lineStyle: { opacity: 0.5 },
        symbol: 'none'
      },
      {
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: chartData.map(item => item[5]),
        itemStyle: {
          color: function(params: any) {
            const dataIndex = params.dataIndex
            const o = chartData[dataIndex][1]
            const c = chartData[dataIndex][2]
            return o > c ? '#26a69a' : '#ef5350'
          }
        }
      }
    ]
  }
  
  klineChart.setOption(option)
}

// 方法：计算均线
const calculateMA = (data: any[], dayCount: number) => {
  const result = []
  for (let i = 0, len = data.length; i < len; i++) {
    if (i < dayCount - 1) {
      result.push(null) // 使用null表示缺失数据，ECharts会更好地处理
      continue
    }
    let sum = 0
    for (let j = 0; j < dayCount; j++) {
      sum += data[i - j][2]
    }
    result.push(parseFloat((sum / dayCount).toFixed(2))) // 返回数字类型而不是字符串
  }
  return result
}

// 方法：处理原理查询
const handleTheoryQuery = async () => {
  if (!queryParams.value.symbol || !theoryQuery.value) {
    alert('请选择股票并输入查询条件')
    return
  }
  
  try {
    const data = await apiService.get<string>('/data/theory/query', {
      symbol: queryParams.value.symbol,
      query: theoryQuery.value,
      start_date: queryParams.value.startDate,
      end_date: queryParams.value.endDate
    })
    theoryResult.value = data
  } catch (error) {
    console.error('原理查询失败:', error)
    alert('原理查询失败，请稍后重试')
  }
}

// 方法：处理数据导出
const handleExport = () => {
  if (!klineData.value.length) return
  
  // 转换为CSV格式
  const headers = ['日期', '开盘', '最高', '最低', '收盘', '成交量', '成交额']
  const csvContent = [
    headers.join(','),
    ...klineData.value.map(item => [
      item.date,
      item.open,
      item.high,
      item.low,
      item.close,
      item.volume,
      item.amount
    ].join(','))
  ].join('\n')
  
  // 创建下载链接
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `${queryParams.value.symbol}_${queryParams.value.period}_${queryParams.value.startDate}_${queryParams.value.endDate}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 方法：获取所有可用股票
const fetchAvailableSymbols = async () => {
  try {
    const data = await apiService.get<any[]>('/data/download/symbols')
    availableSymbols.value = data.map(item => ({
      symbol: item.symbol,
      market: item.symbol.startsWith('sh') ? '沪市' : item.symbol.startsWith('sz') ? '深市' : '其他'
    }))
    
    // 为简单起见，这里使用股票代码作为名称
    data.forEach(item => {
      stockNameMap.value[item.symbol] = item.name || item.symbol
    })
  } catch (error) {
    console.error('获取股票列表失败:', error)
  }
}

// 生命周期钩子
onMounted(() => {
  // 设置默认日期范围（延长到1年以支持MA120计算）
  const today = new Date()
  const oneYearAgo = new Date()
  oneYearAgo.setFullYear(today.getFullYear() - 1)
  
  queryParams.value.startDate = oneYearAgo.toISOString().split('T')[0]
  queryParams.value.endDate = today.toISOString().split('T')[0]
  
  // 初始化K线图
  initKlineChart()
  
  // 获取可用股票列表
  fetchAvailableSymbols()
  
  // 点击外部关闭选择框
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement
    if (!target.closest('.searchable-select')) {
      closeSelect()
    }
  })
})

onUnmounted(() => {
  // 销毁K线图
  klineChart?.dispose()
  window.removeEventListener('resize', () => {
    klineChart?.resize()
  })
})
</script>

<style scoped>
.data-query-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.data-query-content {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.query-form {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

.form-group input,
.form-group select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-group.full-width {
  grid-column: 1 / -1;
  display: flex;
  gap: 12px;
  flex-direction: row;
}

.query-btn {
  padding: 10px 24px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.query-btn:hover {
  background-color: #66b1ff;
}

.export-btn {
  padding: 10px 24px;
  background-color: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.export-btn:hover:not(:disabled) {
  background-color: #85ce61;
}

.export-btn:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
}

/* 搜索选择框样式 */
.searchable-select {
  position: relative;
}

.select-header {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.select-arrow {
  padding: 0 12px;
  cursor: pointer;
  color: #909399;
  transition: transform 0.3s;
}

.select-arrow.active {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  background-color: white;
  z-index: 100;
  display: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.select-dropdown.open {
  display: block;
}

.select-options {
  padding: 8px 0;
}

.select-option {
  padding: 8px 16px;
  cursor: pointer;
  font-size: 14px;
}

.select-option:hover {
  background-color: #f5f7fa;
}

.select-option.selected {
  background-color: #ecf5ff;
  color: #409eff;
}

/* 股票信息样式 */
.stock-info {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.info-value {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.info-value.rise {
  color: #f56c6c;
}

.info-value.fall {
  color: #67c23a;
}

/* K线图样式 */
.kline-section {
  margin-bottom: 30px;
}

.kline-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.ma-settings {
  display: flex;
  align-items: center;
  gap: 12px;
}

.ma-inputs {
  display: flex;
  gap: 8px;
}

.ma-inputs input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  text-align: center;
}

.apply-ma-btn {
  padding: 6px 16px;
  background-color: #e6a23c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.apply-ma-btn:hover {
  background-color: #ebb563;
}

#kline-chart {
  width: 100%;
  height: 400px;
  border: 1px solid #eee;
  border-radius: 4px;
}

/* 原理查询样式 */
.theory-query {
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.theory-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.theory-inputs {
  display: flex;
  gap: 12px;
  align-items: end;
}

.theory-inputs input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.theory-inputs button {
  padding: 8px 24px;
  background-color: #909399;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.theory-inputs button:hover {
  background-color: #a6a9ad;
}

.theory-result {
  padding: 16px;
  background-color: white;
  border-radius: 4px;
  border: 1px solid #ddd;
  max-height: 300px;
  overflow-y: auto;
}

.theory-result h4 {
  margin-top: 0;
  margin-bottom: 12px;
  color: #333;
}

.theory-result pre {
  margin: 0;
  font-family: monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #666;
}

/* 结果表格样式 */
.result-table-container {
  margin-top: 30px;
}

.table-wrapper {
  overflow-x: auto;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.result-table th,
.result-table td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid #eee;
}

.result-table th {
  background-color: #f5f7fa;
  font-weight: bold;
  color: #333;
  text-align: center;
}

.result-table td:first-child {
  text-align: center;
}
</style>