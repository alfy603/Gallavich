<template>
  <div class="mov-type-page">
    <div class="page-header">
      <h2>{{ typeName }} - 分类浏览</h2>
    </div>
    
    <div class="video-grid">
      <div 
        v-for="video in videoList" 
        :key="video.vod_id" 
        class="video-card"
        @click="goToDetail(video.vod_id)"
      >
        <div class="video-poster">
          <img :src="video.vod_pic" :alt="video.vod_name" @error="handleImageError" />
          <div class="video-remarks" v-if="video.vod_remarks">
            {{ video.vod_remarks }}
          </div>
        </div>
        <div class="video-info">
          <h3 class="video-title" :title="video.vod_name">{{ video.vod_name }}</h3>
          <p class="video-year" v-if="video.vod_year">{{ video.vod_year }}</p>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="hasMore">
      <el-button @click="loadMore" :loading="loading">加载更多</el-button>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && videoList.length === 0">
      <p>暂无内容</p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import apiGetMovList from '../apis/getMovInfo'  // 导入正确的API

export default {
  name: 'MovTypePage',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const videoList = ref([])
    const loading = ref(false)
    const hasMore = ref(true)
    const page = ref(1)

    // 类型映射
    const typeMap = {
      '1': { name: '动漫' },
      '2': { name: '电影' },
      '3': { name: '电视剧' },
      '4': { name: '综艺' }
    }

    const typeName = computed(() => {
      return typeMap[route.params.typeId]?.name || '未知分类'
    })

    const fetchVideosByType = async () => {
      if (loading.value) return
      
      loading.value = true
      try {
        const param = {
          page: page.value,
          movtype: parseInt(route.params.typeId)  // 使用 movtype 参数
        }
        
        console.log('MovTypePage 请求参数:', param)
        
        const res = await apiGetMovList(param)  // 使用正确的API
        
        if (res.code === 200) {
          if (page.value === 1) {
            videoList.value = res.data
          } else {
            videoList.value.push(...res.data)
          }
          hasMore.value = res.data && res.data.length > 0
          console.log(`MovTypePage 获取到 ${res.data.length} 条数据`)
        } else {
          ElMessage.error('获取数据失败: ' + res.msg)
        }
      } catch (error) {
        console.error('MovTypePage 获取分类视频失败:', error)
        ElMessage.error('网络请求失败')
      } finally {
        loading.value = false
      }
    }

    const loadMore = () => {
      page.value++
      fetchVideosByType()
    }

    const goToDetail = (vodId) => {
      console.log('=== 🎯 跳转详情页调试 ===')
      console.log('点击的视频ID:', vodId)
      console.log('视频对象:', videoList.value.find(v => v.vod_id === vodId))
      console.log('跳转路径:', `/movdetail/${vodId}`)
  
  router.push(`/movdetail/${vodId}`)
    }

    const handleImageError = (event) => {
      event.target.src = '/imgs/live-default.svg'
    }

    onMounted(() => {
      console.log('MovTypePage 创建，typeId:', route.params.typeId)
      fetchVideosByType()
    })

    return {
      videoList,
      loading,
      hasMore,
      typeName,
      loadMore,
      goToDetail,
      handleImageError
    }
  }
}
</script>
<style scoped>
.mov-type-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.page-header h2 {
  margin: 0;
  color: #333;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.video-card {
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.video-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0,0,0,0.12);
}

.video-poster {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 75%;
  overflow: hidden;
}

.video-poster img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-remarks {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.75);
  color: #fff;
  padding: 3px 8px;
  font-size: 12px;
  border-radius: 4px;
}

.video-info {
  padding: 10px 12px 14px;
}

.video-title {
  margin: 0 0 4px 0;
  font-size: 15px;
  line-height: 1.4;
  height: 2.8em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  color: #333;
}

.video-year {
  margin: 0;
  color: #999;
  font-size: 12px;
}

.load-more {
  text-align: center;
  margin: 20px 0;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>