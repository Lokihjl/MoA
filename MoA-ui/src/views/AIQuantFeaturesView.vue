<template>
  <div class="ai-quant-container">
    <h1 class="page-title">AI量化交易功能展示</h1>
    
    <!-- 功能概览 -->
    <div class="overview-section">
      <div class="section-card">
        <h2 class="section-title">核心功能概览</h2>
        <div class="overview-grid">
          <div class="overview-item">
            <div class="overview-icon">📊</div>
            <div class="overview-content">
              <h3>因子工程</h3>
              <p>基本面、另类数据因子扩展，因子正交化处理</p>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon">🧠</div>
            <div class="overview-content">
              <h3>深度学习</h3>
              <p>LSTM、Transformer、CNN等模型集成</p>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon">🔄</div>
            <div class="overview-content">
              <h3>集成学习</h3>
              <p>Stacking、Bagging等集成方法</p>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon">📈</div>
            <div class="overview-content">
              <h3>形态识别</h3>
              <p>CNN提取价格形态特征</p>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon">📋</div>
            <div class="overview-content">
              <h3>生命周期管理</h3>
              <p>因子注册、评估、监控、版本控制</p>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon">⚖️</div>
            <div class="overview-content">
              <h3>策略权重分配</h3>
              <p>基于信息论的动态权重分配</p>
            </div>
          </div>
          <div class="overview-item">
            <div class="overview-icon">🔍</div>
            <div class="overview-content">
              <h3>市场状态识别</h3>
              <p>HMM、波动率聚类识别市场状态</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 因子工程模块 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">📊 因子工程模块</h2>
        <div class="feature-content">
          <div class="feature-description">
            <h3>基本面与另类数据因子扩展</h3>
            <p>实现了丰富的基本面因子和另类数据因子，包括财务指标、分析师评级、新闻情绪等，为量化策略提供多维度数据支持。</p>
            <ul>
              <li>财务因子：市盈率、市净率、ROE、ROA等</li>
              <li>成长因子：营收增长、利润增长等</li>
              <li>质量因子：资产周转率、毛利率等</li>
              <li>另类因子：新闻情绪、社交媒体热度、分析师评级变化</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// 因子注册示例
const fundamental_factors = AbuFundamentalFactors()
const alternative_factors = AbuAlternativeDataFactors()

// 因子计算
stock_data = fundamental_factors.calculate_factors(stock_data)
stock_data = alternative_factors.calculate_factors(stock_data)</code></pre>
            </div>
          </div>
        </div>
        <div class="feature-content">
          <div class="feature-description">
            <h3>因子正交化处理</h3>
            <p>通过主成分分析(PCA)等方法实现因子正交化，消除因子间的多重共线性，提高策略稳定性和可解释性。</p>
            <ul>
              <li>PCA主成分分析</li>
              <li>线性回归正交化</li>
              <li>因子相关性分析</li>
              <li>正交化效果评估</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// 因子正交化示例
orthogonalizer = AbuFactorOrthogonalization()
orthogonal_factors = orthogonalizer.orthogonalize(factors_data)

// 评估正交化效果
orthogonalizer.evaluate_orthogonalization(factors_data, orthogonal_factors)</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 深度学习模块 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">🧠 深度学习模块</h2>
        <div class="feature-content">
          <div class="feature-description">
            <h3>LSTM时间序列预测</h3>
            <p>基于长短期记忆网络(LSTM)的股价预测模型，能够捕捉时间序列数据中的长期依赖关系。</p>
            <ul>
              <li>多变量时间序列输入</li>
              <li>注意力机制增强</li>
              <li>滑动窗口训练</li>
              <li>模型调优与验证</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// LSTM模型示例
lstm_model = AbuLSTMForecaster()
lstm_model.fit(stock_data)
predictions = lstm_model.predict(stock_data)

// 模型评估
lstm_model.evaluate(stock_data)</code></pre>
            </div>
          </div>
        </div>
        <div class="feature-content">
          <div class="feature-description">
            <h3>Transformer序列建模</h3>
            <p>基于Transformer架构的序列模型，利用自注意力机制捕捉序列数据中的复杂依赖关系。</p>
            <ul>
              <li>多头自注意力机制</li>
              <li>位置编码</li>
              <li>前馈神经网络</li>
              <li>批归一化</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// Transformer模型示例
transformer_model = AbuTransformerForecaster()
transformer_model.fit(stock_data)
predictions = transformer_model.predict(stock_data)

// 模型评估
transformer_model.evaluate(stock_data)</code></pre>
            </div>
          </div>
        </div>
        <div class="feature-content">
          <div class="feature-description">
            <h3>CNN价格形态识别</h3>
            <p>基于卷积神经网络(CNN)的价格形态识别模型，能够自动提取K线图中的形态特征。</p>
            <ul>
              <li>卷积层特征提取</li>
              <li>池化层降维</li>
              <li>全连接层分类</li>
              <li>常见K线形态识别</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// CNN形态识别示例
cnn_pattern_model = AbuCNNPricePattern()
cnn_pattern_model.fit(stock_data)
predicted_patterns = cnn_pattern_model.recognize_patterns(stock_data)

// 形态因子提取
extractor = AbuCNNFactorExtractor()
cnn_factors = extractor.extract_factors(stock_data)</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 集成学习模块 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">🔄 集成学习模块</h2>
        <div class="feature-content">
          <div class="feature-description">
            <h3>Stacking集成学习</h3>
            <p>实现了Stacking集成学习框架，能够结合多个基模型的预测结果，提高预测准确性和稳定性。</p>
            <ul>
              <li>多层模型堆叠</li>
              <li>K折交叉验证</li>
              <li>元学习器训练</li>
              <li>模型权重优化</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// Stacking模型示例
stacking_model = AbuStackingModel(base_models, meta_model)
stacking_model.fit(stock_data)
predictions = stacking_model.predict(stock_data)

// 模型评估
stacking_model.evaluate(stock_data)</code></pre>
            </div>
          </div>
        </div>
        <div class="feature-content">
          <div class="feature-description">
            <h3>Bagging集成学习</h3>
            <p>实现了Bagging集成学习方法，通过自助采样构建多个基模型，降低模型方差，提高泛化能力。</p>
            <ul>
              <li>自助采样</li>
              <li>特征随机选择</li>
              <li>模型投票机制</li>
              <li>并行训练支持</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// Bagging模型示例
bagging_model = AbuBaggingModel(base_model, n_estimators=10)
bagging_model.fit(stock_data)
predictions = bagging_model.predict(stock_data)

// 模型评估
bagging_model.evaluate(stock_data)</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 因子生命周期管理 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">📋 因子生命周期管理</h2>
        <div class="feature-content">
          <div class="feature-description">
            <h3>完整的因子生命周期管理系统</h3>
            <p>实现了因子从注册、评估、部署到监控的全生命周期管理，确保因子质量和策略稳定性。</p>
            <ul>
              <li>因子注册与元数据管理</li>
              <li>因子性能评估与回测</li>
              <li>因子部署与版本控制</li>
              <li>因子监控与预警</li>
              <li>因子退化检测与更新</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// 因子生命周期管理示例
lifecycle_manager = AbuFactorLifecycleManager()

// 因子注册
lifecycle_manager.register_factor(factor_class, factor_config)

// 因子评估
factor_performance = lifecycle_manager.evaluate_factor(factor_id)

// 因子部署
lifecycle_manager.deploy_factor(factor_id, version)

// 因子监控
lifecycle_manager.monitor_factors()</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 策略权重分配 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">⚖️ 基于信息论的策略权重分配</h2>
        <div class="feature-content">
          <div class="feature-description">
            <h3>信息论驱动的策略权重优化</h3>
            <p>利用信息论原理实现策略权重分配，通过最大化策略多样性和信息比率，提高组合收益风险比。</p>
            <ul>
              <li>最大多样性权重分配</li>
              <li>熵权法权重分配</li>
              <li>信息比率权重分配</li>
              <li>动态权重调整</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// 信息论权重分配示例
weighting = AbuInfoTheoryWeighting()

// 计算策略多样性
diversity_matrix = weighting.calculate_diversity(strategy_returns)

// 分配权重
max_diversity_weights = weighting.max_diversity_weighting(strategy_returns)
entropy_weights = weighting.entropy_weighting(strategy_returns)

// 动态权重调整
dynamic_weights = weighting.combined_weighting(strategy_returns, market_states)</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 市场状态识别 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">🔍 市场状态识别与适应</h2>
        <div class="feature-content">
          <div class="feature-description">
            <h3>智能市场状态识别</h3>
            <p>利用隐马尔可夫模型(HMM)和波动率聚类等方法识别市场状态，使策略能够根据不同市场环境自动调整。</p>
            <ul>
              <li>HMM隐马尔可夫模型</li>
              <li>波动率聚类分析</li>
              <li>市场周期识别</li>
              <li>自适应策略调整</li>
            </ul>
          </div>
          <div class="feature-image">
            <div class="code-snippet">
              <pre><code>// 市场状态识别示例
hmm_model = AbuHMMMarketState(n_states=3)
hmm_model.fit(market_data)
market_states = hmm_model.predict(market_data)

// 自适应策略
adaptive_strategy = AbuAdaptiveStrategy()
adaptive_strategy.set_market_states(market_states)
adjusted_positions = adaptive_strategy.adjust_positions(original_positions)</code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用指南 -->
    <div class="feature-section">
      <div class="section-card">
        <h2 class="section-title">📖 使用指南</h2>
        <div class="usage-guide">
          <h3>快速开始</h3>
          <ol>
            <li><strong>因子准备</strong>：使用AbuFundamentalFactors和AbuAlternativeDataFactors计算因子</li>
            <li><strong>因子正交化</strong>：通过AbuFactorOrthogonalization处理因子间相关性</li>
            <li><strong>模型选择</strong>：根据需求选择LSTM、Transformer或CNN模型</li>
            <li><strong>集成学习</strong>：使用Stacking或Bagging提升模型性能</li>
            <li><strong>策略构建</strong>：结合因子生命周期管理和市场状态识别构建策略</li>
            <li><strong>权重分配</strong>：使用信息论方法优化策略权重</li>
          </ol>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

// 页面加载动画
const isLoaded = ref(false);

onMounted(() => {
  isLoaded.value = true;
});
</script>

<style scoped>
.ai-quant-container {
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

.section-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
  margin-bottom: 30px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.section-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.section-title {
  font-size: 1.8rem;
  font-weight: bold;
  color: #34495e;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 概览部分 */
.overview-section {
  margin-bottom: 40px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.overview-item {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  transition: transform 0.3s ease;
}

.overview-item:hover {
  transform: translateY(-3px);
}

.overview-icon {
  font-size: 2.5rem;
  flex-shrink: 0;
}

.overview-content h3 {
  font-size: 1.2rem;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 5px;
}

.overview-content p {
  color: #555;
  font-size: 0.95rem;
  margin: 0;
}

/* 功能部分 */
.feature-section {
  margin-bottom: 40px;
}

.feature-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  margin-bottom: 30px;
  align-items: center;
}

.feature-description h3 {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.feature-description p {
  color: #555;
  line-height: 1.6;
  margin-bottom: 15px;
}

.feature-description ul {
  list-style-type: disc;
  padding-left: 20px;
  color: #555;
}

.feature-description li {
  margin-bottom: 8px;
}

.feature-image {
  display: flex;
  justify-content: center;
  align-items: center;
}

.code-snippet {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.code-snippet pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9rem;
  line-height: 1.5;
}

.code-snippet code {
  background: none;
  color: inherit;
}

/* 使用指南 */
.usage-guide {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.usage-guide h3 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 15px;
}

.usage-guide ol {
  list-style-type: decimal;
  padding-left: 25px;
  color: #555;
}

.usage-guide li {
  margin-bottom: 12px;
  line-height: 1.6;
}

.usage-guide strong {
  color: #2c3e50;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .feature-content {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .page-title {
    font-size: 2rem;
  }
  
  .section-title {
    font-size: 1.5rem;
  }
}
</style>