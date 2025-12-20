<template>
  <div class="alpha-strategy-container">
    <h2>Alpha策略分析</h2>
    
    <div class="alpha-strategy-content">
      <div class="params-section">
        <h3>策略参数设置</h3>
        
        <div class="form-grid">
          <div class="form-group">
            <label for="initialCash">初始资金</label>
            <input 
              type="number" 
              id="initialCash" 
              v-model.number="store.params.initialCash"
              min="1000000" 
              step="1000000"
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
          
          <div class="form-group">
            <label for="startDate">开始日期</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="store.params.startDate"
            />
          </div>
          
          <div class="form-group">
            <label for="endDate">结束日期</label>
            <input 
              type="date" 
              id="endDate" 
              v-model="store.params.endDate"
            />
          </div>
        </div>
        
        <!-- 选股因子配置 -->
        <div class="factors-section">
          <h4>选股因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.stockFactors" :key="index">
              <div class="factor-header">
                <span>{{ factor.name }}</span>
                <button class="btn-remove" @click="removeStockFactor(index)">×</button>
              </div>
              <div class="factor-config">
                <input 
                  type="text" 
                  v-model="factor.params" 
                  placeholder="参数配置（JSON格式）"
                />
              </div>
            </div>
          </div>
          <div class="add-factor">
            <select v-model="newStockFactorName">
              <option value="">选择选股因子</option>
              <option value="AbuPickStockNDay">N日收益率选股</option>
              <option value="AbuPickStockGT">价格突破选股</option>
              <option value="AbuPickStockEV">估值选股</option>
            </select>
            <button class="btn-add" @click="addStockFactor">添加选股因子</button>
          </div>
        </div>
        
        <!-- 买入因子配置 -->
        <div class="factors-section">
          <h4>买入因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.buyFactors" :key="index">
              <div class="factor-header">
                <span>{{ factor.name }}</span>
                <button class="btn-remove" @click="removeBuyFactor(index)">×</button>
              </div>
              <div class="factor-config">
                <input 
                  type="text" 
                  v-model="factor.params" 
                  placeholder="参数配置（JSON格式）"
                />
              </div>
            </div>
          </div>
          <div class="add-factor">
            <select v-model="newBuyFactorName">
              <option value="">选择买入因子</option>
              <option value="AbuFactorBuyBreak">突破买入</option>
              <option value="AbuFactorBuyMeanReversion">均值回归买入</option>
              <option value="AbuFactorBuyGap">缺口买入</option>
            </select>
            <button class="btn-add" @click="addBuyFactor">添加买入因子</button>
          </div>
        </div>
        
        <!-- 卖出因子配置 -->
        <div class="factors-section">
          <h4>卖出因子</h4>
          <div class="factors-list">
            <div class="factor-item" v-for="(factor, index) in store.sellFactors" :key="index">
              <div class="factor-header">
                <span>{{ factor.name }}</span>
                <button class="btn-remove" @click="removeSellFactor(index)">×</button>
              </div>
              <div class="factor-config">
                <input 
                  type="text" 
                  v-model="factor.params" 
                  placeholder="参数配置（JSON格式）"
                />
              </div>
            </div>
          </div>
          <div class="add-factor">
            <select v-model="newSellFactorName">
              <option value="">选择卖出因子</option>
              <option value="AbuFactorSellBreak">突破卖出</option>
              <option value="AbuFactorSellMeanReversion">均值回归卖出</option>
              <option value="AbuFactorSellPreAtrN">ATR止损卖出</option>
              <option value="AbuFactorSellRsi">RSI卖出</option>
            </select>
            <button class="btn-add" @click="addSellFactor">添加卖出因子</button>
          </div>
        </div>
        
        <div class="buttons-group">
          <button 
            class="btn-primary" 
            @click="runStrategy" 
            :disabled="store.isRunning"
          >
            {{ store.isRunning ? '策略执行中...' : '执行策略' }}
          </button>
          <button 
            class="btn-secondary" 
            @click="resetParams"
          >
            重置参数
          </button>
        </div>
      </div>
      
      <div class="results-section">
        <h3>策略执行结果</h3>
        
        <div v-if="store.isRunning" class="loading">
          <div class="loading-spinner"></div>
          <p>正在执行策略，请稍候...</p>
        </div>
        
        <div v-else-if="store.error" class="error">
          <p>{{ store.error }}</p>
        </div>
        
        <div v-else-if="store.result" class="result-content">
          <div class="result-cards">
            <div class="result-card">
              <h4>总收益</h4>
              <p class="result-value">{{ store.result.totalReturn }}%</p>
            </div>
            
            <div class="result-card">
              <h4>年化收益</h4>
              <p class="result-value">{{ store.result.annualReturn }}%</p>
            </div>
            
            <div class="result-card">
              <h4>最大回撤</h4>
              <p class="result-value">{{ store.result.maxDrawdown }}%</p>
            </div>
            
            <div class="result-card">
              <h4>夏普比率</h4>
              <p class="result-value">{{ store.result.sharpeRatio }}</p>
            </div>
            
            <div class="result-card">
              <h4>交易次数</h4>
              <p class="result-value">{{ store.result.tradeCount }}</p>
            </div>
            
            <div class="result-card">
              <h4>胜率</h4>
              <p class="result-value">{{ store.result.winRate }}%</p>
            </div>
          </div>
          
          <div class="chart-section">
            <h4>价格走势</h4>
            <div class="chart-container">
              <!-- 这里可以添加图表组件，如ECharts或Chart.js -->
              <div v-if="store.chartData && store.chartData.price" class="chart-data">
                <p>数据点数: {{ store.chartData.price.length }}</p>
                <div class="chart-preview">
                  <div 
                    v-for="(point, index) in store.chartData.price.slice(0, 5)" 
                    :key="index"
                    class="chart-point"
                  >
                    {{ point.date }}: {{ point.close }}
                  </div>
                  <div v-if="store.chartData.price.length > 5" class="chart-more">
                    ... 还有 {{ store.chartData.price.length - 5 }} 个数据点
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="chart-section">
            <h4>收益率曲线</h4>
            <div class="chart-container">
              <div v-if="store.chartData && store.chartData.cumReturn" class="chart-data">
                <p>数据点数: {{ store.chartData.cumReturn.length }}</p>
                <div class="chart-preview">
                  <div 
                    v-for="(point, index) in store.chartData.cumReturn.slice(0, 5)" 
                    :key="index"
                    class="chart-point"
                  >
                    {{ point.date }}: {{ point.return }}%
                  </div>
                  <div v-if="store.chartData.cumReturn.length > 5" class="chart-more">
                    ... 还有 {{ store.chartData.cumReturn.length - 5 }} 个数据点
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="chart-section">
            <h4>回撤曲线</h4>
            <div class="chart-container">
              <div v-if="store.chartData && store.chartData.drawdown" class="chart-data">
                <p>数据点数: {{ store.chartData.drawdown.length }}</p>
                <div class="chart-preview">
                  <div 
                    v-for="(point, index) in store.chartData.drawdown.slice(0, 5)" 
                    :key="index"
                    class="chart-point"
                  >
                    {{ point.date }}: {{ point.drawdown }}%
                  </div>
                  <div v-if="store.chartData.drawdown.length > 5" class="chart-more">
                    ... 还有 {{ store.chartData.drawdown.length - 5 }} 个数据点
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="empty-results">
          <p>请设置策略参数并点击执行策略</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAlphaStrategyStore } from '../stores/alphaStrategy'

const store = useAlphaStrategyStore()

// 选股因子
const newStockFactorName = ref('')

// 买入因子
const newBuyFactorName = ref('')

// 卖出因子
const newSellFactorName = ref('')

// 添加选股因子
const addStockFactor = () => {
  store.addStockFactor(newStockFactorName.value)
  newStockFactorName.value = ''
}

// 删除选股因子
const removeStockFactor = (index: number) => {
  store.removeStockFactor(index)
}

// 添加买入因子
const addBuyFactor = () => {
  store.addBuyFactor(newBuyFactorName.value)
  newBuyFactorName.value = ''
}

// 删除买入因子
const removeBuyFactor = (index: number) => {
  store.removeBuyFactor(index)
}

// 添加卖出因子
const addSellFactor = () => {
  store.addSellFactor(newSellFactorName.value)
  newSellFactorName.value = ''
}

// 删除卖出因子
const removeSellFactor = (index: number) => {
  store.removeSellFactor(index)
}

// 重置参数
const resetParams = () => {
  store.resetParams()
}

// 执行策略
const runStrategy = () => {
  store.runStrategy()
}
</script>

<style scoped>
.alpha-strategy-container {
  max-width: 1200px;
  margin: 0 auto;
}

.alpha-strategy-content {
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
  background-color: white;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 0.75rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.factor-item:last-child {
  margin-bottom: 0;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.factor-header span {
  font-weight: 600;
  color: #333;
}

.btn-remove {
  background-color: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  line-height: 1;
}

.btn-remove:hover {
  background-color: #c0392b;
}

.factor-config input {
  width: 100%;
  font-family: monospace;
  font-size: 0.9rem;
  padding: 0.5rem;
  background-color: #f8f9fa;
  border: 1px solid #eee;
}

.add-factor {
  display: flex;
  gap: 0.5rem;
  margin-top: 1rem;
}

.add-factor select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
}

.btn-add {
  background-color: #2ecc71;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 0.75rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-add:hover {
  background-color: #27ae60;
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

.result-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
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

.stock-list-section {
  margin-top: 1.5rem;
}

.stock-list-section h4 {
  margin-bottom: 1rem;
  color: #555;
}

.stock-list {
  background-color: #f8f9fa;
  border-radius: 8px;
  overflow: hidden;
}

.stock-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.stock-item:last-child {
  border-bottom: none;
}

.stock-symbol {
  font-weight: bold;
  color: #333;
  min-width: 80px;
}

.stock-name {
  flex: 1;
  margin: 0 1rem;
  color: #666;
}

.stock-score {
  font-weight: bold;
  color: #3498db;
  min-width: 60px;
  text-align: right;
}

.empty-results {
  text-align: center;
  padding: 2rem;
  color: #666;
  background-color: #f8f9fa;
  border-radius: 8px;
}

@media (max-width: 768px) {
  .alpha-strategy-content {
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
  
  .add-factor {
    flex-direction: column;
  }
}
</style>