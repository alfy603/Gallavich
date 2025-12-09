<template>
  <div class="live-room">
    <div class="live-container">
      <!-- 视频播放区域 -->
      <div class="video-section">
        <div class="video-player">
          <video 
            v-if="currentStream?.play_url && currentStream.status === 1"
            ref="videoPlayer"
            controls
            autoplay
            muted
            class="video-element"
          >
            <source :src="currentStream.play_url" type="application/x-mpegURL">
            您的浏览器不支持视频播放
          </video>
          <div v-else class="video-placeholder">
            <el-empty :description="getPlaceholderText()" />
          </div>
        </div>
        
        <div class="stream-info-panel">
          <h1 class="stream-title">{{ currentStream?.title }}</h1>
          <div class="stream-meta">
            <span class="streamer">
              <el-icon><User /></el-icon>
              {{ currentStream?.user_name }}
            </span>
            <span class="viewers" v-if="currentStream?.status === 1">
              <el-icon><View /></el-icon>
              {{ currentStream?.viewer_count }} 观看
            </span>
            <span class="status" :class="getStatusClass(currentStream?.status)">
              {{ getStatusText(currentStream?.status) }}
            </span>
          </div>
          <div class="stream-description" v-if="currentStream?.description">
            {{ currentStream.description }}
          </div>
        </div>
      </div>

      <!-- 聊天区域 -->
      <div class="chat-section">
        <div class="chat-header">
          <h3>聊天室</h3>
          <span class="online-count">{{ comments.length }} 条消息</span>
        </div>
        
        <div class="chat-messages" ref="chatMessages">
          <div 
            v-for="comment in comments" 
            :key="comment.id"
            class="chat-message"
          >
            <span class="message-time">{{ comment.timestamp }}</span>
            <span class="message-user">{{ comment.user_name }}：</span>
            <span class="message-content">{{ comment.content }}</span>
          </div>
        </div>

        <div class="chat-input" v-if="isLoggedIn">
          <el-input 
            v-model="newComment"
            placeholder="说点什么..."
            @keyup.enter="sendComment"
          >
            <template #append>
              <el-button @click="sendComment" :disabled="!newComment.trim()">
                发送
              </el-button>
            </template>
          </el-input>
        </div>
        <div v-else class="login-prompt">
          请<el-button type="text" @click="goToLogin">登录</el-button>后参与聊天
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, View } from '@element-plus/icons-vue'
import { 
  getLiveStreamDetail, 
  getLiveComments, 
  postLiveComment 
} from '@/api/live.js'

const route = useRoute()
const router = useRouter()
const streamId = parseInt(route.params.id)

const currentStream = ref(null)
const comments = ref([])
const newComment = ref('')
const videoPlayer = ref(null)
const chatMessages = ref(null)
let refreshInterval = null

const isLoggedIn = computed(() => {
  return localStorage.getItem('token') !== null
})

const loadStreamDetail = async () => {
  try {
    const response = await getLiveStreamDetail(streamId)
    currentStream.value = response.data
  } catch (error) {
    console.error('加载直播详情失败:', error)
    ElMessage.error('加载直播详情失败')
  }
}

const loadComments = async () => {
  try {
    const response = await getLiveComments(streamId)
    comments.value = response.data
    // 滚动到底部
    nextTick(() => {
      if (chatMessages.value) {
        chatMessages.value.scrollTop = chatMessages.value.scrollHeight
      }
    })
  } catch (error) {
    console.error('加载评论失败:', error)
  }
}

const sendComment = async () => {
  if (!newComment.value.trim()) return

  try {
    await postLiveComment(streamId, {
      content: newComment.value
    })
    newComment.value = ''
    // 重新加载评论
    await loadComments()
  } catch (error) {
    console.error('发送评论失败:', error)
    ElMessage.error('发送评论失败')
  }
}

const getStatusClass = (status) => {
  const statusMap = {
    0: 'not-started',
    1: 'live',
    2: 'ended'
  }
  return statusMap[status] || 'not-started'
}

const getStatusText = (status) => {
  const statusMap = {
    0: '未开始',
    1: '直播中',
    2: '已结束'
  }
  return statusMap[status] || '未开始'
}

const getPlaceholderText = () => {
  if (!currentStream.value) return '加载中...'
  
  const status = currentStream.value.status
  if (status === 0) return '直播尚未开始'
  if (status === 2) return '直播已结束'
  return '等待推流...'
}

const goToLogin = () => {
  router.push('/login')
}

// 设置定时刷新
const setupAutoRefresh = () => {
  refreshInterval = setInterval(() => {
    loadStreamDetail()
    loadComments()
  }, 5000) // 5秒刷新一次
}

onMounted(async () => {
  await loadStreamDetail()
  await loadComments()
  setupAutoRefresh()
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.live-room {
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
}

.live-container {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.video-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.video-player {
  width: 100%;
  background: #000;
}

.video-element {
  width: 100%;
  height: auto;
  max-height: 70vh;
}

.video-placeholder {
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
}

.stream-info-panel {
  padding: 20px;
}

.stream-title {
  margin: 0 0 12px 0;
  font-size: 24px;
  color: #333;
}

.stream-meta {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 12px;
  font-size: 14px;
  color: #666;
}

.stream-meta span {
  display: flex;
  align-items: center;
  gap: 4px;
}

.status.live {
  color: #ff4d4f;
  font-weight: 500;
}

.status.not-started {
  color: #faad14;
}

.status.ended {
  color: #999;
}

.stream-description {
  color: #666;
  line-height: 1.6;
}

.chat-section {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  height: 70vh;
}

.chat-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  color: #333;
}

.online-count {
  font-size: 12px;
  color: #666;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 400px;
}

.chat-message {
  margin-bottom: 12px;
  font-size: 14px;
  line-height: 1.4;
}

.message-time {
  color: #999;
  font-size: 12px;
  margin-right: 8px;
}

.message-user {
  color: #1890ff;
  font-weight: 500;
}

.message-content {
  color: #333;
}

.chat-input {
  padding: 15px 20px;
  border-top: 1px solid #f0f0f0;
}

.login-prompt {
  padding: 20px;
  text-align: center;
  color: #666;
  border-top: 1px solid #f0f0f0;
}

@media (max-width: 768px) {
  .live-container {
    grid-template-columns: 1fr;
  }
  
  .chat-section {
    height: 400px;
  }
}
</style>