<template>
  <div class="broadcast-panel" v-if="isBroadcasting">
    <!-- 主播控制面板 -->
    <el-card class="control-panel" shadow="always">
      <template #header>
        <div class="panel-header">
          <span>🎥 直播控制面板</span>
          <el-button type="danger" @click="endBroadcast" :loading="ending">
            结束直播
          </el-button>
        </div>
      </template>
      
      <div class="stream-info">
        <h3>{{ currentStream.title }}</h3>
        <div class="stats">
          <el-statistic title="观看人数" :value="currentStream.viewer_count" />
          <el-statistic title="点赞数" :value="currentStream.likes" />
          <el-statistic title="直播时长" :value="liveDuration" />
        </div>
      </div>
      
      <div class="stream-config">
        <h4>推流信息</h4>
        <el-alert
          title="请使用OBS等推流软件进行直播"
          type="info"
          :closable="false"
        />
        <div class="stream-urls">
          <el-input
            v-model="currentStream.push_url"
            readonly
            placeholder="推流地址"
          >
            <template #prepend>推流地址</template>
            <template #append>
              <el-button @click="copyText(currentStream.push_url)">复制</el-button>
            </template>
          </el-input>
          <el-input
            v-model="currentStream.stream_key"
            readonly
            placeholder="流密钥"
          >
            <template #prepend>流密钥</template>
            <template #append>
              <el-button @click="copyText(currentStream.stream_key)">复制</el-button>
            </template>
          </el-input>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { endLiveStream } from '../apis/live'

export default {
  name: 'LiveBroadcastPanel',
  props: {
    currentStream: {
      type: Object,
      required: true
    }
  },
  setup(props) {
    const isBroadcasting = ref(true)
    const ending = ref(false)
    const liveDuration = ref(0)
    let durationTimer = null

    const endBroadcast = async () => {
      ending.value = true
      try {
        await endLiveStream(props.currentStream.id)
        ElMessage.success('直播已结束')
        isBroadcasting.value = false
        window.location.reload()
      } catch (error) {
        ElMessage.error('结束直播失败')
      } finally {
        ending.value = false
      }
    }

    const copyText = (text) => {
      navigator.clipboard.writeText(text).then(() => {
        ElMessage.success('已复制到剪贴板')
      })
    }

    const startDurationTimer = () => {
      durationTimer = setInterval(() => {
        liveDuration.value++
      }, 1000)
    }

    onMounted(() => {
      startDurationTimer()
    })

    onUnmounted(() => {
      if (durationTimer) {
        clearInterval(durationTimer)
      }
    })

    return {
      isBroadcasting,
      ending,
      liveDuration,
      endBroadcast,
      copyText
    }
  }
}
</script>

<style scoped>
.broadcast-panel {
  position: fixed;
  top: 80px;
  right: 20px;
  width: 400px;
  z-index: 1000;
}

.control-panel {
  background: white;
  border-radius: 12px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stream-info h3 {
  margin: 0 0 16px 0;
  color: #333;
}

.stats {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  margin-bottom: 20px;
}

.stream-config h4 {
  margin: 0 0 12px 0;
  color: #333;
}

.stream-urls {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}
</style>