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
        <!-- 股票基本信息 -->
        <div class="stock-basic-info" v-if="stockBasicInfo && Object.keys(stockBasicInfo).length > 0">
          <h4>股票基本信息</h4>
          <div class="basic-info-grid">
            <div class="info-item">
              <span class="info-label">股票名称</span>
              <span class="info-value">{{ stockBasicInfo.name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">股票代码</span>
              <span class="info-value">{{ stockBasicInfo.symbol }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">市场类型</span>
              <span class="info-value">{{ stockBasicInfo.market }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">当前价格</span>
              <span class="info-value">{{ stockBasicInfo.currentPrice?.toFixed(2) || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">涨跌幅</span>
              <span class="info-value" :class="stockBasicInfo.changePercent >= 0 ? 'positive' : 'negative'">
                {{ stockBasicInfo.changePercent >= 0 ? '+' : '' }}{{ stockBasicInfo.changePercent?.toFixed(2) || '0' }}%
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">成交量</span>
              <span class="info-value">{{ formatVolume(stockBasicInfo.volume || 0) }}</span>
            </div>
          </div>
        </div>
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
        
        <!-- 均线设置 -->
        <div class="ma-settings" v-if="klineData.length > 0">
          <div class="ma-title">
            <h4>均线设置</h4>
          </div>
          <div class="ma-controls">
            <!-- 预设均线 -->
            <div class="preset-mas">
              <label v-for="ma in presetMAs" :key="ma.days" class="ma-checkbox">
                <input 
                  type="checkbox" 
                  v-model="ma.visible"
                  @change="updateKlineChart"
                >
                <span>{{ ma.name }}</span>
              </label>
            </div>
            
            <!-- 自定义均线 -->
            <div class="custom-ma">
              <label class="ma-checkbox">
                <input 
                  type="checkbox" 
                  v-model="customMA.visible"
                  @change="updateKlineChart"
                >
                <span>自定义均线</span>
              </label>
              <input 
                type="number" 
                v-model.number="customMA.days"
                min="1"
                max="250"
                @change="updateKlineChart"
                :disabled="!customMA.visible"
                placeholder="天数"
              >
            </div>
          </div>
        </div>
        
        <!-- K线图容器 -->
        <div class="kline-chart-container" v-if="klineData.length > 0">
          <div ref="klineChartRef" class="kline-chart"></div>
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
                <td>{{ formatAmount(item.amount) }}</td>
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
import { ref, onMounted, computed, onUnmounted, watch } from 'vue'
import axios from 'axios'
import * as echarts from 'echarts'

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

// 股票基本信息
const stockBasicInfo = ref<any>({})

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
const toggleSelect = () => {
  isSelectOpen.value = !isSelectOpen.value
}

// 选择股票
const selectSymbol = (symbol: string) => {
  queryParams.value.symbol = symbol
  isSelectOpen.value = false
}

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
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})

// 加载状态
const isQuerying = ref(false)

// 排序状态
const sortConfig = ref({
  key: 'date',
  direction: 'desc' // asc: 升序, desc: 降序
})

// K线图相关
const klineChartRef = ref<HTMLElement | null>(null)
let klineChart: echarts.ECharts | null = null

// 均线配置
interface MAConfig {
  days: number
  name: string
  color: string
  visible: boolean
}

// 预设均线配置
const presetMAs = ref<MAConfig[]>([
  { days: 5, name: '5日均线', color: '#FF6B6B', visible: true },
  { days: 10, name: '10日均线', color: '#4ECDC4', visible: true },
  { days: 20, name: '20日均线', color: '#45B7D1', visible: true },
  { days: 60, name: '60日均线', color: '#96CEB4', visible: false }
])

// 自定义均线配置
const customMA = ref<MAConfig>({
  days: 30,
  name: '自定义均线',
  color: '#FFEAA7',
  visible: false
})

// 计算均线数据
const calculateMA = (data: number[], days: number) => {
  const result: (number | null)[] = []
  if (data.length < days) {
    return result.fill(null, 0, data.length)
  }
  
  for (let i = 0; i < data.length; i++) {
    if (i < days - 1) {
      result.push(null)
    } else {
      let sum = 0
      for (let j = i - days + 1; j <= i; j++) {
        sum += data[j]
      }
      result.push(parseFloat((sum / days).toFixed(2)))
    }
  }
  return result
}

// 初始化K线图
const initKlineChart = () => {
  if (klineChartRef.value) {

    // 确保容器有正确的尺寸
    klineChartRef.value.style.width = '100%'
    klineChartRef.value.style.height = '400px'
    
    klineChart = echarts.init(klineChartRef.value)
    
    // 设置默认配置，确保图表显示
    klineChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: ['K线', '成交量', ...presetMAs.value.map(ma => ma.name), customMA.value.name]
      },
      grid: [
        {
          left: '3%',
          right: '4%',
          height: '60%'
        },
        {
          left: '3%',
          right: '4%',
          top: '70%',
          height: '20%'
        }
      ],
      xAxis: [
        {
          type: 'category',
          data: [],
          axisPointer: {
            type: 'shadow'
          }
        },
        {
          type: 'category',
          gridIndex: 1,
          data: []
        }
      ],
      yAxis: [
        {
          scale: true,
          splitArea: {
            show: true
          }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: {
            show: false
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            show: false
          }
        }
      ],
      series: [
        {
          name: 'K线',
          type: 'candlestick',
          data: [],
          itemStyle: {
            color: '#ef5350',
            color0: '#26a69a',
            borderColor: '#ef5350',
            borderColor0: '#26a69a'
          }
        },
        {
          name: '成交量',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: [],
          itemStyle: {
            color: '#ef5350'
          }
        }
      ]
    })
    
    // 监听窗口大小变化，调整图表大小
    window.addEventListener('resize', () => {
      klineChart?.resize()
    })
    
    // 如果已有数据，立即更新图表
    if (klineData.value.length > 0) {
      updateKlineChart()
    }
  }
}

// 更新K线图
const updateKlineChart = () => {

  if (!klineChart || klineData.value.length === 0) {

    return
  }
  
  try {
    // 确保数据按日期排序
    const sortedData = [...klineData.value].sort((a, b) => {
      return new Date(a.date).getTime() - new Date(b.date).getTime()
    })
    
    // 准备K线图数据
    const dates = sortedData.map(item => item.date)
    const closePrices = sortedData.map(item => parseFloat(item.close.toFixed(2)))
    
    const candlestickData = sortedData.map(item => [
      parseFloat(item.open.toFixed(2)),
      parseFloat(item.close.toFixed(2)),
      parseFloat(item.low.toFixed(2)),
      parseFloat(item.high.toFixed(2))
    ])
    
    const volumeData = sortedData.map(item => {
      const open = parseFloat(item.open.toFixed(2))
      const close = parseFloat(item.close.toFixed(2))
      return {
        value: item.volume,
        itemStyle: {
          color: close >= open ? '#ef5350' : '#26a69a'
        }
      }
    })
    
    // 计算所有可见均线数据
    const allMAs = [...presetMAs.value]
    if (customMA.value.visible) {
      allMAs.push(customMA.value)
    }
    
    // 准备series数据，先添加K线和成交量（带唯一ID）
    const series = [
      {
        id: 'kline',
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
        id: 'volume',
        name: '成交量',
        type: 'bar',
        xAxisIndex: 1,
        yAxisIndex: 1,
        data: volumeData
      }
    ]
    
    // 添加所有可见均线（带唯一ID）
    allMAs.forEach(ma => {
      if (ma.visible) {
        const maData = calculateMA(closePrices, ma.days)
        series.push({
          id: `ma_${ma.days}`, // 使用天数作为唯一ID
          name: ma.name,
          type: 'line',
          data: maData,
          smooth: true,
          lineStyle: {
            color: ma.color,
            width: 1.5
          },
          symbol: 'none',
          sampling: 'lttb',
          itemStyle: {
            color: ma.color
          },
          areaStyle: {
            opacity: 0
          }
        })
      }
    })
    
    // 准备图例数据
    const legendData = ['K线', '成交量']
    allMAs.forEach(ma => {
      if (ma.visible) {
        legendData.push(ma.name)
      }
    })
    

    
    // 更新图表配置，使用notMerge: true确保完全替换，包含完整的grid配置
    klineChart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'cross'
        }
      },
      legend: {
        data: legendData
      },
      grid: [
        {
          left: '3%',
          right: '4%',
          height: '60%'
        },
        {
          left: '3%',
          right: '4%',
          top: '70%',
          height: '20%'
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
        },
        {
          type: 'category',
          gridIndex: 1,
          data: dates,
          axisLabel: {
            formatter: (value: string) => {
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
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: {
            show: false
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            show: false
          }
        }
      ],
      dataZoom: [
        {
          type: 'inside',
          xAxisIndex: [0, 1],
          start: Math.max(0, 100 - (30 / dates.length) * 100),
          end: 100
        },
        {
          show: true,
          xAxisIndex: [0, 1],
          type: 'slider',
          bottom: '5%',
          start: Math.max(0, 100 - (30 / dates.length) * 100),
          end: 100
        }
      ],
      series: series
    }, true) // 使用完全替换，确保只显示当前可见的系列
    

  } catch (error) {
    console.error('更新K线图出错:', error)
    // 简化错误处理，移除动态import
    console.error(error)
  }
}

// 监听K线数据变化，更新图表
watch(
  () => klineData.value,
  (newData) => {
    if (newData.length > 0) {
      updateKlineChart()
    }
  },
  { deep: true }
)

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

// 格式化成交额
const formatAmount = (amount: number) => {
  if (!amount) return '-'
  if (amount >= 100000000) {
    return (amount / 100000000).toFixed(2) + '亿'
  } else if (amount >= 10000) {
    return (amount / 10000).toFixed(2) + '万'
  } else {
    return amount.toFixed(2)
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

// 获取股票基本信息
const fetchStockBasicInfo = async (symbol: string, market: string) => {
  try {
    // 调用API获取股票基本信息
    const response = await axios.get('/api/moA/data/stock_basic', {
      params: {
        symbol,
        market
      }
    })
    stockBasicInfo.value = response.data
  } catch (error) {
    console.error('获取股票基本信息失败:', error)
    // 如果获取失败，清空基本信息
    stockBasicInfo.value = {}
  }
}

// 查询数据
const queryData = async () => {
  isQuerying.value = true
  klineData.value = []
  stockBasicInfo.value = {}
  
  try {
    // 销毁现有图表实例，确保切换股票时能重新初始化
    if (klineChart) {

      klineChart.dispose()
      klineChart = null
    }
    
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
    
    // 获取股票基本信息
    if (queryParams.value.symbol) {
      await fetchStockBasicInfo(queryParams.value.symbol, queryParams.value.market)
    }
    

    
    // 重新初始化K线图
    setTimeout(() => {
      initKlineChart()
    }, 100)
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
  // 初始化K线图
  setTimeout(() => {
    initKlineChart()
  }, 100)
})

// 组件卸载时释放资源
onUnmounted(() => {
  // 销毁图表实例
  klineChart?.dispose()
  // 移除事件监听器
  window.removeEventListener('resize', () => {
    klineChart?.resize()
  })
})
</script>

<style scoped>
.data-query-container {
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
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

/* 均线设置样式 */
.ma-settings {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #eee;
}

.ma-title h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1rem;
  color: #555;
}

.ma-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  align-items: center;
}

.preset-mas {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.custom-ma {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ma-checkbox {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  cursor: pointer;
  font-size: 0.9rem;
  color: #333;
  user-select: none;
}

.ma-checkbox input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.custom-ma input[type="number"] {
  width: 80px;
  padding: 0.3rem 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.custom-ma input[type="number"]:disabled {
  background-color: #f0f0f0;
  cursor: not-allowed;
}

/* K线图样式 */
.kline-chart-container {
  margin: 1rem 0;
  border: 1px solid #eee;
  border-radius: 4px;
  background-color: #fafafa;
}

.kline-chart {
  width: 100%;
  height: 400px;
}

@media (max-width: 768px) {
  .kline-chart {
    height: 300px;
  }
  
  .ma-controls {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .preset-mas {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .custom-ma {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
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

/* 搜索选择框样式 */
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
  border-bottom: 1px solid #ddd;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.select-arrow {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #666;
  transition: transform 0.2s;
  pointer-events: none;
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

@media (max-width: 480px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

/* 股票基本信息样式 */
.stock-basic-info {
  margin: 1rem 0;
  padding: 1rem;
  background-color: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #eee;
}

.stock-basic-info h4 {
  margin: 0 0 1rem 0;
  font-size: 1rem;
  color: #555;
}

.basic-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.875rem;
  color: #666;
  font-weight: 500;
}

.info-value {
  font-size: 1rem;
  color: #333;
  font-weight: 600;
}

.info-value.positive {
  color: #e74c3c;
}

.info-value.negative {
  color: #27ae60;
}
</style>