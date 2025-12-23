<template>
  <div class="price-channel-container">
    <h2>价格通道分析</h2>
    
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        :class="['tab-btn', { active: activeTab === tab.id }]"
        @click="activeTab = tab.id"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <div class="tab-content">
      <!-- 单个股票价格通道 -->
      <div v-if="activeTab === 'single'" class="tab-pane">
        <h3>单个股票价格通道分析</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group">
              <label for="single-symbol">股票代码</label>
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
                      :class="{ 'selected': singleParams.symbol === item.symbol }"
                      @click="selectSymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
                <select 
                  id="single-symbol" 
                  v-model="singleParams.symbol"
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
              <label for="single-channel-type">通道类型</label>
              <select id="single-channel-type" v-model="singleParams.channel_type">
                <option value="regress">拟合通道</option>
                <option value="skeleton">骨架通道</option>
                <option value="support">支撑阻力通道</option>
              </select>
            </div>
            <div class="form-group">
              <label for="single-n-folds">数据周期（年）</label>
              <input 
                type="number" 
                id="single-n-folds" 
                v-model.number="singleParams.n_folds" 
                min="1" 
                max="5"
                step="1"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getSinglePriceChannel" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算价格通道' }}
            </button>
          </div>
        </div>
        
        <div v-if="singleResult" class="result-section">
          <h4>价格通道分析结果</h4>
          <div class="result-card">
            <div class="result-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ singleResult.symbol }}</span>
            </div>
            <div class="result-item">
              <span class="label">通道类型：</span>
              <span class="value">{{ channelTypeLabelMap[singleResult.channel_type] }}</span>
            </div>
            <div class="result-item">
              <span class="label">数据点数量：</span>
              <span class="value">{{ singleResult.close.length }}</span>
            </div>
          </div>
          
          <!-- 价格通道图表 -->
          <div class="chart-section">
            <h4>价格通道可视化</h4>
            <div ref="channelChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
      
      <!-- 多只股票价格通道比较 -->
      <div v-else-if="activeTab === 'compare'" class="tab-pane">
        <h3>多只股票价格通道比较</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="compare-symbols">股票代码（逗号分隔）</label>
              <textarea 
                id="compare-symbols" 
                v-model="compareParams.symbolsText"
                placeholder="例如：sh600000,sh600036,sh600519,sz000001,sz000858"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="compare-channel-type">通道类型</label>
              <select id="compare-channel-type" v-model="compareParams.channel_type">
                <option value="regress">拟合通道</option>
                <option value="skeleton">骨架通道</option>
              </select>
            </div>
            <div class="form-group">
              <label for="compare-n-folds">数据周期（年）</label>
              <input 
                type="number" 
                id="compare-n-folds" 
                v-model.number="compareParams.n_folds" 
                min="1" 
                max="5"
                step="1"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getComparePriceChannel" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算多股价格通道比较' }}
            </button>
          </div>
        </div>
        
        <div v-if="compareResult" class="result-section">
          <h4>多只股票价格通道比较结果</h4>
          <div class="result-item">
            <span class="label">通道类型：</span>
            <span class="value">{{ channelTypeLabelMap[compareResult.channel_type] }}</span>
          </div>
          <div class="result-table-container">
            <table class="result-table">
              <thead>
                <tr>
                  <th>股票代码</th>
                  <th>通道宽度 (%)</th>
                  <th>数据点</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in compareResult.results" :key="result.symbol">
                  <td>{{ result.symbol }}</td>
                  <td>{{ result.channel_width.toFixed(4) }}</td>
                  <td>{{ result.data_points }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import * as echarts from 'echarts';
import { apiService } from '../services/api';

// 状态管理
const activeTab = ref('single');
const isLoading = ref(false);
const error = ref('');

// 标签页配置
const tabs = [
  { id: 'single', name: '单个股票通道' },
  { id: 'compare', name: '多只股票比较' }
];

// 通道类型标签映射
const channelTypeLabelMap = {
  'regress': '拟合通道',
  'skeleton': '骨架通道',
  'support': '支撑阻力通道'
};

// 单个股票参数
const singleParams = ref({
  symbol: '',
  channel_type: 'regress',
  n_folds: 2
});
const singleResult = ref<any>(null);

// 多只股票参数
const compareParams = ref({
  symbolsText: '',
  channel_type: 'regress',
  n_folds: 2
});
const compareResult = ref<any>(null);

// 图表引用
const channelChartRef = ref<HTMLElement | null>(null);
let channelChart: echarts.ECharts | null = null;

// API请求函数已移除，替换为apiService

// 获取单个股票价格通道分析
const getSinglePriceChannel = async () => {
  if (!singleParams.value.symbol) {
    error.value = '请选择股票代码';
    return;
  }
  
  try {
    isLoading.value = true;
    error.value = '';
    const result = await apiService.get('/price-channel/single', {
      symbol: singleParams.value.symbol,
      channel_type: singleParams.value.channel_type,
      n_folds: singleParams.value.n_folds
    });
    singleResult.value = result;
    
    // 绘制价格通道图表
    await nextTick();
    drawChannelChart(result);
  } catch (err) {
    console.error('获取单个股票价格通道分析失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// 获取多只股票价格通道比较
const getComparePriceChannel = async () => {
  if (!compareParams.value.symbolsText) {
    error.value = '请输入股票代码列表';
    return;
  }
  
  try {
    const symbols = compareParams.value.symbolsText
      .split(',')
      .map(s => s.trim())
      .filter(s => s);
    
    if (symbols.length < 2) {
      error.value = '请输入至少两只股票代码';
      return;
    }
    
    isLoading.value = true;
    error.value = '';
    const result = await apiService.post('/price-channel/compare', {
      symbols: symbols,
      channel_type: compareParams.value.channel_type,
      n_folds: compareParams.value.n_folds
    });
    
    compareResult.value = result;
  } catch (err) {
    console.error('获取多只股票价格通道比较失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// 绘制价格通道图表
const drawChannelChart = (result: any) => {
  if (!channelChartRef.value) return;
  
  // 初始化图表
  if (!channelChart) {
    channelChart = echarts.init(channelChartRef.value);
  }
  
  // 准备数据
  const dates = result.dates.map((x: number, index: number) => {
    const date = new Date(x);
    return date.toLocaleDateString();
  });
  
  const series = [
    {
      name: '实际价格',
      type: 'line',
      data: result.close,
      smooth: true,
      lineStyle: {
        width: 2,
        color: '#409eff'
      },
      itemStyle: {
        color: '#409eff'
      }
    }
  ];
  
  // 添加通道线
  if (result.channel) {
    if (result.channel.middle) {
      series.push({
        name: '中轨',
        type: 'line',
        data: result.channel.middle,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#67c23a',
          type: 'solid'
        },
        itemStyle: {
          color: '#67c23a'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(103, 194, 58, 0.2)' },
              { offset: 1, color: 'rgba(103, 194, 58, 0.05)' }
            ]
          }
        }
      });
    }
    
    if (result.channel.lower) {
      series.push({
        name: '下轨',
        type: 'line',
        data: result.channel.lower,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#f56c6c',
          type: 'dashed'
        },
        itemStyle: {
          color: '#f56c6c'
        }
      });
    }
    
    if (result.channel.upper) {
      series.push({
        name: '上轨',
        type: 'line',
        data: result.channel.upper,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#f56c6c',
          type: 'dashed'
        },
        itemStyle: {
          color: '#f56c6c'
        }
      });
    }
  }
  
  // 支撑阻力通道
  if (result.support_pos && result.resistance_pos) {
    // 绘制支撑位
    const supportData = [];
    for (const pos of result.support_pos) {
      if (pos >= 0 && pos < result.close.length) {
        supportData.push([dates[pos], result.close[pos]]);
      }
    }
    
    series.push({
      name: '支撑位',
      type: 'scatter',
      data: supportData.map(item => [item[0], item[1]]),
      itemStyle: {
        color: '#67c23a',
        size: 6
      }
    });
    
    // 绘制阻力位
    const resistanceData = [];
    for (const pos of result.resistance_pos) {
      if (pos >= 0 && pos < result.close.length) {
        resistanceData.push([dates[pos], result.close[pos]]);
      }
    }
    
    series.push({
      name: '阻力位',
      type: 'scatter',
      data: resistanceData.map(item => [item[0], item[1]]),
      itemStyle: {
        color: '#f56c6c',
        size: 6
      }
    });
  }
  
  const option = {
    title: {
      text: `${result.symbol} ${channelTypeLabelMap[result.channel_type]}`,
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        label: {
          backgroundColor: '#6a7985'
        }
      }
    },
    legend: {
      data: series.map(item => item.name),
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value'
    },
    series: series
  };
  
  channelChart.setOption(option);
};

// ========== 股票选择相关功能 ==========
// 已下载的股票列表
const symbolsList = ref<any[]>([]);

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
});

// 股票代码搜索文本
const symbolSearchText = ref('');

// 过滤后的股票列表
const filteredSymbols = computed(() => {
  if (!symbolSearchText.value) {
    return symbolsList.value;
  }
  
  const searchText = symbolSearchText.value.toLowerCase();
  return symbolsList.value.filter(item => {
    if (item.symbol.toLowerCase().includes(searchText)) {
      return true;
    }
    
    const stockName = stockNameMap.value[item.symbol]?.toLowerCase() || '';
    if (stockName.includes(searchText)) {
      return true;
    }
    
    return false;
  });
});

// 下拉框显示状态
const isSelectOpen = ref(false);

// 打开下拉框
const openSelect = () => {
  isSelectOpen.value = true;
};

// 切换下拉框显示状态
const toggleSelect = (event?: MouseEvent) => {
  if (event) {
    event.stopPropagation();
  }
  isSelectOpen.value = !isSelectOpen.value;
};

// 选择股票
const selectSymbol = (symbol: string) => {
  singleParams.value.symbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  singleParams.value.symbol = symbolSearchText.value;
};

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  const selectElements = document.querySelectorAll('.searchable-select');
  const target = event.target as HTMLElement;
  
  let clickedInside = false;
  selectElements.forEach(element => {
    if (element.contains(target)) {
      clickedInside = true;
    }
  });
  
  if (!clickedInside) {
    isSelectOpen.value = false;
  }
};

// 获取已下载的股票列表
const fetchSymbolsList = async () => {
  try {
    isLoading.value = true;
    error.value = '';
    const data = await apiService.get('/data/download/symbols');
    symbolsList.value = data;
  } catch (error) {
    console.error('获取已下载股票列表失败:', error);
    // 使用默认股票列表
    symbolsList.value = [
      { symbol: 'sh600000', market: 'cn' },
      { symbol: 'sh600036', market: 'cn' },
      { symbol: 'sh600519', market: 'cn' },
      { symbol: 'sz000001', market: 'cn' },
      { symbol: 'sz000858', market: 'cn' }
    ];
  } finally {
    isLoading.value = false;
  }
};

// 窗口大小变化时调整图表大小
const handleResize = () => {
  if (channelChart) {
    channelChart.resize();
  }
};

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('resize', handleResize);
  fetchSymbolsList();
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('resize', handleResize);
  if (channelChart) {
    channelChart.dispose();
    channelChart = null;
  }
});

// 监听singleResult变化，重新绘制图表
watch(() => singleResult.value, (newVal) => {
  if (newVal) {
    nextTick(() => {
      drawChannelChart(newVal);
    });
  }
});
</script>

<style scoped>
.price-channel-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  color: #666;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #409eff;
}

.tab-btn.active {
  color: #409eff;
  border-bottom-color: #409eff;
}

.tab-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #409eff;
}

.buttons-group {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.btn-primary {
  padding: 10px 20px;
  background-color: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  background-color: #66b1ff;
}

.btn-primary:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.result-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.result-card {
  background-color: #f5f7fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.result-item {
  display: flex;
  margin-bottom: 10px;
  align-items: center;
}

.result-item .label {
  font-weight: 500;
  color: #666;
  margin-right: 10px;
  width: 150px;
}

.result-item .value {
  color: #333;
  font-weight: 600;
  flex: 1;
}

.chart-section {
  margin-top: 30px;
}

.chart-container {
  width: 100%;
  height: 400px;
  margin-top: 20px;
}

.result-table-container {
  overflow-x: auto;
  margin-top: 20px;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-table th,
.result-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.result-table th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #333;
}

.result-table tr:hover {
  background-color: #f5f7fa;
}

.error-message {
  margin-top: 20px;
  padding: 10px;
  background-color: rgba(255, 73, 73, 0.1);
  color: #f56c6c;
  border-radius: 4px;
  font-size: 14px;
}

/* 搜索式下拉选择框样式 */
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
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #409eff;
}

.select-arrow {
  position: absolute;
  right: 10px;
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
  border: 1px solid #dcdfe6;
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
  padding: 5px 0;
}

.select-option {
  padding: 10px 15px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .result-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .result-item .label {
    width: auto;
    margin-bottom: 5px;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>