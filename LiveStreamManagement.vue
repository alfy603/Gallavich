<template>
  <div class="live-stream-management">
    <div class="page-header">
      <h2>直播流管理</h2>
      <p>管理平台所有直播流，包括直播状态、主播信息、观看数据等</p>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateStreamDialog">
        <el-icon><Plus /></el-icon>
        创建直播
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="直播标题">
              <el-input
                v-model="searchForm.title"
                placeholder="输入直播标题"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="主播名称">
              <el-input
                v-model="searchForm.streamer"
                placeholder="输入主播名称"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="直播状态">
              <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
                <el-option label="直播中" :value="1" />
                <el-option label="已结束" :value="0" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <el-button type="primary" @click="handleSearch">搜索</el-button>
              <el-button @click="handleReset">重置</el-button>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 数据表格 -->
    <el-card>
      <template #header>
        <span>直播流列表</span>
        <el-button type="primary" text @click="refreshData">刷新</el-button>
      </template>

      <el-table
        :data="streams"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="直播标题" min-width="200">
          <template #default="{ row }">
            <div class="title-cell">
              <span class="title-text">{{ row.title }}</span>
              <el-tag 
                :type="row.status === 1 ? 'success' : 'info'" 
                size="small"
                style="margin-left: 8px;"
              >
                {{ row.status_text }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="streamer" label="主播" width="120" />
        <el-table-column prop="viewer_count" label="观看人数" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="info">
              {{ row.viewer_count }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="max_viewers" label="最高观看" width="100" align="center">
          <template #default="{ row }">
            <el-tag type="warning">
              {{ row.max_viewers }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="comment_count" label="评论数" width="100" align="center">
          <template #default="{ row }">
            {{ row.comment_count }}
          </template>
        </el-table-column>
        <el-table-column prop="stream_key" label="流密钥" width="150">
          <template #default="{ row }">
            <el-tooltip :content="row.stream_key" placement="top">
              <span class="stream-key">{{ row.stream_key }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="created_time" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.created_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="start_time" label="开始时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.start_time) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button 
              size="small" 
              type="primary" 
              link
              @click="viewStreamDetails(row)"
            >
              详情
            </el-button>
            <el-button 
              size="small" 
              :type="row.status === 1 ? 'warning' : 'success'" 
              link
              @click="toggleStreamStatus(row)"
            >
              {{ row.status === 1 ? '结束直播' : '开启直播' }}
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

    <!-- 创建直播对话框 -->
    <el-dialog 
      v-model="createStreamDialogVisible" 
      title="创建直播" 
      width="500px"
      :before-close="handleCreateStreamDialogClose"
    >
      <el-form
        ref="createStreamFormRef"
        :model="createStreamForm"
        :rules="createStreamRules"
        label-width="100px"
      >
        <el-form-item label="直播标题" prop="title">
          <el-input 
            v-model="createStreamForm.title" 
            placeholder="请输入直播标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="主播" prop="user_id">
          <el-select 
            v-model="createStreamForm.user_id" 
            placeholder="请选择主播"
            style="width: 100%"
            filterable
          >
            <el-option 
              v-for="user in userList" 
              :key="user.id" 
              :label="user.name" 
              :value="user.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="直播描述" prop="description">
          <el-input 
            v-model="createStreamForm.description" 
            type="textarea"
            :rows="3"
            placeholder="请输入直播描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="封面图片" prop="cover_image">
          <el-input 
            v-model="createStreamForm.cover_image" 
            placeholder="请输入封面图片URL"
          />
        </el-form-item>
        
        <el-form-item label="初始状态" prop="status">
          <el-radio-group v-model="createStreamForm.status">
            <el-radio :label="1">直播中</el-radio>
            <el-radio :label="0">已结束</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createStreamDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="createStreamLoading"
          @click="handleCreateStream"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 直播详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="直播详情"
      width="600px"
    >
      <div v-if="currentStream" class="stream-detail">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="直播ID">
            {{ currentStream.id }}
          </el-descriptions-item>
          <el-descriptions-item label="直播状态">
            <el-tag :type="currentStream.status === 1 ? 'success' : 'info'">
              {{ currentStream.status_text }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="直播标题" :span="2">
            {{ currentStream.title }}
          </el-descriptions-item>
          <el-descriptions-item label="主播">
            {{ currentStream.streamer }}
          </el-descriptions-item>
          <el-descriptions-item label="主播ID">
            {{ currentStream.streamer_id }}
          </el-descriptions-item>
          <el-descriptions-item label="当前观看">
            {{ currentStream.viewer_count }}
          </el-descriptions-item>
          <el-descriptions-item label="最高观看">
            {{ currentStream.max_viewers }}
          </el-descriptions-item>
          <el-descriptions-item label="评论数量">
            {{ currentStream.comment_count }}
          </el-descriptions-item>
          <el-descriptions-item label="流密钥">
            <code>{{ currentStream.stream_key }}</code>
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatTime(currentStream.created_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="开始时间">
            {{ formatTime(currentStream.start_time) }}
          </el-descriptions-item>
          <el-descriptions-item label="结束时间">
            {{ formatTime(currentStream.end_time) || '未结束' }}
          </el-descriptions-item>
          <el-descriptions-item label="直播描述" :span="2">
            {{ currentStream.description || '无描述' }}
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getLiveStreams, 
  deleteLiveStreamAdmin, 
  updateLiveStreamStatus,
  getSimpleUsers,
  createLiveStreamAdmin
} from '../../apis/admin'

export default {
  name: 'LiveStreamManagement',
  components: {
    Plus
  },
  setup() {
    const streams = ref([])
    const loading = ref(false)
    const showDetailDialog = ref(false)
    const currentStream = ref(null)
    
    // 创建直播相关状态
    const createStreamDialogVisible = ref(false)
    const createStreamLoading = ref(false)
    const createStreamFormRef = ref()
    const userList = ref([])

    const searchForm = reactive({
      title: '',
      streamer: '',
      status: null
    })

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    // 创建直播表单
    const createStreamForm = reactive({
      title: '',
      user_id: '',
      description: '',
      cover_image: '/api/imgs/live-default.jpg',
      status: 1
    })

    const createStreamRules = {
      title: [
        { required: true, message: '请输入直播标题', trigger: 'blur' },
        { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
      ],
      user_id: [
        { required: true, message: '请选择主播', trigger: 'change' }
      ]
    }

    // 获取直播流数据
    const fetchStreams = async () => {
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

        const res = await getLiveStreams(params)
        
        if (res.code === 200) {
          streams.value = res.data.streams
          pagination.total = res.data.pagination.total
        } else {
          ElMessage.error(res.message || '获取直播流列表失败')
        }
      } catch (error) {
        console.error('获取直播流列表失败:', error)
        ElMessage.error('网络请求失败')
      } finally {
        loading.value = false
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      fetchStreams()
    }

    // 重置搜索
    const handleReset = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.page = 1
      fetchStreams()
    }

    // 刷新数据
    const refreshData = () => {
      fetchStreams()
    }

    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.page_size = size
      pagination.page = 1
      fetchStreams()
    }

    // 页码改变
    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchStreams()
    }

    // 查看详情
    const viewStreamDetails = (stream) => {
      currentStream.value = stream
      showDetailDialog.value = true
    }

    // 切换直播状态
    const toggleStreamStatus = async (stream) => {
      try {
        const newStatus = stream.status === 1 ? 0 : 1
        const action = newStatus === 1 ? '开启' : '结束'
        
        await ElMessageBox.confirm(
          `确定要${action}直播 "${stream.title}" 吗？`,
          '提示',
          {
            confirmButtonText: '确定',
            cancelButtonText: '取消',
            type: 'warning'
          }
        )

        const res = await updateLiveStreamStatus(stream.id, { status: newStatus })
        
        if (res.code === 200) {
          ElMessage.success(`${action}直播成功`)
          fetchStreams() // 刷新数据
        } else {
          ElMessage.error(res.message || `${action}直播失败`)
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('切换直播状态失败:', error)
          ElMessage.error('操作失败')
        }
      }
    }

    // 删除直播
    const handleDelete = async (stream) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除直播 "${stream.title}" 吗？此操作不可恢复。`,
          '删除确认',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'error',
            confirmButtonClass: 'el-button--danger'
          }
        )

        const res = await deleteLiveStreamAdmin(stream.id)
        
        if (res.code === 200) {
          ElMessage.success('删除直播成功')
          fetchStreams() // 刷新数据
        } else {
          ElMessage.error(res.message || '删除直播失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除直播失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      if (!timeStr) return '-'
      return new Date(timeStr).toLocaleString('zh-CN')
    }

    // 加载用户列表
    const loadUserList = async () => {
      try {
        const response = await getSimpleUsers()
        if (response.code === 200) {
          userList.value = response.data.users
        } else {
          ElMessage.error('获取用户列表失败')
        }
      } catch (error) {
        console.error('获取用户列表失败:', error)
      }
    }

    // 显示创建直播对话框
    const showCreateStreamDialog = async () => {
      createStreamDialogVisible.value = true
      await loadUserList()
    }

    // 处理创建直播对话框关闭
    const handleCreateStreamDialogClose = (done) => {
      ElMessageBox.confirm('确定要关闭吗？输入的数据将不会被保存。')
        .then(() => {
          resetCreateStreamForm()
          done()
        })
        .catch(() => {})
    }

    // 重置创建直播表单
    const resetCreateStreamForm = () => {
      createStreamFormRef.value?.resetFields()
      createStreamForm.title = ''
      createStreamForm.user_id = ''
      createStreamForm.description = ''
      createStreamForm.cover_image = '/api/imgs/live-default.jpg'
      createStreamForm.status = 1
    }

    // 创建直播
    const handleCreateStream = async () => {
      if (!createStreamFormRef.value) return

      try {
        await createStreamFormRef.value.validate()
        createStreamLoading.value = true

        const streamData = { ...createStreamForm }

        const response = await createLiveStreamAdmin(streamData)
        if (response.code === 200) {
          ElMessage.success('直播创建成功')
          createStreamDialogVisible.value = false
          resetCreateStreamForm()
          fetchStreams() // 刷新列表
        } else {
          ElMessage.error(response.message || '直播创建失败')
        }
      } catch (error) {
        if (error.response?.data?.detail) {
          ElMessage.error(error.response.data.detail)
        } else if (error.message && error.message !== 'cancel') {
          ElMessage.error('直播创建失败')
        }
      } finally {
        createStreamLoading.value = false
      }
    }

    onMounted(() => {
      fetchStreams()
    })

    return {
      streams,
      loading,
      showDetailDialog,
      currentStream,
      searchForm,
      pagination,
      // 创建直播相关
      createStreamDialogVisible,
      createStreamLoading,
      createStreamFormRef,
      createStreamForm,
      createStreamRules,
      userList,
      handleSearch,
      handleReset,
      refreshData,
      handleSizeChange,
      handleCurrentChange,
      viewStreamDetails,
      toggleStreamStatus,
      handleDelete,
      formatTime,
      showCreateStreamDialog,
      handleCreateStreamDialogClose,
      handleCreateStream
    }
  }
}
</script>

<style scoped>
.live-stream-management {
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

.operation-bar {
  margin-bottom: 20px;
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

.stream-key {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.stream-detail {
  line-height: 1.6;
}

.stream-detail code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}
</style>