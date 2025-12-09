<template>
  <div class="admin-layout">
    <el-container>
      <el-aside width="200px" class="admin-sidebar">
        <div class="sidebar-header">
          <h3>管理后台 徐帆</h3>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          class="sidebar-menu"
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item index="/admin/dashboard">
            <el-icon><Odometer /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <span>用户管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/videos">
            <el-icon><VideoCamera /></el-icon>
            <span>视频管理</span>
          </el-menu-item>
          <el-menu-item index="/admin/comments">
            <el-icon><ChatDotRound /></el-icon>
            <span>评论管理</span>
          </el-menu-item>
          <!-- 在 sidebar-menu 中添加 -->
          <el-menu-item index="/admin/live/streams">
            <el-icon><VideoPlay /></el-icon>
          <span>直播流管理</span>
</el-menu-item>
<el-menu-item index="/admin/live/comments">
  <el-icon><ChatLineRound /></el-icon>
  <span>直播评论管理</span>
</el-menu-item>
        </el-menu>
      </el-aside>
      
      <el-container>
        <el-header class="admin-header">
          <div class="header-left">
            <el-breadcrumb separator="/">
              <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
              <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">管理后台</el-breadcrumb-item>
              <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
            </el-breadcrumb>
          </div>
          <div class="header-right">
            <span>欢迎，{{ userInfo.name }}</span>
            <el-button type="primary" link @click="logout">退出</el-button>
          </div>
        </el-header>
        
        <el-main class="admin-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Odometer,
  User,
  VideoCamera,
  ChatDotRound
} from '@element-plus/icons-vue'

export default {
  name: 'AdminLayout',
  components: {
    Odometer,
    User,
    VideoCamera,
    ChatDotRound
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const store = useStore()

    const currentRouteName = computed(() => {
      const routeMap = {
        '/admin/dashboard': '数据概览',
        '/admin/users': '用户管理',
        '/admin/videos': '视频管理',
        '/admin/comments': '评论管理'
      }
      return routeMap[route.path] || '管理后台'
    })

    const userInfo = computed(() => store.state.appStore.user || {})

    const logout = () => {
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        store.commit('appStore/setLoginState', false)
        store.commit('appStore/setUser', null)
        ElMessage.success('退出成功')
        router.push('/')
      })
    }

    return {
      currentRouteName,
      userInfo,
      logout
    }
  }
}
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  background: #f0f2f5;
}

.admin-sidebar {
  background-color: #304156;
  height: 100vh;
}

.sidebar-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #1f2d3d;
}

.sidebar-header h3 {
  color: #fff;
  margin: 0;
}

.sidebar-menu {
  border: none;
}

.admin-header {
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.admin-main {
  flex: 1;
  padding: 20px;
  overflow-y: auto; /* 🆕 确保可以滚动 */
  background: #f0f2f5;
  max-height: calc(100vh - 60px); /* 🆕 限制最大高度 */
}
/* 🆕 确保表格容器有滚动 */
.el-card__body {
  overflow-x: auto;
}


.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>