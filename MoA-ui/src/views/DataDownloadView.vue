<template>
  <div class="data-download-container">
    <h2>数据下载</h2>
    <div class="data-download-content">
      <div class="download-form">
        <h3>创建数据下载任务</h3>
        <div class="form-grid">
          <div class="form-group">
            <label for="market">市场类型</label>
            <select id="market" v-model="downloadParams.market">
              <option value="cn">A股</option>
            </select>
          </div>
          <div class="form-group">
            <label for="timeMode">时间模式</label>
            <select id="timeMode" v-model="downloadParams.timeMode">
              <option value="years">按年数</option>
              <option value="range">按日期范围</option>
            </select>
          </div>
          <div class="form-group" v-if="downloadParams.timeMode === 'years'">
            <label for="years">年数</label>
            <input 
              type="number" 
              id="years" 
              v-model.number="downloadParams.years"
              min="1"
              max="10"
              placeholder="例如：2"
            />
          </div>
          <div class="form-group" v-if="downloadParams.timeMode === 'range'">
            <label for="startDate">开始日期</label>
            <input 
              type="date" 
              id="startDate" 
              v-model="downloadParams.startDate"
            />
          </div>
          <div class="form-group" v-if="downloadParams.timeMode === 'range'">
            <label for="endDate">结束日期</label>
            <input 
              type="date" 
              id="endDate" 
              v-model="downloadParams.endDate"
            />
          </div>
          <div class="form-group">
            <label for="dataSource">数据源</label>
            <select id="dataSource" v-model="downloadParams.dataSource">
              <option value="tx">腾讯数据源</option>
              <option value="bd">百度数据源</option>
              <option value="nt">网易数据源</option>
            </select>
          </div>
          <div class="form-group full-width">
            <label for="symbols">股票代码（逗号分隔，留空则全市场）</label>
            <input 
              type="text" 
              id="symbols" 
              v-model="symbolsText"
              placeholder="例如：sh600000,sz000001,sz300001，留空则全市场下载"
            />
          </div>
        </div>
        <div class="buttons-group">
          <button class="btn-primary" @click="createDownload" :disabled="isCreating">
            {{ isCreating ? '创建中...' : '从数据源下载更新' }}
          </button>
        </div>
      </div>
      
      <div class="download-records">
        <h3>下载任务记录</h3>
        <div class="records-table">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>市场</th>
                <th>数据类型</th>
                <th>股票代码</th>
                <th>状态</th>
                <th>进度</th>
                <th>处理股票数</th>
                <th>成功股票数</th>
                <th>下载条数</th>
                <th>增量更新条数</th>
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in downloadRecords" :key="record.id">
                <td>{{ record.id }}</td>
                <td>{{ getMarketText(record.market) }}</td>
                <td>{{ getDataTypeText(record.data_type) }}</td>
                <td>
                  <span class="symbols-list">{{ record.symbols.join(', ') }}</span>
                </td>
                <td>
                  <span :class="`status-${record.status}`">
                    {{ getStatusText(record.status) }}
                    <template v-if="record.status === 'completed' && record.total_downloaded === 0">
                      <span style="color: #f39c12; margin-left: 5px;">(数据空)</span>
                    </template>
                  </span>
                </td>
                <td>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: `${record.progress}%` }"></div>
                    <span class="progress-text">{{ record.progress }}%</span>
                  </div>
                </td>
                <td>{{ record.total_symbols }}</td>
                <td>{{ record.success_symbols }}</td>
                <td>{{ record.total_downloaded }}</td>
                <td>{{ record.incremental_downloaded || 0 }}</td>
                <td>{{ record.created_at }}</td>
                <td>
                  <button 
                    class="btn-sm" 
                    @click="retryDownload(record.id)"
                    :disabled="record.status !== 'failed'"
                  >
                    重试
                  </button>
                  <button 
                    class="btn-sm btn-danger" 
                    @click="cancelDownload(record.id)"
                    :disabled="record.status === 'completed' || record.status === 'failed'"
                  >
                    取消
                  </button>
                  <button 
                    class="btn-sm btn-danger" 
                    @click="deleteDownload(record.id)"
                    :disabled="false"
                  >
                    删除
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { apiService } from '../services/api'

interface DownloadParams {
  market: string
  timeMode: 'years' | 'range'
  years: number
  startDate: string
  endDate: string
  dataSource: string
  symbols: string[]
}

interface DownloadRecord {
  id: number
  market: string
  data_type: string
  symbols: string[]
  status: string
  progress: number
  created_at: string
  start_time?: string
  end_time?: string
  error_message?: string
  total_downloaded: number
  total_symbols: number
  success_symbols: number
}

// 转换市场类型为中文
const getMarketText = (market: string): string => {
  const marketMap: Record<string, string> = {
    'cn': 'A股',
    'us': '美股',
    'hk': '港股',
    'futures_cn': '国内期货',
    'futures_global': '全球期货',
    'tc': '数字货币'
  }
  return marketMap[market] || market
}

// 转换数据类型为中文
const getDataTypeText = (dataType: string): string => {
  const dataTypeMap: Record<string, string> = {
    'day': '日线',
    'week': '周线',
    'month': '月线',
    'minute': '分钟线'
  }
  return dataTypeMap[dataType] || dataType
}

// 转换状态为中文
const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    'pending': '等待中',
    'running': '运行中',
    'completed': '已完成',
    'failed': '已失败'
  }
  return statusMap[status] || status
}

// 计算默认日期范围的函数
const getDefaultDateRange = () => {
  const now = new Date()
  const twoYearsAgo = new Date()
  twoYearsAgo.setFullYear(now.getFullYear() - 2)
  
  // 格式化日期为 YYYY-MM-DD
  const formatDate = (date: Date) => {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  }
  
  return {
    startDate: formatDate(twoYearsAgo),
    endDate: formatDate(now)
  }
}

// 下载参数
const downloadParams = ref<DownloadParams>({
  market: 'cn',
  timeMode: 'years',
  years: 2,
  ...getDefaultDateRange(),
  dataSource: 'tx',
  symbols: []
})

// 股票代码文本（用于输入框）
const symbolsText = ref('')

// 下载记录列表
const downloadRecords = ref<DownloadRecord[]>([])

// 加载状态
const isCreating = ref(false)
const isLoadingRecords = ref(false)

// 计算属性：将symbolsText转换为数组
const symbolsArray = computed({
  get: () => downloadParams.value.symbols,
  set: (value) => downloadParams.value.symbols = value
})

// 创建下载任务
const createDownload = async () => {
  const symbolsArray = symbolsText.value.trim() 
    ? symbolsText.value.split(',').map(s => s.trim()).filter(s => s) 
    : []
  
  isCreating.value = true
  try {
    await apiService.post('/data/download', {
      ...downloadParams.value,
      symbols: symbolsArray
    })
    fetchDownloadRecords()
    symbolsText.value = ''
    alert('下载任务创建成功，正在后台执行...')
  } catch (error) {
    console.error('创建下载任务失败:', error)
    let errorMsg = '创建下载任务失败，请检查网络连接或服务器状态'
    if (typeof error === 'object' && error !== null && 'response' in error) {
      const typedError = error as any
      if (typedError.response && typedError.response.data && typedError.response.data.error) {
        errorMsg = `创建下载任务失败: ${typedError.response.data.error}`
      }
    }
    alert(errorMsg)
  } finally {
    isCreating.value = false
  }
}


// 获取下载记录
const fetchDownloadRecords = async () => {
  isLoadingRecords.value = true
  try {
    downloadRecords.value = await apiService.get('/data/download/records')
  } catch (error) {
    console.error('获取下载记录失败:', error)
  } finally {
    isLoadingRecords.value = false
  }
}

// 取消下载任务
const cancelDownload = async (recordId: number) => {
  try {
    await apiService.put(`/data/download/records/${recordId}/cancel`)
    fetchDownloadRecords()
  } catch (error) {
    console.error('取消下载任务失败:', error)
    alert('取消下载任务失败')
  }
}

// 重新执行下载任务
const retryDownload = async (recordId: number) => {
  try {
    await apiService.post(`/data/download/records/${recordId}/retry`)
    fetchDownloadRecords()
  } catch (error) {
    console.error('重新执行下载任务失败:', error)
    alert('重新执行下载任务失败')
  }
}

// 删除下载记录
const deleteDownload = async (recordId: number) => {
  try {
    await apiService.delete(`/data/download/records/${recordId}`)
    fetchDownloadRecords()
  } catch (error) {
    console.error('删除下载记录失败:', error)
    alert('删除下载记录失败')
  }
}

// 组件挂载时获取下载记录
let timeoutId: number | null = null

// 立即停止定时器的函数
const stopTimeout = () => {
  if (timeoutId !== null) {

    clearTimeout(timeoutId)
    timeoutId = null
  }
}

// 一次性检查是否需要刷新的函数
const checkAndFetch = async () => {
  // 检查是否有下载任务
  const hasDownloadTasks = downloadRecords.value.length > 0
  

  
  // 如果没有下载任务，停止所有定时器
  if (!hasDownloadTasks) {
    stopTimeout()
    return
  }
  
  // 检查是否有活跃的下载任务
  const hasActiveDownloads = downloadRecords.value.some(record => 
    record.status === 'running' || record.status === 'pending'
  )
  

  
  // 如果有活跃任务，刷新记录并重新设置定时器
  if (hasActiveDownloads) {

    await fetchDownloadRecords()
    
    // 重新设置定时器，确保每次刷新后都检查状态
    stopTimeout()
    timeoutId = setTimeout(() => {
      checkAndFetch()
    }, 5000)
  }
  // 如果没有活跃任务，停止定时器
  else {

    stopTimeout()
  }
}

// 检查并设置定时器的函数
const checkAndSetTimeout = () => {
  // 检查是否有下载任务
  const hasDownloadTasks = downloadRecords.value.length > 0
  
  // 如果没有下载任务，停止定时器
  if (!hasDownloadTasks) {
    stopTimeout()
    return
  }
  
  // 检查是否有活跃的下载任务
  const hasActiveDownloads = downloadRecords.value.some(record => 
    record.status === 'running' || record.status === 'pending'
  )
  
  // 如果有活跃任务且定时器未运行，启动一次性定时器
  if (hasActiveDownloads && timeoutId === null) {

    timeoutId = setTimeout(() => {
      checkAndFetch()
    }, 5000)
  }
  // 如果没有活跃任务，停止定时器
  else if (!hasActiveDownloads) {
    stopTimeout()
  }
}

onMounted(async () => {
  // 直接获取下载记录，不设置初始定时器
  await fetchDownloadRecords()
  // 获取记录后检查是否需要设置定时器
  checkAndSetTimeout()
})

// 监听下载记录变化，每次获取新记录后检查定时器
watch(downloadRecords, () => {
  checkAndSetTimeout()
}, { deep: true })

// 组件卸载时清除定时器
onUnmounted(() => {
  if (timeoutId !== null) {
    console.log('组件卸载，清除定时器')
    clearTimeout(timeoutId)
    timeoutId = null
  }
})
</script>

<style scoped>
.data-download-container {
  width: 100%;
  margin: 0 auto;
  box-sizing: border-box;
}

.data-download-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-top: 2rem;
}

.download-form,
.download-records {
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

.form-group input,
.form-group select {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.buttons-group {
  display: flex;
  gap: 1rem;
}

.btn-primary,
.btn-secondary,
.btn-sm {
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

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-danger:disabled {
  background-color: #ec7063;
  cursor: not-allowed;
}

.records-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

th, td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

th {
  background-color: #f8f9fa;
  font-weight: 600;
  color: #555;
}

.status-pending {
  color: #f39c12;
}

.status-running {
  color: #3498db;
}

.status-completed {
  color: #27ae60;
}

.status-failed {
  color: #e74c3c;
}

.progress-bar {
  position: relative;
  width: 100%;
  height: 20px;
  background-color: #ecf0f1;
  border-radius: 10px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background-color: #3498db;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .buttons-group {
    flex-direction: column;
  }
  
  table {
    font-size: 0.875rem;
  }
  
  th, td {
    padding: 0.5rem;
  }
}

.symbols-list {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.875rem;
  color: #555;
}
</style>
