<template>
  <div class="gap-analysis-container">
    <h2>跳空缺口分析</h2>
    <div class="gap-analysis-content">
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
                  @input="onSymbolInput"
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
          <div class="form-group">
            <label for="threshold">缺口阈值</label>
            <input 
              type="number" 
              id="threshold" 
              v-model="queryParams.threshold"
              step="0.001"
              min="0.001"
              max="0.1"
              placeholder="请输入缺口阈值"
            />
            <span class="threshold-unit">（默认0.5%）</span>
          </div>
        </div>
        <div class="buttons-group">
          <button class="btn-primary" @click="analyzeGaps" :disabled="isAnalyzing || !queryParams.symbol">
            {{ isAnalyzing ? '分析中...' : '分析跳空缺口' }}
          </button>
          <button class="btn-secondary" @click="clearQuery">
            清除条件
          </button>
        </div>
      </div>
      
      <div class="analysis-results">
        <!-- 缺口统计信息 -->
        <div class="gap-stats">
          <h4>缺口统计信息</h4>
          <div class="stats-grid">
            <div class="stat-card">
              <div class="stat-label">总缺口数</div>
              <div class="stat-value">{{ gapStats.total_gaps }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">向上缺口</div>
              <div class="stat-value up">{{ gapStats.up_gaps }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">向下缺口</div>
              <div class="stat-value down">{{ gapStats.down_gaps }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">已回补缺口</div>
              <div class="stat-value filled">{{ gapStats.filled_gaps }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">未回补缺口</div>
              <div class="stat-value unfilled">{{ gapStats.unfilled_gaps }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">平均缺口大小</div>
              <div class="stat-value">{{ gapStats.avg_gap_size.toFixed(2) }}</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">平均缺口百分比</div>
              <div class="stat-value">{{ gapStats.avg_gap_percent.toFixed(2) }}%</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">最大缺口百分比</div>
              <div class="stat-value">{{ gapStats.max_gap_percent.toFixed(2) }}%</div>
            </div>
          </div>
        </div>
        
        <!-- 跳空缺口列表 -->
        <div class="gaps-list">
          <h4>跳空缺口数据</h4>
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th @click="toggleSort('date')">缺口日期{{ getSortIcon('date') }}</th>
                  <th @click="toggleSort('type')">缺口类型{{ getSortIcon('type') }}</th>
                  <th @click="toggleSort('prev_close')">前收盘价{{ getSortIcon('prev_close') }}</th>
                  <th @click="toggleSort('curr_open')">当日开盘价{{ getSortIcon('curr_open') }}</th>
                  <th @click="toggleSort('gap_size')">缺口大小{{ getSortIcon('gap_size') }}</th>
                  <th @click="toggleSort('gap_percent')">缺口百分比{{ getSortIcon('gap_percent') }}</th>
                  <th @click="toggleSort('is_filled')">是否回补{{ getSortIcon('is_filled') }}</th>
                  <th @click="toggleSort('fill_date')">回补日期{{ getSortIcon('fill_date') }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in sortedGapData" :key="index" :class="{ 'up-gap': item.type === 'up', 'down-gap': item.type === 'down' }">
                  <td>{{ item.date }}</td>
                  <td>
                    <span class="gap-type" :class="item.type">
                      {{ item.type === 'up' ? '向上跳空' : '向下跳空' }}
                    </span>
                  </td>
                  <td>{{ item.prev_close.toFixed(2) }}</td>
                  <td>{{ item.curr_open.toFixed(2) }}</td>
                  <td>{{ item.gap_size.toFixed(2) }}</td>
                  <td>{{ item.gap_percent.toFixed(2) }}%</td>
                  <td>
                    <span class="filled-status" :class="{ 'filled': item.is_filled, 'unfilled': !item.is_filled }">
                      {{ item.is_filled ? '已回补' : '未回补' }}
                    </span>
                  </td>
                  <td>{{ item.fill_date || '-' }}</td>
                </tr>
                <tr v-if="sortedGapData.length === 0 && !isAnalyzing" class="no-data">
                  <td colspan="8">暂无数据，请调整分析参数</td>
                </tr>
                <tr v-if="isAnalyzing" class="loading">
                  <td colspan="8">正在分析数据...</td>
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
import { apiService } from '../services/api'

// 查询参数
const queryParams = ref({
  symbol: '',
  market: 'cn',
  start_date: '',
  end_date: '',
  threshold: 0.005
})

// 已下载的股票列表
const symbolsList = ref<any[]>([])

// 跳空缺口数据
const gapData = ref<any[]>([])

// 排序状态
const sortConfig = ref({
  key: 'date',
  direction: 'desc' as 'asc' | 'desc'
})

// 缺口统计信息
const gapStats = ref({
  total_gaps: 0,
  up_gaps: 0,
  down_gaps: 0,
  filled_gaps: 0,
  unfilled_gaps: 0,
  avg_gap_size: 0,
  avg_gap_percent: 0,
  max_gap_size: 0,
  max_gap_percent: 0
})

// 排序后的缺口数据
const sortedGapData = computed(() => {
  const data = [...gapData.value]
  
  return data.sort((a, b) => {
    let aValue: any = a[sortConfig.value.key]
    let bValue: any = b[sortConfig.value.key]
    
    // 处理日期类型
    if (sortConfig.value.key === 'date' || sortConfig.value.key === 'prev_date' || sortConfig.value.key === 'fill_date') {
      aValue = new Date(aValue || 0).getTime()
      bValue = new Date(bValue || 0).getTime()
    }
    
    // 处理布尔类型
    if (sortConfig.value.key === 'is_filled') {
      aValue = aValue ? 1 : 0
      bValue = bValue ? 1 : 0
    }
    
    // 处理字符串类型
    if (typeof aValue === 'string' && typeof bValue === 'string') {
      return sortConfig.value.direction === 'asc' 
        ? aValue.localeCompare(bValue) 
        : bValue.localeCompare(aValue)
    }
    
    // 处理数值类型
    if (sortConfig.value.direction === 'asc') {
      return aValue - bValue
    } else {
      return bValue - aValue
    }
  })
})

// 切换排序
const toggleSort = (key: string) => {
  if (sortConfig.value.key === key) {
    // 如果点击的是当前排序的列，切换排序方向
    sortConfig.value.direction = sortConfig.value.direction === 'asc' ? 'desc' : 'asc'
  } else {
    // 如果点击的是其他列，设置新的排序列，默认排序方向为升序
    sortConfig.value.key = key
    sortConfig.value.direction = 'asc'
  }
}

// 获取排序图标
const getSortIcon = (key: string) => {
  if (sortConfig.value.key !== key) {
    return ''
  }
  return sortConfig.value.direction === 'asc' ? ' ↑' : ' ↓'
}

// 股票代码搜索文本
const symbolSearchText = ref('')

// 股票名称映射表
const stockNameMap = ref<Record<string, string>>({})

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

// 下拉框显示状态
const isSelectOpen = ref(false)

// 分析状态
const isAnalyzing = ref(false)

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
  symbolSearchText.value = symbol
  isSelectOpen.value = false
}

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  // 当用户在输入框中输入时，更新queryParams.symbol
  queryParams.value.symbol = symbolSearchText.value
}

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  const selectElement = document.querySelector('.searchable-select')
  const target = event.target as HTMLElement
  
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
})

// 初始化日期范围
const initDateRange = () => {
  const endDate = new Date()
  const startDate = new Date()
  startDate.setMonth(startDate.getMonth() - 6)
  
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
    const data = await apiService.get<any[]>('/data/download/symbols')
    symbolsList.value = data
    
    // 动态构建股票名称映射表
    data.forEach(item => {
      stockNameMap.value[item.symbol] = item.name || item.symbol
    })
  } catch (error) {
    console.error('获取已下载股票列表失败:', error)
    symbolsList.value = [
      { symbol: 'sh600000', market: 'cn' },
      { symbol: 'sh600036', market: 'cn' },
      { symbol: 'sh600519', market: 'cn' },
      { symbol: 'sz000001', market: 'cn' },
      { symbol: 'sz000858', market: 'cn' }
    ]
    
    // 为默认股票列表构建名称映射
    symbolsList.value.forEach(item => {
      stockNameMap.value[item.symbol] = item.name || item.symbol
    })
  }
}

// 清除查询条件
const clearQuery = () => {
  queryParams.value = {
    symbol: '',
    market: 'cn',
    start_date: '',
    end_date: '',
    threshold: 0.005
  }
  gapData.value = []
  gapStats.value = {
    total_gaps: 0,
    up_gaps: 0,
    down_gaps: 0,
    filled_gaps: 0,
    unfilled_gaps: 0,
    avg_gap_size: 0,
    avg_gap_percent: 0,
    max_gap_size: 0,
    max_gap_percent: 0
  }
  initDateRange()
}

// 分析跳空缺口
const analyzeGaps = async () => {
  if (!queryParams.value.symbol) {
    alert('请选择股票代码')
    return
  }
  
  isAnalyzing.value = true
  
  try {
    const response = await apiService.get(`/stock/${queryParams.value.symbol}/gaps`, {
      start_date: queryParams.value.start_date,
      end_date: queryParams.value.end_date,
      threshold: queryParams.value.threshold
    })
    
    gapData.value = response.gaps
    
    const statsResponse = await apiService.get(`/stock/${queryParams.value.symbol}/gaps/stats`, {
      start_date: queryParams.value.start_date,
      end_date: queryParams.value.end_date,
      threshold: queryParams.value.threshold
    })
    
    gapStats.value = statsResponse.stats
  } catch (error) {
    console.error('分析跳空缺口失败:', error)
    alert('分析失败，请检查网络连接或参数设置')
  } finally {
    isAnalyzing.value = false
  }
}
</script>

<style scoped>
.gap-analysis-container {
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.gap-analysis-content {
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

.threshold-unit {
  font-size: 0.875rem;
  color: #666;
  margin-left: 0.5rem;
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

.gap-stats {
  margin-bottom: 2rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
}

.stat-card {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

.stat-value.up {
  color: #e74c3c;
}

.stat-value.down {
  color: #27ae60;
}

.stat-value.filled {
  color: #3498db;
}

.stat-value.unfilled {
  color: #f39c12;
}

.gaps-list {
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
  text-align: right;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #333;
}

th:first-child, td:first-child {
  text-align: left;
}

th:nth-child(2), td:nth-child(2) {
  text-align: left;
}

.gap-type {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
}

.gap-type.up {
  background-color: #ffebee;
  color: #e74c3c;
}

.gap-type.down {
  background-color: #e8f5e8;
  color: #27ae60;
}

.filled-status {
  padding: 0.25rem 0.75rem;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.875rem;
}

.filled-status.filled {
  background-color: #e3f2fd;
  color: #3498db;
}

.filled-status.unfilled {
  background-color: #fff3e0;
  color: #f39c12;
}

.up-gap {
  background-color: #fef2f2;
}

.down-gap {
  background-color: #f0fdf4;
}

/* 表头样式 */
th {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

th:hover {
  background-color: #e9ecef;
}

/* 排序图标样式 */
th span.sort-icon {
  margin-left: 0.25rem;
  font-size: 0.75rem;
}

.no-data {
  text-align: center;
  color: #95a5a6;
  font-style: italic;
}

.loading {
  text-align: center;
  color: #3498db;
  font-style: italic;
}

@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: 1fr 1fr 1fr;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .buttons-group {
    flex-direction: column;
  }
}
</style>