<template>
  <div class="live-manage">
    <div class="manage-header">
      <h2>直播管理</h2>
      <el-button 
        v-if="currentStream?.status === 1" 
        type="danger" 
        @click="stopStream"
        :loading="stopping"
      >
        结束直播
      </el-button>
      <el-button 
        v-else-if="currentStream?.status === 0" 
        type="success" 
        @click="startStream"
        :loading="starting"
      >
        开始直播
      </el-button>
    </div>

    <div class="stream-info">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>直播信息</span>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <label>直播标题：</label>
            <span>{{ currentStream?.title }}</span>
          </div>
          <div class="info-item">
            <label>直播状态：</label>
            <el-tag :type="getStatusTagType(currentStream?.status)">
              {{ getStatusText(currentStream?.status) }}
            </el-tag>
          </div>
          <div class="info-item">
            <label>流密钥：</label>
            <span class="stream-key">{{ currentStream?.stream_key }}</span>
            <el-button type="text" @click="copyStreamKey">复制</el-button>
          </div>
          <div class="info-item" v-if="streamConfig.push_url">
            <label>推流地址：</label>
            <span class="push-url">{{ streamConfig.push_url }}</span>
            <el-button type="text" @click="copyPushUrl">复制</el-button>
          </div>
          <div class="info-item" v-if="streamConfig.play_url">
            <label>播放地址：</label>
            <span class="play-url">{{ streamConfig.play_url }}</span>
            <el-button type="text" @click="copyPlayUrl">复制</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <div class="push-guide">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>推流指南</span>
          </div>
        </template>
        
        <div class="guide-content">
          <h4>OBS推流设置：</h4>
          <ol>
            <li>打开OBS Studio</li>
            <li>进入"设置" → "推流"</li>
            <li>服务选择"自定义"</li>
            <li>服务器填写：<code>rtmp://127.0.0.1:1935/live</code></li>
            <li>推流码填写您的流密钥：<code>{{ currentStream?.stream_key }}</code></li>
            <li>点击"确定"保存设置</li>
            <li>点击"开始推流"</li>
            <li>返回此页面点击"开始直播"</li>
          </ol>
          
          <div class="tips">
            <h4>注意事项：</h4>
            <ul>
              <li>请确保推流软件和直播页面都使用相同的流密钥</li>
              <li>推流成功后，观众可以在直播列表看到您的直播</li>
              <li>直播结束后请及时点击"结束直播"</li>
            </ul>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  getLiveStreamDetail, 
  startLiveStream, 
  stopLiveStream 
} from '@/api/live.js'

const route = useRoute()
const streamId = parseInt(route.params.id)

const currentStream = ref(null)
const streamConfig = ref({})
const starting = ref(false)
const stopping = ref(false)

const loadStreamDetail = async () => {
  try {
    const response = await getLiveStreamDetail(streamId)
    currentStream.value = response.data
    
    // 生成推流和播放地址
    if (currentStream.value) {
      streamConfig.value = {
        push_url: `rtmp://127.0.0.1:1935/live/${currentStream.value.stream_key}`,
        play_url: `http://127.0.0.1:8000/live/${currentStream.value.stream_key}.m3u8`
      }
    }
  } catch (error) {
    console.error('加载直播详情失败:', error)
    ElMessage.error('加载直播详情失败')
  }
}

const startStream = async () => {
  starting.value = true
  try {
    await startLiveStream(streamId)
    ElMessage.success('直播已开始')
    await loadStreamDetail()
  } catch (error) {
    console.error('开始直播失败:', error)
    ElMessage.error('开始直播失败')
  } finally {
    starting.value = false
  }
}

const stopStream = async () => {
  stopping.value = true
  try {
    await stopLiveStream(streamId)
    ElMessage.success('直播已结束')
    await loadStreamDetail()
  } catch (error) {
    console.error('结束直播失败:', error)
    ElMessage.error('结束直播失败')
  } finally {
    stopping.value = false
  }
}

const copyStreamKey = async () => {
  try {
    await navigator.clipboard.writeText(currentStream.value.stream_key)
    ElMessage.success('流密钥已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const copyPushUrl = async () => {
  try {
    await navigator.clipboard.writeText(streamConfig.value.push_url)
    ElMessage.success('推流地址已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const copyPlayUrl = async () => {
  try {
    await navigator.clipboard.writeText(streamConfig.value.play_url)
    ElMessage.success('播放地址已复制')
  } catch (error) {
    ElMessage.error('复制失败')
  }
}

const getStatusTagType = (status) => {
  const typeMap = {
    0: 'warning',
    1: 'success',
    2: 'info'
  }
  return typeMap[status] || 'info'
}

const getStatusText = (status) => {
  const statusMap = {
    0: '未开始',
    1: '直播中',
    2: '已结束'
  }
  return statusMap[status] || '未知'
}

onMounted(() => {
  loadStreamDetail()
})
</script>

<style scoped>
.live-manage {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.manage-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stream-info,
.push-guide {
  margin-bottom: 20px;
}

.card-header {
  font-weight: 600;
  color: #333;
}

.info-grid {
  display: grid;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.info-item label {
  font-weight: 500;
  min-width: 80px;
  color: #666;
}

.stream-key,
.push-url,
.play-url {
  font-family: 'Courier New', monospace;
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 14px;
}

.guide-content h4 {
  margin: 16px 0 8px 0;
  color: #333;
}

.guide-content ol,
.guide-content ul {
  margin: 8px 0;
  padding-left: 20px;
}

.guide-content li {
  margin-bottom: 4px;
  line-height: 1.6;
}

.guide-content code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #e74c3c;
}

.tips {
  margin-top: 20px;
  padding: 16px;
  background: #f0f7ff;
  border-radius: 4px;
  border-left: 4px solid #1890ff;
}

.tips h4 {
  margin-top: 0;
  color: #1890ff;
}
</style>