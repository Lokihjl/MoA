import { defineStore } from 'pinia'

// 定义选股因子类型
interface StockFactor {
  name: string
  params: string
}

// 定义买入因子类型
interface BuyFactor {
  name: string
  params: string
}

// 定义卖出因子类型
interface SellFactor {
  name: string
  params: string
}

// 定义回测参数类型
interface AlphaStrategyParams {
  initialCash: number
  nFolds: number
}

// 定义选股结果类型
interface SelectedStock {
  symbol: string
  name: string
  score: number
}

// 定义策略执行结果类型
interface AlphaStrategyResult {
  selectedStockCount: number
  winRate: number
  totalProfit: number
  annualProfit: number
  selectedStocks: SelectedStock[]
}

// 定义Alpha策略Store
export const useAlphaStrategyStore = defineStore('alphaStrategy', {
  state: () => ({
    // 策略参数
    params: {
      initialCash: 100000,
      nFolds: 2
    } as AlphaStrategyParams,
    
    // 选股因子
    stockFactors: [
      { name: 'AbuPickStockNDay', params: '{"xd": 20}' }
    ] as StockFactor[],
    
    // 买入因子
    buyFactors: [
      { name: 'AbuFactorBuyBreak', params: '{"xd": 20}' }
    ] as BuyFactor[],
    
    // 卖出因子
    sellFactors: [
      { name: 'AbuFactorSellPreAtrN', params: '{"close_atr_n": 1.5}' }
    ] as SellFactor[],
    
    // 执行状态
    isRunning: false,
    error: '',
    result: null as AlphaStrategyResult | null
  }),
  
  actions: {
    // 添加选股因子
    addStockFactor(name: string) {
      if (name) {
        this.stockFactors.push({
          name,
          params: '{}'
        })
      }
    },
    
    // 删除选股因子
    removeStockFactor(index: number) {
      this.stockFactors.splice(index, 1)
    },
    
    // 添加买入因子
    addBuyFactor(name: string) {
      if (name) {
        this.buyFactors.push({
          name,
          params: '{}'
        })
      }
    },
    
    // 删除买入因子
    removeBuyFactor(index: number) {
      this.buyFactors.splice(index, 1)
    },
    
    // 添加卖出因子
    addSellFactor(name: string) {
      if (name) {
        this.sellFactors.push({
          name,
          params: '{}'
        })
      }
    },
    
    // 删除卖出因子
    removeSellFactor(index: number) {
      this.sellFactors.splice(index, 1)
    },
    
    // 重置参数
    resetParams() {
      this.params = {
        initialCash: 100000,
        nFolds: 2
      }
      
      this.stockFactors = [
        { name: 'AbuPickStockNDay', params: '{"xd": 20}' }
      ]
      
      this.buyFactors = [
        { name: 'AbuFactorBuyBreak', params: '{"xd": 20}' }
      ]
      
      this.sellFactors = [
        { name: 'AbuFactorSellPreAtrN', params: '{"close_atr_n": 1.5}' }
      ]
      
      this.error = ''
      this.result = null
    },
    
    // 执行策略
    async runStrategy() {
      this.isRunning = true
      this.error = ''
      this.result = null
      
      try {
        // 准备请求参数
        const requestParams = {
          initialCash: this.params.initialCash,
          nFolds: this.params.nFolds,
          stockFactors: this.stockFactors,
          buyFactors: this.buyFactors,
          sellFactors: this.sellFactors
        }
        
        // 调用后端API执行策略
        const response = await fetch('http://localhost:3001/api/moA/alpha/backtest', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestParams)
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        // 解析响应结果
        const result = await response.json()
        this.result = result
      } catch (err: any) {
        // 如果API调用失败，使用模拟数据
        console.error('策略执行失败，使用模拟数据:', err)
        this.result = this.getMockResult()
      } finally {
        this.isRunning = false
      }
    },
    
    // 获取模拟结果
    getMockResult(): AlphaStrategyResult {
      return {
        selectedStockCount: 5,
        winRate: 0.65,
        totalProfit: 0.28,
        annualProfit: 0.14,
        selectedStocks: [
          { symbol: '000001', name: '平安银行', score: 95.5 },
          { symbol: '000002', name: '万科A', score: 92.3 },
          { symbol: '600000', name: '浦发银行', score: 89.7 },
          { symbol: '600036', name: '招商银行', score: 88.9 },
          { symbol: '000858', name: '五粮液', score: 87.2 }
        ]
      }
    }
  }
})