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

.result-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.result-card h5 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #333;
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

/* 新增：结果子区域样式 */
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

.result-subsection h6 {
  margin-top: 0;
  margin-bottom: 8px;
  color: #555;
  font-size: 14px;
  font-weight: 500;
}

/* 新增：结果网格布局 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .result-cards {
    grid-template-columns: 1fr;
  }
  
  .result-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}
</style>
