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
              <option value="us">美股</option>
              <option value="cn">A股</option>
              <option value="hk">港股</option>
              <option value="futures_cn">国内期货</option>
              <option value="futures_global">国际期货</option>
              <option value="tc">数字货币</option>
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
              <option value="sn_us">新浪美股</option>
              <option value="nt">网易数据源</option>
            </select>
          </div>
          <div class="form-group full-width">
            <label for="symbols">股票代码（逗号分隔，留空则全市场）</label>
            <input 
              type="text" 
              id="symbols" 
              v-model="symbolsText"
              placeholder="例如：usAAPL,usGOOG,usMSFT，留空则全市场下载"
            />
          </div>
        </div>
        <div class="buttons-group">
          <button class="btn-primary" @click="createDownload" :disabled="isCreating">
            {{ isCreating ? '创建中...' : '从数据源下载更新' }}
          </button>
          <button class="btn-secondary" @click="runCloudDownload" :disabled="isCreating">
            {{ isCreating ? '创建中...' : '云盘下载6年数据' }}
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
                <th>创建时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="record in downloadRecords" :key="record.id">
                <td>{{ record.id }}</td>
                <td>{{ record.market }}</td>
                <td>{{ record.data_type }}</td>
                <td>
                  <span class="symbols-list">{{ record.symbols.join(', ') }}</span>
                </td>
                <td>
                  <span :class="`status-${record.status}`">{{ record.status }}</span>
                </td>
                <td>
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: `${record.progress}%` }"></div>
                    <span class="progress-text">{{ record.progress }}%</span>
                  </div>
                </td>
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
import axios from 'axios'

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
}

// 下载参数
const downloadParams = ref<DownloadParams>({
  market: 'us',
  timeMode: 'years',
  years: 2,
  startDate: '2021-12-19',
  endDate: '2025-12-19',
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
  // 转换股票代码
  const symbolsArray = symbolsText.value.trim() 
    ? symbolsText.value.split(',').map(s => s.trim()).filter(s => s) 
    : []
  
  isCreating.value = true
  try {
    const response = await axios.post('/api/abu/data/download', {
      ...downloadParams.value,
      symbols: symbolsArray
    })
    // 立即刷新下载记录，查看任务状态
    fetchDownloadRecords()
    // 清空输入
    symbolsText.value = ''
  } catch (error) {
    console.error('创建下载任务失败:', error)
    alert('创建下载任务失败')
  } finally {
    isCreating.value = false
  }
}

// 云盘下载
const runCloudDownload = async () => {
  try {
    const response = await axios.post('/api/abu/data/download/cloud')
    alert('云盘下载已启动，请在后端查看下载进度')
  } catch (error) {
    console.error('云盘下载失败:', error)
    alert('云盘下载失败')
  }
}

// 获取下载记录
const fetchDownloadRecords = async () => {
  isLoadingRecords.value = true
  try {
    const response = await axios.get('/api/abu/data/download/records')
    downloadRecords.value = response.data
  } catch (error) {
    console.error('获取下载记录失败:', error)
  } finally {
    isLoadingRecords.value = false
  }
}

// 取消下载任务
const cancelDownload = async (recordId: number) => {
  try {
    await axios.put(`/api/abu/data/download/records/${recordId}/cancel`)
    // 刷新下载记录
    fetchDownloadRecords()
  } catch (error) {
    console.error('取消下载任务失败:', error)
    alert('取消下载任务失败')
  }
}

// 重新执行下载任务
const retryDownload = async (recordId: number) => {
  try {
    await axios.post(`/api/abu/data/download/records/${recordId}/retry`)
    // 刷新下载记录
    fetchDownloadRecords()
  } catch (error) {
    console.error('重新执行下载任务失败:', error)
    alert('重新执行下载任务失败')
  }
}

// 删除下载记录
const deleteDownload = async (recordId: number) => {
  try {
    await axios.delete(`/api/abu/data/download/records/${recordId}`)
    // 刷新下载记录
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
    console.log('强制停止定时器')
    clearTimeout(timeoutId)
    timeoutId = null
  }
}

// 一次性检查是否需要刷新的函数
const checkAndFetch = async () => {
  // 检查是否有下载任务
  const hasDownloadTasks = downloadRecords.value.length > 0
  
  console.log('检查刷新状态:', {
    hasDownloadTasks,
    recordCount: downloadRecords.value.length
  })
  
  // 如果没有下载任务，停止所有定时器
  if (!hasDownloadTasks) {
    stopTimeout()
    return
  }
  
  // 检查是否有活跃的下载任务
  const hasActiveDownloads = downloadRecords.value.some(record => 
    record.status === 'running' || record.status === 'pending'
  )
  
  console.log('活跃任务检查:', {
    hasActiveDownloads,
    activeTasks: downloadRecords.value.filter(record => 
      record.status === 'running' || record.status === 'pending'
    ).length
  })
  
  // 如果有活跃任务，刷新记录并重新设置定时器
  if (hasActiveDownloads) {
    console.log('执行刷新')
    await fetchDownloadRecords()
    
    // 重新设置定时器，确保每次刷新后都检查状态
    stopTimeout()
    timeoutId = setTimeout(() => {
      checkAndFetch()
    }, 5000)
  }
  // 如果没有活跃任务，停止定时器
  else {
    console.log('无活跃任务，停止刷新')
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
    console.log('启动一次性定时器')
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
  max-width: 1200px;
  margin: 0 auto;
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
