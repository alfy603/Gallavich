<template>
  <el-menu
    :default-active="activeIndex"
    background-color="white"
    text-color="black"
    active-text-color="#24b8f2"
    :router="true"
    class="el-menu-demo"
    mode="horizontal"
    :ellipsis="false"
    @select="handleSelect"
  >
    <!-- 左侧：Logo和菜单项 -->
    <el-menu-item index="/" style="font-size:larger; color:#409EFF; margin-right: 20px;">Avalon</el-menu-item>
    <el-menu-item index="/movtype/1">动漫</el-menu-item>
    <el-menu-item index="/movtype/2">电影</el-menu-item>
    <el-menu-item index="/movtype/3">电视剧</el-menu-item>
    <el-menu-item index="/movtype/4">综艺</el-menu-item>
    <el-menu-item index="/ai-search">🤖 AI搜索</el-menu-item>
    <el-menu-item index="/live">直播中心</el-menu-item>
    
    <!-- 中间：弹性空间 -->
    <div class="flex-grow"></div>
    
    <!-- 右侧：搜索框和用户信息 -->
    <div class="right-section">
      <!-- 搜索框 -->
      <div class="menu-input">
        <el-input
          v-model="input"
          placeholder="搜索视频..."
          @keyup.enter="handleSearch"
          clearable
          size="small"
          style="width: 180px;"
        >
          <template #suffix>
            <el-icon @click="handleSearch" style="cursor: pointer;">
              <Search />
            </el-icon>
          </template>
        </el-input>
      </div>
      
      <!-- 用户信息 -->
      <div class="user-section">
        <el-dropdown v-if="isLogining" trigger="click" style="margin: 0 10px;">
          <span class="el-dropdown-link user-name">
            👤 {{ user.name || user.username }}
            <el-icon class="el-icon--right"><arrow-down /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item>
                <router-link :to="'/personSpace/'+ user.id" style="text-decoration: none; color: #606266">
                  个人空间
                </router-link>
              </el-dropdown-item>
              <el-dropdown-item @click="loginOut">登出</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>

        <el-button 
          v-else 
          @click="login" 
          type="primary" 
          link 
          style="margin: 0 10px; color: black;"
        >
          登录/注册
        </el-button>
        
        <!-- 管理员入口：仅登录且角色为 admin 时显示 -->
        <div v-if="isLogining && user && user.role === 'admin'" class="admin-entry">
          <el-button type="primary" @click="goToAdmin" size="small">
            <el-icon><Setting /></el-icon>
            管理后台
          </el-button>
        </div>
      </div>
    </div>
  </el-menu>
</template>

<script>
// 导航栏
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { localRemove } from '../utils'
import { getUserInfo } from '../apis/login'
import { ElMessage } from 'element-plus'
import { Search, ArrowDown, Setting } from '@element-plus/icons-vue'

export default {
    name: "SakuraMenu",
    setup() {
        const store = useStore()
        const router = useRouter()
        const activeIndex = ref('/')
        const input = ref('')
        
        // 🆕 使用 computed 获取响应式状态
        const isLogining = computed(() => store.state.appStore.isLogining)
        const user = computed(() => store.state.appStore.user)
        
        const loginOut = function() {
          // 🆕 使用新的 mutations
          store.commit('SET_LOGIN_STATE', false)
          store.commit('SET_USER', {})
          localRemove('token')
          localRemove('user')
          ElMessage.success('已退出登录')
          router.push('/')
        }

        const login = function() {
          router.push({ name: 'Login' })
        }

        const handleSelect = (key, keyPath) => {
            activeIndex.value = key
            input.value = ''
        }
        
        const handleSearch = () => {
          console.log('搜索关键词:', input.value)
          
          if (input.value && input.value.trim()) {
            activeIndex.value = '/'
            router.push({ 
              path: '/search',
              query: { keyword: input.value.trim() }
            }).then(() => {
              console.log('搜索跳转成功')
            })
          }
        }

        const goToAdmin = () => {
          router.push('/admin/dashboard')
        }

        // 🆕 获取用户信息的方法
        const fetchUserInfo = async () => {
          if (isLogining.value) {
            try {
              const res = await getUserInfo()
              if (res.data.code == 200) {
                // 🆕 使用新的 mutation 更新用户信息
                store.commit('SET_USER', res.data.data)
                console.log('用户信息已更新:', store.state.appStore.user)
              } else {
                ElMessage.warning(res.data.message)
              }
            } catch (error) {
              console.error('获取用户信息失败:', error)
            }
          } 
        }

        return {
            router,
            activeIndex,
            input,
            store,
            isLogining,
            user,  // 🆕 返回 computed user
            loginOut,
            login,
            handleSelect,
            handleSearch,
            goToAdmin,
            fetchUserInfo,
            Search,
            ArrowDown,
            Setting
        }
    },

    mounted() {
      this.router.isReady().then(
        () => {
          var currentPath = this.$route.fullPath
          if (currentPath.indexOf('search?keyword=') > -1) {
            this.input = this.$route.query.keyword ? this.$route.query.keyword : ''
          } else if (currentPath.indexOf('/movtype/') > -1) {
            this.activeIndex = currentPath
          }
        }
      ).catch(
        () => {
          this.input = ''
          this.activeIndex = '/'
        }
      )
      
      // 🆕 组件挂载时获取用户信息
      this.fetchUserInfo()
    }
}
</script>

<style scoped>
.flex-grow {
  flex-grow: 1;
}

.right-section {
  display: flex;
  align-items: center;
  margin-left: auto;
}

.menu-input {
  margin-right: 15px;
}

.user-name {
  color: #606266;
  cursor: pointer;
  padding: 0 8px;
}

.user-name:hover {
  color: #24b8f2;
}

/* 取消过渡效果 */
.el-menu-item {
  border-bottom: 0 !important;
}

.el-menu-item.is-active {
  background-color: white !important;
  border-bottom: 0 !important;
}

.el-menu-item:focus {
  background-color: white !important;
}

.el-menu-item:hover {
  background-color: white !important;
  color: #24b8f2 !important;
}

.el-menu {
  border: none !important;
  height: 60px;
  display: flex;
  align-items: center;
}

/* 管理员入口样式 */
.admin-entry {
  margin-left: 10px;
  display: flex;
  align-items: center;
}

/* 确保搜索框和用户信息在移动端也能正常显示 */
@media (max-width: 768px) {
  .menu-input {
    display: none;
  }
  
  .right-section {
    margin-left: 0;
  }
}
</style>