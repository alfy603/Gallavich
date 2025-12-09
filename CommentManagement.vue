<template>
  <div class="comment-management">
    <h2>评论管理</h2>

    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加评论
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="评论内容">
          <el-input v-model="searchForm.content" placeholder="请输入评论内容" clearable />
        </el-form-item>
        <el-form-item label="用户名称">
          <el-input v-model="searchForm.username" placeholder="请输入用户名称" clearable />
        </el-form-item>
        <el-form-item label="视频名称">
          <el-input v-model="searchForm.vod_name" placeholder="请输入视频名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 评论表格 -->
    <el-card>
      <el-table :data="commentList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="body" label="评论内容" min-width="200" show-overflow-tooltip />
        <el-table-column prop="user_name" label="用户" width="120" />
        <el-table-column prop="vod_name" label="视频" min-width="150" show-overflow-tooltip />
        <el-table-column prop="timestamp" label="评论时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.timestamp) }}
          </template>
        </el-table-column>
        <el-table-column prop="is_reply" label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_reply ? 'warning' : 'primary'">
              {{ scope.row.is_reply ? '回复' : '评论' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="scope">
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
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
      v-model="createDialogVisible" 
      title="添加评论" 
      width="600px"
      :before-close="handleCreateDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="用户" prop="user_id">
          <el-select 
            v-model="createForm.user_id" 
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
        
        <el-form-item label="视频" prop="movdetail_id">
          <el-select 
            v-model="createForm.movdetail_id" 
            placeholder="请选择视频"
            style="width: 100%"
            filterable
          >
            <el-option 
              v-for="video in videoList" 
              :key="video.id" 
              :label="video.vod_name" 
              :value="video.id" 
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="评论内容" prop="body">
          <el-input 
            v-model="createForm.body" 
            type="textarea"
            :rows="4"
            placeholder="请输入评论内容"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="回复评论">
          <el-select 
            v-model="createForm.replied_id" 
            placeholder="请选择要回复的评论（可选）"
            style="width: 100%"
            clearable
            filterable
          >
            <el-option 
              v-for="comment in commentList" 
              :key="comment.id" 
              :label="`${comment.user_name}: ${comment.body.substring(0, 30)}...`" 
              :value="comment.id" 
            />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="createLoading"
          @click="handleCreateComment"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getComments, 
  deleteCommentAdmin, 
  createComment,
  getSimpleUsers,
  getSimpleVideos
} from '../../apis/admin'

export default {
  name: 'CommentManagement',
  components: {
    Plus
  },
  setup() {
    const loading = ref(false)
    const commentList = ref([])

    const searchForm = reactive({
      content: '',
      username: '',
      vod_name: ''
    })

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    // 添加评论相关状态
    const createDialogVisible = ref(false)
    const createLoading = ref(false)
    const createFormRef = ref()
    const userList = ref([])
    const videoList = ref([])

    const createForm = reactive({
      body: '',
      user_id: '',
      movdetail_id: '',
      replied_id: null
    })

    const createRules = {
      body: [
        { required: true, message: '请输入评论内容', trigger: 'blur' },
        { min: 1, max: 500, message: '评论内容长度在 1 到 500 个字符', trigger: 'blur' }
      ],
      user_id: [
        { required: true, message: '请选择用户', trigger: 'change' }
      ],
      movdetail_id: [
        { required: true, message: '请选择视频', trigger: 'change' }
      ]
    }

    const fetchCommentList = async () => {
      loading.value = true
      try {
        const params = {
          page: pagination.page,
          page_size: pagination.page_size,
          ...searchForm
        }
        // 移除空值
        Object.keys(params).forEach(key => {
          if (params[key] === '') {
            delete params[key]
          }
        })

        const response = await getComments(params)
        if (response.code === 200) {
          commentList.value = response.data.comments
          pagination.total = response.data.pagination.total
        } else {
          ElMessage.error('获取评论列表失败')
        }
      } catch (error) {
        ElMessage.error('网络错误')
        console.error('获取评论列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      pagination.page = 1
      fetchCommentList()
    }

    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.page = 1
      fetchCommentList()
    }

    const handleSizeChange = (size) => {
      pagination.page_size = size
      pagination.page = 1
      fetchCommentList()
    }

    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchCommentList()
    }

    const handleDelete = (comment) => {
      ElMessageBox.confirm(
        `确定要删除这条评论吗？此操作不可恢复。`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          const response = await deleteCommentAdmin(comment.id)
          if (response.code === 200) {
            ElMessage.success('删除评论成功')
            fetchCommentList()
          } else {
            ElMessage.error('删除评论失败')
          }
        } catch (error) {
          ElMessage.error('网络错误')
          console.error('删除评论失败:', error)
        }
      })
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      try {
        const date = new Date(dateString)
        return date.toLocaleString('zh-CN', {
          year: 'numeric',
          month: '2-digit',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        })
      } catch (error) {
        console.error('时间格式化错误:', error)
        return String(dateString).substring(0, 16)
      }
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
        // 添加更详细的错误信息
        if (error.response?.status === 422) {
          ElMessage.error('参数错误:page_size 值过大')
        }
      }
    }

    // 加载视频列表
    const loadVideoList = async () => {
      try {
        const response = await getSimpleVideos()
        if (response.code === 200) {
          videoList.value = response.data.videos
        } else {
          ElMessage.error('获取视频列表失败')
        }
      } catch (error) {
        console.error('获取视频列表失败:', error)
        if (error.response?.status === 422) {
          ElMessage.error('参数错误:page_size 值过大')
        }
      }
    }

    // 显示创建对话框
    const showCreateDialog = async () => {
      createDialogVisible.value = true
      await Promise.all([loadUserList(), loadVideoList()])
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
      createForm.body = ''
      createForm.user_id = ''
      createForm.movdetail_id = ''
      createForm.replied_id = null
    }

    // 创建评论
    const handleCreateComment = async () => {
      if (!createFormRef.value) return

      try {
        await createFormRef.value.validate()
        createLoading.value = true

        const commentData = { ...createForm }
        // 如果 replied_id 为空字符串，设置为 null
        if (commentData.replied_id === '') {
          commentData.replied_id = null
        }

        const response = await createComment(commentData)
        if (response.code === 200) {
          ElMessage.success('评论创建成功')
          createDialogVisible.value = false
          resetCreateForm()
          fetchCommentList() // 刷新列表
          
          // 触发统计更新事件
          window.dispatchEvent(new CustomEvent('stats-update'))
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
        createLoading.value = false
      }
    }

    // 🔥 新增：监听统计更新事件
    const handleStatsUpdate = () => {
      console.log('🔄 评论管理：收到统计更新事件')
      // 可以选择重新加载评论列表
      fetchCommentList()
    }

    onMounted(() => {
      fetchCommentList()
      // 🔥 监听统计更新事件
      window.addEventListener('stats-update', handleStatsUpdate)
      console.log('🎯 CommentManagement 已监听统计更新事件')
    })

    // 🔥 修复：现在正确导入了 onUnmounted
    onUnmounted(() => {
      window.removeEventListener('stats-update', handleStatsUpdate)
      console.log('🧹 CommentManagement 已移除事件监听')
    })

    return {
      loading,
      commentList,
      searchForm,
      pagination,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleDelete,
      formatDate,
      // 添加评论相关
      createDialogVisible,
      createLoading,
      createFormRef,
      createForm,
      createRules,
      userList,
      videoList,
      showCreateDialog,
      handleCreateDialogClose,
      handleCreateComment
    }
  }
}
</script>

<style scoped>
.operation-bar {
  margin-bottom: 20px;
}

.comment-management {
  padding: 20px;
}

.search-card {
  margin-bottom: 20px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>