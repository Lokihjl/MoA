import { defineStore } from 'pinia'
import { apiService } from '../services/api'

export interface LoopBackParams {
  initialCash: number
  nFolds: number
  symbols: string[]
  buyFactors: any[]
  sellFactors: any[]
}

export interface TradeRecord {
  id: number
  symbol: string
  buy_date: string
  sell_date: string
  buy_price: number
  sell_price: number
  quantity: number
  profit: number
  hold_days: number
  profit_rate: number
}

export interface LoopBackResult {
  winRate: number
  totalProfit: number
  annualProfit: number
  sharpeRatio: number
  maxDrawdown: number
  tradesCount: number
  tradeRecords: TradeRecord[]
  dataSource: string
}

export const useLoopBackStore = defineStore('loopback', {
  state: () => ({
    params: {
      initialCash: 1000000,
      nFolds: 2,
      symbols: ['sh600000', 'sh600036', 'sh600519', 'sz000001', 'sz000858'],
      buyFactors: [
        { xd: 42, class: 'AbuFactorBuyBreak' },
        { xd: 60, class: 'AbuFactorBuyBreak' }
      ],
      sellFactors: [
        { class: 'AbuFactorCloseAtrNStop', close_atr_n: 1.5 }
      ]
    } as LoopBackParams,
    result: null as LoopBackResult | null,
    isLoading: false,
    error: null as string | null
  }),
  actions: {
    async runLoopBack() {
      this.isLoading = true
      this.error = null
      try {
        this.result = await apiService.post<LoopBackResult>('/loopback', this.params)
      } catch (err) {
        this.error = '回测失败: ' + (err as Error).message
        console.error('回测失败:', err)
      } finally {
        this.isLoading = false
      }
    },
    resetParams() {
      this.params = {
        initialCash: 1000000,
        nFolds: 2,
        symbols: ['sh600000', 'sh600036', 'sh600519', 'sz000001', 'sz000858'],
        buyFactors: [
          { xd: 42, class: 'AbuFactorBuyBreak' },
          { xd: 60, class: 'AbuFactorBuyBreak' }
        ],
        sellFactors: [
          { class: 'AbuFactorCloseAtrNStop', close_atr_n: 1.5 }
        ]
      }
    }
  }
})
