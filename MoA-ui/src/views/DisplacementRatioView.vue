<template>
  <div class="displacement-ratio-container">
    <h2>位移路程比分析</h2>
    
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
      <!-- 单个股票位移路程比 -->
      <div v-if="activeTab === 'single'" class="tab-pane">
        <h3>单个股票位移路程比分析</h3>
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
            <div class="form-group">
              <label for="single-window">计算窗口（天）</label>
              <input 
                type="number" 
                id="single-window" 
                v-model.number="singleParams.window" 
                min="5" 
                max="100"
                step="5"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getSingleDisplacementRatio" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算位移路程比' }}
            </button>
          </div>
        </div>
        
        <div v-if="singleResult" class="result-section">
          <h4>位移路程比分析结果</h4>
          <div class="result-card">
            <div class="result-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ singleResult.symbol }}</span>
            </div>
            <div class="result-item">
              <span class="label">数据周期：</span>
              <span class="value">{{ singleResult.n_folds }} 年</span>
            </div>
            <div class="result-item">
              <span class="label">计算窗口：</span>
              <span class="value">{{ singleResult.window }} 天</span>
            </div>
          </div>
          
          <!-- 不同窗口大小的DDR对比 -->
          <div class="chart-section">
            <h4>不同窗口大小的位移路程比</h4>
            <div ref="windowChartRef" class="chart-container"></div>
          </div>
          
          <!-- 位移路程比时间序列 -->
          <div class="chart-section">
            <h4>位移路程比时间序列</h4>
            <div ref="ddrChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
      
      <!-- 多只股票位移路程比比较 -->
      <div v-else-if="activeTab === 'compare'" class="tab-pane">
        <h3>多只股票位移路程比比较</h3>
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
            <div class="form-group">
              <label for="compare-window">计算窗口（天）</label>
              <input 
                type="number" 
                id="compare-window" 
                v-model.number="compareParams.window" 
                min="5" 
                max="100"
                step="5"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getCompareDisplacementRatio" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算多股位移路程比' }}
            </button>
          </div>
        </div>
        
        <div v-if="compareResult" class="result-section">
          <h4>多只股票位移路程比比较结果</h4>
          <div class="result-item">
            <span class="label">计算窗口：</span>
            <span class="value">{{ compareResult.window }} 天</span>
          </div>
          <div class="chart-section">
            <h4>不同周期位移路程比对比</h4>
            <div ref="compareChartRef" class="chart-container"></div>
          </div>
          <div class="result-table-container">
            <table class="result-table">
              <thead>
                <tr>
                  <th>股票代码</th>
                  <th>短期DDR (20天)</th>
                  <th>中期DDR (60天)</th>
                  <th>长期DDR (120天)</th>
                  <th>平均DDR</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in compareResult.results" :key="result.symbol">
                  <td>{{ result.symbol }}</td>
                  <td>{{ result.short_term_ddr.toFixed(4) }}</td>
                  <td>{{ result.medium_term_ddr.toFixed(4) }}</td>
                  <td>{{ result.long_term_ddr.toFixed(4) }}</td>
                  <td>{{ result.avg_ddr.toFixed(4) }}</td>
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
  { id: 'single', name: '单个股票DDR' },
  { id: 'compare', name: '多只股票比较' }
];

// 单个股票参数
const singleParams = ref({
  symbol: '',
  n_folds: 2,
  window: 20
});
const singleResult = ref<any>(null);

// 多只股票参数
const compareParams = ref({
  symbolsText: '',
  n_folds: 2,
  window: 20
});
const compareResult = ref<any>(null);

// 图表引用
const windowChartRef = ref<HTMLElement | null>(null);
const ddrChartRef = ref<HTMLElement | null>(null);
const compareChartRef = ref<HTMLElement | null>(null);

let windowChart: echarts.ECharts | null = null;
let ddrChart: echarts.ECharts | null = null;
let compareChart: echarts.ECharts | null = null;

// API请求函数已移除，替换为apiService

// 获取单个股票位移路程比分析
const getSingleDisplacementRatio = async () => {
  if (!singleParams.value.symbol) {
    error.value = '请选择股票代码';
    return;
  }
  
  try {
    isLoading.value = true;
    error.value = '';
    const result = await apiService.get('/displacement-ratio/single', {
      symbol: singleParams.value.symbol,
      n_folds: singleParams.value.n_folds,
      window: singleParams.value.window
    });
    singleResult.value = result;
    
    // 绘制图表
    await nextTick();
    drawWindowChart(result);
    drawDDRChart(result);
  } catch (err) {
    console.error('获取单个股票位移路程比分析失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// 获取多只股票位移路程比比较
const getCompareDisplacementRatio = async () => {
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
    const result = await apiService.post('/displacement-ratio/compare', {
      symbols: symbols,
      n_folds: compareParams.value.n_folds,
      window: compareParams.value.window
    });
    
    compareResult.value = result;
    
    // 绘制比较图表
    await nextTick();
    drawCompareChart(result);
  } catch (err) {
    console.error('获取多只股票位移路程比比较失败:', err);
  } finally {
    isLoading.value = false;
  }
};

// 绘制不同窗口大小的DDR对比图表
const drawWindowChart = (result: any) => {
  if (!windowChartRef.value) return;
  
  // 初始化图表
  if (!windowChart) {
    windowChart = echarts.init(windowChartRef.value);
  }
  
  // 准备数据
  const windowSizes = result.ddr_results.map((item: any) => item.window_size);
  const avgDdr = result.ddr_results.map((item: any) => item.avg_ddr);
  const maxDdr = result.ddr_results.map((item: any) => item.max_ddr);
  const minDdr = result.ddr_results.map((item: any) => item.min_ddr);
  
  const option = {
    title: {
      text: `${result.symbol} 不同窗口大小的位移路程比`,
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
      data: ['平均DDR', '最大DDR', '最小DDR'],
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
      data: windowSizes,
      name: '窗口大小（天）',
      nameLocation: 'middle',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: '位移路程比',
      min: 0,
      max: 1
    },
    series: [
      {
        name: '平均DDR',
        type: 'line',
        data: avgDdr,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409eff'
        },
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        }
      },
      {
        name: '最大DDR',
        type: 'line',
        data: maxDdr,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#67c23a',
          type: 'dashed'
        },
        itemStyle: {
          color: '#67c23a'
        }
      },
      {
        name: '最小DDR',
        type: 'line',
        data: minDdr,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#f56c6c',
          type: 'dashed'
        },
        itemStyle: {
          color: '#f56c6c'
        }
      }
    ]
  };
  
  windowChart.setOption(option);
};

// 绘制位移路程比时间序列图表
const drawDDRChart = (result: any) => {
  if (!ddrChartRef.value) return;
  
  // 初始化图表
  if (!ddrChart) {
    ddrChart = echarts.init(ddrChartRef.value);
  }
  
  // 准备数据
  const dates = result.specified_ddr_list.map((item: any) => {
    const date = new Date(item.date);
    return date.toLocaleDateString();
  });
  const ddrValues = result.specified_ddr_list.map((item: any) => item.ddr);
  
  const option = {
    title: {
      text: `${result.symbol} 位移路程比时间序列 (${result.window}天窗口)`,
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
      data: ['位移路程比'],
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '15%',
      containLabel: true
    },
    toolbox: {
      feature: {
        saveAsImage: {}
      }
    },
    xAxis: {
      type: 'category',
      data: dates,
      name: '日期',
      nameLocation: 'middle',
      nameGap: 40,
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '位移路程比',
      min: 0,
      max: 1
    },
    series: [
      {
        name: '位移路程比',
        type: 'line',
        data: ddrValues,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409eff'
        },
        itemStyle: {
          color: '#409eff'
        },
        areaStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
              { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
            ]
          }
        }
      }
    ]
  };
  
  ddrChart.setOption(option);
};

// 绘制多只股票位移路程比比较图表
const drawCompareChart = (result: any) => {
  if (!compareChartRef.value) return;
  
  // 初始化图表
  if (!compareChart) {
    compareChart = echarts.init(compareChartRef.value);
  }
  
  // 准备数据
  const symbols = result.results.map((item: any) => item.symbol);
  const shortTerm = result.results.map((item: any) => item.short_term_ddr);
  const mediumTerm = result.results.map((item: any) => item.medium_term_ddr);
  const longTerm = result.results.map((item: any) => item.long_term_ddr);
  
  const option = {
    title: {
      text: '多只股票不同周期位移路程比对比',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['短期 (20天)', '中期 (60天)', '长期 (120天)'],
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
      data: symbols,
      name: '股票代码',
      nameLocation: 'middle',
      nameGap: 40
    },
    yAxis: {
      type: 'value',
      name: '位移路程比',
      min: 0,
      max: 1
    },
    series: [
      {
        name: '短期 (20天)',
        type: 'bar',
        data: shortTerm,
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '中期 (60天)',
        type: 'bar',
        data: mediumTerm,
        itemStyle: {
          color: '#67c23a'
        }
      },
      {
        name: '长期 (120天)',
        type: 'bar',
        data: longTerm,
        itemStyle: {
          color: '#f56c6c'
        }
      }
    ]
  };
  
  compareChart.setOption(option);
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
}

// 窗口大小变化时调整图表大小
const handleResize = () => {
  if (windowChart) {
    windowChart.resize();
  }
  if (ddrChart) {
    ddrChart.resize();
  }
  if (compareChart) {
    compareChart.resize();
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
  if (windowChart) {
    windowChart.dispose();
    windowChart = null;
  }
  if (ddrChart) {
    ddrChart.dispose();
    ddrChart = null;
  }
  if (compareChart) {
    compareChart.dispose();
    compareChart = null;
  }
});

// 监听singleResult变化，重新绘制图表
watch(() => singleResult.value, (newVal) => {
  if (newVal) {
    nextTick(() => {
      drawWindowChart(newVal);
      drawDDRChart(newVal);
    });
  }
});

// 监听compareResult变化，重新绘制图表
watch(() => compareResult.value, (newVal) => {
  if (newVal) {
    nextTick(() => {
      drawCompareChart(newVal);
    });
  }
});
</script>

<style scoped>
.displacement-ratio-container {
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