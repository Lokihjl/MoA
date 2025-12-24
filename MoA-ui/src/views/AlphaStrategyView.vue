<template>
  <div class="alpha-strategy-container">
    <h2>Alpha策略分析</h2>
    
    <div class="alpha-strategy-content">
      <div class="params-section">
        <h3>策略参数设置</h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="initialCash">初始资金</label>
            <input 
              type="number" 
              id="initialCash" 
              v-model.number="store.params.initialCash"
              min="1000000" 
              step="1000000"
            />
          </div>
          
          <div class="form-group">
            <label for="nFolds">回测年数</label>
            <input 
              type="number" 
              id="nFolds" 
              v-model.number="store.params.nFolds"
              min="1" 
              max="10"
              step="1"
            />
          </div>
          
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
                  @input="onSymbolInput"
                  :disabled="store.isLoadingStocks"
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
                    :class="{ 'selected': store.params.symbol === item.symbol }"
                    @click="selectSymbol(item.symbol)"
                  >
                    {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                  </div>
                </div>
              </div>
              <!-- 隐藏的select元素，用于表单提交 -->
              <select 
                id="symbol" 
                v-model="store.params.symbol"
                class="hidden-select"
                :disabled="store.isLoadingStocks"
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
            <label for="startDate">开始日期</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="store.params.startDate"
            />
          </div>
          
          <div class="form-group">
            <label for="endDate">结束日期</label>
            <input 
              type="date" 
              id="endDate" 
              v-model="store.params.endDate"
            />
          </div>
        </div>
        
        <!-- 选股因子配置 -->
        <div class="factors-section">
          <h4>选股因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.stockFactors" :key="index">
              <div class="factor-header">
                <span>{{ factor.name }}</span>
                <button class="btn-remove" @click="removeStockFactor(index)">×</button>
              </div>
              <div class="factor-config">
                <input 
                  type="text" 
                  v-model="factor.params" 
                  placeholder="参数配置（JSON格式）"
                />
              </div>
            </div>
          </div>
          <div class="add-factor">
            <select v-model="newStockFactorName">
              <option value="">选择选股因子</option>
              <option value="AbuPickStockNDay">N日收益率选股</option>
              <option value="AbuPickStockGT">价格突破选股</option>
              <option value="AbuPickStockEV">估值选股</option>
            </select>
            <button class="btn-add" @click="addStockFactor">添加选股因子</button>
          </div>
        </div>
        
        <!-- 买入因子配置 -->
        <div class="factors-section">
          <h4>买入因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.buyFactors" :key="index">
              <div class="factor-header">
                <span>{{ factor.name }}</span>
                <button class="btn-remove" @click="removeBuyFactor(index)">×</button>
              </div>
              <div class="factor-config">
                <input 
                  type="text" 
                  v-model="factor.params" 
                  placeholder="参数配置（JSON格式）"
                />
              </div>
            </div>
          </div>
          <div class="add-factor">
            <select v-model="newBuyFactorName">
              <option value="">选择买入因子</option>
              <option value="AbuFactorBuyBreak">突破买入</option>
              <option value="AbuFactorBuyMeanReversion">均值回归买入</option>
              <option value="AbuFactorBuyGap">缺口买入</option>
            </select>
            <button class="btn-add" @click="addBuyFactor">添加买入因子</button>
          </div>
        </div>
        
        <!-- 卖出因子配置 -->
        <div class="factors-section">
          <h4>卖出因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.sellFactors" :key="index">
              <div class="factor-header">
                <span>{{ factor.name }}</span>
                <button class="btn-remove" @click="removeSellFactor(index)">×</button>
              </div>
              <div class="factor-config">
                <input 
                  type="text" 
                  v-model="factor.params" 
                  placeholder="参数配置（JSON格式）"
                />
              </div>
            </div>
          </div>
          <div class="add-factor">
            <select v-model="newSellFactorName">
              <option value="">选择卖出因子</option>
              <option value="AbuFactorSellBreak">突破卖出</option>
              <option value="AbuFactorSellMeanReversion">均值回归卖出</option>
              <option value="AbuFactorSellPreAtrN">ATR止损卖出</option>
              <option value="AbuFactorSellRsi">RSI卖出</option>
            </select>
            <button class="btn-add" @click="addSellFactor">添加卖出因子</button>
          </div>
        </div>
        
        <div class="buttons-group">
          <button 
            class="btn-primary" 
            @click="runStrategy" 
            :disabled="store.isRunning"
          >
            {{ store.isRunning ? '策略执行中...' : '执行策略' }}
          </button>
          <button 
            class="btn-secondary" 
            @click="resetParams"
          >
            重置参数
          </button>
        </div>
      </div>
      
      <div class="results-section">
        <h3>策略执行结果</h3>
        
        <div v-if="store.isRunning" class="loading">
          <div class="loading-spinner"></div>
          <p>正在执行策略，请稍候...</p>
        </div>
        
        <div v-else-if="store.error" class="error">
          <p>{{ store.error }}</p>
        </div>
        
        <div v-else-if="store.result" class="result-content">
          <div class="result-cards">
            <div class="result-card">
              <h4>总收益</h4>
              <p class="result-value">{{ store.result.totalReturn }}%</p>
            </div>
            
            <div class="result-card">
              <h4>年化收益</h4>
              <p class="result-value">{{ store.result.annualReturn }}%</p>
            </div>
            
            <div class="result-card">
              <h4>最大回撤</h4>
              <p class="result-value">{{ store.result.maxDrawdown }}%</p>
            </div>
            
            <div class="result-card">
              <h4>夏普比率</h4>
              <p class="result-value">{{ store.result.sharpeRatio }}</p>
            </div>
            
            <div class="result-card">
              <h4>交易次数</h4>
              <p class="result-value">{{ store.result.tradeCount }}</p>
            </div>
            
            <div class="result-card">
              <h4>胜率</h4>
              <p class="result-value">{{ store.result.winRate }}%</p>
            </div>
          </div>
          
          <div class="chart-section">
            <h4>价格走势</h4>
            <div class="chart-container" ref="priceChartRef"></div>
          </div>
          
          <div class="chart-section">
            <h4>收益率曲线</h4>
            <div class="chart-container" ref="returnChartRef"></div>
          </div>
          
          <div class="chart-section">
            <h4>回撤曲线</h4>
            <div class="chart-container" ref="drawdownChartRef"></div>
          </div>
        </div>
        
        <div v-else class="empty-results">
          <p>请设置策略参数并点击执行策略</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAlphaStrategyStore } from '../stores/alphaStrategy'
import { apiService } from '../services/api'
import * as echarts from 'echarts'

const store = useAlphaStrategyStore()

// 已下载的股票列表
const symbolsList = ref<any[]>([])

// 股票代码搜索文本
const symbolSearchText = ref('')

// 股票名称映射表
const stockNameMap = ref<Record<string, string>>({})

// 下拉框显示状态
const isSelectOpen = ref(false)

// 过滤后的股票列表
const filteredSymbols = computed(() => {
  if (!symbolSearchText.value) {
    return symbolsList.value
  }
  
  const searchText = symbolSearchText.value.toLowerCase()
  return symbolsList.value.filter(item => {
    if (item.symbol.toLowerCase().includes(searchText)) {
      return true
    }
    
    const stockName = stockNameMap.value[item.symbol]?.toLowerCase() || ''
    if (stockName.includes(searchText)) {
      return true
    }
    
    return false
  })
})

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
  store.params.symbol = symbol
  symbolSearchText.value = symbol
  isSelectOpen.value = false
}

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  // 当用户在输入框中输入时，更新store.params.symbol
  store.params.symbol = symbolSearchText.value
}

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  const selectElement = document.querySelector('.searchable-select')
  const target = event.target as HTMLElement
  
  if (selectElement && !selectElement.contains(target)) {
    isSelectOpen.value = false
  }
}

// 获取已下载的股票列表
const fetchSymbolsList = async () => {
  try {
    store.isLoadingStocks = true
    const data = await apiService.get<any[]>('/data/symbols')
    symbolsList.value = data
    
    // 动态构建股票名称映射表
    data.forEach(item => {
      stockNameMap.value[item.symbol] = item.name || item.market
    })
    
    // 如果还没有选择股票，默认选择第一个
    if (symbolsList.value.length > 0 && !store.params.symbol) {
      store.params.symbol = symbolsList.value[0].symbol
      symbolSearchText.value = symbolsList.value[0].symbol
    }
  } catch (error) {
    console.error('获取股票列表失败:', error)
  } finally {
    store.isLoadingStocks = false
  }
}

// 组件加载时初始化数据
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  
  // 获取股票列表
  fetchSymbolsList()
  
  // 设置默认的开始和结束日期
  const endDate = new Date().toISOString().split('T')[0]
  const startDate = new Date()
  startDate.setFullYear(startDate.getFullYear() - 2)
  const startDateStr = startDate.toISOString().split('T')[0]
  
  store.params.startDate = startDateStr
  store.params.endDate = endDate
  
  // 延迟初始化图表，确保DOM已经完全渲染
  setTimeout(() => {
    initCharts()
  }, 100)
  
  // 添加窗口大小变化事件监听
  window.addEventListener('resize', handleResize)
})

// 窗口大小变化时重绘图表
const handleResize = () => {
  priceChart.value?.resize()
  returnChart.value?.resize()
  drawdownChart.value?.resize()
}

// 选股因子
const newStockFactorName = ref('')

// 买入因子
const newBuyFactorName = ref('')

// 卖出因子
const newSellFactorName = ref('')

// 添加选股因子
const addStockFactor = () => {
  store.addStockFactor(newStockFactorName.value)
  newStockFactorName.value = ''
}

// 删除选股因子
const removeStockFactor = (index: number) => {
  store.removeStockFactor(index)
}

// 添加买入因子
const addBuyFactor = () => {
  store.addBuyFactor(newBuyFactorName.value)
  newBuyFactorName.value = ''
}

// 删除买入因子
const removeBuyFactor = (index: number) => {
  store.removeBuyFactor(index)
}

// 添加卖出因子
const addSellFactor = () => {
  store.addSellFactor(newSellFactorName.value)
  newSellFactorName.value = ''
}

// 删除卖出因子
const removeSellFactor = (index: number) => {
  store.removeSellFactor(index)
}

// 重置参数
const resetParams = () => {
  store.resetParams()
}

// 图表容器引用
const priceChartRef = ref<HTMLElement | null>(null)
const returnChartRef = ref<HTMLElement | null>(null)
const drawdownChartRef = ref<HTMLElement | null>(null)

// 图表实例
const priceChart = ref<echarts.ECharts | null>(null)
const returnChart = ref<echarts.ECharts | null>(null)
const drawdownChart = ref<echarts.ECharts | null>(null)

// 初始化图表
const initCharts = () => {
  console.log('Initializing charts...')
  console.log('Price chart ref:', priceChartRef.value)
  console.log('Return chart ref:', returnChartRef.value)
  console.log('Drawdown chart ref:', drawdownChartRef.value)
  
  // 确保图表容器有正确的尺寸
  if (priceChartRef.value) {
    // 设置固定尺寸
    priceChartRef.value.style.width = '100%'
    priceChartRef.value.style.height = '400px'
    priceChart.value = echarts.init(priceChartRef.value)
    console.log('Price chart initialized:', priceChart.value)
    // 设置空的图表选项
    priceChart.value.setOption({
      xAxis: { type: 'time' },
      yAxis: { type: 'value' },
      series: []
    })
  }
  if (returnChartRef.value) {
    // 设置固定尺寸
    returnChartRef.value.style.width = '100%'
    returnChartRef.value.style.height = '400px'
    returnChart.value = echarts.init(returnChartRef.value)
    console.log('Return chart initialized:', returnChart.value)
    // 设置空的图表选项
    returnChart.value.setOption({
      xAxis: { type: 'time' },
      yAxis: { type: 'value' },
      series: []
    })
  }
  if (drawdownChartRef.value) {
    // 设置固定尺寸
    drawdownChartRef.value.style.width = '100%'
    drawdownChartRef.value.style.height = '400px'
    drawdownChart.value = echarts.init(drawdownChartRef.value)
    console.log('Drawdown chart initialized:', drawdownChart.value)
    // 设置空的图表选项
    drawdownChart.value.setOption({
      xAxis: { type: 'time' },
      yAxis: { type: 'value' },
      series: []
    })
  }
}

// 更新价格走势图表
const updatePriceChart = () => {
  console.log('Updating price chart...')
  console.log('Price chart instance:', priceChart.value)
  console.log('Price chart data:', store.chartData?.price)
  
  if (!priceChart.value || !store.chartData?.price) {
    console.log('Skipping price chart update - missing instance or data')
    return
  }
  
  const data = store.chartData.price.map((item: any) => [
    item.date,
    parseFloat(item.close)
  ])
  
  console.log('Processed price data:', data)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue
        const close = params[0].value
        return `${date}<br/>收盘价: ${close.toFixed(2)}`
      }
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: '{MM}/{dd}'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '收盘价',
        type: 'line',
        data: data,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409eff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
          ])
        }
      }
    ]
  }
  
  console.log('Price chart option:', option)
  priceChart.value.setOption(option)
}

// 更新收益率曲线图表
const updateReturnChart = () => {
  if (!returnChart.value || !store.chartData?.cumReturn) return
  
  const data = store.chartData.cumReturn.map((item: any) => [
    item.date,
    parseFloat(item.return)
  ])
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue
        const returnValue = params[0].value
        return `${date}<br/>累计收益率: ${returnValue.toFixed(2)}%`
      }
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: '{MM}/{dd}'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '累计收益率',
        type: 'line',
        data: data,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#67c23a'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(103, 194, 58, 0.3)' },
            { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
          ])
        }
      }
    ]
  }
  
  returnChart.value.setOption(option)
}

// 更新回撤曲线图表
const updateDrawdownChart = () => {
  if (!drawdownChart.value || !store.chartData?.drawdown) return
  
  const data = store.chartData.drawdown.map((item: any) => [
    item.date,
    parseFloat(item.drawdown)
  ])
  
  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const date = params[0].axisValue
        const drawdownValue = params[0].value
        return `${date}<br/>回撤率: ${drawdownValue.toFixed(2)}%`
      }
    },
    xAxis: {
      type: 'time',
      axisLabel: {
        formatter: '{MM}/{dd}'
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '{value}%'
      }
    },
    series: [
      {
        name: '回撤率',
        type: 'line',
        data: data,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#f56c6c'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(245, 108, 108, 0.3)' },
            { offset: 1, color: 'rgba(245, 108, 108, 0.05)' }
          ])
        }
      }
    ]
  }
  
  drawdownChart.value.setOption(option)
}

// 执行策略
const runStrategy = () => {
  store.runStrategy()
}

// 监听策略执行结果变化，更新图表
watch(
  () => store.result,
  (newResult) => {
    console.log('Store result changed:', newResult)
    console.log('Chart data available:', store.chartData)
    
    if (newResult && store.chartData) {
      console.log('Updating charts...')
      console.log('Price data:', store.chartData.price)
      console.log('Return data:', store.chartData.cumReturn)
      console.log('Drawdown data:', store.chartData.drawdown)
      
      // 确保图表实例已初始化
      if (!priceChart.value || !returnChart.value || !drawdownChart.value) {
        console.log('Charts not initialized, initializing now...')
        initCharts()
      }
      
      updatePriceChart()
      updateReturnChart()
      updateDrawdownChart()
    }
  },
  { deep: true }
)

// 监听点击外部事件
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  
  // 移除窗口大小变化事件监听
  window.removeEventListener('resize', handleResize)
  
  // 销毁图表实例
  priceChart.value?.dispose()
  returnChart.value?.dispose()
  drawdownChart.value?.dispose()
})
</script>

<style scoped>
/* 可搜索下拉框样式 */
.searchable-select {
  position: relative;
  width: 100%;
}

.searchable-select .select-header {
  position: relative;
  display: flex;
  align-items: center;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 0 12px;
  height: 36px;
  cursor: pointer;
}

.searchable-select .search-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 0;
  font-size: 14px;
  height: 100%;
  background: transparent;
  cursor: pointer;
}

.searchable-select .search-input:focus {
  cursor: text;
}

.searchable-select .select-arrow {
  margin-left: 8px;
  font-size: 12px;
  color: #909399;
  transition: transform 0.2s;
}

.searchable-select .select-arrow.active {
  transform: rotate(180deg);
}

.searchable-select .select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  background-color: #fff;
  border: 1px solid #dcdfe6;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 10;
  display: none;
}

.searchable-select .select-dropdown.open {
  display: block;
}

.searchable-select .select-options {
  padding: 4px 0;
}

.searchable-select .select-option {
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.searchable-select .select-option:hover {
  background-color: #ecf5ff;
}

.searchable-select .select-option.selected {
  background-color: #409eff;
  color: #fff;
}

.searchable-select .hidden-select {
  display: none;
}

/* 图表容器样式 */
.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 10px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  background-color: #ffffff;
}
.alpha-strategy-container {
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.alpha-strategy-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.params-section,
.results-section {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.factors-section {
  margin: 1.5rem 0;
}

.factors-section h4 {
  margin-bottom: 0.5rem;
  color: #555;
}

.factors-list {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.factor-item {
  background-color: white;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.factor-item:last-child {
  margin-bottom: 0;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.factor-header span {
  font-weight: 600;
  color: #333;
}

.btn-remove {
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}

.btn-remove:hover {
  background-color: #c0392b;
}

.factor-config input {
  width: 100%;
  font-family: monospace;
  font-size: 0.9rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #eee;
}

.add-factor {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.add-factor select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

.btn-add {
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-add:hover {
  background-color: #27ae60;
}

.buttons-group {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
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
  background-color: #ecf0f1;
  color: #333;
}

.btn-secondary:hover {
  background-color: #bdc3c7;
}

.results-section h3 {
  margin-bottom: 1.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #3498db;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background-color: #fee;
  color: #c00;
  padding: 1rem;
  border-radius: 4px;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.result-card {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.result-card h4 {
  margin: 0 0 1rem 0;
  color: #555;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-value {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.stock-list-section {
  margin-top: 1.5rem;
}

.stock-list-section h4 {
  margin-bottom: 1rem;
  color: #555;
}

.stock-list {
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.stock-item:last-child {
  border-bottom: none;
}

.stock-symbol {
  font-weight: bold;
  color: #333;
  min-width: 80px;
}

.stock-name {
  flex: 1;
  margin: 0 1rem;
  color: #666;
}

.stock-score {
  font-weight: bold;
  color: #3498db;
  min-width: 60px;
  text-align: right;
}

.empty-results {
  text-align: center;
  padding: 2rem;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .alpha-strategy-content {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .buttons-group {
    flex-direction: column;
  }
  
  .result-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .add-factor {
    flex-direction: column;
  }
}
</style>