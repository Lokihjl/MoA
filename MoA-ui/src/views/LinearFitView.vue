<template>
  <div class="linear-fit-container">
    <h2>线性拟合分析</h2>
    
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
      <!-- 单个股票线性拟合 -->
      <div v-if="activeTab === 'single'" class="tab-pane">
        <h3>单个股票线性拟合分析</h3>
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
              <label for="single-poly">多项式次数</label>
              <input 
                type="number" 
                id="single-poly" 
                v-model.number="singleParams.poly" 
                min="1" 
                max="20"
                step="1"
              />
            </div>
            <div class="form-group">
              <label for="single-metric">评估指标</label>
              <select id="single-metric" v-model="singleParams.metric">
                <option value="rmse">均方根误差 (RMSE)</option>
                <option value="mae">平均绝对误差 (MAE)</option>
                <option value="mse">均方误差 (MSE)</option>
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
              @click="getSingleLinearFit" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算拟合' }}
            </button>
          </div>
        </div>
        
        <div v-if="singleResult" class="result-section">
          <h4>线性拟合分析结果</h4>
          <div class="result-card">
            <div class="result-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ singleResult.symbol }}</span>
            </div>
            <div class="result-item">
              <span class="label">多项式次数：</span>
              <span class="value">{{ singleResult.poly }}</span>
            </div>
            <div class="result-item">
              <span class="label">评估指标：</span>
              <span class="value">{{ metricLabelMap[singleResult.metric] }}</span>
            </div>
            <div class="result-item highlight">
              <span class="label">拟合优度（R²）：</span>
              <span class="value">{{ singleResult.r2.toFixed(4) }}</span>
            </div>
            <div class="result-item">
              <span class="label">斜率：</span>
              <span class="value">{{ singleResult.slope.toFixed(4) }}</span>
            </div>
            <div class="result-item">
              <span class="label">截距：</span>
              <span class="value">{{ singleResult.intercept.toFixed(4) }}</span>
            </div>
            <div class="result-item">
              <span class="label">拟合直线角度：</span>
              <span class="value">{{ singleResult.deg.toFixed(2) }}°</span>
            </div>
            <div class="result-item">
              <span class="label">评估值：</span>
              <span class="value">{{ singleResult.metrics_value.toFixed(4) }}</span>
            </div>
            <div class="result-item">
              <span class="label">拟合效果：</span>
              <span class="value" :class="singleResult.is_valid ? 'valid' : 'invalid'">
                {{ singleResult.is_valid ? '有效' : '无效' }}
              </span>
            </div>
            <div class="result-item">
              <span class="label">数据点数量：</span>
              <span class="value">{{ singleResult.data_points }}</span>
            </div>
          </div>
          
          <!-- 拟合图表 -->
          <div class="chart-section">
            <h4>拟合结果可视化</h4>
            <div ref="fitChartRef" class="chart-container"></div>
          </div>
        </div>
      </div>
      
      <!-- 最佳多项式拟合次数 -->
      <div v-else-if="activeTab === 'best-poly'" class="tab-pane">
        <h3>最佳多项式拟合次数分析</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group">
              <label for="best-symbol">股票代码</label>
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
                      :class="{ 'selected': bestPolyParams.symbol === item.symbol }"
                      @click="selectBestPolySymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
                <select 
                  id="best-symbol" 
                  v-model="bestPolyParams.symbol"
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
              <label for="best-metric">评估指标</label>
              <select id="best-metric" v-model="bestPolyParams.metric">
                <option value="rmse">均方根误差 (RMSE)</option>
                <option value="mae">平均绝对误差 (MAE)</option>
                <option value="mse">均方误差 (MSE)</option>
              </select>
            </div>
            <div class="form-group">
              <label for="best-poly-min">最小多项式次数</label>
              <input 
                type="number" 
                id="best-poly-min" 
                v-model.number="bestPolyParams.poly_min" 
                min="1" 
                max="50"
                step="1"
              />
            </div>
            <div class="form-group">
              <label for="best-poly-max">最大多项式次数</label>
              <input 
                type="number" 
                id="best-poly-max" 
                v-model.number="bestPolyParams.poly_max" 
                min="2" 
                max="100"
                step="1"
              />
            </div>
            <div class="form-group">
              <label for="best-n-folds">数据周期（年）</label>
              <input 
                type="number" 
                id="best-n-folds" 
                v-model.number="bestPolyParams.n_folds" 
                min="1" 
                max="5"
                step="1"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getBestPoly" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '寻找最佳拟合次数' }}
            </button>
          </div>
        </div>
        
        <div v-if="bestPolyResult" class="result-section">
          <h4>最佳多项式拟合次数结果</h4>
          <div class="result-card">
            <div class="result-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ bestPolyResult.symbol }}</span>
            </div>
            <div class="result-item">
              <span class="label">评估指标：</span>
              <span class="value">{{ metricLabelMap[bestPolyResult.metric] }}</span>
            </div>
            <div class="result-item highlight">
              <span class="label">最佳多项式次数：</span>
              <span class="value">{{ bestPolyResult.best_poly }}</span>
            </div>
            <div class="result-item">
              <span class="label">最小有效多项式次数：</span>
              <span class="value">{{ bestPolyResult.least_valid_poly }}</span>
            </div>
            <div class="result-item">
              <span class="label">搜索范围：</span>
              <span class="value">{{ bestPolyResult.poly_min }} - {{ bestPolyResult.poly_max }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 多只股票线性拟合比较 -->
      <div v-else-if="activeTab === 'compare'" class="tab-pane">
        <h3>多只股票线性拟合比较</h3>
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
              <label for="compare-poly">多项式次数</label>
              <input 
                type="number" 
                id="compare-poly" 
                v-model.number="compareParams.poly" 
                min="1" 
                max="20"
                step="1"
              />
            </div>
            <div class="form-group">
              <label for="compare-metric">评估指标</label>
              <select id="compare-metric" v-model="compareParams.metric">
                <option value="rmse">均方根误差 (RMSE)</option>
                <option value="mae">平均绝对误差 (MAE)</option>
                <option value="mse">均方误差 (MSE)</option>
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
              @click="getCompareLinearFit" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算多股拟合比较' }}
            </button>
          </div>
        </div>
        
        <div v-if="compareResult" class="result-section">
          <h4>多只股票拟合比较结果</h4>
          <div class="result-item">
            <span class="label">多项式次数：</span>
            <span class="value">{{ compareResult.poly }}</span>
          </div>
          <div class="result-item">
            <span class="label">评估指标：</span>
            <span class="value">{{ metricLabelMap[compareResult.metric] }}</span>
          </div>
          <div class="result-table-container">
            <table class="result-table">
              <thead>
                <tr>
                  <th>股票代码</th>
                  <th>拟合优度 (R²)</th>
                  <th>斜率</th>
                  <th>角度 (°)</th>
                  <th>评估值</th>
                  <th>拟合效果</th>
                  <th>数据点</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="result in compareResult.results" :key="result.symbol">
                  <td>{{ result.symbol }}</td>
                  <td>{{ result.r2.toFixed(4) }}</td>
                  <td>{{ result.slope.toFixed(4) }}</td>
                  <td>{{ result.deg.toFixed(2) }}</td>
                  <td>{{ result.metrics_value.toFixed(4) }}</td>
                  <td>
                    <span :class="result.is_valid ? 'valid' : 'invalid'">
                      {{ result.is_valid ? '有效' : '无效' }}
                    </span>
                  </td>
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

// 状态管理
const activeTab = ref('single');
const isLoading = ref(false);
const error = ref('');

// 标签页配置
const tabs = [
  { id: 'single', name: '单个股票拟合' },
  { id: 'best-poly', name: '最佳多项式拟合次数' },
  { id: 'compare', name: '多只股票拟合比较' }
];

// 评估指标标签映射
const metricLabelMap = {
  'rmse': '均方根误差 (RMSE)',
  'mae': '平均绝对误差 (MAE)',
  'mse': '均方误差 (MSE)'
};

// 单个股票参数
const singleParams = ref({
  symbol: '',
  poly: 1,
  metric: 'rmse',
  n_folds: 2
});
const singleResult = ref<any>(null);

// 最佳多项式拟合参数
const bestPolyParams = ref({
  symbol: '',
  metric: 'rmse',
  poly_min: 1,
  poly_max: 10,
  n_folds: 2
});
const bestPolyResult = ref<any>(null);

// 多只股票参数
const compareParams = ref({
  symbolsText: '',
  poly: 1,
  metric: 'rmse',
  n_folds: 2
});
const compareResult = ref<any>(null);

// 图表引用
const fitChartRef = ref<HTMLElement | null>(null);
let fitChart: echarts.ECharts | null = null;

// API请求函数
const fetchApi = async (url: string, options: any = {}) => {
  isLoading.value = true;
  error.value = '';
  
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || `请求失败: ${response.status}`);
    }
    
    return await response.json();
  } catch (err: any) {
    error.value = err.message;
    throw err;
  } finally {
    isLoading.value = false;
  }
};

// 获取单个股票线性拟合分析
const getSingleLinearFit = async () => {
  if (!singleParams.value.symbol) {
    error.value = '请选择股票代码';
    return;
  }
  
  try {
    const params = new URLSearchParams({
      symbol: singleParams.value.symbol,
      poly: singleParams.value.poly.toString(),
      metric: singleParams.value.metric,
      n_folds: singleParams.value.n_folds.toString()
    });
    
    const result = await fetchApi(`/api/moA/linear-fit/single?${params}`);
    singleResult.value = result;
    
    // 绘制拟合图表
    await nextTick();
    drawFitChart(result);
  } catch (err) {
    console.error('获取单个股票线性拟合分析失败:', err);
  }
};

// 获取最佳多项式拟合次数
const getBestPoly = async () => {
  if (!bestPolyParams.value.symbol) {
    error.value = '请选择股票代码';
    return;
  }
  
  if (bestPolyParams.value.poly_min >= bestPolyParams.value.poly_max) {
    error.value = '最小多项式次数必须小于最大多项式次数';
    return;
  }
  
  try {
    const params = new URLSearchParams({
      symbol: bestPolyParams.value.symbol,
      poly_min: bestPolyParams.value.poly_min.toString(),
      poly_max: bestPolyParams.value.poly_max.toString(),
      metric: bestPolyParams.value.metric,
      n_folds: bestPolyParams.value.n_folds.toString()
    });
    
    const result = await fetchApi(`/api/moA/linear-fit/best-poly?${params}`);
    bestPolyResult.value = result;
  } catch (err) {
    console.error('获取最佳多项式拟合次数失败:', err);
  }
};

// 获取多只股票线性拟合比较
const getCompareLinearFit = async () => {
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
    
    const result = await fetchApi('/api/moA/linear-fit/compare', {
      method: 'POST',
      body: JSON.stringify({
        symbols: symbols,
        poly: compareParams.value.poly,
        metric: compareParams.value.metric,
        n_folds: compareParams.value.n_folds
      })
    });
    
    compareResult.value = result;
  } catch (err) {
    console.error('获取多只股票线性拟合比较失败:', err);
  }
};

// 绘制拟合图表
const drawFitChart = (result: any) => {
  if (!fitChartRef.value) return;
  
  // 初始化图表
  if (!fitChart) {
    fitChart = echarts.init(fitChartRef.value);
  }
  
  // 准备数据
  const dates = result.x.map((x: number, index: number) => {
    const date = new Date(x);
    return date.toLocaleDateString();
  });
  
  const option = {
    title: {
      text: `${result.symbol} 股价拟合结果`,
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
      data: ['实际股价', '拟合曲线'],
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
    series: [
      {
        name: '实际股价',
        type: 'line',
        data: result.y,
        smooth: true,
        lineStyle: {
          width: 2,
          color: '#409eff'
        },
        itemStyle: {
          color: '#409eff'
        }
      },
      {
        name: '拟合曲线',
        type: 'line',
        data: result.predicted,
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
  
  fitChart.setOption(option);
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

const selectBestPolySymbol = (symbol: string) => {
  bestPolyParams.value.symbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  singleParams.value.symbol = symbolSearchText.value;
  bestPolyParams.value.symbol = symbolSearchText.value;
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
    const response = await fetch('/api/moA/data/download/symbols');
    if (response.ok) {
      const data = await response.json();
      symbolsList.value = data;
    } else {
      // 如果API请求失败，使用默认股票列表
      symbolsList.value = [
        { symbol: 'sh600000', market: 'cn' },
        { symbol: 'sh600036', market: 'cn' },
        { symbol: 'sh600519', market: 'cn' },
        { symbol: 'sz000001', market: 'cn' },
        { symbol: 'sz000858', market: 'cn' }
      ];
    }
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
  }
};

// 窗口大小变化时调整图表大小
const handleResize = () => {
  if (fitChart) {
    fitChart.resize();
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
  if (fitChart) {
    fitChart.dispose();
    fitChart = null;
  }
});

// 监听singleResult变化，重新绘制图表
watch(() => singleResult.value, (newVal) => {
  if (newVal) {
    nextTick(() => {
      drawFitChart(newVal);
    });
  }
});
</script>

<style scoped>
.linear-fit-container {
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

.result-item.highlight {
  background-color: rgba(64, 158, 255, 0.1);
  padding: 10px;
  border-radius: 4px;
  margin-top: 10px;
}

.result-item.highlight .value {
  color: #409eff;
  font-size: 18px;
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

.valid {
  color: #67c23a;
  font-weight: 600;
}

.invalid {
  color: #f56c6c;
  font-weight: 600;
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