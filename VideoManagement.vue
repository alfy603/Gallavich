<template>
  <div class="video-management">
    <div class="page-header">
      <h2>视频管理</h2>
      <p>管理平台所有视频内容</p>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加视频
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="视频名称">
          <el-input 
            v-model="searchForm.vod_name" 
            placeholder="请输入视频名称" 
            clearable 
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="searchForm.type_name" placeholder="请选择分类" clearable>
            <el-option label="全部" value="" />
            <el-option label="动漫" value="动漫" />
            <el-option label="电影" value="电影" />
            <el-option label="电视剧" value="电视剧" />
            <el-option label="综艺" value="综艺" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch" :loading="loading">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <template #header>
        <span>视频列表</span>
        <el-button type="primary" text @click="refreshData">刷新</el-button>
      </template>

      <el-table
        :data="videoList"
        :key="tableKey"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="vod_name" label="视频标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-text">{{ row.vod_name }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="type_name" label="分类" width="120" />
        <el-table-column prop="vod_remarks" label="备注" width="120" />
        <el-table-column prop="comment_count" label="评论数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info" size="small">
              {{ row.comment_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="vod_time" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.vod_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="viewVideoDetails(row)"
            >
              详情
            </el-button>
            <el-button 
              size="small" 
              type="danger" 
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.page_size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 添加视频对话框 -->
    <el-dialog 
      v-model="createDialogVisible" 
      title="添加视频" 
      width="600px"
      :before-close="handleCreateDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="视频标题" prop="vod_name">
          <el-input 
            v-model="createForm.vod_name" 
            placeholder="请输入视频标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="视频分类" prop="type_name">
          <el-select 
            v-model="createForm.type_name" 
            placeholder="请选择分类"
            style="width: 100%"
          >
            <el-option 
              v-for="type in videoTypes" 
              :key="type" 
              :label="type" 
              :value="type" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="封面图片">
          <el-input 
            v-model="createForm.vod_pic" 
            placeholder="请输入封面图片URL"
          />
        </el-form-item>
        
        <el-form-item label="视频备注">
          <el-input 
            v-model="createForm.vod_remarks" 
            placeholder="请输入视频备注"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="播放地址">
          <el-input 
            v-model="createForm.vod_play_url" 
            type="textarea"
            :rows="3"
            placeholder="请输入视频播放地址"
          />
        </el-form-item>
        
        <el-form-item label="视频描述">
          <el-input 
            v-model="createForm.vod_content" 
            type="textarea"
            :rows="4"
            placeholder="请输入视频描述"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="createLoading"
          @click="handleCreateVideo"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 视频详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="视频详情"
      width="600px"
    >
      <div v-if="currentVideo" class="video-detail">
        <el-descriptions :column="1" border>
          <el-descriptions-item label="视频ID">
            {{ currentVideo.id }}
          </el-descriptions-item>
          <el-descriptions-item label="视频标题">
            {{ currentVideo.vod_name }}
          </el-descriptions-item>
          <el-descriptions-item label="视频分类">
            {{ currentVideo.type_name }}
          </el-descriptions-item>
          <el-descriptions-item label="视频备注">
            {{ currentVideo.vod_remarks || '无' }}
          </el-descriptions-item>
          <el-descriptions-item label="评论数量">
            {{ currentVideo.comment_count }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatTime(currentVideo.vod_time) }}
          </el-descriptions-item>
        </el-descriptions>
        
        <div class="video-poster" v-if="currentVideo.vod_pic">
          <h4>视频封面:</h4>
          <img :src="currentVideo.vod_pic" :alt="currentVideo.vod_name" class="poster-image" />
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getVideos, 
  deleteVideo, 
  createVideo, 
  getVideoTypes 
} from '../../apis/admin'

export default {
  name: 'VideoManagement',
  components: {
    Plus
  },
  setup() {
    const videoList = ref([])
    const loading = ref(false)
    const tableKey = ref(0)
    const showDetailDialog = ref(false)
    const currentVideo = ref(null)

    const searchForm = reactive({
      vod_name: '',
      type_name: ''
    })

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    // 添加视频相关状态
    const createDialogVisible = ref(false)
    const createLoading = ref(false)
    const createFormRef = ref()
    const videoTypes = ref([])

    const createForm = reactive({
      vod_name: '',
      type_name: '',
      vod_pic: '',
      vod_remarks: '',
      vod_play_url: '',
      vod_content: '',
      type_id: 0
    })

    const createRules = {
      vod_name: [
        { required: true, message: '请输入视频标题', trigger: 'blur' }
      ],
      type_name: [
        { required: true, message: '请选择视频分类', trigger: 'change' }
      ]
    }

    // 获取视频列表
    const fetchVideoList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.page_size,
          ...searchForm
        }

        // 清理空参数
        Object.keys(params).forEach(key => {
          if (params[key] === '' || params[key] === null) {
            delete params[key]
          }
        })

        console.log('� 发送视频列表请求参数:', params)
        const res = await getVideos(params)
        console.log('� 视频列表响应:', res)
        
        if (res.code === 200) {
          // 使用数组解构确保响应式更新
          videoList.value = [...(res.data.videos || [])]
          pagination.total = res.data.pagination.total
          tableKey.value += 1 // 强制表格重新渲染
          console.log(`✅ 获取到 ${videoList.value.length} 条视频数据`)
        } else {
          ElMessage.error(res.message || '获取视频列表失败')
        }
      } catch (error) {
        console.error('获取视频列表失败:', error)
        ElMessage.error('网络请求失败')
      } finally {
        loading.value = false
      }
    }

    // 查看视频详情
    const viewVideoDetails = (video) => {
      currentVideo.value = video
      showDetailDialog.value = true
      console.log('📺 查看视频详情:', video)
    }

    // 删除视频
    const handleDelete = async (video) => {
      try {
        console.log('🗑️ 尝试删除视频:', video)
        
        await ElMessageBox.confirm(
          `确定要删除视频 "${video.vod_name}" 吗？此操作将同时删除相关评论，且不可恢复。`,
          '删除确认',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'error',
            confirmButtonClass: 'el-button--danger'
          }
        )

        console.log(`🗑️ 确认删除视频 ID: ${video.id}`)
        const res = await deleteVideo(video.id)
        console.log('�️ 删除视频响应:', res)
        
        if (res.code === 200) {
          ElMessage.success('视频删除成功')
          // 重新加载数据
          fetchVideoList()
        } else {
          ElMessage.error(res.message || '删除视频失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除视频失败:', error)
          ElMessage.error('删除失败，请稍后重试')
        } else {
          console.log('用户取消删除操作')
        }
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      fetchVideoList()
    }

    // 重置搜索
    const resetSearch = () => {
      searchForm.vod_name = ''
      searchForm.type_name = ''
      pagination.page = 1
      fetchVideoList()
    }

    // 刷新数据
    const refreshData = () => {
      fetchVideoList()
    }

    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.page_size = size
      pagination.page = 1
      fetchVideoList()
    }

    // 页码改变
    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchVideoList()
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return '-'
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    // 显示创建对话框
    const showCreateDialog = async () => {
      createDialogVisible.value = true
      await loadVideoTypes()
    }

    // 加载视频分类
    const loadVideoTypes = async () => {
      try {
        const response = await getVideoTypes()
        if (response.code === 200) {
          videoTypes.value = response.data.types
        } else {
          ElMessage.error('获取分类列表失败')
        }
      } catch (error) {
        console.error('获取分类列表失败:', error)
      }
    }

    // 处理创建对话框关闭
    const handleCreateDialogClose = (done) => {
      ElMessageBox.confirm('确定要关闭吗？输入的数据将不会被保存。')
        .then(() => {
          resetCreateForm()
          done()
        })
        .catch(() => {})
    }

    // 重置创建表单
    const resetCreateForm = () => {
      createFormRef.value?.resetFields()
      createForm.vod_name = ''
      createForm.type_name = ''
      createForm.vod_pic = ''
      createForm.vod_remarks = ''
      createForm.vod_play_url = ''
      createForm.vod_content = ''
      createForm.type_id = 0
    }

    // 创建视频
    const handleCreateVideo = async () => {
      if (!createFormRef.value) return

      try {
        await createFormRef.value.validate()
        createLoading.value = true

        const videoData = { ...createForm }

        const response = await createVideo(videoData)
        if (response.code === 200) {
          ElMessage.success('视频创建成功')
          createDialogVisible.value = false
          resetCreateForm()
          fetchVideoList() // 刷新列表
        } else {
          ElMessage.error(response.message || '视频创建失败')
        }
      } catch (error) {
        if (error.response?.data?.detail) {
          ElMessage.error(error.response.data.detail)
        } else if (error.message && error.message !== 'cancel') {
          ElMessage.error('视频创建失败')
        }
      } finally {
        createLoading.value = false
      }
    }

    onMounted(() => {
      fetchVideoList()
    })

    return {
      videoList,
      loading,
      tableKey,
      showDetailDialog,
      currentVideo,
      searchForm,
      pagination,
      fetchVideoList,
      viewVideoDetails,
      handleDelete,
      handleSearch,
      resetSearch,
      refreshData,
      handleSizeChange,
      handleCurrentChange,
      formatTime,
      // 添加视频相关
      createDialogVisible,
      createLoading,
      createFormRef,
      createForm,
      createRules,
      videoTypes,
      showCreateDialog,
      handleCreateDialogClose,
      handleCreateVideo
    }
  }
}
</script>

<style scoped>
.operation-bar {
  margin-bottom: 20px;
}

.video-management {
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}

.page-header p {
  margin: 0;
  color: #606266;
  font-size: 14px;
}

.search-card {
  margin-bottom: 20px;
}

.title-cell {
  display: flex;
  align-items: center;
}

.title-text {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.video-detail {
  line-height: 1.6;
}

.video-poster {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.video-poster h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.poster-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>