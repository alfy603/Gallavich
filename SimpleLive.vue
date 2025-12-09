<template>
  <div class="live-container">
    <!-- 直播头部 -->
    <div class="live-header">
      <div class="header-left">
        <h1>🎥 直播中心</h1>
        <p>发现精彩直播内容，开启你的直播之旅</p>
      </div>
      <div class="header-right">
        <el-button 
          type="primary" 
          size="large" 
          @click="showCreateDialog = true"
          v-if="isLoggedIn && !isBroadcasting"
        >
          <el-icon><VideoCamera /></el-icon>
          开始直播
        </el-button>
        <el-button type="info" size="large" @click="goToLogin" v-else-if="!isLoggedIn">
          登录后开播
        </el-button>
      </div>
    </div>

    <!-- 创建直播对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建直播"
      width="500px"
    >
      <el-form :model="createForm" label-width="80px">
        <el-form-item label="直播标题">
          <el-input
            v-model="createForm.title"
            placeholder="请输入直播标题"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="直播分类">
          <el-select v-model="createForm.category" placeholder="选择分类" style="width: 100%">
            <el-option label="游戏直播" value="gaming" />
            <el-option label="娱乐直播" value="entertainment" />
            <el-option label="音乐直播" value="music" />
            <el-option label="知识分享" value="education" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="直播描述">
          <el-input
            v-model="createForm.description"
            type="textarea"
            placeholder="请输入直播描述"
            :rows="3"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-input
            v-model="createForm.tags"
            placeholder="请输入标签，用逗号分隔"
          />
        </el-form-item>
        <el-form-item label="封面图片">
          <div class="cover-upload" @click="triggerCoverUpload">
            <img v-if="createForm.cover_image" :src="createForm.cover_image" class="cover-preview">
            <div v-else class="cover-upload-placeholder">
              <el-icon><Plus /></el-icon>
              <span>点击上传封面</span>
            </div>
            <input 
              ref="coverInput" 
              type="file" 
              accept="image/*" 
              style="display: none" 
              @change="handleCoverChange"
            >
          </div>
          <div class="cover-tips">
            建议上传 800x450 比例的图片，大小不超过 2MB
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="startCameraPreview" v-if="!cameraStarted">开启摄像头</el-button>
        <el-button type="primary" plain @click="startCameraPreview" v-else>重新预览</el-button>
        <el-button type="success" @click="createLive" :loading="creating">
          开始直播
        </el-button>
      </template>
    </el-dialog>

    <!-- 摄像头预览 -->
    <div v-if="showCameraPreview" class="camera-preview-dialog">
      <div class="camera-preview">
        <div class="preview-header">
          <h3>摄像头预览</h3>
          <el-button type="danger" size="small" @click="stopCameraPreview">
            <el-icon><Close /></el-icon>关闭
          </el-button>
        </div>
        <div class="video-container">
          <video ref="cameraVideo" autoplay muted playsinline class="camera-video"></video>
          <div v-if="!cameraStarted" class="camera-placeholder">
            <el-icon size="48"><VideoCamera /></el-icon>
            <p>正在请求摄像头权限...</p>
          </div>
        </div>
        <div class="camera-controls">
          <el-button @click="switchCamera" :disabled="cameras.length <= 1">
            <el-icon><Refresh /></el-icon>切换摄像头
          </el-button>
          <el-button @click="toggleCamera" :type="cameraActive ? 'warning' : 'success'">
            <el-icon><VideoPause v-if="cameraActive" /><VideoPlay v-else /></el-icon>
            {{ cameraActive ? '关闭摄像头' : '开启摄像头' }}
          </el-button>
          <el-button @click="toggleMicrophone" :type="microphoneActive ? 'warning' : 'success'">
            <el-icon><Microphone /></el-icon>
            {{ microphoneActive ? '关闭麦克风' : '开启麦克风' }}
          </el-button>
        </div>
      </div>
    </div>

    <!-- 主播控制面板 -->
    <div v-if="isBroadcasting" class="broadcast-panel">
      <div class="broadcast-info">
        <div class="broadcast-status">
          <h3>🎬 直播中 - {{ currentBroadcast?.title }}</h3>
          <p>主播：{{ currentBroadcast?.streamer || currentUserName }}</p>
          <p>实时状态：摄像头 {{ cameraActive ? '开启' : '关闭' }} / 麦克风 {{ microphoneActive ? '开启' : '关闭' }}</p>
        </div>
        <div class="broadcast-actions">
          <el-button @click="toggleCamera" :type="cameraActive ? 'warning' : 'success'">
            <el-icon><VideoPause v-if="cameraActive" /><VideoPlay v-else /></el-icon>
            {{ cameraActive ? '暂停视频' : '开启视频' }}
          </el-button>
          <el-button @click="toggleMicrophone" :type="microphoneActive ? 'warning' : 'success'">
            <el-icon><Microphone /></el-icon>
            {{ microphoneActive ? '关闭麦克风' : '开启麦克风' }}
          </el-button>
          <el-button @click="switchCamera" :disabled="cameras.length <= 1">
            <el-icon><Refresh /></el-icon>切换
          </el-button>
          <el-button type="danger" @click="endBroadcast">
            <el-icon><SwitchButton /></el-icon>结束直播
          </el-button>
        </div>
      </div>
      <div class="broadcast-content">
        <div class="camera-feed">
          <video ref="broadcastVideo" autoplay muted playsinline class="broadcast-video"></video>
          <div v-if="!cameraActive" class="camera-off-placeholder">
            <el-icon size="48"><VideoCamera /></el-icon>
            <p>摄像头已关闭</p>
          </div>
        </div>
        <!-- 主播评论区（复用聊天室 UI） -->
        <div class="broadcast-chat chat-section">
          <div class="chat-header">
            <h3>聊天室 ({{ chatMessages.length }})</h3>
            <div class="chat-stats">
              <el-tag type="info">在线 {{ onlineCount }} 人</el-tag>
              <el-tag type="success">热度 {{ calculateHotValue() }}</el-tag>
            </div>
          </div>
          <div class="chat-messages" ref="broadcastChatEl">
            <div
              v-for="msg in chatMessages"
              :key="msg.id"
              class="chat-message"
              :class="{ 'own-message': msg.isOwn, 'system-message': msg.isSystem }"
            >
              <el-avatar :size="28" :src="msg.avatar" />
              <div class="message-content">
                <div class="message-header">
                  <span class="username">{{ msg.username }}</span>
                  <span class="time">{{ msg.time }}</span>
                </div>
                <p class="message-text">{{ msg.content }}</p>
              </div>
            </div>
          </div>
          <div class="chat-input-area">
            <div class="quick-actions">
              <el-button
                v-for="action in quickActions"
                :key="action.text"
                size="small"
                :type="action.type"
                @click="sendQuickMessage(action)"
              >
                {{ action.text }}
              </el-button>
            </div>
            <div class="input-wrapper">
              <el-input
                v-model="newMessage"
                placeholder="和观众聊点什么..."
                @keyup.enter="sendMessage"
                size="large"
                :maxlength="100"
                show-word-limit
              >
                <template #append>
                  <el-button type="primary" @click="sendMessage" :disabled="!newMessage.trim()">
                    发送
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </div>
        <div class="broadcast-stream-info">
          <h4>直播信息</h4>
          <div class="info-item">
            <strong>推流地址:</strong>
            <code>{{ currentBroadcast?.push_url }}</code>
          </div>
          <div class="info-item">
            <strong>流密钥:</strong>
            <code>{{ currentBroadcast?.stream_key }}</code>
          </div>
          <p class="stream-tips">若需外部推流（OBS 等），请使用上方地址与密钥。</p>
        </div>
      </div>
    </div>

    <!-- 直播分类 -->
    <div class="live-categories">
      <el-radio-group v-model="currentCategory" @change="onCategoryChange">
        <el-radio-button label="all">全部直播</el-radio-button>
        <el-radio-button label="gaming">游戏直播</el-radio-button>
        <el-radio-button label="entertainment">娱乐直播</el-radio-button>
        <el-radio-button label="music">音乐直播</el-radio-button>
        <el-radio-button label="education">知识分享</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 直播列表 -->
    <div class="live-grid">
      <div 
        v-for="stream in liveStreams" 
        :key="stream.id" 
        class="live-card"
      >
        <div class="card-cover" @click="enterLiveRoom(stream)">
          <img :src="stream.cover || '/imgs/live-default.svg'" alt="直播封面" @error="handleImageError">
          <div class="live-badge" :class="getStatusClass(stream.status)">
            {{ getStatusText(stream.status) }}
          </div>
          <div class="viewer-count">
            <el-icon><View /></el-icon>
            {{ formatViewerCount(stream.viewer_count || 0) }}
          </div>
          <div class="live-tag">{{ getCategoryText(stream.category) }}</div>
          <!-- 删除按钮（只有自己创建的直播才显示） -->
          <el-button 
            v-if="isMyStream(stream)"
            class="delete-btn"
            type="danger" 
            size="small" 
            circle
            @click.stop="confirmDelete(stream)"
            title="删除直播"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>
        
        <div class="card-content" @click="enterLiveRoom(stream)">
          <div class="streamer-info">
            <el-avatar :size="32" :src="stream.avatar" />
            <div class="streamer-details">
              <h4 class="stream-title">{{ stream.title }}</h4>
              <p class="streamer-name">{{ stream.streamer || currentUserName }}</p>
            </div>
          </div>
          
          <!-- 添加描述 -->
          <p v-if="stream.description" class="stream-description">
            {{ stream.description }}
          </p>
          
          <!-- 添加标签 -->
          <div v-if="stream.tags" class="stream-tags">
            <el-tag
              v-for="tag in stream.tags.split(',')"
              :key="tag"
              size="small"
              class="tag-item"
            >
              {{ tag.trim() }}
            </el-tag>
          </div>
          
          <div class="stream-stats">
            <span class="stat-item">
              <el-icon><ChatDotRound /></el-icon>
              {{ stream.chat_count || 0 }}
            </span>
            <span class="stat-item">
              <el-icon><Star /></el-icon>
              {{ formatLikeCount(stream.likes || 0) }}
            </span>
            <span class="stat-item">
              <el-icon><Clock /></el-icon>
              {{ stream.created_time }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="hasMore && !loading && liveStreams.length">
      <el-button type="primary" plain @click="loadMore" :loading="loading">加载更多</el-button>
    </div>

    <!-- 空状态 -->
    <div v-if="liveStreams.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无直播内容">
        <el-button type="primary" @click="showCreateDialog = true" v-if="isLoggedIn">
          成为第一个主播
        </el-button>
        <el-button type="primary" @click="goToLogin" v-else>
          登录后开播
        </el-button>
      </el-empty>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="6" animated />
    </div>

    <!-- 直播间弹窗 -->
    <el-dialog 
      v-model="showLiveRoom" 
      :title="currentLive?.title" 
      width="90%" 
      fullscreen
      :show-close="true"
      @close="closeLiveRoom"
    >
      <div class="live-room">
        <!-- 视频区域 -->
        <div class="video-section">
          <div class="video-player">
            <div class="video-placeholder">
                <!-- 真实 video 元素，供 flv.js 使用 -->
                <video 
                  ref="liveRoomVideo" 
                  autoplay 
                  playsinline 
                  controls 
                  muted 
                  class="broadcast-video"
                  @loadedmetadata="() => console.log('🎥 视频元素元数据加载完成', liveRoomVideo)"
                  @canplay="() => console.log('🎥 视频可以播放', liveRoomVideo)"
                />
                <div class="placeholder-content">
                  <el-icon size="64"><VideoPlay /></el-icon>
                  <h3>直播画面区域</h3>
                  <p>当前直播: {{ currentLive?.title }}</p>
                  <div class="stream-status">
                    <el-tag type="success" size="large">直播中</el-tag>
                    <span class="viewer-count-large">
                      <el-icon><View /></el-icon>
                      {{ formatViewerCount(currentLive?.viewer_count || 0) }} 观看
                    </span>
                  </div>
                </div>
              </div>
          </div>
          
          <div class="stream-info">
            <h2>{{ currentLive?.title }}</h2>
            
            <!-- 添加描述和标签 -->
            <p v-if="currentLive?.description" class="live-description">
              {{ currentLive.description }}
            </p>
            
            <div v-if="currentLive?.tags" class="live-tags">
              <el-tag
                v-for="tag in currentLive.tags.split(',')"
                :key="tag"
                type="info"
                class="tag-item"
              >
                {{ tag.trim() }}
              </el-tag>
            </div>
            
            <div class="stream-meta">
              <div class="streamer">
                <el-avatar :size="40" :src="currentLive?.avatar" />
                <div class="streamer-details">
                  <strong>{{ currentLive?.streamer || currentUserName }}</strong>
                  <span>主播</span>
                </div>
              </div>
              <div class="stats">
                <el-statistic title="观看人数" :value="currentLive?.viewer_count || 0" />
                <el-statistic title="点赞数" :value="currentLive?.likes || 0" />
              </div>
            </div>
            <div class="action-buttons">
              <el-button type="primary" @click="sendLike" :icon="Star">
                点赞 {{ formatLikeCount(currentLive?.likes || 0) }}
              </el-button>
              <el-button type="success" @click="shareLive">
                <el-icon><Share /></el-icon>
                分享
              </el-button>
              <el-button type="info" @click="followStreamer" v-if="!isFollowing">
                <el-icon><Plus /></el-icon>
                关注主播
              </el-button>
              <el-button type="info" @click="unfollowStreamer" v-else>
                <el-icon><Check /></el-icon>
                已关注
              </el-button>
            </div>
          </div>
        </div>

        <!-- 聊天区域 -->
        <div class="chat-section">
          <div class="chat-header">
            <h3>聊天室 ({{ chatMessages.length }})</h3>
            <div class="chat-stats">
              <el-tag type="info">在线 {{ onlineCount }} 人</el-tag>
              <el-tag type="success">热度 {{ calculateHotValue() }}</el-tag>
            </div>
          </div>
          
          <div class="chat-messages" ref="liveRoomChatEl">
            <div 
              v-for="msg in chatMessages" 
              :key="msg.id"
              class="chat-message"
              :class="{ 'own-message': msg.isOwn, 'system-message': msg.isSystem }"
            >
              <el-avatar :size="28" :src="msg.avatar" />
              <div class="message-content">
                <div class="message-header">
                  <span class="username">{{ msg.username }}</span>
                  <span class="time">{{ msg.time }}</span>
                </div>
                <p class="message-text">{{ msg.content }}</p>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <div class="quick-actions">
              <el-button 
                v-for="action in quickActions" 
                :key="action.text"
                size="small" 
                :type="action.type"
                @click="sendQuickMessage(action)"
              >
                {{ action.text }}
              </el-button>
            </div>
            
            <div class="input-wrapper">
              <el-input
                v-model="newMessage"
                placeholder="和主播聊点什么..."
                @keyup.enter="sendMessage"
                size="large"
                :maxlength="100"
                show-word-limit
              >
                <template #prepend>
                  <el-button :icon="Star" @click="sendLike">点赞</el-button>
                </template>
                <template #append>
                  <el-button type="primary" @click="sendMessage" :disabled="!newMessage.trim()">
                    发送
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, onUnmounted } from 'vue'
import flvjs from 'flv.js'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  VideoCamera, 
  View, 
  ChatDotRound, 
  Star, 
  VideoPlay,
  Plus,
  Share,
  SwitchButton,
  Check,
  Clock,
  Close,
  Refresh,
  VideoPause,
  Microphone,
  Delete
} from '@element-plus/icons-vue'
import { createLiveStream, getLiveStreams, getLiveStreamDetail, likeLiveStream, addLiveComment, getLiveComments, endLiveStream, deleteLiveStream } from '../apis/live'
import LiveBroadcastPanel from '../components/LiveBroadcastPanel.vue'

export default {
  name: 'SimpleLive',
  components: {
    LiveBroadcastPanel,
    VideoCamera,
    View,
    ChatDotRound,
    Star,
    VideoPlay,
    Plus,
    Share,
    SwitchButton,
    Check,
    Clock,
    Close,
    Refresh,
    VideoPause,
    Microphone,
    Delete
  },
  setup() {
    const router = useRouter()
    
    // 状态管理
    const currentCategory = ref('all')
    const showLiveRoom = ref(false)
    const showCreateDialog = ref(false)
    const creating = ref(false)
    const loading = ref(false)
    const isBroadcasting = ref(false)
    const isFollowing = ref(false)
    const currentLive = ref(null)
    const currentBroadcast = ref(null)
    const newMessage = ref('')
    const onlineCount = ref(156)
    const coverInput = ref(null)
    const showCameraPreview = ref(false)
    const cameraVideo = ref(null)
    const broadcastVideo = ref(null)
    const cameraStarted = ref(false)
    const cameraActive = ref(false)
    const microphoneActive = ref(true)
    const cameras = ref([])
    const currentCameraIndex = ref(0)
    let mediaStream = null

    // 添加轮询定时器变量
    const pollInterval = ref(null)

    // 模拟数据
    const liveStreams = ref([])
    const page = ref(1)
    const pageSize = ref(20)
    const hasMore = ref(true)

    // 聊天消息数据
    const chatMessages = ref([
      {
        id: 1,
        username: '系统消息',
        avatar: '/api/imgs/avatar-default.jpg',
        content: '欢迎来到直播间！聊天室规则：请文明发言，尊重主播和其他观众',
        time: '12:00',
        isOwn: false,
        isSystem: true
      }
    ])

    const quickActions = [
      { text: '👍 点赞', type: 'primary' },
      { text: '🎉 666', type: 'success' },
      { text: '❤️ 喜欢', type: 'danger' },
      { text: '🔥 太棒了', type: 'warning' },
      { text: '👏 鼓掌', type: 'info' }
    ]

    // DOM 元素 refs
    const broadcastChatEl = ref(null)
    const liveRoomChatEl = ref(null)
    // 视频元素 refs（用于 flv 播放）
    const liveRoomVideo = ref(null)

    // 简单的 FLV 播放器管理
    const flvPlayer = ref(null)

    // 修改后的播放器设置函数，新增 isBroadcaster 逻辑
    const setupFLVPlayer = (videoElement, streamKey, isBroadcaster = false) => {
      console.log('🎥 设置播放器，用户身份:', isBroadcaster ? '主播' : '观众')
      
      if (!streamKey) {
        console.error('❌ 没有流密钥')
        return
      }

      // 使用 HLS 地址
      const hlsUrl = `http://localhost:8080/hls/${streamKey}.m3u8`
      console.log('📺 HLS 地址:', hlsUrl)

      // 测试 HLS 流是否可访问
      testHLSStream(hlsUrl).then(available => {
        if (available) {
          setupHLSVideo(videoElement, hlsUrl)
        } else {
          console.log('HLS 流暂不可用')
          // 🔥 关键修改：只有主播才显示推流指南，观众显示等待提示
          if (isBroadcaster) {
            showStreamingGuide(videoElement, streamKey)
          } else {
            showWaitingPrompt(videoElement)
          }
        }
      })
    }

    // 新增：观众等待提示
    const showWaitingPrompt = (videoElement) => {
      const waitingHTML = `
        <div style="width:100%;height:100%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;border-radius:8px;padding:20px;text-align:center;">
          <el-icon size="48"><VideoCamera /></el-icon>
          <h3 style="margin:16px 0 8px 0;">等待主播开播</h3>
          <p>主播正在准备，请稍候...</p>
          <p style="font-size:12px;opacity:0.8;margin-top:8px;">如果长时间无画面，请刷新页面</p>
        </div>
      `
      
      if (videoElement.parentNode) {
        const guideDiv = document.createElement('div')
        guideDiv.innerHTML = waitingHTML
        videoElement.parentNode.appendChild(guideDiv)
      }
    }

    const testHLSStream = async (hlsUrl) => {
      try {
        const response = await fetch(hlsUrl)
        return response.ok
      } catch (error) {
        console.log('HLS 流测试失败:', error.message)
        return false
      }
    }

    const setupHLSVideo = (videoElement, hlsUrl) => {
      // 使用原生 HLS 支持
      videoElement.src = hlsUrl
      videoElement.controls = true
      
      videoElement.addEventListener('loadeddata', () => {
        console.log('✅ HLS 视频加载成功')
        videoElement.play().catch(e => {
          console.log('自动播放被阻止，需要用户点击:', e)
        })
      })
      
      videoElement.addEventListener('error', (e) => {
        console.error('HLS 播放错误:', e)
      })
    }

    const showStreamingGuide = (videoElement, streamKey) => {
      // 显示友好的推流指南
      const guideHTML = `
        <div style="width:100%;height:100%;background:linear-gradient(135deg,#667eea 0%,#764ba2 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;color:white;border-radius:8px;padding:20px;text-align:center;">
          <el-icon size="48"><VideoCamera /></el-icon>
          <h3 style="margin:16px 0 8px 0;">直播推流指南</h3>
          <p>流密钥: <code style="background:rgba(0,0,0,0.3);padding:4px 8px;border-radius:4px;">${streamKey}</code></p>
          <div style="margin-top:16px;background:rgba(255,255,255,0.1);padding:12px;border-radius:6px;text-align:left;">
            <p style="margin:4px 0;font-size:14px;"><strong>服务器:</strong> rtmp://localhost:1935/live</p>
            <p style="margin:4px 0;font-size:14px;"><strong>流密钥:</strong> ${streamKey}</p>
          </div>
        </div>
      `
      
      if (videoElement.parentNode) {
        const guideDiv = document.createElement('div')
        guideDiv.innerHTML = guideHTML
        videoElement.parentNode.appendChild(guideDiv)
      }
    }

    // 添加播放错误处理
    const handlePlaybackError = () => {
      console.log('播放失败，显示离线状态')
      ElMessage.warning('直播流加载失败，请检查网络或联系主播')
    }

    const stopFLVPlayer = () => {
      try {
        if (flvPlayer.value) {
          flvPlayer.value.destroy()
          flvPlayer.value = null
        }
      } catch (e) {
        console.warn('停止 FLV 播放器失败', e)
      }
    }

    // 统一滚动到底部辅助
    const scrollChatToBottom = () => {
      const target = liveRoomChatEl.value || broadcastChatEl.value
      if (target) {
        try { target.scrollTop = target.scrollHeight } catch { /* ignore */ }
      } else {
        const legacy = document.querySelector('.chat-messages')
        if (legacy) legacy.scrollTop = legacy.scrollHeight
      }
    }

    const createForm = ref({
      title: '',
      category: 'entertainment',
      description: '',
      tags: '',
      cover_image: ''
    })

    // 计算属性
    const isLoggedIn = computed(() => {
      return localStorage.getItem('token') !== null
    })
    
    // 获取用户名
    const decodeJWTName = () => {
      const token = localStorage.getItem('token')
      if (!token || !token.includes('.')) return null
      try {
        const payload = token.split('.')[1]
          .replace(/-/g, '+').replace(/_/g, '/')
        const json = JSON.parse(decodeURIComponent(escape(atob(payload))))
        return json.username || json.userName || json.name || json.nick || json.nickname || json.sub || null
      } catch { return null }
    }
    
    const getStoredUsername = () => {
      const direct = localStorage.getItem('username') || localStorage.getItem('userName') || localStorage.getItem('name')
      if (direct) return direct
      const buckets = ['user', 'userInfo', 'profile', 'account', 'currentUser', 'loginUser']
      for (const k of buckets) {
        const raw = localStorage.getItem(k)
        if (!raw) continue
        try {
          const obj = JSON.parse(raw)
          const v = obj?.username || obj?.userName || obj?.name || obj?.nick || obj?.nickname || obj?.profile?.name
          if (v) return v
        } catch { /* ignore */ }
      }
      const jwt = decodeJWTName()
      return jwt || '匿名主播'
    }
    
    const currentUserName = computed(() => getStoredUsername())

    // 添加轮询函数
    const startChatPolling = () => {
      // 清除之前的轮询
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
      }
      
      // 每3秒获取一次最新消息
      pollInterval.value = setInterval(async () => {
        let streamId = null
        if (currentLive.value?.id) {
          // 观众视角
          streamId = currentLive.value.id
        } else if (isBroadcasting.value && currentBroadcast.value?.stream_id) {
          // 主播视角
          streamId = currentBroadcast.value.stream_id
        }
        
        if (streamId) {
          console.log('轮询获取聊天消息，streamId:', streamId)
          await loadChatMessages(streamId)
        }
      }, 3000) // 3秒一次
    }
    
    // 停止轮询
    const stopChatPolling = () => {
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
        pollInterval.value = null
        console.log('停止聊天轮询')
      }
    }

    // 方法
    // 初始化摄像头
    const initCamera = async () => {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices()
        cameras.value = devices.filter(d => d.kind === 'videoinput')
        const selectedId = cameras.value[currentCameraIndex.value]?.deviceId
        const constraints = {
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            ...(selectedId ? { deviceId: { exact: selectedId } } : {})
          },
          audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
        }
        mediaStream = await navigator.mediaDevices.getUserMedia(constraints)
        if (cameraVideo.value) {
          cameraVideo.value.srcObject = mediaStream
          cameraVideo.value.play?.().catch(()=>{})
        }
        cameraStarted.value = true
        cameraActive.value = true
        microphoneActive.value = true
        ElMessage.success('摄像头已启动')
      } catch (e) {
        console.error('摄像头启动失败', e)
        ElMessage.error('摄像头或麦克风无法访问，请检查权限')
        throw e
      }
    }

    const ensureCameraStarted = async () => {
      if (!cameraStarted.value) {
        await initCamera()
      }
    }

    const startCameraPreview = async () => {
      showCameraPreview.value = true
      await ensureCameraStarted()
    }

    const stopCameraPreview = () => {
      showCameraPreview.value = false
    }

    const switchCamera = async () => {
      if (cameras.value.length <= 1) return
      currentCameraIndex.value = (currentCameraIndex.value + 1) % cameras.value.length
      if (mediaStream) {
        mediaStream.getTracks().forEach(t => t.stop())
      }
      await initCamera()
    }

    const toggleCamera = () => {
      if (!mediaStream) return
      const track = mediaStream.getVideoTracks()[0]
      if (!track) return
      track.enabled = !track.enabled
      cameraActive.value = track.enabled
      ElMessage.info(track.enabled ? '摄像头已开启' : '摄像头已关闭')
    }

    const toggleMicrophone = () => {
      if (!mediaStream) return
      const track = mediaStream.getAudioTracks()[0]
      if (!track) return
      track.enabled = !track.enabled
      microphoneActive.value = track.enabled
      ElMessage.info(track.enabled ? '麦克风已开启' : '麦克风已关闭')
    }

    const cleanupMedia = () => {
      if (mediaStream) {
        mediaStream.getTracks().forEach(t => t.stop())
        mediaStream = null
      }
      cameraStarted.value = false
      cameraActive.value = false
  // 停止 FLV 播放器
  stopFLVPlayer()
    }

    const createLive = async () => {
      if (!createForm.value.title.trim()) {
        ElMessage.warning('请输入直播标题')
        return
      }
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录')
        goToLogin()
        return
      }
      
      try {
        await ensureCameraStarted()
      } catch (e) {
        // 不阻断创建，已在 initCamera 内提示
      }
      
      creating.value = true
      try {
        const submitData = {
          title: createForm.value.title,
          category: createForm.value.category,
          description: createForm.value.description,
          tags: createForm.value.tags,
          streamer_name: currentUserName.value,
          streamer: currentUserName.value
        }
        const res = await createLiveStream(submitData)
        if (res.code === 200) {
          ElMessage.success('直播创建成功！')
          currentBroadcast.value = res.data
          if (!currentBroadcast.value.streamer) {
            currentBroadcast.value.streamer = currentBroadcast.value.streamer_name || currentUserName.value
          }
          isBroadcasting.value = true
          showCreateDialog.value = false
          showCameraPreview.value = false
          createForm.value = {
            title: '',
            category: 'entertainment',
            description: '',
            tags: '',
            cover_image: ''
          }
          loadStreams()
          
          nextTick(() => {
            if (broadcastVideo.value && mediaStream) {
              broadcastVideo.value.srcObject = mediaStream
              broadcastVideo.value.play?.().catch(()=>{})
            }
          })
          
          // 加载当前直播的聊天记录
          if (currentBroadcast.value?.stream_id) {
            await loadChatMessages(currentBroadcast.value.stream_id)
            // 新增：开始轮询
            startChatPolling()
            // 使用流密钥启动播放器（主播预览）
            console.log('🚀 创建直播成功，准备启动播放器', currentBroadcast.value)
            nextTick(() => {
              console.log('📺 启动主播播放器', {
                videoElement: broadcastVideo.value, 
                streamKey: currentBroadcast.value?.stream_key
              })
              try {
                if (broadcastVideo.value && currentBroadcast.value?.stream_key) {
                  const streamKey = currentBroadcast.value.stream_key
                  console.log('✅ 主播使用流密钥启动播放器:', streamKey)
                  setupFLVPlayer(broadcastVideo.value, streamKey, true) // 传 true 表示主播
                }
              } catch (e) { console.warn('启动主播播放器失败', e) }
            })
          }
        } else {
          ElMessage.error(res.message || '创建直播失败')
        }
      } catch (error) {
        console.error('创建直播失败:', error)
        ElMessage.error('创建直播失败')
      } finally {
        creating.value = false
      }
    }

    const endBroadcast = async () => {
  try {
    console.log('🛑 === 点击结束直播按钮 ===')
    console.log('🔍 当前直播状态:')
    console.log('   isBroadcasting:', isBroadcasting.value)
    console.log('   currentBroadcast:', currentBroadcast.value)
    
    if (!currentBroadcast.value) {
      console.error('❌ currentBroadcast 为空！')
      ElMessage.error('找不到直播信息，请刷新页面重试')
      return
    }
    
    const streamId = currentBroadcast.value.stream_id || currentBroadcast.value.id
    console.log('🔍 要结束的直播ID:', streamId)
    
    if (!streamId) {
      console.error('❌ 无法获取直播ID')
      ElMessage.error('无法获取直播ID')
      return
    }
    
    // 🔒 修复权限检查逻辑
    console.log('🔍 检查用户权限...')
    
    // 直接从JWT token获取当前用户ID
    const token = localStorage.getItem('token')
    if (!token) {
      ElMessage.warning('请先登录')
      return
    }
    
    try {
      const payload = token.split('.')[1]
      const userInfo = JSON.parse(atob(payload))
      const currentUserId = userInfo.id
      console.log('🔍 当前用户ID:', currentUserId)
      
      // 注意：这里我们信任后端会做正确的权限验证
      // 前端只做基本检查，真正的权限验证在后端
      
    } catch (e) {
      console.error('解析用户信息失败:', e)
    }
    
    console.log('✅ 准备弹出确认对话框...')
    
    await ElMessageBox.confirm('确定要结束直播吗？', '结束直播', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    console.log('✅ 用户确认结束，调用API...')
    
    const res = await endLiveStream(streamId)
    console.log('📡 API响应:', res)
    
    if (res.code === 200) {
      ElMessage.success('直播已结束')
      isBroadcasting.value = false
      currentBroadcast.value = null
      stopChatPolling()
      loadStreams()
      cleanupMedia()
    } else {
      ElMessage.error(res.message || '结束直播失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('❌ 结束直播异常:', error)
      ElMessage.error('结束直播失败')
    }
  }
}

    const triggerCoverUpload = () => {
      coverInput.value?.click()
    }

    const handleCoverChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        const maxSize = 2 * 1024 * 1024
        if (file.size > maxSize) {
          ElMessage.warning('图片大小不能超过 2MB')
          event.target.value = ''
          return
        }
        
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif']
        if (!allowedTypes.includes(file.type)) {
          ElMessage.warning('请选择 JPEG、PNG 或 GIF 格式的图片')
          event.target.value = ''
          return
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          createForm.value.cover_image = e.target.result
        }
        reader.readAsDataURL(file)
      }
    }

    const enterLiveRoom = async (stream) => {
      loading.value = true
      try {
        const res = await getLiveStreamDetail(stream.id)
        if (res.code === 200) {
          currentLive.value = res.data
          if (!currentLive.value.streamer) {
            currentLive.value.streamer = currentLive.value.streamer_name || currentUserName.value
          }
          showLiveRoom.value = true
          
          // 加载聊天记录
          await loadChatMessages(stream.id)
          
          // 开始轮询
          startChatPolling()
          
          console.log('🚀 进入直播间成功，准备启动播放器', currentLive.value)
          
          // 🔥 修正：等待 DOM 完全渲染后再初始化播放器
          nextTick(() => {
            setTimeout(() => {
              console.log('📺 延迟启动观众播放器', {
                videoElement: liveRoomVideo.value,
                streamKey: currentLive.value?.stream_key
              })
              
              try {
                if (liveRoomVideo.value) {
                  const streamKey = currentLive.value?.stream_key
                  if (streamKey) {
                    console.log('✅ 观众使用流密钥启动播放器:', streamKey)
                    setupFLVPlayer(liveRoomVideo.value, streamKey, false) // 传 false 表示观众
                  } else {
                    console.error('❌ 没有流密钥')
                    ElMessage.warning('该直播暂无画面')
                  }
                } else {
                  console.error('❌ video 元素未找到')
                }
              } catch (e) { 
                console.warn('启动观众播放器失败', e)
                ElMessage.error('播放器初始化失败')
              }
              
              scrollChatToBottom()
            }, 800) // 🔥 增加延迟确保 DOM 完全渲染
          })
        } else {
          ElMessage.error('进入直播间失败')
        }
      } catch (error) {
        console.error('进入直播间失败:', error)
        ElMessage.error('进入直播间失败')
      } finally {
        loading.value = false
      }
    }

    const closeLiveRoom = () => {
      showLiveRoom.value = false
      currentLive.value = null
      newMessage.value = ''
      isFollowing.value = false
      // 新增：停止轮询
      stopChatPolling()
  // 停止 flv 播放器并刷新直播列表更新观看人数
  stopFLVPlayer()
  loadStreams()
    }

    const sendMessage = async () => {
      // 1. 基础校验
      const content = newMessage.value.trim()
      if (!content) return
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录后再发言')
        return
      }

      // 2. 解析当前直播 ID（主播或观众视角）
      const resolveActiveStreamId = () => {
        const broadcastId = isBroadcasting.value && currentBroadcast.value && (currentBroadcast.value.stream_id || currentBroadcast.value.id)
        if (broadcastId) return broadcastId
        const liveId = currentLive.value && (currentLive.value.stream_id || currentLive.value.id)
        return liveId || null
      }
      const activeStreamId = resolveActiveStreamId()
      if (!activeStreamId) {
        ElMessage.error('无法确定当前直播间 ID')
        return
      }

      // 3. 组装提交数据（后端应从 Token 中解析用户身份，前端不再硬编码 user_id）
      const messageData = { stream_id: activeStreamId, content }
      // console.debug('[Chat] sendMessage payload=', messageData)

      try {
        const res = await addLiveComment(messageData)
        if (res.code !== 200) {
          ElMessage.error(res.message || '发送消息失败')
          return
        }

        // 4. 本地追加消息（乐观更新）
        if (!Array.isArray(chatMessages.value)) chatMessages.value = []
        chatMessages.value.push({
          id: Date.now(),
            username: currentUserName.value,
            avatar: '/api/imgs/avatar-default.jpg',
            content,
            time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
            isOwn: true,
            isSystem: false
        })
        newMessage.value = ''
        nextTick(scrollChatToBottom)
      } catch (err) {
        console.error('[Chat] 发送消息失败:', err)
        ElMessage.error('发送消息失败')
      }
    }

    const sendQuickMessage = (action) => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录后再发言')
        return
      }

      const message = {
        id: Date.now(),
        username: currentUserName.value,
        avatar: '/api/imgs/avatar-default.jpg',
        content: action.text,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        isOwn: true,
        isSystem: false
      }
      
      if (!Array.isArray(chatMessages.value)) {
        console.warn('chatMessages 不是数组，重新初始化')
        chatMessages.value = []
      }
      
      chatMessages.value.push(message)
      nextTick(scrollChatToBottom)
    }

    const sendLike = async () => {
      if (!currentLive.value) return

      try {
        const res = await likeLiveStream(currentLive.value.id)
        if (res.code === 200) {
          ElMessage.success('点赞成功！')
          currentLive.value.likes = res.data.likes
          const stream = liveStreams.value.find(s => s.id === currentLive.value.id)
          if (stream) {
            stream.likes = res.data.likes
          }
        } else {
          ElMessage.error('点赞失败')
        }
      } catch (error) {
        console.error('点赞失败:', error)
        ElMessage.error('点赞失败')
      }
    }

    const shareLive = () => {
      const url = window.location.origin + `/live?room=${currentLive.value.id}`
      navigator.clipboard.writeText(url).then(() => {
        ElMessage.success('直播链接已复制到剪贴板')
      }).catch(() => {
        const textArea = document.createElement('textarea')
        textArea.value = url
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
        ElMessage.success('直播链接已复制到剪贴板')
      })
    }

    const followStreamer = () => {
      if (!isLoggedIn.value) {
        ElMessage.warning('请先登录后再关注')
        return
      }
      isFollowing.value = true
      ElMessage.success('关注成功！')
    }

    const unfollowStreamer = () => {
      isFollowing.value = false
      ElMessage.info('已取消关注')
    }

    const loadChatMessages = async (streamId) => {
      try {
        const res = await getLiveComments(streamId)
        console.log('聊天记录响应:', res)
        
        if (res.code === 200) {
          if (Array.isArray(res.data)) {
            chatMessages.value = [
              {
                id: 0,
                username: '系统消息',
                avatar: '/api/imgs/avatar-default.jpg',
                content: '欢迎来到直播间！聊天室规则：请文明发言，尊重主播和其他观众',
                time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
                isOwn: false,
                isSystem: true
              },
              ...res.data
            ]
          } else {
            console.warn('聊天数据不是数组:', res.data)
            chatMessages.value = getMockChatMessages()
          }
        } else {
          console.error('获取聊天记录失败:', res.message)
          chatMessages.value = getMockChatMessages()
        }
      } catch (error) {
        console.error('加载聊天记录失败:', error)
        chatMessages.value = getMockChatMessages()
      }
    }

    // 添加模拟聊天数据方法
    const getMockChatMessages = () => {
      return [
        {
          id: 1,
          username: '系统消息',
          avatar: '/api/imgs/avatar-default.jpg',
          content: '欢迎来到直播间！聊天室规则：请文明发言，尊重主播和其他观众',
          time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
          isOwn: false,
          isSystem: true
        }
      ]
    }

    const normalizeCategory = (raw) => {
      if (raw === undefined || raw === null || raw === '') return 'other'
      if (typeof raw === 'number') {
        const numMap = { 0: 'gaming', 1: 'entertainment', 2: 'music', 3: 'education', 4: 'other' }
        return numMap[raw] || 'other'
      }
      const v = String(raw).trim().toLowerCase()
      const enMap = {
        gaming: 'gaming', game: 'gaming', games: 'gaming', play: 'gaming',
        entertainment: 'entertainment', ent: 'entertainment', fun: 'entertainment', leisure: 'entertainment',
        music: 'music', song: 'music', songs: 'music', audio: 'music',
        education: 'education', edu: 'education', teach: 'education', study: 'education', knowledge: 'education', learning: 'education',
        other: 'other', misc: 'other', else: 'other'
      }
      const cnMap = {
        '游戏': 'gaming', '游戏直播': 'gaming', '游戏区': 'gaming',
        '娱乐': 'entertainment', '娱乐直播': 'entertainment', '休闲': 'entertainment', '综艺': 'entertainment',
        '音乐': 'music', '音乐直播': 'music', '歌唱': 'music', '唱歌': 'music',
        '知识': 'education', '知识分享': 'education', '教育': 'education', '教学': 'education', '学习': 'education',
        '其他': 'other'
      }
      return enMap[v] || cnMap[v] || 'other'
    }

    const loadStreams = async (reset = false) => {
      if (loading.value) return
      loading.value = true
      try {
        if (reset) {
          page.value = 1
          hasMore.value = true
          liveStreams.value = []
        }
        const params = { page: page.value, pageSize: pageSize.value }
        if (currentCategory.value !== 'all') {
          params.category = currentCategory.value
        }
        const res = await getLiveStreams(params)
        console.debug('[Live] loadStreams params=', params, 'response=', res)
        if (res.code === 200) {
          const raw = res.data?.list || res.data || []
          const mapped = raw.map(it => ({
            ...it,
            streamer: it.streamer || it.streamer_name || it.user_name || it.owner_name || '匿名主播',
            category: normalizeCategory(it.category || it.type || it.live_type)
          }))
          if (page.value === 1) {
            liveStreams.value = mapped
          } else {
            liveStreams.value.push(...mapped)
          }
          hasMore.value = mapped.length === pageSize.value
          console.debug('[Live] page=', page.value, 'received=', mapped.length, 'hasMore=', hasMore.value)
        } else {
          ElMessage.error('加载直播列表失败')
        }
      } catch (error) {
        console.error('加载直播列表失败:', error)
        ElMessage.error('网络异常，请稍后重试')
        if (page.value === 1) {
          liveStreams.value = []
        }
        hasMore.value = false
      } finally {
        loading.value = false
      }
    }

    const onCategoryChange = () => {
      loadStreams(true)
    }

    const loadMore = () => {
      if (!hasMore.value) return
      page.value += 1
      loadStreams(false)
    }

    const goToLogin = () => {
      router.push('/login')
    }

    const getStatusClass = (status) => {
      return status === 1 ? 'live' : 'offline'
    }

    const getStatusText = (status) => {
      return status === 1 ? '直播中' : '已结束'
    }

    const getCategoryText = (category) => {
      const categories = {
        gaming: '🎮 游戏',
        entertainment: '🎭 娱乐',
        music: '🎵 音乐',
        education: '📚 知识',
        other: '🔮 其他'
      }
      return categories[category] || categories.other
    }

    const formatViewerCount = (count) => {
      if (count >= 10000) {
        return (count / 10000).toFixed(1) + '万'
      }
      return count
    }

    const formatLikeCount = (count) => {
      if (count >= 1000) {
        return (count / 1000).toFixed(1) + 'k'
      }
      return count
    }

    const calculateHotValue = () => {
      if (!currentLive.value) return 0
      const viewerCount = currentLive.value.viewer_count || 0
      const likeCount = currentLive.value.likes || 0
      const chatCount = chatMessages.value.length
      return viewerCount + likeCount * 2 + chatCount * 3
    }

    const handleImageError = (event) => {
      event.target.src = '/imgs/live-default.svg'
    }

    // 添加播放状态检测方法
    const checkPlaybackStatus = () => {
      if (liveRoomVideo.value) {
        const video = liveRoomVideo.value
        console.log('播放器状态:', {
          readyState: video.readyState,
          networkState: video.networkState,
          currentTime: video.currentTime,
          buffered: video.buffered.length,
          paused: video.paused
        })
        
        // 如果长时间没有画面，显示提示
        if (video.readyState < 2 && video.networkState === 3) {
          console.warn('视频加载异常')
          ElMessage.warning('直播流加载中，请稍候...')
        }
      }
    }

    // 判断是否是当前用户创建的直播
    const isMyStream = (stream) => {
      if (!isLoggedIn.value) return false
      const getCurrentUserId = () => {
        try {
          const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
          return userInfo.id || userInfo.userId || null
        } catch { return null }
      }
      const currentUserId = getCurrentUserId()
      const streamUserId = stream.user_id || stream.userId
      if (currentUserId && streamUserId) {
        return currentUserId === streamUserId
      }
      const myName = currentUserName.value
      const streamUser = stream.streamer || stream.streamer_name || stream.user_name
      return myName === streamUser
    }

    // 确认删除直播
    const confirmDelete = async (stream) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除直播"${stream.title}"吗？此操作不可恢复。`,
          '删除直播',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'warning',
            confirmButtonClass: 'el-button--danger'
          }
        )
        await deleteStream(stream)
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除确认失败:', error)
        }
      }
    }

    // 删除直播
    const deleteStream = async (stream) => {
      try {
        const streamId = stream.stream_id || stream.id
        if (!streamId) {
          ElMessage.error('无法获取直播ID')
          return
        }
        const res = await deleteLiveStream(streamId)
        if (res.code === 200) {
          ElMessage.success('直播已删除')
          liveStreams.value = liveStreams.value.filter(s => {
            const sid = s.stream_id || s.id
            return sid !== streamId
          })
        } else {
          ElMessage.error(res.message || '删除失败')
        }
      } catch (error) {
        console.error('删除直播失败:', error)
        ElMessage.error('删除失败，请稍后重试')
      }
    }

    onMounted(() => {
      loadStreams(true)
      // 在播放器初始化后开始检测
      setInterval(checkPlaybackStatus, 5000)
    })

    onUnmounted(() => {
      cleanupMedia()
      // 新增：组件卸载时停止轮询
      stopChatPolling()
    })

    return {
      // 状态
      currentCategory,
      showLiveRoom,
      showCreateDialog,
      showCameraPreview,
      creating,
      loading,
      isBroadcasting,
      isFollowing,
      currentLive,
      currentBroadcast,
      newMessage,
      onlineCount,
      coverInput,
      cameraVideo,
      broadcastVideo,
      liveRoomVideo,
      cameraStarted,
      cameraActive,
      microphoneActive,
      cameras,
      pollInterval,
      
      // 数据
      liveStreams,
      page,
      pageSize,
      hasMore,
      chatMessages,
      quickActions,
      createForm,
      
      // 计算属性
      isLoggedIn,
      currentUserName,
      
      // 方法
      createLive,
      startCameraPreview,
      stopCameraPreview,
      switchCamera,
      toggleCamera,
      toggleMicrophone,
      endBroadcast,
      triggerCoverUpload,
      handleCoverChange,
      enterLiveRoom,
      closeLiveRoom,
      sendMessage,
      sendQuickMessage,
      sendLike,
      shareLive,
      followStreamer,
      unfollowStreamer,
      loadStreams,
      onCategoryChange,
      loadMore,
      goToLogin,
      getStatusClass,
      getStatusText,
      getCategoryText,
      formatViewerCount,
      formatLikeCount,
      calculateHotValue,
      handleImageError,
      checkPlaybackStatus,
      handlePlaybackError,
      isMyStream,
      confirmDelete,
      startChatPolling,
      stopChatPolling,
      setupFLVPlayer, // 暴露修改后的函数（如需调试）
      Star
    }
  }
}
</script>

<style scoped>
.live-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.live-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.header-left h1 {
  margin: 0;
  font-size: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.header-left p {
  margin: 8px 0 0 0;
  color: #666;
  font-size: 16px;
}

/* 主播控制面板样式 */
.broadcast-panel {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.broadcast-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.broadcast-status h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
}

.broadcast-status p {
  margin: 0;
  opacity: 0.9;
}

.stream-key-info {
  background: rgba(255,255,255,0.1);
  padding: 16px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,0.2);
}

.stream-key-info p {
  margin: 8px 0;
  font-size: 14px;
}

.stream-key-info code {
  background: rgba(0,0,0,0.3);
  padding: 6px 12px;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  margin-left: 8px;
}

.stream-tips {
  font-size: 12px;
  opacity: 0.8;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.live-categories {
  margin-bottom: 30px;
  text-align: center;
}

.live-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
  margin-bottom: 40px;
}

.live-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;
}

.live-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-cover {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.live-card:hover .card-cover img {
  transform: scale(1.05);
}

.live-badge {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  color: white;
  z-index: 2;
}

.live-badge.live {
  background: #ff4d4f;
}

.live-badge.offline {
  background: #999;
}

.viewer-count {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
  z-index: 2;
}

.live-tag {
  position: absolute;
  bottom: 12px;
  left: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  z-index: 2;
}

.delete-btn {
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 3;
  opacity: 0;
  transition: opacity 0.2s;
}

.live-card:hover .delete-btn {
  opacity: 1;
}

.card-content {
  padding: 16px;
}

.streamer-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.streamer-details {
  flex: 1;
}

.stream-title {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.streamer-name {
  margin: 0;
  font-size: 14px;
  color: #666;
}

/* 新增样式 */
.stream-description {
  margin: 8px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.4;
  display: -webkit-box;
  /* 非标准属性的兼容性增强写法 */
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stream-tags {
  margin: 8px 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag-item {
  margin: 2px;
}

.stream-stats {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #999;
}

/* 封面上传样式 */
.cover-upload {
  width: 100%;
  height: 120px;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color 0.3s;
}

.cover-upload:hover {
  border-color: #409eff;
}

.cover-upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: #8c939d;
}

.cover-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 6px;
}

.cover-tips {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

/* 加载状态 */
.loading-state {
  padding: 40px 0;
}

/* 空状态 */
.empty-state {
  grid-column: 1 / -1;
  padding: 60px 0;
  text-align: center;
}

.load-more {
  text-align: center;
  margin: 16px 0 32px;
}

/* 直播间样式 */
.live-room {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  height: 80vh;
}

.video-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.video-player {
  flex: 1;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.video-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.placeholder-content {
  text-align: center;
}

.placeholder-content h3 {
  margin: 16px 0 8px 0;
  font-size: 24px;
}

.placeholder-content p {
  margin: 0 0 16px 0;
  opacity: 0.9;
}

.stream-status {
  display: flex;
  align-items: center;
  gap: 16px;
  justify-content: center;
}

.viewer-count-large {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 16px;
}

.stream-info {
  background: white;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stream-info h2 {
  margin: 0 0 16px 0;
  font-size: 24px;
  color: #333;
}

/* 新增样式 */
.live-description {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #666;
  line-height: 1.5;
}

.live-tags {
  margin-bottom: 16px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.stream-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.streamer {
  display: flex;
  align-items: center;
  gap: 12px;
}

.streamer-details {
  display: flex;
  flex-direction: column;
}

.streamer-details strong {
  font-size: 16px;
}

.streamer-details span {
  font-size: 14px;
  color: #666;
}

.stats {
  display: flex;
  gap: 24px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 聊天区域样式 */
.chat-section {
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.chat-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  color: #333;
}

.chat-stats {
  display: flex;
  gap: 8px;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  max-height: 400px;
  background: #fafafa;
}

.chat-message {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: flex-start;
}

.chat-message.own-message {
  flex-direction: row-reverse;
}

.chat-message.own-message .message-content {
  align-items: flex-end;
}

.chat-message.system-message .message-text {
  background: #fff2e8;
  color: #fa541c;
  font-style: italic;
}

.message-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  max-width: 70%;
}

.message-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.username {
  font-weight: 600;
  font-size: 14px;
  color: #333;
}

.time {
  font-size: 12px;
  color: #999;
}

.message-text {
  margin: 0;
  padding: 8px 12px;
  background: #f5f5f5;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.4;
  word-break: break-word;
}

.chat-message.own-message .message-text {
  background: #e6f7ff;
  color: #1890ff;
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.quick-actions {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.input-wrapper {
  display: flex;
  gap: 8px;
}

/* 摄像头预览与主播视频区 */
.camera-preview-dialog {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
}

.camera-preview {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  width: 90%;
  max-width: 820px;
  max-height: 90vh;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.video-container {
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 16px;
}

.camera-video {
  width: 100%;
  height: 420px;
  object-fit: cover;
}

.camera-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #fff;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(2px);
}

.camera-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.broadcast-content {
  display: grid;
  grid-template-columns: 2fr 1.2fr 320px;
  gap: 20px;
  margin-top: 16px;
}

.camera-feed {
  position: relative;
  background: #000;
  border-radius: 10px;
  overflow: hidden;
  min-height: 360px;
}

.broadcast-chat {
  display: flex;
  flex-direction: column;
}

.broadcast-chat .chat-messages {
  max-height: 300px;
}

.broadcast-video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-off-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.6);
  color: #fff;
}

.broadcast-stream-info {
  background: rgba(255,255,255,0.15);
  backdrop-filter: blur(4px);
  padding: 20px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.3);
  color: #fff;
}

.broadcast-stream-info h4 { margin: 0 0 12px 0; }

.broadcast-stream-info .info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-size: 13px;
}



.broadcast-stream-info code {
  background: rgba(0,0,0,0.35);
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  word-break: break-all;
  flex: 1;
}

.broadcast-stream-info .stream-tips {
  font-size: 12px;
  opacity: .85;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.3);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .live-room {
    grid-template-columns: 1fr;
    height: auto;
  }
  
  .live-grid {
    grid-template-columns: 1fr;
  }
  
  .live-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .chat-section {
    height: 300px;
  }
  
  .broadcast-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stream-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .stats {
    width: 100%;
    justify-content: space-around;
  }
  
  .action-buttons {
    justify-content: center;
  }
}
</style>