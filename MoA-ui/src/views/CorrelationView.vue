<template>
  <div class="correlation-container">
    <h2>相关性分析</h2>
    
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
      <!-- 两只股票相关性分析 -->
      <div v-if="activeTab === 'pair'" class="tab-pane">
        <h3>两只股票相关性分析</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group">
              <label for="pair-symbol">股票代码</label>
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
                      :class="{ 'selected': pairParams.symbol === item.symbol }"
                      @click="selectSymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
                <select 
                  id="pair-symbol" 
                  v-model="pairParams.symbol"
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
              <label for="pair-benchmark">基准股票</label>
              <div class="searchable-select">
                <div class="select-header" @click="toggleBenchmarkSelect($event)">
                  <input 
                    type="text" 
                    class="search-input" 
                    v-model="benchmarkSymbolSearchText" 
                    placeholder="搜索基准股票代码或名称..."
                    @focus="openBenchmarkSelect"
                    @click="$event.stopPropagation(); openBenchmarkSelect()"
                    @input="onBenchmarkSymbolInput"
                  />
                  <span 
                    class="select-arrow" 
                    :class="{ 'active': isBenchmarkSelectOpen }"
                    @click="toggleBenchmarkSelect($event)"
                  >▼</span>
                </div>
                <div 
                  class="select-dropdown" 
                  :class="{ 'open': isBenchmarkSelectOpen }"
                >
                  <div class="select-options">
                    <div 
                      v-for="item in filteredBenchmarkSymbols" 
                      :key="item.symbol"
                      class="select-option"
                      :class="{ 'selected': pairParams.benchmark_symbol === item.symbol }"
                      @click="selectBenchmarkSymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
                <select 
                  id="pair-benchmark" 
                  v-model="pairParams.benchmark_symbol"
                  class="hidden-select"
                >
                  <option value="">请选择基准股票代码</option>
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
              <label for="pair-corr-type">相关系数类型</label>
              <select id="pair-corr-type" v-model="pairParams.corr_type">
                <option value="pears">皮尔逊相关系数</option>
                <option value="sperm">斯皮尔曼相关系数</option>
                <option value="sign">序列正负符号相关系数</option>
              </select>
            </div>
            <div class="form-group">
              <label for="pair-n-folds">数据周期（年）</label>
              <input 
                type="number" 
                id="pair-n-folds" 
                v-model.number="pairParams.n_folds" 
                min="1" 
                max="5"
                step="1"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getPairCorrelation" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算相关性' }}
            </button>
          </div>
        </div>
        
        <div v-if="pairResult" class="result-section">
          <h4>相关性分析结果</h4>
          <div class="result-card">
            <div class="result-item">
              <span class="label">相关系数类型：</span>
              <span class="value">{{ corrTypeLabelMap[pairResult.corr_type] }}</span>
            </div>
            <div class="result-item highlight">
              <span class="label">相关系数：</span>
              <span class="value">{{ pairResult.correlation.toFixed(4) }}</span>
            </div>
            <div class="result-item">
              <span class="label">数据点数量：</span>
              <span class="value">{{ pairResult.data_points }}</span>
            </div>
            
            <!-- 滚动相关系数 -->
            <div v-if="Object.keys(pairResult.rolling_correlations).length > 0" class="result-subsection">
              <h5>不同时间窗口滚动相关系数</h5>
              <div class="result-grid">
                <div v-for="(corr, window) in pairResult.rolling_correlations" :key="window" class="result-item">
                  <span class="label">{{ window.replace('window_', '') }}天：</span>
                  <span class="value">{{ corr.toFixed(4) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 多只股票相关性矩阵 -->
      <div v-else-if="activeTab === 'matrix'" class="tab-pane">
        <h3>多只股票相关性矩阵</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="matrix-symbols">股票代码（逗号分隔）</label>
              <textarea 
                id="matrix-symbols" 
                v-model="matrixParams.symbolsText"
                placeholder="例如：sh600000,sh600036,sh600519,sz000001,sz000858"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="matrix-corr-type">相关系数类型</label>
              <select id="matrix-corr-type" v-model="matrixParams.corr_type">
                <option value="pears">皮尔逊相关系数</option>
                <option value="sperm">斯皮尔曼相关系数</option>
                <option value="sign">序列正负符号相关系数</option>
              </select>
            </div>
            <div class="form-group">
              <label for="matrix-n-folds">数据周期（年）</label>
              <input 
                type="number" 
                id="matrix-n-folds" 
                v-model.number="matrixParams.n_folds" 
                min="1" 
                max="5"
                step="1"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getMatrixCorrelation" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算相关性矩阵' }}
            </button>
          </div>
        </div>
        
        <div v-if="matrixResult" class="result-section">
          <h4>相关性矩阵</h4>
          <div class="result-item">
            <span class="label">相关系数类型：</span>
            <span class="value">{{ corrTypeLabelMap[matrixResult.corr_type] }}</span>
          </div>
          <div class="matrix-container">
            <table class="correlation-matrix">
              <thead>
                <tr>
                  <th></th>
                  <th v-for="symbol in matrixResult.symbols" :key="symbol">{{ symbol }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="symbol in matrixResult.symbols" :key="symbol">
                  <td class="symbol-label">{{ symbol }}</td>
                  <td 
                    v-for="benchmark in matrixResult.symbols" 
                    :key="benchmark"
                    :class="['correlation-cell', getCorrelationClass(matrixResult.correlation_matrix[symbol][benchmark])]"
                  >
                    {{ matrixResult.correlation_matrix[symbol][benchmark].toFixed(3) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="correlation-legend">
            <h5>相关性颜色说明</h5>
            <div class="legend-items">
              <div class="legend-item">
                <span class="legend-color strong-positive"></span>
                <span class="legend-text">强正相关 (0.8 - 1.0)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color positive"></span>
                <span class="legend-text">正相关 (0.5 - 0.8)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color weak-positive"></span>
                <span class="legend-text">弱正相关 (0.2 - 0.5)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color neutral"></span>
                <span class="legend-text">中性 (-0.2 - 0.2)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color weak-negative"></span>
                <span class="legend-text">弱负相关 (-0.5 - -0.2)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color negative"></span>
                <span class="legend-text">负相关 (-0.8 - -0.5)</span>
              </div>
              <div class="legend-item">
                <span class="legend-color strong-negative"></span>
                <span class="legend-text">强负相关 (-1.0 - -0.8)</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 相似股票查找 -->
      <div v-else-if="activeTab === 'similar'" class="tab-pane">
        <h3>相似股票查找</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group">
              <label for="similar-symbol">股票代码</label>
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
                      :class="{ 'selected': similarParams.symbol === item.symbol }"
                      @click="selectSimilarSymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
                <select 
                  id="similar-symbol" 
                  v-model="similarParams.symbol"
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
              <label for="similar-top-n">返回数量</label>
              <input 
                type="number" 
                id="similar-top-n" 
                v-model.number="similarParams.top_n" 
                min="1" 
                max="20"
                step="1"
              />
            </div>
            <div class="form-group">
              <label for="similar-n-folds">数据周期（年）</label>
              <input 
                type="number" 
                id="similar-n-folds" 
                v-model.number="similarParams.n_folds" 
                min="1" 
                max="5"
                step="1"
              />
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getSimilarStocks" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '查找相似股票' }}
            </button>
          </div>
        </div>
        
        <div v-if="similarResult" class="result-section">
          <h4>相似股票列表</h4>
          <div class="result-item">
            <span class="label">基准股票：</span>
            <span class="value">{{ similarResult.symbol }}</span>
          </div>
          <div class="similar-stocks-list">
            <table class="result-table">
              <thead>
                <tr>
                  <th>排名</th>
                  <th>股票代码</th>
                  <th>股票名称</th>
                  <th>相关系数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stock in similarResult.similar_stocks" :key="stock.symbol">
                  <td>{{ stock.rank }}</td>
                  <td>{{ stock.symbol }}</td>
                  <td>{{ stock.name || '-' }}</td>
                  <td 
                    :class="['correlation-value', getCorrelationClass(stock.correlation)]"
                  >
                    {{ stock.correlation.toFixed(4) }}
                  </td>
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
import { ref, computed, onMounted, onUnmounted } from 'vue';

// 状态管理
const activeTab = ref('pair');
const isLoading = ref(false);
const error = ref('');

// 标签页配置
const tabs = [
  { id: 'pair', name: '两只股票相关性' },
  { id: 'matrix', name: '多只股票相关性矩阵' },
  { id: 'similar', name: '相似股票查找' }
];

// 相关系数类型标签映射
const corrTypeLabelMap = {
  'pears': '皮尔逊相关系数',
  'sperm': '斯皮尔曼相关系数',
  'sign': '序列正负符号相关系数'
};

// 两只股票参数
const pairParams = ref({
  symbol: '',
  benchmark_symbol: '',
  corr_type: 'pears',
  n_folds: 2
});
const pairResult = ref<any>(null);

// 多只股票参数
const matrixParams = ref({
  symbolsText: '',
  corr_type: 'pears',
  n_folds: 2
});
const matrixResult = ref<any>(null);

// 相似股票参数
const similarParams = ref({
  symbol: '',
  top_n: 5,
  n_folds: 2
});
const similarResult = ref<any>(null);

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

// 获取两只股票相关性
const getPairCorrelation = async () => {
  if (!pairParams.value.symbol || !pairParams.value.benchmark_symbol) {
    error.value = '请选择两只股票代码';
    return;
  }
  
  try {
    const params = new URLSearchParams({
      symbol: pairParams.value.symbol,
      benchmark_symbol: pairParams.value.benchmark_symbol,
      corr_type: pairParams.value.corr_type,
      n_folds: pairParams.value.n_folds.toString()
    });
    
    const result = await fetchApi(`/api/moA/correlation/pair?${params}`);
    pairResult.value = result;
  } catch (err) {
    console.error('获取两只股票相关性分析失败:', err);
  }
};

// 获取多只股票相关性矩阵
const getMatrixCorrelation = async () => {
  if (!matrixParams.value.symbolsText) {
    error.value = '请输入股票代码列表';
    return;
  }
  
  try {
    const symbols = matrixParams.value.symbolsText
      .split(',')
      .map(s => s.trim())
      .filter(s => s);
    
    if (symbols.length < 2) {
      error.value = '请输入至少两只股票代码';
      return;
    }
    
    const result = await fetchApi('/api/moA/correlation/matrix', {
      method: 'POST',
      body: JSON.stringify({
        symbols: symbols,
        corr_type: matrixParams.value.corr_type,
        n_folds: matrixParams.value.n_folds
      })
    });
    
    matrixResult.value = result;
  } catch (err) {
    console.error('获取多只股票相关性矩阵失败:', err);
  }
};

// 获取相似股票
const getSimilarStocks = async () => {
  if (!similarParams.value.symbol) {
    error.value = '请选择股票代码';
    return;
  }
  
  try {
    const params = new URLSearchParams({
      symbol: similarParams.value.symbol,
      top_n: similarParams.value.top_n.toString(),
      n_folds: similarParams.value.n_folds.toString()
    });
    
    const result = await fetchApi(`/api/moA/correlation/similar?${params}`);
    similarResult.value = result;
  } catch (err) {
    console.error('查找相似股票失败:', err);
  }
};

// 获取相关性单元格样式类
const getCorrelationClass = (correlation: number) => {
  if (correlation >= 0.8) {
    return 'strong-positive';
  } else if (correlation >= 0.5) {
    return 'positive';
  } else if (correlation >= 0.2) {
    return 'weak-positive';
  } else if (correlation >= -0.2) {
    return 'neutral';
  } else if (correlation >= -0.5) {
    return 'weak-negative';
  } else if (correlation >= -0.8) {
    return 'negative';
  } else {
    return 'strong-negative';
  }
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
const benchmarkSymbolSearchText = ref('');

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

// 过滤后的基准股票列表
const filteredBenchmarkSymbols = computed(() => {
  if (!benchmarkSymbolSearchText.value) {
    return symbolsList.value;
  }
  
  const searchText = benchmarkSymbolSearchText.value.toLowerCase();
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
const isBenchmarkSelectOpen = ref(false);

// 打开下拉框
const openSelect = () => {
  isSelectOpen.value = true;
  isBenchmarkSelectOpen.value = false;
};

const openBenchmarkSelect = () => {
  isBenchmarkSelectOpen.value = true;
  isSelectOpen.value = false;
};

// 切换下拉框显示状态
const toggleSelect = (event?: MouseEvent) => {
  if (event) {
    event.stopPropagation();
  }
  isSelectOpen.value = !isSelectOpen.value;
  if (isSelectOpen.value) {
    isBenchmarkSelectOpen.value = false;
  }
};

const toggleBenchmarkSelect = (event?: MouseEvent) => {
  if (event) {
    event.stopPropagation();
  }
  isBenchmarkSelectOpen.value = !isBenchmarkSelectOpen.value;
  if (isBenchmarkSelectOpen.value) {
    isSelectOpen.value = false;
  }
};

// 选择股票
const selectSymbol = (symbol: string) => {
  pairParams.value.symbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

const selectBenchmarkSymbol = (symbol: string) => {
  pairParams.value.benchmark_symbol = symbol;
  benchmarkSymbolSearchText.value = symbol;
  isBenchmarkSelectOpen.value = false;
};

const selectSimilarSymbol = (symbol: string) => {
  similarParams.value.symbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  pairParams.value.symbol = symbolSearchText.value;
  similarParams.value.symbol = symbolSearchText.value;
};

const onBenchmarkSymbolInput = () => {
  pairParams.value.benchmark_symbol = benchmarkSymbolSearchText.value;
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
    isBenchmarkSelectOpen.value = false;
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

// 生命周期钩子
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  fetchSymbolsList();
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.correlation-container {
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
}

.result-item .value {
  color: #333;
  font-weight: 600;
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

/* 结果子区域样式 */
.result-subsection {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px dashed #e0e0e0;
}

.result-subsection h5 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

/* 结果网格布局 */
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.result-grid .result-item {
  margin-bottom: 5px;
}

.result-grid .result-item .label {
  font-size: 12px;
  color: #666;
  margin-right: 5px;
}

.result-grid .result-item .value {
  font-size: 14px;
  color: #333;
  font-weight: 600;
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

/* 相关性矩阵样式 */
.matrix-container {
  overflow-x: auto;
  margin: 20px 0;
}

.correlation-matrix {
  border-collapse: collapse;
  width: 100%;
  background-color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.correlation-matrix th,
.correlation-matrix td {
  padding: 12px;
  text-align: center;
  border: 1px solid #e0e0e0;
  font-size: 14px;
}

.correlation-matrix th {
  background-color: #f5f7fa;
  font-weight: 600;
  color: #333;
  position: sticky;
  top: 0;
  z-index: 10;
}

.correlation-matrix .symbol-label {
  font-weight: 600;
  color: #333;
  background-color: #f5f7fa;
  position: sticky;
  left: 0;
  z-index: 5;
}

.correlation-cell {
  font-weight: 600;
  transition: all 0.3s ease;
}

/* 相关性颜色样式 */
.correlation-cell.strong-positive {
  background-color: #4caf50;
  color: white;
}

.correlation-cell.positive {
  background-color: #81c784;
  color: white;
}

.correlation-cell.weak-positive {
  background-color: #c8e6c9;
  color: #2e7d32;
}

.correlation-cell.neutral {
  background-color: #e0e0e0;
  color: #616161;
}

.correlation-cell.weak-negative {
  background-color: #ffccbc;
  color: #c62828;
}

.correlation-cell.negative {
  background-color: #ff8a65;
  color: white;
}

.correlation-cell.strong-negative {
  background-color: #f44336;
  color: white;
}

.correlation-value {
  font-weight: 600;
}

.correlation-value.strong-positive {
  color: #4caf50;
}

.correlation-value.positive {
  color: #66bb6a;
}

.correlation-value.weak-positive {
  color: #81c784;
}

.correlation-value.neutral {
  color: #9e9e9e;
}

.correlation-value.weak-negative {
  color: #ff7043;
}

.correlation-value.negative {
  color: #f44336;
}

.correlation-value.strong-negative {
  color: #d32f2f;
}

/* 相关性图例 */
.correlation-legend {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 8px;
}

.correlation-legend h5 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-color.strong-positive {
  background-color: #4caf50;
}

.legend-color.positive {
  background-color: #81c784;
}

.legend-color.weak-positive {
  background-color: #c8e6c9;
}

.legend-color.neutral {
  background-color: #e0e0e0;
}

.legend-color.weak-negative {
  background-color: #ffccbc;
}

.legend-color.negative {
  background-color: #ff8a65;
}

.legend-color.strong-negative {
  background-color: #f44336;
}

/* 表格样式 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .matrix-container {
    font-size: 12px;
  }
  
  .correlation-matrix th,
  .correlation-matrix td {
    padding: 8px;
  }
  
  .legend-items {
    flex-direction: column;
    gap: 10px;
  }
}
</style>