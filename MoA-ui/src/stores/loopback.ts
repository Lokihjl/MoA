import { defineStore } from 'pinia'
import axios from 'axios'

export interface LoopBackParams {
  initialCash: number
  nFolds: number
  symbols: string[]
  buyFactors: any[]
  sellFactors: any[]
}

export interface LoopBackResult {
  winRate: number
  totalProfit: number
  annualProfit: number
  sharpeRatio: number
  maxDrawdown: number
  tradesCount: number
}

export const useLoopBackStore = defineStore('loopback', {
  state: () => ({
    params: {
      initialCash: 1000000,
      nFolds: 2,
      symbols: ['usAAPL', 'usGOOG', 'usMSFT'],
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
        // TODO: Replace with actual API endpoint
        const response = await axios.post('/api/loopback', this.params)
        this.result = response.data
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
        symbols: ['usAAPL', 'usGOOG', 'usMSFT'],
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
