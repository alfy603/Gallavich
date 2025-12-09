<template>
  <div class="live-comment-management">
    <div class="page-header">
      <h2>直播评论管理</h2>
      <p>管理所有直播间的评论内容</p>
    </div>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateCommentDialog">
        <el-icon><Plus /></el-icon>
        添加评论
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" label-width="80px">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="评论内容">
              <el-input
                v-model="searchForm.content"
                placeholder="输入评论内容"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="用户名称">
              <el-input
                v-model="searchForm.username"
                placeholder="输入用户名称"
                clearable
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="直播标题">
              <el-input
                v-model="searchForm.stream_title"
                placeholder="输入直播标题"
                clearable
              />
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
        <span>直播评论列表</span>
        <el-button type="primary" text @click="refreshData">刷新</el-button>
      </template>

      <el-table
        :data="comments"
        v-loading="loading"
        stripe
        style="width: 100%"
      >
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="content" label="评论内容" min-width="200">
          <template #default="{ row }">
            <div class="content-cell">
              {{ row.content }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="user_id" label="用户ID" width="100" />
        <el-table-column prop="stream_title" label="所属直播" min-width="150">
          <template #default="{ row }">
            <el-tooltip :content="row.stream_title" placement="top">
              <span class="stream-title">{{ row.stream_title }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
        <el-table-column prop="stream_id" label="直播ID" width="100" />
        <el-table-column prop="timestamp" label="评论时间" width="180">
          <template #default="{ row }">
            {{ formatTime(row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
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

    <!-- 添加评论对话框 -->
    <el-dialog 
      v-model="createCommentDialogVisible" 
      title="添加直播评论" 
      width="500px"
      :before-close="handleCreateCommentDialogClose"
    >
      <el-form
        ref="createCommentFormRef"
        :model="createCommentForm"
        :rules="createCommentRules"
        label-width="100px"
      >
        <el-form-item label="用户" prop="user_id">
          <el-select 
            v-model="createCommentForm.user_id" 
            placeholder="请选择用户"
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
        
        <el-form-item label="直播" prop="stream_id">
          <el-select 
            v-model="createCommentForm.stream_id" 
            placeholder="请选择直播"
            style="width: 100%"
            filterable
          >
            <el-option 
              v-for="stream in streamList" 
              :key="stream.id" 
              :label="stream.title" 
              :value="stream.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="评论内容" prop="content">
          <el-input 
            v-model="createCommentForm.content" 
            type="textarea"
            :rows="3"
            placeholder="请输入评论内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createCommentDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="createCommentLoading"
          @click="handleCreateComment"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getLiveComments, 
  deleteLiveCommentAdmin,
  getSimpleUsers,
  getLiveStreams,
  createLiveCommentAdmin
} from '../../apis/admin'

export default {
  name: 'LiveCommentManagement',
  components: {
    Plus
  },
  setup() {
    const comments = ref([])
    const loading = ref(false)
    
    // 创建评论相关状态
    const createCommentDialogVisible = ref(false)
    const createCommentLoading = ref(false)
    const createCommentFormRef = ref()
    const userList = ref([])
    const streamList = ref([])

    const searchForm = reactive({
      content: '',
      username: '',
      stream_title: ''
    })

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    // 创建评论表单
    const createCommentForm = reactive({
      user_id: '',
      stream_id: '',
      content: ''
    })

    const createCommentRules = {
      user_id: [
        { required: true, message: '请选择用户', trigger: 'change' }
      ],
      stream_id: [
        { required: true, message: '请选择直播', trigger: 'change' }
      ],
      content: [
        { required: true, message: '请输入评论内容', trigger: 'blur' },
        { min: 1, max: 500, message: '评论内容长度在 1 到 500 个字符', trigger: 'blur' }
      ]
    }

    // 获取评论数据
    const fetchComments = async () => {
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

        const res = await getLiveComments(params)
        
        if (res.code === 200) {
          comments.value = res.data.comments
          pagination.total = res.data.pagination.total
        } else {
          ElMessage.error(res.message || '获取评论列表失败')
        }
      } catch (error) {
        console.error('获取评论列表失败:', error)
        ElMessage.error('网络请求失败')
      } finally {
        loading.value = false
      }
    }

    // 搜索
    const handleSearch = () => {
      pagination.page = 1
      fetchComments()
    }

    // 重置搜索
    const handleReset = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.page = 1
      fetchComments()
    }

    // 刷新数据
    const refreshData = () => {
      fetchComments()
    }

    // 分页大小改变
    const handleSizeChange = (size) => {
      pagination.page_size = size
      pagination.page = 1
      fetchComments()
    }

    // 页码改变
    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchComments()
    }

    // 删除评论
    const handleDelete = async (comment) => {
      try {
        await ElMessageBox.confirm(
          `确定要删除用户 "${comment.user_name}" 的评论吗？`,
          '删除确认',
          {
            confirmButtonText: '删除',
            cancelButtonText: '取消',
            type: 'error',
            confirmButtonClass: 'el-button--danger'
          }
        )

        const res = await deleteLiveCommentAdmin(comment.id)
        
        if (res.code === 200) {
          ElMessage.success('删除评论成功')
          fetchComments() // 刷新数据
        } else {
          ElMessage.error(res.message || '删除评论失败')
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除评论失败:', error)
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
        console.log('🔄 开始加载用户列表...')
        const response = await getSimpleUsers()
        console.log('📊 用户列表响应:', response)
        
        if (response.code === 200) {
          userList.value = response.data.users
          console.log('✅ 用户列表加载成功，数量:', userList.value?.length)
        } else {
          console.error('❌ 获取用户列表失败:', response.message)
          ElMessage.error('获取用户列表失败')
        }
      } catch (error) {
        console.error('❌ 获取用户列表异常:', error)
        ElMessage.error('获取用户列表失败')
      }
    }

    // 加载直播列表
    const loadStreamList = async () => {
      try {
        console.log('🔄 开始加载直播列表...')
        const response = await getLiveStreams({ page_size: 100 })  // 改为100,避免422错误
        console.log('📊 直播列表响应:', response)
        
        if (response.code === 200) {
          streamList.value = response.data.streams
          console.log('✅ 直播列表加载成功，数量:', streamList.value?.length)
        } else {
          console.error('❌ 获取直播列表失败:', response.message)
          ElMessage.error('获取直播列表失败')
        }
      } catch (error) {
        console.error('❌ 获取直播列表异常:', error)
        // 添加更详细的错误信息
        if (error.response?.status === 422) {
          ElMessage.error('参数错误: page_size 值过大')
        } else {
          ElMessage.error('获取直播列表失败')
        }
      }
    }

    // 显示创建评论对话框
    const showCreateCommentDialog = async () => {
      console.log('🎬 显示创建评论对话框')
      createCommentDialogVisible.value = true
      
      try {
        await Promise.all([loadUserList(), loadStreamList()])
        console.log('✅ 用户和直播列表加载完成')
        console.log('用户列表:', userList.value)
        console.log('直播列表:', streamList.value)
      } catch (error) {
        console.error('❌ 加载数据失败:', error)
      }
    }

    // 处理创建评论对话框关闭
    const handleCreateCommentDialogClose = (done) => {
      ElMessageBox.confirm('确定要关闭吗？输入的数据将不会被保存。')
        .then(() => {
          resetCreateCommentForm()
          done()
        })
        .catch(() => {})
    }

    // 重置创建评论表单
    const resetCreateCommentForm = () => {
      createCommentFormRef.value?.resetFields()
      createCommentForm.user_id = ''
      createCommentForm.stream_id = ''
      createCommentForm.content = ''
    }

    // 创建评论
    const handleCreateComment = async () => {
      if (!createCommentFormRef.value) return

      try {
        await createCommentFormRef.value.validate()
        createCommentLoading.value = true

        const commentData = { ...createCommentForm }

        const response = await createLiveCommentAdmin(commentData)
        if (response.code === 200) {
          ElMessage.success('评论创建成功')
          createCommentDialogVisible.value = false
          resetCreateCommentForm()
          fetchComments() // 刷新列表
        } else {
          ElMessage.error(response.message || '评论创建失败')
        }
      } catch (error) {
        if (error.response?.data?.detail) {
          ElMessage.error(error.response.data.detail)
        } else if (error.message && error.message !== 'cancel') {
          ElMessage.error('评论创建失败')
        }
      } finally {
        createCommentLoading.value = false
      }
    }

    onMounted(() => {
      fetchComments()
    })

    return {
      comments,
      loading,
      searchForm,
      pagination,
      // 创建评论相关
      createCommentDialogVisible,
      createCommentLoading,
      createCommentFormRef,
      createCommentForm,
      createCommentRules,
      userList,
      streamList,
      handleSearch,
      handleReset,
      refreshData,
      handleSizeChange,
      handleCurrentChange,
      handleDelete,
      formatTime,
      showCreateCommentDialog,
      handleCreateCommentDialogClose,
      handleCreateComment
    }
  }
}
</script>

<style scoped>
.live-comment-management {
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

.content-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stream-title {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>