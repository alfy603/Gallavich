<template>
  <div class="collect-videos">
    <div class="page-header">
      <h2>我的收藏</h2>
      <p v-if="collections.length > 0">共收藏 {{ pagination.total }} 个视频</p>
    </div>

    <!-- 收藏视频列表 -->
    <div class="video-grid" v-if="collections.length > 0">
      <div 
        v-for="video in collections" 
        :key="video.vod_id" 
        class="video-card"
        @click="goToDetail(video.vod_id)"
      >
        <div class="video-poster">
          <img :src="video.vod_pic" :alt="video.vod_name" @error="handleImageError" />
          <div class="video-remarks" v-if="video.vod_remarks">
            {{ video.vod_remarks }}
          </div>
          <div class="collect-actions">
            <el-button 
              size="small" 
              type="danger" 
              @click.stop="removeCollection(video.vod_id)"
            >
              取消收藏
            </el-button>
          </div>
        </div>
        <div class="video-info">
          <h3 class="video-title">{{ video.vod_name }}</h3>
          <p class="video-type">{{ video.type_name }}</p>
        </div>
      </div>
    </div>

    <!-- 加载更多 -->
    <div class="load-more" v-if="pagination.has_more && !loading">
      <el-button @click="loadMore" :loading="loadingMore">加载更多</el-button>
    </div>

    <!-- 空状态 -->
    <div class="empty-state" v-if="!loading && collections.length === 0">
      <el-empty description="暂无收藏视频">
        <el-button type="primary" @click="goToHome">去首页看看</el-button>
      </el-empty>
    </div>

    <!-- 加载状态 -->
    <div class="loading-state" v-if="loading">
      <el-skeleton :rows="6" animated />
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { showCollectVideo, removeCollectVideo } from '../apis/videoCollection'
import { getUserInfo } from '../apis/login'

export default {
  name: 'CollectVideos',
  setup() {
    const router = useRouter()
    const collections = ref([])
    const loading = ref(false)
    const loadingMore = ref(false)
    const currentUser = ref(null)
    
    const pagination = ref({
      current_page: 1,
      per_page: 12,
      total: 0,
      has_more: false
    })

    // 获取当前用户信息
    const fetchUserInfo = async () => {
      try {
        const res = await getUserInfo()
        if (res.data.code === 200) {
          currentUser.value = res.data.data
          console.log('当前用户信息:', currentUser.value)
        }
      } catch (error) {
        console.error('获取用户信息失败:', error)
      }
    }

    // 获取收藏列表
    const fetchCollections = async (page = 1, isLoadMore = false) => {
      if (loading.value) return
      
      if (!isLoadMore) {
        loading.value = true
        collections.value = []
      } else {
        loadingMore.value = true
      }

      try {
        // 确保有用户ID
        if (!currentUser.value) {
          await fetchUserInfo()
        }

        const params = {
          page: page,
          per_page: pagination.value.per_page
        }

        // 如果有用户ID，添加到参数中
        if (currentUser.value && currentUser.value.id) {
          params.user_id = currentUser.value.id
        }

        console.log('请求收藏列表参数:', params)
        
        const res = await showCollectVideo(params)
        console.log('收藏列表响应:', res)

        if (res.code === 200) {
          const data = res.data
          if (isLoadMore) {
            collections.value.push(...data.collections)
          } else {
            collections.value = data.collections || []
          }
          
          pagination.value = {
            ...data.pagination,
            current_page: page
          }
          
          console.log(`获取到 ${data.collections.length} 个收藏视频`)
        } else {
          ElMessage.error(res.message || '获取收藏列表失败')
        }
      } catch (error) {
        console.error('获取收藏列表失败:', error)
        ElMessage.error('网络请求失败')
      } finally {
        loading.value = false
        loadingMore.value = false
      }
    }

    // 加载更多
    const loadMore = () => {
      if (pagination.value.has_more) {
        fetchCollections(pagination.value.current_page + 1, true)
      }
    }

    // 取消收藏
    const removeCollection = async (vodId) => {
      try {
        await ElMessageBox.confirm('确定要取消收藏吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })

        if (!currentUser.value) {
          await fetchUserInfo()
        }

        const params = {
          vod_id: vodId
        }

        if (currentUser.value && currentUser.value.id) {
          params.user_id = currentUser.value.id
        }

        const res = await removeCollectVideo(params)
        
        if (res.code === 200) {
          ElMessage.success('取消收藏成功')
          // 重新加载收藏列表
          fetchCollections(1)
        } else {
          ElMessage.error(res.message || '取消收藏失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('取消收藏失败:', error)
          ElMessage.error('取消收藏失败')
        }
      }
    }

    // 跳转到视频详情
    const goToDetail = (vodId) => {
      router.push(`/movdetail/${vodId}`)
    }

    // 跳转到首页
    const goToHome = () => {
      router.push('/')
    }

    // 图片加载失败处理
    const handleImageError = (event) => {
      event.target.src = '/imgs/live-default.svg'
    }

    onMounted(() => {
      fetchUserInfo().then(() => {
        fetchCollections(1)
      })
    })

    return {
      collections,
      loading,
      loadingMore,
      pagination,
      fetchCollections,
      loadMore,
      removeCollection,
      goToDetail,
      goToHome,
      handleImageError
    }
  }
}
</script>

<style scoped>
.collect-videos {
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
  margin: 0 0 8px 0;
  color: #333;
}

.page-header p {
  margin: 0;
  color: #666;
  font-size: 14px;
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
  padding-bottom: 140%;
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

.collect-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.video-card:hover .collect-actions {
  opacity: 1;
}

.video-info {
  padding: 12px;
}

.video-title {
  margin: 0 0 6px 0;
  font-size: 14px;
  line-height: 1.4;
  height: 2.8em;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  color: #333;
}

.video-type {
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
  padding: 40px 20px;
}

.loading-state {
  padding: 20px 0;
}

@media (max-width: 768px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>