<template>
  <div class="ai-quant-workbench">
    <h1 class="page-title">AI量化交易工作台</h1>
    
    <!-- 功能选项卡 -->
    <div class="tab-container">
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'factor' }"
        @click="activeTab = 'factor'"
      >
        📊 因子计算
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'model' }"
        @click="activeTab = 'model'"
      >
        🧠 模型训练
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'orthogonal' }"
        @click="activeTab = 'orthogonal'"
      >
        🔄 因子正交化
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'market' }"
        @click="activeTab = 'market'"
      >
        🔍 市场状态识别
      </div>
      <div 
        class="tab-item" 
        :class="{ active: activeTab === 'weight' }"
        @click="activeTab = 'weight'"
      >
        ⚖️ 权重分配
      </div>
    </div>

    <!-- 因子计算选项卡 -->
    <div v-if="activeTab === 'factor'" class="tab-content">
      <div class="section-card">
        <h2 class="section-title">因子计算测试</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="stock-symbol">股票代码</label>
            <div class="searchable-select">
              <div class="select-header" @click="toggleSelect('factor', $event)">
                <input 
                  type="text" 
                  class="search-input" 
                  v-model="symbolSearchText" 
                  placeholder="搜索股票代码或名称..."
                  @focus="openSelect('factor')"
                  @click="$event.stopPropagation(); openSelect('factor')"
                  @input="onSymbolInput"
                />
                <span 
                  class="select-arrow" 
                  :class="{ 'active': isSelectOpen }"
                  @click="toggleSelect('factor', $event)"
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
                    :class="{ 'selected': factorParams.stockSymbol === item.symbol }"
                    @click="selectSymbol(item.symbol)"
                  >
                    {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                  </div>
                </div>
              </div>
              <!-- 隐藏的select元素，用于表单提交 -->
              <select 
                id="stock-symbol" 
                v-model="factorParams.stockSymbol"
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
            <label for="factor-type">因子类型</label>
            <select id="factor-type" v-model="factorParams.factorType">
              <option value="fundamental">基本面因子</option>
              <option value="alternative">另类数据因子</option>
              <option value="technical">技术因子</option>
            </select>
          </div>
          <div class="form-group">
            <label for="factor-list">选择因子</label>
            <select id="factor-list" v-model="factorParams.selectedFactors" multiple>
              <option value="pe">市盈率(PE)</option>
              <option value="pb">市净率(PB)</option>
              <option value="roe">净资产收益率(ROE)</option>
              <option value="roa">资产收益率(ROA)</option>
              <option value="revenue_growth">营收增长率</option>
              <option value="profit_growth">利润增长率</option>
              <option value="sentiment">新闻情绪</option>
              <option value="social_heat">社交媒体热度</option>
            </select>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="calculateFactors" :disabled="isCalculating">
              {{ isCalculating ? '计算中...' : '计算因子' }}
            </button>
            <button class="btn btn-secondary" @click="resetFactorParams">重置</button>
          </div>
        </div>
        
        <!-- 结果展示 -->
        <div v-if="factorResults.length > 0" class="results-container">
          <h3>计算结果</h3>
          <div class="results-table">
            <table>
              <thead>
                <tr>
                  <th>日期</th>
                  <th v-for="factor in factorParams.selectedFactors" :key="factor">
                    {{ factorMap[factor] }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(result, index) in factorResults" :key="index">
                  <td>{{ result.date }}</td>
                  <td v-for="factor in factorParams.selectedFactors" :key="factor">
                    {{ result[factor]?.toFixed(4) || '-' }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 模型训练选项卡 -->
    <div v-if="activeTab === 'model'" class="tab-content">
      <div class="section-card">
        <h2 class="section-title">深度学习模型训练与预测</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="model-type">模型类型</label>
            <select id="model-type" v-model="modelParams.modelType">
              <option value="lstm">LSTM</option>
              <option value="transformer">Transformer</option>
              <option value="cnn">CNN</option>
            </select>
          </div>
          <div class="form-group">
            <label for="training-days">训练天数</label>
            <input 
              id="training-days" 
              type="number" 
              v-model="modelParams.trainingDays" 
              min="30" 
              max="365"
            >
          </div>
          <div class="form-group">
            <label for="prediction-days">预测天数</label>
            <input 
              id="prediction-days" 
              type="number" 
              v-model="modelParams.predictionDays" 
              min="1" 
              max="30"
            >
          </div>
          <div class="form-group">
            <label>输入特征</label>
            <div class="checkbox-group">
              <label v-for="feature in modelFeatures" :key="feature.value">
                <input 
                  type="checkbox" 
                  v-model="modelParams.selectedFeatures" 
                  :value="feature.value"
                >
                {{ feature.label }}
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="trainModel" :disabled="isTraining">
              {{ isTraining ? '训练中...' : '训练模型' }}
            </button>
            <button class="btn btn-secondary" @click="resetModelParams">重置</button>
          </div>
        </div>
        
        <!-- 模型训练结果 -->
        <div v-if="modelResults" class="results-container">
          <h3>模型训练结果</h3>
          <div class="model-metrics">
            <div class="metric-item">
              <span class="metric-label">训练损失</span>
              <span class="metric-value">{{ modelResults.trainLoss?.toFixed(4) || '-' }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">验证损失</span>
              <span class="metric-value">{{ modelResults.valLoss?.toFixed(4) || '-' }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">准确率</span>
              <span class="metric-value">{{ (modelResults.accuracy * 100)?.toFixed(2) || '-' }}%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">R²得分</span>
              <span class="metric-value">{{ modelResults.r2Score?.toFixed(4) || '-' }}</span>
            </div>
          </div>
          
          <!-- 预测结果 -->
          <div v-if="modelResults.predictions" class="predictions-chart">
            <h4>价格预测结果</h4>
            <div class="chart-placeholder">
              <!-- 这里可以集成ECharts等图表库 -->
              <div class="chart-mock">
                <div class="chart-line actual"></div>
                <div class="chart-line predicted"></div>
                <div class="chart-legend">
                  <span><div class="legend-dot actual"></div>实际价格</span>
                  <span><div class="legend-dot predicted"></div>预测价格</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 因子正交化选项卡 -->
    <div v-if="activeTab === 'orthogonal'" class="tab-content">
      <div class="section-card">
        <h2 class="section-title">因子正交化处理</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="orthogonal-method">正交化方法</label>
            <select id="orthogonal-method" v-model="orthogonalParams.method">
              <option value="pca">PCA主成分分析</option>
              <option value="linear">线性回归</option>
              <option value="gram_schmidt">Gram-Schmidt</option>
            </select>
          </div>
          <div class="form-group">
            <label for="variance-threshold">方差阈值</label>
            <input 
              id="variance-threshold" 
              type="number" 
              v-model="orthogonalParams.varianceThreshold" 
              min="0.5" 
              max="1.0" 
              step="0.05"
            >
          </div>
          <div class="form-group">
            <label>选择因子</label>
            <div class="checkbox-group">
              <label v-for="factor in orthogonalFactors" :key="factor">
                <input 
                  type="checkbox" 
                  v-model="orthogonalParams.selectedFactors" 
                  :value="factor"
                >
                {{ factorMap[factor] }}
              </label>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="performOrthogonalization" :disabled="isOrthogonalizing">
              {{ isOrthogonalizing ? '处理中...' : '执行正交化' }}
            </button>
            <button class="btn btn-secondary" @click="resetOrthogonalParams">重置</button>
          </div>
        </div>
        
        <!-- 正交化结果 -->
        <div v-if="orthogonalResults" class="results-container">
          <h3>正交化结果</h3>
          <div class="orthogonal-metrics">
            <div class="metric-item">
              <span class="metric-label">保留主成分数</span>
              <span class="metric-value">{{ orthogonalResults.componentsCount }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">累计方差解释率</span>
              <span class="metric-value">{{ (orthogonalResults.cumulativeVariance * 100)?.toFixed(2) }}%</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">相关性降低比例</span>
              <span class="metric-value">{{ (orthogonalResults.correlationReduction * 100)?.toFixed(2) }}%</span>
            </div>
          </div>
          
          <!-- 因子载荷矩阵 -->
          <div v-if="orthogonalResults.loadings" class="loadings-matrix">
            <h4>因子载荷矩阵</h4>
            <div class="matrix-placeholder">
              <div class="matrix-cell" v-for="(row, i) in orthogonalResults.loadings" :key="i">
                <div v-for="(value, j) in row" :key="j" class="matrix-value">
                  {{ value.toFixed(3) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场状态识别选项卡 -->
    <div v-if="activeTab === 'market'" class="tab-content">
      <div class="section-card">
        <h2 class="section-title">市场状态识别</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="market-model">模型类型</label>
            <select id="market-model" v-model="marketParams.modelType">
              <option value="hmm">HMM隐马尔可夫模型</option>
              <option value="volatility">波动率聚类</option>
              <option value="cycle">市场周期识别</option>
            </select>
          </div>
          <div class="form-group">
            <label for="state-count">状态数量</label>
            <input 
              id="state-count" 
              type="number" 
              v-model="marketParams.stateCount" 
              min="2" 
              max="5"
            >
          </div>
          <div class="form-group">
            <label for="market-data">市场指数</label>
            <select id="market-data" v-model="marketParams.marketIndex">
              <option value="spy">标普500(SPY)</option>
              <option value="nasdaq">纳斯达克(NASDAQ)</option>
              <option value="dow">道琼斯(DOW)</option>
            </select>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="identifyMarketState" :disabled="isIdentifying">
              {{ isIdentifying ? '识别中...' : '识别市场状态' }}
            </button>
            <button class="btn btn-secondary" @click="resetMarketParams">重置</button>
          </div>
        </div>
        
        <!-- 识别结果 -->
        <div v-if="marketResults" class="results-container">
          <h3>市场状态识别结果</h3>
          <div class="market-states">
            <div class="state-item" v-for="(state, index) in marketResults.states" :key="index">
              <div class="state-header">
                <span class="state-name">状态{{ index + 1 }}</span>
                <span class="state-label">{{ state.label }}</span>
              </div>
              <div class="state-metrics">
                <div class="metric-item">
                  <span class="metric-label">平均收益率</span>
                  <span class="metric-value">{{ (state.avgReturn * 100)?.toFixed(2) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">波动率</span>
                  <span class="metric-value">{{ (state.volatility * 100)?.toFixed(2) }}%</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">持续时间</span>
                  <span class="metric-value">{{ state.duration }}天</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 当前状态 -->
          <div class="current-state">
            <h4>当前市场状态</h4>
            <div class="state-card">
              <div class="state-icon">{{ marketResults.currentState.icon }}</div>
              <div class="state-info">
                <h5>{{ marketResults.currentState.label }}</h5>
                <p>{{ marketResults.currentState.description }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 权重分配选项卡 -->
    <div v-if="activeTab === 'weight'" class="tab-content">
      <div class="section-card">
        <h2 class="section-title">策略权重分配</h2>
        <div class="form-container">
          <div class="form-group">
            <label for="weight-method">分配方法</label>
            <select id="weight-method" v-model="weightParams.method">
              <option value="max_diversity">最大多样性</option>
              <option value="entropy">熵权法</option>
              <option value="information_ratio">信息比率</option>
              <option value="combined">组合权重</option>
            </select>
          </div>
          <div class="form-group">
            <label>选择策略</label>
            <div class="checkbox-group">
              <label v-for="strategy in weightStrategies" :key="strategy">
                <input 
                  type="checkbox" 
                  v-model="weightParams.selectedStrategies" 
                  :value="strategy"
                >
                {{ strategyMap[strategy] }}
              </label>
            </div>
          </div>
          <div class="form-group">
            <label for="risk-tolerance">风险容忍度</label>
            <input 
              id="risk-tolerance" 
              type="range" 
              v-model="weightParams.riskTolerance" 
              min="0.1" 
              max="1.0" 
              step="0.1"
            >
            <span class="range-value">{{ weightParams.riskTolerance }}</span>
          </div>
          <div class="form-actions">
            <button class="btn btn-primary" @click="calculateWeights" :disabled="isCalculatingWeights">
              {{ isCalculatingWeights ? '计算中...' : '计算权重' }}
            </button>
            <button class="btn btn-secondary" @click="resetWeightParams">重置</button>
          </div>
        </div>
        
        <!-- 权重结果 -->
        <div v-if="weightResults" class="results-container">
          <h3>权重分配结果</h3>
          <div class="weights-chart">
            <div class="chart-placeholder">
              <div class="pie-chart-mock">
                <div 
                  class="pie-slice" 
                  v-for="(weight, index) in weightResults.weights" 
                  :key="index"
                  :style="{ 
                    transform: `rotate(${weight.cumulativeAngle}deg)`,
                    backgroundColor: weightColors[index % weightColors.length]
                  }"
                ></div>
              </div>
              <div class="pie-legend">
                <div 
                  class="legend-item" 
                  v-for="(weight, index) in weightResults.weights" 
                  :key="index"
                >
                  <div 
                    class="legend-color" 
                    :style="{ backgroundColor: weightColors[index % weightColors.length] }"
                  ></div>
                  <span>{{ weight.strategy }}: {{ (weight.weight * 100).toFixed(2) }}%</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 性能指标 -->
          <div class="performance-metrics">
            <h4>组合性能指标</h4>
            <div class="metrics-grid">
              <div class="metric-card">
                <div class="metric-title">夏普比率</div>
                <div class="metric-value">{{ weightResults.performance.sharpe?.toFixed(2) || '-' }}</div>
              </div>
              <div class="metric-card">
                <div class="metric-title">最大回撤</div>
                <div class="metric-value">{{ (weightResults.performance.maxDrawdown * 100)?.toFixed(2) }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-title">年化收益率</div>
                <div class="metric-value">{{ (weightResults.performance.annualReturn * 100)?.toFixed(2) }}%</div>
              </div>
              <div class="metric-card">
                <div class="metric-title">信息比率</div>
                <div class="metric-value">{{ weightResults.performance.informationRatio?.toFixed(2) || '-' }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

// 活跃选项卡
const activeTab = ref('factor');

// 因子计算参数
const factorParams = reactive({
  stockSymbol: '',
  factorType: 'fundamental',
  selectedFactors: ['pe', 'pb', 'roe']
});

// 因子计算状态
const isCalculating = ref(false);
const factorResults = ref([]);

// 因子映射
const factorMap = {
  pe: '市盈率(PE)',
  pb: '市净率(PB)',
  roe: '净资产收益率(ROE)',
  roa: '资产收益率(ROA)',
  revenue_growth: '营收增长率',
  profit_growth: '利润增长率',
  sentiment: '新闻情绪',
  social_heat: '社交媒体热度'
};

// 股票名称映射
const stockNameMap = ref({
  'sh600000': '浦发银行',
  'sh600036': '招商银行',
  'sh600519': '贵州茅台',
  'sh601318': '中国平安',
  'sh601857': '中国石油',
  'sh601118': '海南橡胶',
  'sz000001': '平安银行',
  'sz000002': '万科A',
  'sz000858': '五粮液',
  'sz002415': '海康威视',
  'sz300750': '宁德时代'
});

// 股票列表
const symbolsList = ref([
  { symbol: 'sh600000', market: 'cn' },
  { symbol: 'sh600036', market: 'cn' },
  { symbol: 'sh600519', market: 'cn' },
  { symbol: 'sh601318', market: 'cn' },
  { symbol: 'sh601857', market: 'cn' },
  { symbol: 'sh601118', market: 'cn' },
  { symbol: 'sz000001', market: 'cn' },
  { symbol: 'sz000002', market: 'cn' },
  { symbol: 'sz000858', market: 'cn' },
  { symbol: 'sz002415', market: 'cn' },
  { symbol: 'sz300750', market: 'cn' }
]);

// 搜索文本
const symbolSearchText = ref('');

// 下拉框显示状态
const isSelectOpen = ref(false);

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

// 打开下拉框
const openSelect = (type: string) => {
  isSelectOpen.value = true;
};

// 切换下拉框显示状态
const toggleSelect = (type: string, event?: MouseEvent) => {
  if (event) {
    event.stopPropagation();
  }
  isSelectOpen.value = !isSelectOpen.value;
};

// 选择股票
const selectSymbol = (symbol: string) => {
  factorParams.stockSymbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

// 处理搜索输入框输入事件
const onSymbolInput = () => {
  // 当用户在输入框中输入时，更新factorParams.stockSymbol
  factorParams.stockSymbol = symbolSearchText.value;
};

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  const selectElement = document.querySelector('.searchable-select');
  const target = event.target as HTMLElement;
  
  if (selectElement && !selectElement.contains(target)) {
    isSelectOpen.value = false;
  }
};

// 监听点击外部事件
onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

// 模型训练参数
const modelParams = reactive({
  modelType: 'lstm',
  trainingDays: 180,
  predictionDays: 10,
  selectedFeatures: ['open', 'high', 'low', 'close', 'volume']
});

// 模型特征选项
const modelFeatures = [
  { value: 'open', label: '开盘价' },
  { value: 'high', label: '最高价' },
  { value: 'low', label: '最低价' },
  { value: 'close', label: '收盘价' },
  { value: 'volume', label: '成交量' },
  { value: 'pe', label: '市盈率' },
  { value: 'pb', label: '市净率' },
  { value: 'sentiment', label: '新闻情绪' }
];

// 模型训练状态
const isTraining = ref(false);
const modelResults = ref(null);

// 因子正交化参数
const orthogonalParams = reactive({
  method: 'pca',
  varianceThreshold: 0.9,
  selectedFactors: ['pe', 'pb', 'roe', 'roa']
});

// 正交化因子选项
const orthogonalFactors = ['pe', 'pb', 'roe', 'roa', 'revenue_growth', 'profit_growth'];

// 正交化状态
const isOrthogonalizing = ref(false);
const orthogonalResults = ref(null);

// 市场状态识别参数
const marketParams = reactive({
  modelType: 'hmm',
  stateCount: 3,
  marketIndex: 'spy'
});

// 市场状态识别状态
const isIdentifying = ref(false);
const marketResults = ref(null);

// 权重分配参数
const weightParams = reactive({
  method: 'max_diversity',
  selectedStrategies: ['momentum', 'value', 'growth', 'quality'],
  riskTolerance: 0.5
});

// 权重分配策略
const weightStrategies = ['momentum', 'value', 'growth', 'quality', 'low_volatility', 'high_dividend'];

// 策略映射
const strategyMap = {
  momentum: '动量策略',
  value: '价值策略',
  growth: '成长策略',
  quality: '质量策略',
  low_volatility: '低波动策略',
  high_dividend: '高股息策略'
};

// 权重颜色
const weightColors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F'];

// 权重分配状态
const isCalculatingWeights = ref(false);
const weightResults = ref(null);

// 真实因子计算
const calculateFactors = async () => {
  if (!factorParams.stockSymbol) {
    alert('请选择股票代码');
    return;
  }

  isCalculating.value = true;
  factorResults.value = [];

  try {
    // 调用真实API获取因子数据
    const response = await axios.get(`/api/moA/stock/${factorParams.stockSymbol}/factors`, {
      params: {
        factorType: factorParams.factorType,
        selectedFactors: factorParams.selectedFactors.join(','),
        limit: 31 // 获取最近31天的数据
      }
    });

    // 假设API返回的数据格式与我们需要的一致
    // 如果API返回格式不同，需要在这里进行转换
    factorResults.value = response.data.factors || [];

    // 如果API没有返回数据，使用模拟数据作为备选
    if (factorResults.value.length === 0) {
      generateMockFactors();
    }
  } catch (error) {
    console.error('获取因子数据失败:', error);
    alert('获取因子数据失败，将使用模拟数据');
    generateMockFactors();
  } finally {
    isCalculating.value = false;
  }
};

// 生成模拟因子数据（当API调用失败时使用）
const generateMockFactors = () => {
  const results = [];
  const today = new Date();
  
  for (let i = 30; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(today.getDate() - i);
    
    const result = {
      date: date.toISOString().split('T')[0]
    };
    
    // 为每个选择的因子生成随机值
    factorParams.selectedFactors.forEach(factor => {
      switch (factor) {
        case 'pe':
          result[factor] = 15 + Math.random() * 20;
          break;
        case 'pb':
          result[factor] = 1 + Math.random() * 5;
          break;
        case 'roe':
          result[factor] = 0.05 + Math.random() * 0.2;
          break;
        case 'roa':
          result[factor] = 0.02 + Math.random() * 0.1;
          break;
        case 'revenue_growth':
          result[factor] = -0.1 + Math.random() * 0.5;
          break;
        case 'profit_growth':
          result[factor] = -0.2 + Math.random() * 0.6;
          break;
        case 'sentiment':
          result[factor] = -1 + Math.random() * 2;
          break;
        case 'social_heat':
          result[factor] = 100 + Math.random() * 900;
          break;
      }
    });
    
    results.push(result);
  }
  
  factorResults.value = results;
};

// 重置因子计算参数
const resetFactorParams = () => {
  factorParams.stockSymbol = '';
  factorParams.factorType = 'fundamental';
  factorParams.selectedFactors = ['pe', 'pb', 'roe'];
  symbolSearchText.value = '';
  factorResults.value = [];
};

// 模拟模型训练
const trainModel = () => {
  isTraining.value = true;
  
  // 模拟API调用延迟
  setTimeout(() => {
    // 生成模拟结果
    modelResults.value = {
      trainLoss: 0.0234,
      valLoss: 0.0312,
      accuracy: 0.8567,
      r2Score: 0.7892,
      predictions: {
        dates: Array.from({ length: modelParams.predictionDays }, (_, i) => {
          const date = new Date();
          date.setDate(date.getDate() + i + 1);
          return date.toISOString().split('T')[0];
        }),
        actual: Array.from({ length: modelParams.predictionDays }, () => 150 + Math.random() * 20),
        predicted: Array.from({ length: modelParams.predictionDays }, () => 150 + Math.random() * 20)
      }
    };
    
    isTraining.value = false;
  }, 2000);
};

// 重置模型训练参数
const resetModelParams = () => {
  modelParams.modelType = 'lstm';
  modelParams.trainingDays = 180;
  modelParams.predictionDays = 10;
  modelParams.selectedFeatures = ['open', 'high', 'low', 'close', 'volume'];
  modelResults.value = null;
};

// 模拟因子正交化
const performOrthogonalization = () => {
  isOrthogonalizing.value = true;
  
  // 模拟API调用延迟
  setTimeout(() => {
    // 生成模拟结果
    const componentsCount = Math.ceil(orthogonalParams.selectedFactors.length * orthogonalParams.varianceThreshold);
    
    orthogonalResults.value = {
      componentsCount,
      cumulativeVariance: orthogonalParams.varianceThreshold,
      correlationReduction: 0.75 + Math.random() * 0.2,
      loadings: Array.from({ length: componentsCount }, () => 
        Array.from({ length: orthogonalParams.selectedFactors.length }, () => 
          Math.random() * 2 - 1
        )
      )
    };
    
    isOrthogonalizing.value = false;
  }, 1800);
};

// 重置因子正交化参数
const resetOrthogonalParams = () => {
  orthogonalParams.method = 'pca';
  orthogonalParams.varianceThreshold = 0.9;
  orthogonalParams.selectedFactors = ['pe', 'pb', 'roe', 'roa'];
  orthogonalResults.value = null;
};

// 模拟市场状态识别
const identifyMarketState = () => {
  isIdentifying.value = true;
  
  // 模拟API调用延迟
  setTimeout(() => {
    // 生成模拟结果
    const stateLabels = ['熊市', '震荡市', '牛市'];
    const stateIcons = ['📉', '📊', '📈'];
    
    const states = Array.from({ length: marketParams.stateCount }, (_, i) => ({
      label: stateLabels[i % stateLabels.length],
      avgReturn: -0.05 + Math.random() * 0.2,
      volatility: 0.1 + Math.random() * 0.3,
      duration: 30 + Math.floor(Math.random() * 100)
    }));
    
    marketResults.value = {
      states,
      currentState: {
        icon: stateIcons[1],
        label: '震荡市',
        description: '当前市场处于震荡状态，波动适中，建议采取中性策略'
      },
      confidence: 0.85 + Math.random() * 0.15
    };
    
    isIdentifying.value = false;
  }, 1600);
};

// 重置市场状态识别参数
const resetMarketParams = () => {
  marketParams.modelType = 'hmm';
  marketParams.stateCount = 3;
  marketParams.marketIndex = 'spy';
  marketResults.value = null;
};

// 模拟权重分配计算
const calculateWeights = () => {
  isCalculatingWeights.value = true;
  
  // 模拟API调用延迟
  setTimeout(() => {
    // 生成模拟权重
    const weights = [];
    let total = 0;
    
    // 为每个选择的策略生成权重
    weightParams.selectedStrategies.forEach(strategy => {
      const weight = Math.random();
      weights.push({ strategy, weight });
      total += weight;
    });
    
    // 归一化权重
    weights.forEach(weight => {
      weight.weight /= total;
    });
    
    // 计算累计角度（用于饼图）
    let cumulativeAngle = 0;
    weights.forEach(weight => {
      weight.angle = weight.weight * 360;
      weight.cumulativeAngle = cumulativeAngle;
      cumulativeAngle += weight.angle;
    });
    
    // 生成性能指标
    weightResults.value = {
      weights,
      performance: {
        sharpe: 1.5 + Math.random() * 1.5,
        maxDrawdown: 0.1 + Math.random() * 0.2,
        annualReturn: 0.1 + Math.random() * 0.3,
        informationRatio: 1.0 + Math.random() * 1.0
      }
    };
    
    isCalculatingWeights.value = false;
  }, 1700);
};

// 重置权重分配参数
const resetWeightParams = () => {
  weightParams.method = 'max_diversity';
  weightParams.selectedStrategies = ['momentum', 'value', 'growth', 'quality'];
  weightParams.riskTolerance = 0.5;
  weightResults.value = null;
};
</script>

<style scoped>
.ai-quant-workbench {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  font-size: 2.5rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* 选项卡样式 */
.tab-container {
  display: flex;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 30px;
  overflow-x: auto;
}

.tab-item {
  padding: 12px 24px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s ease;
  white-space: nowrap;
  font-weight: 500;
  color: #555;
}

.tab-item:hover {
  background: #e9ecef;
}

.tab-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.tab-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 卡片样式 */
.section-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 30px;
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #34495e;
  margin-bottom: 20px;
}

/* 表单样式 */
.form-container {
  margin-bottom: 30px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.form-group input,
.form-group select {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
}

/* 搜索下拉框样式 */
.searchable-select {
  position: relative;
  width: 100%;
}

.select-header {
  display: flex;
  align-items: center;
  width: 100%;
}

.search-input {
  flex: 1;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px 0 0 6px;
  font-size: 1rem;
  border-right: none;
}

.select-arrow {
  padding: 12px 15px;
  background-color: #f8f9fa;
  border: 1px solid #ddd;
  border-radius: 0 6px 6px 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.select-arrow:hover {
  background-color: #e9ecef;
}

.select-arrow.active {
  transform: rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  max-height: 300px;
  overflow-y: auto;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: none;
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
  transition: background-color 0.2s ease;
}

.select-option:hover {
  background-color: #f8f9fa;
}

.select-option.selected {
  background-color: #e9ecef;
  font-weight: 500;
}

.hidden-select {
  display: none;
}

.form-group select[multiple] {
  height: 120px;
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
}

.form-actions {
  display: flex;
  gap: 15px;
  margin-top: 30px;
}

/* 按钮样式 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
  transform: translateY(-1px);
}

/* 结果展示样式 */
.results-container {
  margin-top: 30px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.results-container h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.results-table {
  overflow-x: auto;
}

.results-table table {
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 6px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.results-table th,
.results-table td {
  padding: 12px;
  text-align: right;
  border-bottom: 1px solid #eee;
}

.results-table th {
  background: #667eea;
  color: white;
  font-weight: 500;
}

.results-table td:first-child,
.results-table th:first-child {
  text-align: left;
}

/* 模型指标样式 */
.model-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metric-label {
  font-weight: 500;
  color: #555;
}

.metric-value {
  font-size: 1.2rem;
  font-weight: bold;
  color: #667eea;
}

/* 图表占位符样式 */
.chart-placeholder {
  height: 300px;
  background: white;
  border-radius: 6px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-top: 20px;
}

.chart-mock {
  width: 80%;
  height: 200px;
  position: relative;
}

.chart-line {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  background: #667eea;
  width: 100%;
  animation: drawLine 2s ease-out;
}

.chart-line.actual {
  background: #FF6B6B;
  height: 3px;
}

.chart-line.predicted {
  background: #4ECDC4;
  height: 3px;
  transform: translateY(10px);
}

@keyframes drawLine {
  from { width: 0; }
  to { width: 100%; }
}

.chart-legend {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  justify-content: center;
}

.chart-legend span {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #555;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.actual {
  background: #FF6B6B;
}

.legend-dot.predicted {
  background: #4ECDC4;
}

/* 市场状态样式 */
.market-states {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.state-item {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.state-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.state-name {
  font-weight: bold;
  color: #2c3e50;
}

.state-label {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
  background: #e9ecef;
  color: #495057;
}

.current-state {
  margin-top: 30px;
}

.state-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px;
  border-radius: 12px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.state-icon {
  font-size: 4rem;
  margin-bottom: 20px;
}

.state-info h5 {
  font-size: 1.5rem;
  margin-bottom: 10px;
}

/* 权重分配样式 */
.weights-chart {
  margin-bottom: 30px;
}

.pie-chart-mock {
  width: 200px;
  height: 200px;
  border-radius: 50%;
  overflow: hidden;
  position: relative;
  background: #f8f9fa;
}

.pie-slice {
  position: absolute;
  width: 100%;
  height: 100%;
  transform-origin: bottom right;
}

.pie-legend {
  margin-left: 50px;
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 3px;
}

.performance-metrics {
  margin-top: 30px;
}

.performance-metrics h4 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 20px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.metric-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.metric-title {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 10px;
}

.metric-value {
  font-size: 1.8rem;
  font-weight: bold;
  color: #667eea;
}

/* 矩阵样式 */
.matrix-placeholder {
  max-height: 300px;
  overflow: auto;
}

.matrix-cell {
  display: flex;
  margin-bottom: 5px;
}

.matrix-value {
  width: 80px;
  height: 40px;
  border: 1px solid #eee;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
}

/* 范围滑块样式 */
input[type="range"] {
  width: 80%;
  margin-right: 10px;
}

.range-value {
  display: inline-block;
  width: 60px;
  text-align: center;
  font-weight: 500;
  color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions .btn {
    width: 100%;
  }
  
  .model-metrics,
  .market-states,
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-placeholder {
    flex-direction: column;
  }
  
  .pie-legend {
    margin-left: 0;
    margin-top: 20px;
  }
}
</style>