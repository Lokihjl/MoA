<template>
  <div class="loopback-container">
    <h2>历史回测</h2>
    
    <div class="loopback-content">
      <div class="params-section">
        <h3>回测参数设置</h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="initialCash">初始资金</label>
            <input 
              type="number" 
              id="initialCash" 
              v-model.number="store.params.initialCash"
              min="10000" 
              step="10000"
            />
          </div>
          
          <div class="form-group">
            <label for="nFolds">回测年数</label>
            <input 
              type="number" 
              id="nFolds" 
              v-model.number="store.params.nFolds"
              min="1" 
              max="10"
              step="1"
            />
          </div>
          
          <div class="form-group full-width">
            <label for="symbols">股票代码（逗号分隔）</label>
            <input 
              type="text" 
              id="symbols" 
              v-model="symbolsText"
              placeholder="例如：usAAPL,usGOOG,usMSFT"
            />
          </div>
        </div>
        
        <div class="factors-section">
          <h4>买入因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.params.buyFactors" :key="index">
              <span>{{ factor.class }} (xd: {{ factor.xd }})</span>
            </div>
          </div>
          
          <h4>卖出因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.params.sellFactors" :key="index">
              <span>{{ factor.class }} (close_atr_n: {{ factor.close_atr_n }})</span>
            </div>
          </div>
        </div>
        
        <div class="buttons-group">
          <button 
            class="btn-primary" 
            @click="store.runLoopBack" 
            :disabled="store.isLoading"
          >
            {{ store.isLoading ? '回测中...' : '开始回测' }}
          </button>
          <button 
            class="btn-secondary" 
            @click="store.resetParams"
          >
            重置参数
          </button>
        </div>
      </div>
      
      <div class="results-section">
        <h3>回测结果</h3>
        
        <div v-if="store.isLoading" class="loading">
          <div class="loading-spinner"></div>
          <p>正在进行回测，请稍候...</p>
        </div>
        
        <div v-else-if="store.error" class="error">
          <p>{{ store.error }}</p>
        </div>
        
        <div v-else-if="store.result" class="result-cards">
          <div class="result-card">
            <h4>胜率</h4>
            <p class="result-value">{{ (store.result.winRate * 100).toFixed(2) }}%</p>
          </div>
          
          <div class="result-card">
            <h4>总收益</h4>
            <p class="result-value">{{ (store.result.totalProfit * 100).toFixed(2) }}%</p>
          </div>
          
          <div class="result-card">
            <h4>年化收益</h4>
            <p class="result-value">{{ (store.result.annualProfit * 100).toFixed(2) }}%</p>
          </div>
          
          <div class="result-card">
            <h4>夏普比率</h4>
            <p class="result-value">{{ store.result.sharpeRatio.toFixed(3) }}</p>
          </div>
          
          <div class="result-card">
            <h4>最大回撤</h4>
            <p class="result-value negative">{{ (store.result.maxDrawdown * 100).toFixed(2) }}%</p>
          </div>
          
          <div class="result-card">
            <h4>交易次数</h4>
            <p class="result-value">{{ store.result.tradesCount }}</p>
          </div>
        </div>
        
        <div v-else class="empty-results">
          <p>请设置回测参数并点击开始回测</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLoopBackStore } from '../stores/loopback'

const store = useLoopBackStore()

const symbolsText = computed({
  get: () => store.params.symbols.join(','),
  set: (value) => {
    store.params.symbols = value.split(',').map(s => s.trim()).filter(s => s)
  }
})
</script>

<style scoped>
.loopback-container {
  max-width: 1200px;
  margin: 0 auto;
}

.loopback-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.params-section,
.results-section {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 600;
  color: #333;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.factors-section {
  margin: 1.5rem 0;
}

.factors-section h4 {
  margin-bottom: 0.5rem;
  color: #555;
}

.factors-list {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}

.factor-item {
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}

.factor-item:last-child {
  border-bottom: none;
}

.buttons-group {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
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
  background-color: #ecf0f1;
  color: #333;
}

.btn-secondary:hover {
  background-color: #bdc3c7;
}

.results-section h3 {
  margin-bottom: 1.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
}

.loading-spinner {
  border: 4px solid rgba(0, 0, 0, 0.1);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border-left-color: #3498db;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background-color: #fee;
  color: #c00;
  padding: 1rem;
  border-radius: 4px;
}

.result-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.result-card {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.result-card h4 {
  margin: 0 0 1rem 0;
  color: #555;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.result-value {
  font-size: 1.8rem;
  font-weight: bold;
  margin: 0;
  color: #2c3e50;
}

.result-value.negative {
  color: #e74c3c;
}

.empty-results {
  text-align: center;
  padding: 2rem;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .loopback-content {
    grid-template-columns: 1fr;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .buttons-group {
    flex-direction: column;
  }
  
  .result-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
