<template>
  <div class="price-change-container">
    <h2>涨跌幅分析</h2>
    
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
      <!-- 单个股票涨跌幅 -->
      <div v-if="activeTab === 'single'" class="tab-pane">
        <h3>单个股票涨跌幅分析</h3>
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
                <!-- 隐藏的select元素，用于表单提交 -->
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
              <label for="single-period">时间周期</label>
              <select id="single-period" v-model="singleParams.period">
                <option value="1d">日K</option>
                <option value="1w">周K</option>
                <option value="1m">月K</option>
              </select>
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getSinglePriceChange" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '分析涨跌幅' }}
            </button>
          </div>
        </div>
        
        <div v-if="singleResult" class="result-section">
          <h4>分析结果</h4>
          <div class="result-card">
            <div class="result-item">
              <span class="label">股票代码：</span>
              <span class="value">{{ singleResult.symbol }}</span>
            </div>
            <div class="result-item">
              <span class="label">时间周期：</span>
              <span class="value">{{ periodLabelMap[singleResult.period] }}</span>
            </div>
            <div class="result-item">
              <span class="label">最新价格：</span>
              <span class="value">{{ singleResult.latest_price.toFixed(2) }}</span>
            </div>
            <div class="result-item">
              <span class="label">起始价格：</span>
              <span class="value">{{ singleResult.start_price.toFixed(2) }}</span>
            </div>
            
            <!-- 统计信息 -->
            <div class="result-subsection">
              <h5>统计信息</h5>
              <div class="result-grid">
                <div class="result-item">
                  <span class="label">总交易天数：</span>
                  <span class="value">{{ singleResult.stats.total_days }}</span>
                </div>
                <div class="result-item highlight">
                  <span class="label">总收益率：</span>
                  <span class="value">{{ singleResult.stats.total_return.toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">平均涨跌幅：</span>
                  <span class="value">{{ singleResult.stats.avg_change.toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">最大涨幅：</span>
                  <span class="value">{{ singleResult.stats.max_change.toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">最大跌幅：</span>
                  <span class="value">{{ singleResult.stats.min_change.toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">上涨天数：</span>
                  <span class="value">{{ singleResult.stats.positive_days }}</span>
                </div>
                <div class="result-item">
                  <span class="label">下跌天数：</span>
                  <span class="value">{{ singleResult.stats.negative_days }}</span>
                </div>
                <div class="result-item">
                  <span class="label">平盘天数：</span>
                  <span class="value">{{ singleResult.stats.zero_days }}</span>
                </div>
              </div>
            </div>
            
            <!-- 最近N天涨跌幅 -->
            <div class="result-subsection">
              <h5>最近N天涨跌幅</h5>
              <div class="result-grid">
                <div class="result-item">
                  <span class="label">5天：</span>
                  <span class="value">{{ singleResult.recent_days['5_days'].toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">10天：</span>
                  <span class="value">{{ singleResult.recent_days['10_days'].toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">30天：</span>
                  <span class="value">{{ singleResult.recent_days['30_days'].toFixed(2) }}%</span>
                </div>
                <div class="result-item">
                  <span class="label">60天：</span>
                  <span class="value">{{ singleResult.recent_days['60_days'].toFixed(2) }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 两只股票涨跌幅对比 -->
      <div v-else-if="activeTab === 'pair'" class="tab-pane">
        <h3>两只股票涨跌幅对比</h3>
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
                <!-- 隐藏的select元素，用于表单提交 -->
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
                <!-- 隐藏的select元素，用于表单提交 -->
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
              <label for="pair-period">时间周期</label>
              <select id="pair-period" v-model="pairParams.period">
                <option value="1d">日K</option>
                <option value="1w">周K</option>
                <option value="1m">月K</option>
              </select>
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getPairPriceChange" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算对比分析' }}
            </button>
          </div>
        </div>
        
        <div v-if="pairResult" class="result-section">
          <h4>对比结果</h4>
          <div class="result-item">
            <span class="label">时间周期：</span>
            <span class="value">{{ periodLabelMap[pairResult.period] }}</span>
          </div>
          <div class="result-cards">
            <div class="result-card">
              <h5>{{ pairResult.symbol }}</h5>
              <!-- 基本信息 -->
              <div class="result-item">
                <span class="label">最新价格：</span>
                <span class="value">{{ pairResult.symbol_change.latest_price.toFixed(2) }}</span>
              </div>
              <!-- 核心统计信息 -->
              <div class="result-subsection">
                <h6>核心统计</h6>
                <div class="result-grid">
                  <div class="result-item highlight">
                    <span class="label">总收益率：</span>
                    <span class="value">{{ pairResult.symbol_change.stats.total_return.toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">平均涨跌幅：</span>
                    <span class="value">{{ pairResult.symbol_change.stats.avg_change.toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">最大涨幅：</span>
                    <span class="value">{{ pairResult.symbol_change.stats.max_change.toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">最大跌幅：</span>
                    <span class="value">{{ pairResult.symbol_change.stats.min_change.toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
              <!-- 最近N天涨跌幅 -->
              <div class="result-subsection">
                <h6>最近涨跌幅</h6>
                <div class="result-grid">
                  <div class="result-item">
                    <span class="label">5天：</span>
                    <span class="value">{{ pairResult.symbol_change.recent_days['5_days'].toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">30天：</span>
                    <span class="value">{{ pairResult.symbol_change.recent_days['30_days'].toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">60天：</span>
                    <span class="value">{{ pairResult.symbol_change.recent_days['60_days'].toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="result-card">
              <h5>{{ pairResult.benchmark_symbol }}</h5>
              <!-- 基本信息 -->
              <div class="result-item">
                <span class="label">最新价格：</span>
                <span class="value">{{ pairResult.benchmark_change.latest_price.toFixed(2) }}</span>
              </div>
              <!-- 核心统计信息 -->
              <div class="result-subsection">
                <h6>核心统计</h6>
                <div class="result-grid">
                  <div class="result-item highlight">
                    <span class="label">总收益率：</span>
                    <span class="value">{{ pairResult.benchmark_change.stats.total_return.toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">平均涨跌幅：</span>
                    <span class="value">{{ pairResult.benchmark_change.stats.avg_change.toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">最大涨幅：</span>
                    <span class="value">{{ pairResult.benchmark_change.stats.max_change.toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">最大跌幅：</span>
                    <span class="value">{{ pairResult.benchmark_change.stats.min_change.toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
              <!-- 最近N天涨跌幅 -->
              <div class="result-subsection">
                <h6>最近涨跌幅</h6>
                <div class="result-grid">
                  <div class="result-item">
                    <span class="label">5天：</span>
                    <span class="value">{{ pairResult.benchmark_change.recent_days['5_days'].toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">30天：</span>
                    <span class="value">{{ pairResult.benchmark_change.recent_days['30_days'].toFixed(2) }}%</span>
                  </div>
                  <div class="result-item">
                    <span class="label">60天：</span>
                    <span class="value">{{ pairResult.benchmark_change.recent_days['60_days'].toFixed(2) }}%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 多只股票涨跌幅对比 -->
      <div v-else-if="activeTab === 'multi'" class="tab-pane">
        <h3>多只股票涨跌幅对比</h3>
        <div class="form-section">
          <div class="form-grid">
            <div class="form-group full-width">
              <label for="multi-symbols">股票代码（逗号分隔）</label>
              <textarea 
                id="multi-symbols" 
                v-model="multiParams.symbolsText"
                placeholder="例如：sh600000,sh600036,sz000001,sz000858"
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="multi-period">时间周期</label>
              <select id="multi-period" v-model="multiParams.period">
                <option value="1d">日K</option>
                <option value="1w">周K</option>
                <option value="1m">月K</option>
              </select>
            </div>
          </div>
          <div class="buttons-group">
            <button 
              class="btn-primary" 
              @click="getMultiPriceChange" 
              :disabled="isLoading"
            >
              {{ isLoading ? '计算中...' : '计算多股分析' }}
            </button>
          </div>
        </div>
        
        <div v-if="multiResult" class="result-section">
          <h4>对比结果</h4>
          <div class="result-item">
            <span class="label">时间周期：</span>
            <span class="value">{{ periodLabelMap[multiResult.period] }}</span>
          </div>
          <div class="result-table-container">
            <table class="result-table">
              <thead>
                <tr>
                  <th>股票代码</th>
                  <th>最新价格</th>
                  <th>总收益率</th>
                  <th>平均涨跌幅</th>
                  <th>最大涨幅</th>
                  <th>最大跌幅</th>
                  <th>5天涨跌幅</th>
                  <th>30天涨跌幅</th>
                  <th>60天涨跌幅</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in multiResult.results" :key="item.symbol">
                  <td>{{ item.symbol }}</td>
                  <td>{{ item.latest_price.toFixed(2) }}</td>
                  <td>{{ item.total_return.toFixed(2) }}%</td>
                  <td>{{ item.avg_change.toFixed(2) }}%</td>
                  <td>{{ item.max_change.toFixed(2) }}%</td>
                  <td>{{ item.min_change.toFixed(2) }}%</td>
                  <td>{{ item.recent_days['5_days'].toFixed(2) }}%</td>
                  <td>{{ item.recent_days['30_days'].toFixed(2) }}%</td>
                  <td>{{ item.recent_days['60_days'].toFixed(2) }}%</td>
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
const activeTab = ref('single');
const isLoading = ref(false);
const error = ref('');

// 周期标签映射
const periodLabelMap = {
  '1d': '日K',
  '1w': '周K',
  '1m': '月K'
};

// 标签页配置
const tabs = [
  { id: 'single', name: '单个股票' },
  { id: 'pair', name: '两只股票对比' },
  { id: 'multi', name: '多只股票对比' }
];

// 单个股票参数
const singleParams = ref({
  symbol: '',
  period: '1d' // 新增：时间周期参数
});
const singleResult = ref<any>(null);

// 两只股票参数
const pairParams = ref({
  symbol: '',
  benchmark_symbol: '',
  period: '1d' // 新增：时间周期参数
});
const pairResult = ref<any>(null);

// 多只股票参数
const multiParams = ref({
  symbolsText: '',
  period: '1d' // 新增：时间周期参数
});
const multiResult = ref<any>(null);

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

// 获取单个股票涨跌幅分析
const getSinglePriceChange = async () => {
  if (!singleParams.value.symbol) {
    error.value = '请选择股票代码';
    return;
  }
  
  try {
    const params = new URLSearchParams({
      symbol: singleParams.value.symbol,
      period: singleParams.value.period // 新增：传递时间周期参数
    });
    
    const result = await fetchApi(`/api/moA/price-change/single?${params}`);
    singleResult.value = result;
  } catch (err) {
    console.error('获取单个股票涨跌幅分析失败:', err);
  }
};

// 获取两只股票涨跌幅对比
const getPairPriceChange = async () => {
  if (!pairParams.value.symbol || !pairParams.value.benchmark_symbol) {
    error.value = '请选择两只股票的代码';
    return;
  }
  
  try {
    const params = new URLSearchParams({
      symbol: pairParams.value.symbol,
      benchmark_symbol: pairParams.value.benchmark_symbol,
      period: pairParams.value.period // 新增：传递时间周期参数
    });
    
    const result = await fetchApi(`/api/moA/price-change/pair?${params}`);
    pairResult.value = result;
  } catch (err) {
    console.error('获取两只股票涨跌幅对比失败:', err);
  }
};

// 获取多只股票涨跌幅对比
const getMultiPriceChange = async () => {
  if (!multiParams.value.symbolsText) {
    error.value = '请输入股票代码列表';
    return;
  }
  
  try {
    const symbols = multiParams.value.symbolsText
      .split(',')
      .map(s => s.trim())
      .filter(s => s);
    
    if (symbols.length === 0) {
      error.value = '请输入有效的股票代码';
      return;
    }
    
    const result = await fetchApi('/api/moA/price-change/multi', {
      method: 'POST',
      body: JSON.stringify({
        symbols: symbols,
        period: multiParams.value.period // 新增：传递时间周期参数
      })
    });
    
    multiResult.value = result;
  } catch (err) {
    console.error('获取多只股票涨跌幅对比失败:', err);
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
  singleParams.value.symbol = symbol;
  pairParams.value.symbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

const selectBenchmarkSymbol = (symbol: string) => {
  pairParams.value.benchmark_symbol = symbol;
  benchmarkSymbolSearchText.value = symbol;
  isBenchmarkSelectOpen.value = false;
};

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  // 当用户在输入框中输入时，更新symbol值
  singleParams.value.symbol = symbolSearchText.value;
  pairParams.value.symbol = symbolSearchText.value;
};

const onBenchmarkSymbolInput = () => {
  // 当用户在输入框中输入时，更新benchmark_symbol值
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
.price-change-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  animation: fadeIn 0.8s ease-out;
}

/* 标签页样式 */
.tabs {
  display: flex;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-light);
  background: white;
  padding: 4px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  gap: 4px;
}

.tab-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-secondary);
  border-radius: 8px;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
  flex: 1;
  min-width: 120px;
}

.tab-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 0;
  height: 100%;
  background: var(--gradient-primary);
  opacity: 0;
  transition: all var(--transition-normal);
  z-index: -1;
}

.tab-btn:hover {
  color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.tab-btn.active {
  color: white;
  background: var(--gradient-primary);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.tab-btn.active::before {
  width: 100%;
  opacity: 1;
}

/* 标签页内容 */
.tab-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  animation: fadeInUp 0.6s ease-out 0.2s both;
}

/* 表单区域 */
.form-section {
  margin-bottom: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  animation: fadeIn 0.6s ease-out 0.3s both;
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
  padding: 12px 40px 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
  transition: all var(--transition-normal);
  background: white;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
  transform: translateY(-2px);
}

.select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--text-tertiary);
  transition: all var(--transition-normal);
  font-size: 18px;
}

.select-arrow.active {
  transform: translateY(-50%) rotate(180deg);
  color: var(--primary-color);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background-color: white;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  display: none;
  overflow-y: auto;
  max-height: 300px;
  margin-top: 8px;
  animation: fadeInDown 0.3s ease-out;
}

.select-dropdown.open {
  display: block;
}

.select-options {
  padding: 8px 0;
}

.select-option {
  padding: 12px 16px;
  cursor: pointer;
  transition: all var(--transition-normal);
  color: var(--text-primary);
  font-size: 14px;
  border-radius: 4px;
  margin: 0 8px;
}

.select-option:hover {
  background-color: var(--bg-tertiary);
  color: var(--primary-color);
  transform: translateX(4px);
}

.select-option.selected {
  background: var(--bg-tertiary);
  color: var(--primary-color);
  font-weight: 600;
  border-left: 4px solid var(--primary-color);
  transform: translateX(4px);
}

.hidden-select {
  display: none;
}

/* 按钮组 */
.buttons-group {
  display: flex;
  gap: 12px;
  margin-top: 24px;
  animation: fadeInUp 0.6s ease-out 0.4s both;
}

/* 结果区域 */
.result-section {
  margin-top: 32px;
  padding-top: 24px;
  border-top: 2px dashed var(--border-light);
  animation: fadeInUp 0.6s ease-out 0.5s both;
}

.result-card {
  background: white;
  padding: 24px;
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-light);
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.result-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: var(--gradient-primary);
}

.result-card:hover {
  box-shadow: var(--shadow-lg);
  transform: translateY(-4px);
  border-color: var(--primary-color);
}

.result-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.result-card h5 {
  margin-top: 0;
  margin-bottom: 20px;
  color: var(--text-primary);
  font-size: 20px;
  font-weight: 700;
  padding-left: 16px;
}

.result-item {
  display: flex;
  margin-bottom: 16px;
  align-items: center;
  padding-left: 16px;
}

.result-item .label {
  font-weight: 600;
  color: var(--text-secondary);
  margin-right: 12px;
  min-width: 120px;
  font-size: 14px;
}

.result-item .value {
  color: var(--text-primary);
  font-weight: 700;
  font-size: 16px;
  transition: all var(--transition-normal);
}

.result-item.highlight {
  background: linear-gradient(135deg, rgba(64, 158, 255, 0.1) 0%, rgba(103, 194, 58, 0.1) 100%);
  padding: 16px;
  border-radius: 8px;
  margin: 12px 0 12px 16px;
  border: 1px solid rgba(64, 158, 255, 0.2);
  animation: pulse 2s infinite;
}

.result-item.highlight .value {
  color: var(--primary-color);
  font-size: 20px;
}

/* 表格样式 */
.result-table-container {
  overflow-x: auto;
  margin-top: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.result-table th,
.result-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid var(--border-light);
  transition: all var(--transition-normal);
}

.result-table th {
  background: var(--bg-secondary);
  font-weight: 700;
  color: var(--text-primary);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: sticky;
  top: 0;
  z-index: 100;
}

.result-table tr {
  transition: all var(--transition-normal);
}

.result-table tr:hover {
  background: var(--bg-tertiary);
  transform: translateX(4px);
  box-shadow: inset 4px 0 0 var(--primary-color);
}

.result-table tr:last-child td {
  border-bottom: none;
}

/* 结果子区域 */
.result-subsection {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px dashed var(--border-light);
  padding-left: 16px;
}

.result-subsection h5 {
  margin-top: 0;
  margin-bottom: 16px;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
  padding-left: 0;
}

.result-subsection h6 {
  margin-top: 0;
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 16px;
  font-weight: 600;
  padding-left: 0;
}

/* 结果网格布局 */
.result-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.result-grid .result-item {
  margin-bottom: 0;
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 8px;
  border: 1px solid var(--border-light);
  transition: all var(--transition-normal);
  margin-left: 0;
  padding-left: 12px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
}

.result-grid .result-item:hover {
  background: var(--bg-tertiary);
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.result-grid .result-item .label {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-right: 0;
  font-weight: 500;
  min-width: auto;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-grid .result-item .value {
  font-size: 18px;
  color: var(--text-primary);
  font-weight: 700;
}

/* 错误消息 */
.error-message {
  margin-top: 24px;
  padding: 16px;
  background: linear-gradient(135deg, rgba(245, 108, 108, 0.1) 0%, rgba(245, 108, 108, 0.05) 100%);
  color: var(--accent-color);
  border-radius: 8px;
  font-size: 14px;
  border: 1px solid rgba(245, 108, 108, 0.2);
  animation: fadeIn 0.6s ease-out;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .price-change-container {
    padding: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .result-cards {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .result-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .tabs {
    flex-direction: column;
    gap: 8px;
  }
  
  .tab-btn {
    min-width: auto;
    width: 100%;
  }
  
  .tab-content {
    padding: 16px;
  }
}
</style>
