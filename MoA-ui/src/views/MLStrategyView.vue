<template>
  <div class="ml-strategy-view">
    <h1 class="page-title">机器学习策略</h1>
    
    <!-- 选项卡切换 -->
    <div class="tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.key" 
        :class="['tab-btn', { active: activeTab === tab.key }]"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>
    
    <!-- 内容区域 -->
    <div class="tab-content">
      <!-- 模型管理 -->
      <div v-if="activeTab === 'model'" class="tab-panel">
        <div class="panel-header">
          <h2>模型管理</h2>
          <div class="model-list">
            <h3>可用模型</h3>
            <ul>
              <li v-for="model in availableModels" :key="model.model_id">
                <span class="model-info">
                  <strong>{{ model.model_name }}</strong>
                  <small>({{ model.model_id }})</small>
                </span>
                <button class="delete-btn" @click="deleteModel(model.model_id)">删除</button>
              </li>
              <li v-if="availableModels.length === 0" class="empty">暂无可用模型</li>
            </ul>
          </div>
        </div>
        
        <div class="create-model-form">
          <h3>创建模型</h3>
          <div class="form-row">
            <div class="form-group">
              <label>模型类型</label>
              <select v-model="modelForm.model_type" class="form-control">
                <option value="random_forest">随机森林</option>
                <option value="xgb">XGBoost</option>
                <option value="svc">SVC</option>
                <option value="knn">KNN</option>
                <option value="decision_tree">决策树</option>
              </select>
            </div>
            <div class="form-group">
              <label>拟合类型</label>
              <select v-model="modelForm.fit_type" class="form-control">
                <option value="clf">分类</option>
                <option value="reg">回归</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>模型名称</label>
              <input 
                type="text" 
                v-model="modelForm.model_name" 
                placeholder="请输入模型名称（可选）" 
                class="form-control"
              >
              <small class="form-hint">不输入将使用默认名称</small>
            </div>
          </div>
          <button class="btn btn-primary" @click="createModel" :disabled="creatingModel">
            <span v-if="creatingModel" class="loading"></span>
            {{ creatingModel ? '创建中...' : '创建模型' }}
          </button>
        </div>
        
        <div class="train-model-form">
          <h3>训练模型</h3>
          <div class="form-row">
            <div class="form-group">
              <label>选择模型</label>
              <select v-model="trainForm.model_id" class="form-control">
                <option v-for="model in availableModels" :key="model.model_id" :value="model.model_id">{{ model.model_name }} ({{ model.model_id }})</option>
                <option value="" disabled>请先创建模型</option>
              </select>
            </div>
            <div class="form-group">
              <label>股票代码</label>
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
                      :class="{ 'selected': trainForm.symbol === item.symbol }"
                      @click="selectSymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="form-group">
              <label>回溯天数</label>
              <input type="number" v-model.number="trainForm.lookback_days" placeholder="默认20" class="form-control">
            </div>
          </div>
          <button class="btn btn-success" @click="trainModel" :disabled="trainingModel || !trainForm.model_id">
            <span v-if="trainingModel" class="loading"></span>
            {{ trainingModel ? '训练中...' : '训练模型' }}
          </button>
        </div>
        
        <!-- 训练信息显示 -->
        <div v-if="trainInfo" class="train-info-panel">
          <h3>训练信息</h3>
          <div class="train-info-header">
            <div class="info-item">
              <span class="info-label">开始时间:</span>
              <span class="info-value">{{ trainInfo.start_time }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">结束时间:</span>
              <span class="info-value">{{ trainInfo.end_time || '训练中...' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">总耗时:</span>
              <span class="info-value">{{ trainInfo.total_time || '计算中...' }}</span>
            </div>
          </div>
          
          <div class="train-steps">
            <h4>训练步骤</h4>
            <div class="steps-list">
              <div 
                v-for="(step, index) in trainInfo.steps" 
                :key="index"
                class="step-item"
              >
                <div class="step-header">
                  <span class="step-index">{{ index + 1 }}</span>
                  <span class="step-title">{{ step.step }}</span>
                  <span class="step-time">{{ step.timestamp }}</span>
                </div>
                <div class="step-content">
                  {{ step.message }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 智能选股 -->
      <div v-if="activeTab === 'pick'" class="tab-panel">
        <h2>智能选股</h2>
        <div class="pick-stocks-form">
          <div class="form-row">
            <div class="form-group">
              <label>选择模型</label>
              <select v-model="pickForm.model_id" class="form-control">
                <option v-for="model in availableModels" :key="model.model_id" :value="model.model_id">{{ model.model_name }} ({{ model.model_id }})</option>
                <option value="" disabled>请先创建模型</option>
              </select>
            </div>
            <div class="form-group">
              <label>股票代码（多个用逗号分隔）</label>
              <input type="text" v-model="pickForm.symbols" placeholder="如：sz000002,sh600036" class="form-control">
            </div>
            <div class="form-group">
              <label>选中数量</label>
              <input type="number" v-model.number="pickForm.top_n" placeholder="默认10" class="form-control">
            </div>
          </div>
          <button class="btn btn-primary" @click="pickStocks" :disabled="pickingStocks || !pickForm.model_id">
            <span v-if="pickingStocks" class="loading"></span>
            {{ pickingStocks ? '选股中...' : '智能选股' }}
          </button>
        </div>
        
        <div v-if="selectedStocks.length > 0" class="stock-results">
          <h3>选股结果</h3>
          <div class="stock-grid">
            <div v-for="stock in selectedStocks" :key="stock.symbol" class="stock-card">
              <div class="stock-header">
                <h4>{{ stock.symbol }}</h4>
                <span class="probability" :style="{ '--probability': stock.probability }">
                  {{ (stock.probability * 100).toFixed(1) }}%
                </span>
              </div>
              <div class="stock-info">
                <p>最新价格: {{ stock.latest_price }}</p>
                <p>最新日期: {{ stock.latest_date }}</p>
                <p>预测结果: <span class="prediction" :class="stock.prediction === 1 ? 'up' : 'down'">
                  {{ stock.prediction === 1 ? '上涨' : '下跌' }}
                </span></p>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 动态止盈止损 -->
      <div v-if="activeTab === 'stop'" class="tab-panel">
        <h2>动态止盈止损</h2>
        <div class="stop-form">
          <div class="form-row">
            <div class="form-group">
              <label>选择模型</label>
              <select v-model="stopForm.model_id" class="form-control">
                <option v-for="model in availableModels" :key="model.model_id" :value="model.model_id">{{ model.model_name }} ({{ model.model_id }})</option>
                <option value="" disabled>请先创建模型</option>
              </select>
            </div>
            <div class="form-group">
              <label>股票代码</label>
              <div class="searchable-select">
                <div class="select-header" @click="toggleStopSelect($event)">
                  <input 
                    type="text" 
                    class="search-input" 
                    v-model="stopSymbolSearchText" 
                    placeholder="搜索股票代码或名称..."
                    @focus="openStopSelect"
                    @click="$event.stopPropagation(); openStopSelect()"
                    @input="onStopSymbolInput"
                  />
                  <span 
                    class="select-arrow" 
                    :class="{ 'active': isStopSelectOpen }"
                    @click="toggleStopSelect($event)"
                  >▼</span>
                </div>
                <div 
                  class="select-dropdown" 
                  :class="{ 'open': isStopSelectOpen }"
                >
                  <div class="select-options">
                    <div 
                      v-for="item in filteredStopSymbols" 
                      :key="item.symbol"
                      class="select-option"
                      :class="{ 'selected': stopForm.symbol === item.symbol }"
                      @click="selectStopSymbol(item.symbol)"
                    >
                      {{ item.symbol }} ({{ stockNameMap[item.symbol] || item.market }})
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>初始止损比例</label>
              <input type="number" v-model.number="stopForm.current_params.stop_loss" placeholder="默认0.05" class="form-control">
            </div>
            <div class="form-group">
              <label>初始止盈比例</label>
              <input type="number" v-model.number="stopForm.current_params.take_profit" placeholder="默认0.1" class="form-control">
            </div>
          </div>
          <button class="btn btn-primary" @click="adjustStopParams" :disabled="adjustingParams || !stopForm.model_id">
            <span v-if="adjustingParams" class="loading"></span>
            {{ adjustingParams ? '调整中...' : '调整参数' }}
          </button>
        </div>
        
        <div v-if="adjustedParams" class="adjusted-params">
          <h3>调整后参数</h3>
          <div class="params-grid">
            <div class="param-card">
              <h4>止损比例</h4>
              <p class="param-value">{{ (adjustedParams.stop_loss * 100).toFixed(2) }}%</p>
              <p class="param-change" :class="adjustedParams.stop_loss > stopForm.current_params.stop_loss ? 'increase' : 'decrease'">
                {{ adjustedParams.stop_loss > stopForm.current_params.stop_loss ? '放宽' : '收紧' }}了{{ Math.abs((adjustedParams.stop_loss - stopForm.current_params.stop_loss) * 100).toFixed(2) }}%
              </p>
            </div>
            <div class="param-card">
              <h4>止盈比例</h4>
              <p class="param-value">{{ (adjustedParams.take_profit * 100).toFixed(2) }}%</p>
              <p class="param-change" :class="adjustedParams.take_profit > stopForm.current_params.take_profit ? 'increase' : 'decrease'">
                {{ adjustedParams.take_profit > stopForm.current_params.take_profit ? '放宽' : '收紧' }}了{{ Math.abs((adjustedParams.take_profit - stopForm.current_params.take_profit) * 100).toFixed(2) }}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="message.type">
      {{ message.text }}
      <button class="close" @click="message = null">×</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

// API基础URL
const API_BASE_URL = '/api/moA';

// 选项卡数据
const tabs = [
  { key: 'model', label: '模型管理' },
  { key: 'pick', label: '智能选股' },
  { key: 'stop', label: '动态止盈止损' }
];

// 当前激活的选项卡
const activeTab = ref('model');

// 可用模型列表，改为包含模型ID和名称的对象数组
const availableModels = ref<Array<{model_id: string, model_name: string}>>([]);

// 创建模型表单
const modelForm = ref({
  model_type: 'random_forest',
  fit_type: 'clf',
  model_name: ''  // 添加模型名称字段
});

// 训练模型表单
const trainForm = ref({
  model_id: '',
  symbol: '',
  lookback_days: 20
});

// 股票代码搜索文本（训练模型）
const symbolSearchText = ref('');

// 股票代码搜索文本（动态止盈止损）
const stopSymbolSearchText = ref('');

// 已下载的股票列表
const symbolsList = ref<any[]>([]);

// 股票名称映射表，从API获取真实数据
const stockNameMap = ref<Record<string, string>>({});

// 过滤后的股票列表（训练模型）
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

// 过滤后的股票列表（动态止盈止损）
const filteredStopSymbols = computed(() => {
  if (!stopSymbolSearchText.value) {
    return symbolsList.value;
  }
  
  const searchText = stopSymbolSearchText.value.toLowerCase();
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

// 下拉框显示状态（训练模型）
const isSelectOpen = ref(false);

// 下拉框显示状态（动态止盈止损）
const isStopSelectOpen = ref(false);

// 获取已下载的股票列表
const fetchSymbolsList = async () => {
  try {
    const response = await axios.get('/api/moA/data/download/symbols');
    symbolsList.value = response.data;
    // 从响应数据中提取股票代码和名称，构建股票名称映射表
    // 注意：实际API响应中可能不包含股票名称，需要根据实际情况调整
    // 如果API不返回股票名称，可以考虑添加一个新的API来获取股票名称
  } catch (error) {
    console.error('获取已下载股票列表失败:', error);
    symbolsList.value = [];
  }
};

// 打开下拉框（训练模型）
const openSelect = () => {
  isSelectOpen.value = true;
};

// 打开下拉框（动态止盈止损）
const openStopSelect = () => {
  isStopSelectOpen.value = true;
};

// 切换下拉框显示状态（训练模型）
const toggleSelect = (event?: MouseEvent) => {
  if (event) {
    event.stopPropagation();
  }
  isSelectOpen.value = !isSelectOpen.value;
};

// 切换下拉框显示状态（动态止盈止损）
const toggleStopSelect = (event?: MouseEvent) => {
  if (event) {
    event.stopPropagation();
  }
  isStopSelectOpen.value = !isStopSelectOpen.value;
};

// 选择股票（训练模型）
const selectSymbol = (symbol: string) => {
  trainForm.value.symbol = symbol;
  symbolSearchText.value = symbol;
  isSelectOpen.value = false;
};

// 选择股票（动态止盈止损）
const selectStopSymbol = (symbol: string) => {
  stopForm.value.symbol = symbol;
  stopSymbolSearchText.value = symbol;
  isStopSelectOpen.value = false;
};

// 处理搜索输入框输入事件（训练模型）
const onSymbolInput = () => {
  // 当用户在输入框中输入时，更新trainForm.symbol
  trainForm.value.symbol = symbolSearchText.value;
};

// 处理搜索输入框输入事件（动态止盈止损）
const onStopSymbolInput = () => {
  // 当用户在输入框中输入时，更新stopForm.symbol
  stopForm.value.symbol = stopSymbolSearchText.value;
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
    isStopSelectOpen.value = false;
  }
};

// 智能选股表单
const pickForm = ref({
  model_id: '',
  symbols: '',
  top_n: 3
});

// 选中的股票
const selectedStocks = ref<any[]>([]);

// 止盈止损表单
const stopForm = ref({
  model_id: '',
  symbol: '',
  current_params: {
    stop_loss: 0.05,
    take_profit: 0.1
  }
});

// 调整后的参数
const adjustedParams = ref<any>(null);

// 加载状态
const creatingModel = ref(false);
const trainingModel = ref(false);
const pickingStocks = ref(false);
const adjustingParams = ref(false);

// 训练信息
const trainInfo = ref<any>(null);

// 消息提示
const message = ref<{ text: string; type: 'success' | 'error' | 'info' } | null>(null);

// 显示消息
const showMessage = (text: string, type: 'success' | 'error' | 'info' = 'info') => {
  message.value = { text, type };
  setTimeout(() => {
    message.value = null;
  }, 3000);
};

// 获取可用模型列表
const fetchAvailableModels = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/ml_strategy/available_models`);
    if (response.data.success) {
      availableModels.value = response.data.models;
    }
  } catch (error) {
    console.error('获取可用模型失败:', error);
    showMessage('获取可用模型失败', 'error');
  }
};

// 创建模型
const createModel = async () => {
  creatingModel.value = true;
  try {
    const response = await axios.post(`${API_BASE_URL}/ml_strategy/create_model`, modelForm.value);
    if (response.data.success) {
      showMessage('模型创建成功', 'success');
      await fetchAvailableModels();
      // 清空模型名称输入框
      modelForm.value.model_name = '';
    }
  } catch (error) {
    console.error('创建模型失败:', error);
    showMessage('创建模型失败', 'error');
  } finally {
    creatingModel.value = false;
  }
};

// 删除模型
const deleteModel = async (modelId: string) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/ml_strategy/delete_model`, { model_id: modelId });
    if (response.data.success) {
      showMessage('模型删除成功', 'success');
      await fetchAvailableModels();
    } else {
      showMessage(`模型删除失败: ${response.data.message}`, 'error');
    }
  } catch (error) {
    console.error('删除模型失败:', error);
    showMessage('模型删除失败', 'error');
  }
};

// 训练模型
const trainModel = async () => {
  if (!trainForm.value.model_id) {
    showMessage('请先选择模型', 'error');
    return;
  }
  
  trainingModel.value = true;
  // 重置训练信息
  trainInfo.value = null;
  
  try {
    const response = await axios.post(`${API_BASE_URL}/ml_strategy/train_model`, trainForm.value);
    if (response.data.success) {
      showMessage('模型训练成功', 'success');
      // 保存训练信息
      if (response.data.train_info) {
        trainInfo.value = response.data.train_info;
      }
    } else {
      showMessage(`模型训练失败: ${response.data.message}`, 'error');
      // 保存训练信息（即使失败）
      if (response.data.train_info) {
        trainInfo.value = response.data.train_info;
      }
    }
  } catch (error) {
    console.error('训练模型失败:', error);
    showMessage('训练模型失败', 'error');
  } finally {
    trainingModel.value = false;
  }
};

// 智能选股
const pickStocks = async () => {
  if (!pickForm.value.model_id) {
    showMessage('请先选择模型', 'error');
    return;
  }
  
  pickingStocks.value = true;
  try {
    const response = await axios.post(`${API_BASE_URL}/ml_strategy/smart_pick`, {
      ...pickForm.value,
      symbols: pickForm.value.symbols.split(',').map(s => s.trim())
    });
    if (response.data.success) {
      selectedStocks.value = response.data.selected_stocks;
      showMessage('智能选股成功', 'success');
    } else {
      showMessage(`智能选股失败: ${response.data.message}`, 'error');
    }
  } catch (error) {
    console.error('智能选股失败:', error);
    showMessage('智能选股失败', 'error');
  } finally {
    pickingStocks.value = false;
  }
};

// 调整止盈止损参数
const adjustStopParams = async () => {
  if (!stopForm.value.model_id) {
    showMessage('请先选择模型', 'error');
    return;
  }
  
  adjustingParams.value = true;
  try {
    const response = await axios.post(`${API_BASE_URL}/ml_strategy/adjust_stop_params`, stopForm.value);
    if (response.data.success) {
      adjustedParams.value = response.data.adjusted_params;
      showMessage('止盈止损参数调整成功', 'success');
    } else {
      showMessage(`止盈止损参数调整失败: ${response.data.message}`, 'error');
    }
  } catch (error) {
    console.error('调整止盈止损参数失败:', error);
    showMessage('调整止盈止损参数失败', 'error');
  } finally {
    adjustingParams.value = false;
  }
};

// 页面加载时获取可用模型和股票列表
onMounted(() => {
  fetchAvailableModels();
  fetchSymbolsList();
  document.addEventListener('click', handleClickOutside);
});

// 组件卸载时移除事件监听
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.ml-strategy-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-title {
  text-align: center;
  color: var(--primary-color);
  margin-bottom: 30px;
  font-size: 2rem;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
}

.tab-btn {
  padding: 10px 20px;
  background: var(--background-color);
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--text-color);
  cursor: pointer;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.3s ease;
  border-radius: 5px 5px 0 0;
}

.tab-btn:hover {
  background: var(--hover-color);
  transform: translateY(-2px);
}

.tab-btn.active {
  border-bottom-color: var(--primary-color);
  color: var(--primary-color);
  background: var(--card-background);
  box-shadow: 0 -2px 5px rgba(0, 0, 0, 0.1);
}

.tab-content {
  background: var(--card-background);
  border-radius: 10px;
  padding: 20px;
  box-shadow: var(--shadow-lg);
}

.tab-panel {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 20px;
}

.model-list {
  flex: 1;
  min-width: 200px;
  background: var(--background-color);
  padding: 15px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
}

.model-list h3 {
  margin-bottom: 10px;
  color: var(--text-color);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.model-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.model-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: var(--card-background);
  border-radius: 4px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.model-list li:hover {
  box-shadow: var(--shadow-md);
}

.model-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.model-info strong {
  color: var(--text-color);
  font-weight: 500;
}

.model-info small {
  color: var(--text-secondary);
  font-size: 0.8rem;
}

.form-hint {
  display: block;
  margin-top: 5px;
  color: var(--text-secondary);
  font-size: 0.85rem;
}

.model-list li.empty {
  color: var(--text-secondary);
  justify-content: center;
  border: 1px dashed var(--border-color);
  background: transparent;
}

.delete-btn {
  padding: 6px 12px;
  background: var(--danger-color);
  color: rgb(241, 9, 9);
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
}

.delete-btn:hover {
  background: var(--danger-hover);
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

/* 表单样式 */
.create-model-form,
.train-model-form,
.pick-stocks-form,
.stop-form {
  background: var(--background-color);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: var(--shadow-sm);
}

.create-model-form h3,
.train-model-form h3,
.pick-stocks-form h3,
.stop-form h3 {
  margin-bottom: 15px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group label {
  margin-bottom: 5px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.form-control {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--card-background);
  color: var(--text-color);
  font-size: 14px;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.form-control:disabled {
  background: var(--disabled-background);
  color: var(--text-secondary);
  cursor: not-allowed;
}

/* 按钮样式 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: inherit;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-primary {
  background: var(--gradient-primary);
  color: white;
  box-shadow: var(--shadow-md);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.btn-success {
  background: var(--gradient-secondary);
  color: white;
  box-shadow: var(--shadow-md);
}

.btn-success:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

/* 加载动画 */
.loading {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 股票结果样式 */
.stock-results {
  margin-top: 20px;
}

.stock-results h3 {
  margin-bottom: 15px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
}

.stock-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 15px;
}

.stock-card {
  background: var(--card-background);
  padding: 20px;
  border-radius: 10px;
  box-shadow: var(--shadow-md);
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.stock-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

.stock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.stock-header h4 {
  margin: 0;
  color: var(--text-color);
  font-size: 18px;
  font-weight: 600;
}

.probability {
  padding: 6px 12px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  background-size: 200% 200%;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.stock-info p {
  margin: 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.prediction {
  font-weight: 600;
}

.prediction.up {
  color: var(--success-color);
}

.prediction.down {
  color: var(--danger-color);
}

/* 止盈止损参数样式 */
.adjusted-params {
  margin-top: 20px;
}

.adjusted-params h3 {
  margin-bottom: 15px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
}

.params-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.param-card {
  background: var(--card-background);
  padding: 20px;
  border-radius: 10px;
  box-shadow: var(--shadow-md);
  text-align: center;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.param-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-lg);
}

.param-card h4 {
  margin: 0 0 10px 0;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.param-value {
  margin: 0 0 5px 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--primary-color);
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.param-change {
  margin: 5px 0 0 0;
  font-size: 12px;
  font-weight: 600;
}

.param-change.increase {
  color: var(--success-color);
}

.param-change.decrease {
  color: var(--danger-color);
}

/* 消息提示样式 */
.message {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  animation: slideIn 0.3s ease;
  display: flex;
  align-items: center;
  gap: 10px;
}

.message.success {
  background: var(--success-color);
}

.message.error {
  background: var(--danger-color);
}

.message.info {
  background: var(--info-color);
}

.message .close {
  background: none;
  border: none;
  color: white;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.2s ease;
}

.message .close:hover {
  background: rgba(255, 255, 255, 0.2);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* 搜索选择组件样式 */
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
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
  background: var(--card-background);
  color: var(--text-color);
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.1);
}

.select-arrow {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: var(--text-secondary);
  transition: transform 0.2s ease;
  font-size: 12px;
}

.select-arrow.active {
  transform: translateY(-50%) rotate(180deg);
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--card-background);
  border: 1px solid var(--border-color);
  border-radius: 0 0 6px 6px;
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  display: none;
  overflow-y: auto;
  max-height: 300px;
  margin-top: -1px;
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
  font-size: 14px;
  color: var(--text-color);
}

.select-option:hover {
  background-color: var(--hover-color);
}

.select-option.selected {
  background-color: rgba(64, 158, 255, 0.1);
  color: var(--primary-color);
  font-weight: 500;
}

.hidden-select {
  display: none;
}

/* 训练信息面板样式 */
.train-info-panel {
  background: var(--background-color);
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
}

.train-info-panel h3 {
  margin-bottom: 15px;
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
}

.train-info-panel h4 {
  margin: 20px 0 10px 0;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.train-info-header {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 15px;
  background: var(--card-background);
  border-radius: 6px;
  box-shadow: var(--shadow-sm);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.info-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-value {
  font-size: 16px;
  color: var(--primary-color);
  font-weight: 600;
}

.train-steps {
  background: var(--card-background);
  border-radius: 6px;
  padding: 15px;
  box-shadow: var(--shadow-sm);
}

.steps-list {
  max-height: 400px;
  overflow-y: auto;
}

.step-item {
  margin-bottom: 15px;
  padding: 15px;
  background: var(--background-color);
  border-radius: 6px;
  border-left: 3px solid var(--primary-color);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.step-item:hover {
  box-shadow: var(--shadow-md);
  transform: translateX(5px);
}

.step-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.step-index {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: var(--primary-color);
  color: white;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
}

.step-title {
  font-weight: 600;
  color: var(--text-color);
  font-size: 14px;
  flex: 1;
}

.step-time {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.step-content {
  font-size: 14px;
  color: var(--text-color);
  line-height: 1.5;
  margin-left: 34px;
  padding-left: 10px;
  border-left: 1px dashed var(--border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ml-strategy-view {
    padding: 10px;
  }
  
  .tabs {
    flex-direction: column;
  }
  
  .tab-btn {
    width: 100%;
    text-align: left;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .stock-grid {
    grid-template-columns: 1fr;
  }
  
  .params-grid {
    grid-template-columns: 1fr;
  }
  
  .panel-header {
    flex-direction: column;
  }
  
  .model-list {
    width: 100%;
  }
}
</style>
