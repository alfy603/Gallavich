<template>
  <div class="user-management">
    <h2>用户管理</h2>
    
    <!-- 操作栏 -->
    <div class="operation-bar">
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加用户
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="search-card">
      <el-form :model="searchForm" inline>
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="searchForm.role" placeholder="请选择角色" clearable>
            <el-option label="全部" value="" />
            <el-option label="管理员" value="admin" />
            <el-option label="普通用户" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.is_active" placeholder="请选择状态" clearable>
            <el-option label="全部" value="" />
            <el-option label="启用" :value="true" />
            <el-option label="禁用" :value="false" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="resetSearch">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 用户表格 -->
    <el-card>
      <el-table :data="userList" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="用户名" />
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'primary'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'danger'">
              {{ scope.row.is_active ? '启用' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="注册时间" width="180">
          <template #default="scope">
            {{ formatDate(scope.row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="video_count" label="视频数" width="100" />
        <el-table-column prop="comment_count" label="评论数" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="scope">
            <el-button size="small" @click="handleEditRole(scope.row)">修改角色</el-button>
            <el-button 
              size="small" 
              :type="scope.row.is_active ? 'danger' : 'success'"
              @click="handleToggleStatus(scope.row)"
            >
              {{ scope.row.is_active ? '禁用' : '启用' }}
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

    <!-- 添加用户对话框 -->
    <el-dialog 
      v-model="createDialogVisible" 
      title="添加用户" 
      width="500px"
      :before-close="handleCreateDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="name">
          <el-input 
            v-model="createForm.name" 
            placeholder="请输入用户名"
            maxlength="30"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="createForm.password" 
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="createForm.confirmPassword" 
            type="password"
            placeholder="请再次输入密码"
            show-password
          />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="createForm.role" placeholder="请选择角色">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="状态" prop="is_active">
          <el-switch
            v-model="createForm.is_active"
            active-text="启用"
            inactive-text="禁用"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button 
          type="primary" 
          :loading="createLoading"
          @click="handleCreateUser"
        >
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 修改角色对话框 -->
    <el-dialog v-model="roleDialogVisible" title="修改用户角色" width="400px">
      <el-form :model="roleForm" label-width="80px">
        <el-form-item label="用户角色">
          <el-select v-model="roleForm.role">
            <el-option label="普通用户" value="user" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRole">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import { 
  getUsers, 
  updateUserRole, 
  updateUserStatus, 
  createUser 
} from '../../apis/admin'

export default {
  name: 'UserManagement',
  components: {
    Plus
  },
  setup() {
    const loading = ref(false)
    const userList = ref([])
    const roleDialogVisible = ref(false)
    const currentUser = ref(null)

    const searchForm = reactive({
      username: '',
      role: '',
      is_active: ''
    })

    const pagination = reactive({
      page: 1,
      page_size: 20,
      total: 0
    })

    const roleForm = reactive({
      role: ''
    })

    // 添加用户相关状态
    const createDialogVisible = ref(false)
    const createLoading = ref(false)
    const createFormRef = ref()

    const createForm = reactive({
      name: '',
      password: '',
      confirmPassword: '',
      role: 'user',
      is_active: true
    })

    const createRules = {
      name: [
        { required: true, message: '请输入用户名', trigger: 'blur' },
        { min: 2, max: 30, message: '用户名长度在 2 到 30 个字符', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少 6 个字符', trigger: 'blur' }
        // 🔥 移除最大长度限制，让后端自动处理
      ],
      confirmPassword: [
        { required: true, message: '请确认密码', trigger: 'blur' },
        {
          validator: (rule, value, callback) => {
            if (value !== createForm.password) {
              callback(new Error('两次输入密码不一致'))
            } else {
              callback()
            }
          },
          trigger: 'blur'
        }
      ],
      role: [
        { required: true, message: '请选择角色', trigger: 'change' }
      ]
    }

    const fetchUserList = async () => {
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

        const response = await getUsers(params)
        if (response.code === 200) {
          userList.value = response.data.users
          pagination.total = response.data.pagination.total
        } else {
          ElMessage.error('获取用户列表失败')
        }
      } catch (error) {
        ElMessage.error('网络错误')
        console.error('获取用户列表失败:', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      pagination.page = 1
      fetchUserList()
    }

    const resetSearch = () => {
      Object.keys(searchForm).forEach(key => {
        searchForm[key] = ''
      })
      pagination.page = 1
      fetchUserList()
    }

    const handleSizeChange = (size) => {
      pagination.page_size = size
      pagination.page = 1
      fetchUserList()
    }

    const handleCurrentChange = (page) => {
      pagination.page = page
      fetchUserList()
    }

    const handleEditRole = (user) => {
      currentUser.value = user
      roleForm.role = user.role
      roleDialogVisible.value = true
    }

    const confirmRole = async () => {
      try {
        const response = await updateUserRole(currentUser.value.id, roleForm)
        if (response.code === 200) {
          ElMessage.success('修改角色成功')
          roleDialogVisible.value = false
          fetchUserList()
        } else {
          ElMessage.error('修改角色失败')
        }
      } catch (error) {
        ElMessage.error('网络错误')
        console.error('修改角色失败:', error)
      }
    }

    const handleToggleStatus = (user) => {
      ElMessageBox.confirm(
        `确定要${user.is_active ? '禁用' : '启用'}用户 ${user.name} 吗？`,
        '提示',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      ).then(async () => {
        try {
          const response = await updateUserStatus(user.id, { is_active: !user.is_active })
          if (response.code === 200) {
            ElMessage.success(`${user.is_active ? '禁用' : '启用'}成功`)
            fetchUserList()
          } else {
            ElMessage.error('操作失败')
          }
        } catch (error) {
          ElMessage.error('网络错误')
          console.error('操作失败:', error)
        }
      })
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString()
    }

    // 显示创建对话框
    const showCreateDialog = () => {
      createDialogVisible.value = true
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
      createForm.name = ''
      createForm.password = ''
      createForm.confirmPassword = ''
      createForm.role = 'user'
      createForm.is_active = true
    }

    // 创建用户
    const handleCreateUser = async () => {
      if (!createFormRef.value) return

      try {
        await createFormRef.value.validate()
        createLoading.value = true

        const userData = {
          name: createForm.name,
          password: createForm.password,
          role: createForm.role,
          is_active: createForm.is_active
        }

        const response = await createUser(userData)
        if (response.code === 200) {
          ElMessage.success('用户创建成功')
          createDialogVisible.value = false
          resetCreateForm()
          fetchUserList() // 刷新列表
          
          // 触发统计更新事件
          window.dispatchEvent(new CustomEvent('stats-update'))
        } else {
          ElMessage.error(response.message || '用户创建失败')
        }
      } catch (error) {
        if (error.response?.data?.detail) {
          ElMessage.error(error.response.data.detail)
        } else if (error.message && error.message !== 'cancel') {
          ElMessage.error('用户创建失败')
        }
      } finally {
        createLoading.value = false
      }
    }

    onMounted(() => {
      fetchUserList()
    })

    return {
      loading,
      userList,
      searchForm,
      pagination,
      roleDialogVisible,
      roleForm,
      handleSearch,
      resetSearch,
      handleSizeChange,
      handleCurrentChange,
      handleEditRole,
      confirmRole,
      handleToggleStatus,
      formatDate,
      // 添加用户相关
      createDialogVisible,
      createLoading,
      createFormRef,
      createForm,
      createRules,
      showCreateDialog,
      handleCreateDialogClose,
      handleCreateUser
    }
  }
}
</script>

<style scoped>
.operation-bar {
  margin-bottom: 20px;
}

.user-management {
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