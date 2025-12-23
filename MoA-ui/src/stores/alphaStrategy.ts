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

// 定义回测参数类型
interface AlphaStrategyParams {
  initialCash: number
  nFolds: number
  startDate: string
  endDate: string
}

// 定义Alpha策略Store
export const useAlphaStrategyStore = defineStore('alphaStrategy', {
  state: () => ({
    // 策略参数
    params: {
      initialCash: 1000000,
      nFolds: 2,
      startDate: '2020-01-01',
      endDate: '2023-12-31'
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
    result: null as any,
    // 图表数据
    chartData: null as any
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
        initialCash: 1000000,
        nFolds: 2,
        startDate: '2020-01-01',
        endDate: '2023-12-31'
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
      this.chartData = null
    },
    
    // 执行策略
    async runStrategy() {
      this.isRunning = true
      this.error = ''
      this.result = null
      this.chartData = null
      
      try {
        // 准备请求参数
        const requestParams = {
          stockPool: 'hs300',
          buyAlphaFactors: this.buyFactors.map(factor => factor.name),
          sellAlphaFactors: this.sellFactors.map(factor => factor.name),
          startDate: this.params.startDate,
          endDate: this.params.endDate,
          capital: this.params.initialCash,
          nFolds: this.params.nFolds
        }
        
        // 调用后端API执行策略
        const response = await fetch('/api/moA/alpha/backtest', {
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
        if (result.success) {
          this.result = result.data.backtestResult
          this.chartData = result.data.chartData
        } else {
          this.error = result.message || '策略执行失败'
        }
      } catch (err: any) {
        // 如果API调用失败，使用模拟数据
        console.error('策略执行失败，使用模拟数据:', err)
        this.error = err.message || '策略执行失败'
      } finally {
        this.isRunning = false
      }
    }
  }
})