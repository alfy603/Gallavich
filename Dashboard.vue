<template>
  <div class="dashboard">
    <h2>数据概览</h2>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-cards">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon user-icon">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.user_count || 0 }}</div>
              <div class="stat-label">总用户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon video-icon">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.video_count || 0 }}</div>
              <div class="stat-label">总视频数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon comment-icon">
              <el-icon><ChatDotRound /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.comment_count || 0 }}</div>
              <div class="stat-label">总评论数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon live-icon">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.live_count || 0 }}</div>
              <div class="stat-label">直播场次</div>
            </div>
          </div>
        </el-card>
      </el-col>

    </el-row>

    <!-- 今日数据 -->
    <el-row :gutter="20" class="today-stats">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>今日数据</span>
          </template>
          <div class="today-content">
            <div class="today-item">
              <span class="today-label">新增用户:</span>
              <span class="today-value">{{ stats.today_users || 0 }}</span>
            </div>
            <div class="today-item">
              <span class="today-label">新增评论:</span>
              <span class="today-value">{{ stats.today_comments || 0 }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ElMessage } from 'element-plus'
import { User, VideoCamera, ChatDotRound, Monitor } from '@element-plus/icons-vue'
import { getStats } from '../../apis/admin'
import { ref, onMounted, onUnmounted } from 'vue'

export default {
  name: 'Dashboard',
  components: {
    User,
    VideoCamera,
    ChatDotRound,
    Monitor
  },
  setup() {
    const stats = ref({})

    const fetchStats = async () => {
      try {
        console
.log('📊 获取统计数据...')
        const response = await getStats()
        if (response.code === 200) {
          stats
.value = response.
data
          console
.log('✅ 统计数据获取成功:', stats.value)
        } else {
          console
.error('❌ 获取统计数据失败:', response.message)
          ElMessage
.error('获取统计数据失败')
        }
      } catch (error) {
        console
.error('💥 获取统计数据异常:', error)
        ElMessage
.error('获取统计数据失败')
      }
    }

    // 🔥 新增：监听统计更新事件
    const handleStatsUpdate = () => {
      console
.log('🔄 收到统计更新事件，重新获取数据...')
      fetchStats()
    }

    onMounted(() => {
      fetchStats()
      // 🔥 监听统计更新事件
      window
.addEventListener('stats-update', handleStatsUpdate)
      console
.log('🎯 Dashboard 已监听统计更新事件')
    })

    // 🔥 新增：组件卸载时移除事件监听
    onUnmounted(() => {
      window
.removeEventListener('stats-update', handleStatsUpdate)
    })

    return {
      stats
,
      fetchStats 
// 暴露方法供外部调用
    }
}
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stats-cards {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 24px;
  color: #fff;
}

.user-icon { background: #67c23a; }
.video-icon { background: #409eff; }
.comment-icon { background: #e6a23c; }
.live-icon { background: #f56c6c; }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}

.today-stats {
  margin-top: 20px;
}

.today-content {
  padding: 10px 0;
}

.today-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.today-item:last-child {
  border-bottom: none;
}

.today-label {
  color: #606266;
}

.today-value {
  font-weight: bold;
  color: #303133;
}
</style>