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
              <li v-for="modelId in availableModels" :key="modelId">
                {{ modelId }}
                <button class="delete-btn" @click="deleteModel(modelId)">删除</button>
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
                <option v-for="modelId in availableModels" :key="modelId" :value="modelId">{{ modelId }}</option>
                <option value="" disabled>请先创建模型</option>
              </select>
            </div>
            <div class="form-group">
              <label>股票代码</label>
              <input type="text" v-model="trainForm.symbol" placeholder="如：sz000002" class="form-control">
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
      </div>
      
      <!-- 智能选股 -->
      <div v-if="activeTab === 'pick'" class="tab-panel">
        <h2>智能选股</h2>
        <div class="pick-stocks-form">
          <div class="form-row">
            <div class="form-group">
              <label>选择模型</label>
              <select v-model="pickForm.model_id" class="form-control">
                <option v-for="modelId in availableModels" :key="modelId" :value="modelId">{{ modelId }}</option>
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
                <option v-for="modelId in availableModels" :key="modelId" :value="modelId">{{ modelId }}</option>
                <option value="" disabled>请先创建模型</option>
              </select>
            </div>
            <div class="form-group">
              <label>股票代码</label>
              <input type="text" v-model="stopForm.symbol" placeholder="如：sz000002" class="form-control">
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
import { ref, onMounted } from 'vue';
import axios from 'axios';

// API基础URL
const API_BASE_URL = '/api/moA/ml_strategy';

// 选项卡数据
const tabs = [
  { key: 'model', label: '模型管理' },
  { key: 'pick', label: '智能选股' },
  { key: 'stop', label: '动态止盈止损' }
];

// 当前激活的选项卡
const activeTab = ref('model');

// 可用模型列表
const availableModels = ref<string[]>([]);

// 创建模型表单
const modelForm = ref({
  model_type: 'random_forest',
  fit_type: 'clf'
});

// 训练模型表单
const trainForm = ref({
  model_id: '',
  symbol: 'sz000002',
  lookback_days: 20
});

// 智能选股表单
const pickForm = ref({
  model_id: '',
  symbols: 'sz000002,sh600036,sz000858,sh601318,sz000333',
  top_n: 3
});

// 选中的股票
const selectedStocks = ref<any[]>([]);

// 止盈止损表单
const stopForm = ref({
  model_id: '',
  symbol: 'sz000002',
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
    const response = await axios.get(`${API_BASE_URL}/available_models`);
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
    const response = await axios.post(`${API_BASE_URL}/create_model`, modelForm.value);
    if (response.data.success) {
      showMessage('模型创建成功', 'success');
      await fetchAvailableModels();
    }
  } catch (error) {
    console.error('创建模型失败:', error);
    showMessage('创建模型失败', 'error');
  } finally {
    creatingModel.value = false;
  }
};

// 删除模型
const deleteModel = (modelId: string) => {
  // 这里可以添加删除模型的逻辑
  showMessage('模型删除功能暂未实现', 'info');
};

// 训练模型
const trainModel = async () => {
  if (!trainForm.value.model_id) {
    showMessage('请先选择模型', 'error');
    return;
  }
  
  trainingModel.value = true;
  try {
    const response = await axios.post(`${API_BASE_URL}/train_model`, trainForm.value);
    if (response.data.success) {
      showMessage('模型训练成功', 'success');
    } else {
      showMessage(`模型训练失败: ${response.data.message}`, 'error');
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
    const response = await axios.post(`${API_BASE_URL}/smart_pick`, {
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
    const response = await axios.post(`${API_BASE_URL}/adjust_stop_params`, stopForm.value);
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

// 页面加载时获取可用模型
onMounted(() => {
  fetchAvailableModels();
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
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s ease;
  border: 1px solid var(--border-color);
}

.model-list li:hover {
  box-shadow: var(--shadow-md);
  transform: translateX(5px);
}

.model-list li.empty {
  color: var(--text-secondary);
  justify-content: center;
  border: 1px dashed var(--border-color);
  background: transparent;
}

.delete-btn {
  padding: 4px 8px;
  background: var(--danger-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.delete-btn:hover {
  background: var(--danger-hover);
  transform: scale(1.05);
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
