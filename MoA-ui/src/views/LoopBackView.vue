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
              placeholder="例如：sh600000,sh600036,sz000001,sz000858"
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
        
        <div v-else-if="store.result" class="result-content">
          <!-- 数据来源信息 -->
          <div class="data-source-info">
            <span class="label">数据来源：</span>
            <span class="value">{{ store.result && store.result.dataSource ? store.result.dataSource : 'ABU框架' }}</span>
          </div>
          
          <!-- 回测统计卡片 -->
          <div class="result-cards">
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
            
            <div class="result-card trades-count">
              <h4>交易次数</h4>
              <p class="result-value trades-count-value">{{ store.result.tradesCount }}</p>
            </div>
          </div>
          
          <!-- 交易记录表格 -->
          <div class="trade-records-section">
            <h4>交易记录</h4>
            <div class="trade-records-table">
              <table>
                <thead>
                  <tr>
                    <th>序号</th>
                    <th>股票代码</th>
                    <th>买入日期</th>
                    <th>卖出日期</th>
                    <th>持有天数</th>
                    <th>买入价格</th>
                    <th>卖出价格</th>
                    <th>交易数量</th>
                    <th>利润</th>
                    <th>利润率</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="record in (store.result.tradeRecords || [])" :key="record.id">
                    <td>{{ record.id }}</td>
                    <td>{{ record.symbol }}</td>
                    <td>{{ record.buy_date }}</td>
                    <td>{{ record.sell_date }}</td>
                    <td>{{ record.hold_days }}天</td>
                    <td>{{ record.buy_price.toFixed(2) }}</td>
                    <td>{{ record.sell_price.toFixed(2) }}</td>
                    <td>{{ record.quantity }}</td>
                    <td :class="record.profit >= 0 ? 'profit-positive' : 'profit-negative'">
                      {{ record.profit >= 0 ? '+' : '' }}{{ record.profit.toFixed(2) }}
                    </td>
                    <td :class="record.profit_rate >= 0 ? 'profit-positive' : 'profit-negative'">
                      {{ record.profit_rate >= 0 ? '+' : '' }}{{ record.profit_rate.toFixed(2) }}%
                    </td>
                  </tr>
                  <tr v-if="!(store.result.tradeRecords && store.result.tradeRecords.length > 0)">
                    <td colspan="10" class="no-data">暂无交易记录</td>
                  </tr>
                </tbody>
              </table>
            </div>
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
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
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

/* 交易次数卡片样式，使其更明显 */
.result-card.trades-count {
  background-color: #3498db;
  color: white;
  box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
}

.result-card.trades-count h4 {
  color: white;
}

.result-value.trades-count-value {
  font-size: 2.5rem;
  color: white;
}

/* 数据来源信息样式 */
.data-source-info {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.data-source-info .label {
  font-weight: bold;
  color: #555;
}

.data-source-info .value {
  color: #3498db;
}

/* 交易记录部分样式 */
.trade-records-section {
  margin-top: 2rem;
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.trade-records-section h4 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

/* 交易记录表格样式 */
.trade-records-table {
  overflow-x: auto;
}

.trade-records-table table {
  width: 100%;
  border-collapse: collapse;
}

.trade-records-table th {
  background-color: #f8f9fa;
  color: #555;
  font-weight: 600;
  padding: 0.75rem;
  text-align: left;
  border-bottom: 2px solid #dee2e6;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.trade-records-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #e9ecef;
  color: #333;
}

.trade-records-table tbody tr:hover {
  background-color: #f8f9fa;
}

/* 利润样式 */
.profit-positive {
  color: #27ae60;
  font-weight: 600;
}

.profit-negative {
  color: #e74c3c;
  font-weight: 600;
}

/* 无数据样式 */
.no-data {
  text-align: center;
  color: #666;
  padding: 2rem;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .trade-records-table {
    font-size: 0.8rem;
  }
  
  .trade-records-table th,
  .trade-records-table td {
    padding: 0.5rem;
  }
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
