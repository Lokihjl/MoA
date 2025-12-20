import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/loopback',
      name: 'loopback',
      component: () => import('../views/LoopBackView.vue')
    },
    {
      path: '/resistance-support',
      name: 'resistance-support',
      component: () => import('../views/ResistanceSupportView.vue')
    },
    {
      path: '/gap-analysis',
      name: 'gap-analysis',
      component: () => import('../views/GapAnalysisView.vue')
    },
    {
      path: '/trend-speed',
      name: 'trend-speed',
      component: () => import('../views/TrendSpeedView.vue')
    },
    {
      path: '/distance-ratio',
      name: 'distance-ratio',
      component: () => import('../views/DistanceRatioView.vue')
    },
    {
      path: '/linear-fit',
      name: 'linear-fit',
      component: () => import('../views/LinearFitView.vue')
    },
    {
      path: '/golden-section',
      name: 'golden-section',
      component: () => import('../views/GoldenSectionView.vue')
    },
    {
      path: '/price-channel',
      name: 'price-channel',
      component: () => import('../views/PriceChannelView.vue')
    },
    {
      path: '/correlation',
      name: 'correlation',
      component: () => import('../views/CorrelationView.vue')
    },
    {
      path: '/change-analysis',
      name: 'change-analysis',
      component: () => import('../views/ChangeAnalysisView.vue')
    },
    {
      path: '/stock-info',
      name: 'stock-info',
      component: () => import('../views/StockInfoView.vue')
    },
    {
      path: '/data-download',
      name: 'data-download',
      component: () => import('../views/DataDownloadView.vue')
    },
    {
      path: '/finance-api-test',
      name: 'finance-api-test',
      component: () => import('../views/FinanceApiTestView.vue')
    },
    {
      path: '/alpha-strategy',
      name: 'alpha-strategy',
      component: () => import('../views/AlphaStrategyView.vue')
    },
    {
      path: '/data-query',
      name: 'data-query',
      component: () => import('../views/DataQueryView.vue')
    },
    {
      path: '/price-change',
      name: 'price-change',
      component: () => import('../views/PriceChangeView.vue')
    }
  ]
})

export default router
