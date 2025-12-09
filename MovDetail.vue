<template>
    <div class="vod-detail" style="margin: 20px 0; width: 90%; overflow: hidden;">
        <el-row class="vod-detail" v-if="Object.keys(mov_detail).length > 0">
            <el-col :xs="24" :sm="6" class="vod-detail">
                <div class="vod-detail">
                    <img :src="mov_detail.vod_pic" :alt="mov_detail.vod_name" @error="handleImageError"/>
                </div>
                
            </el-col>
            <el-col  :sm="18" style="padding: 0 10px">
                <el-row style="margin: 0 0 15px 0">
                    <p style="margin: 0; font-size: 18px;">{{ mov_detail.vod_name }}</p>
                </el-row>

                <el-row v-if="mov_detail.vod_sub">
                    <span class="des-name">
                        又名:&nbsp; &nbsp; 
                        <p class="des-content">{{ mov_detail.vod_sub }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">地区:&nbsp;&nbsp;</span>
                    <p class="des-content"> {{ mov_detail.vod_area || '暂无信息' }}</p>
                </el-row>

                <el-row>
                    <span class="des-name">
                        语言:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_lang || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        类型:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.type_name || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        上映:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_year || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        集数:&nbsp; &nbsp;
                        <p class="des-content">{{ mov_detail.vod_remarks || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        导演:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_director || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        更新时间:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_time || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row>
                    <span class="des-name">
                        收藏:&nbsp;&nbsp;
                        <p class="des-content"> 
                            <el-icon :size="26" style="vertical-align: middle;" v-if="!isCollect" color="#999" @click="addCollect"><StarFilled /></el-icon>
                            <el-icon :size="26" style="vertical-align: middle" v-else color="yellow" @click="removeCollect"><StarFilled /></el-icon>  
                        </p>
                    </span>
                    
                </el-row>

                

                <el-row>
                    <span class="des-name">
                        主演:&nbsp;&nbsp;
                        <p class="des-content"> {{ mov_detail.vod_actor || '暂无信息' }}</p>
                    </span>
                    
                </el-row>

                <el-row class="detail3">
                    <span class="des-name">
                        详情:&nbsp;&nbsp; 
                        <p class="des-content" style="font-size:15px" v-if="checkHtml(mov_detail.vod_content)" v-html="mov_detail.vod_content"/>
                        <p class="des-content" style="font-size:15px" v-else>{{ mov_detail.vod_content || '暂无剧情简介' }}</p>
                    </span>  
                    
                </el-row>

            </el-col>  
        </el-row>

        <!-- 加载状态 -->
        <div v-else-if="loading" style="text-align: center; padding: 40px;">
            <el-icon class="is-loading" :size="30"><Loading /></el-icon>
            <p>加载中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else style="text-align: center; padding: 40px; color: #f56c6c;">
            <p>加载失败，请检查视频ID是否正确</p>
            <el-button @click="getMovDetail">重试</el-button>
        </div>

        <!-- 播放链接区域 -->
        <el-row class="vod-play-url" v-if="mov_detail.vod_play_url && Object.keys(mov_detail.vod_play_url).length > 0">
            <el-col class="vod-play-url"
                v-for="(v, k) in mov_detail.vod_play_url" 
                :key="k"
                :xs="8" :sm="3"
                style="margin: 5px 0;"
                >
                <el-button 
                class="vod-play-url" 
                style="float: left;" 
                @click="videoPlay(k)" 
                :class="[{active: activeName == v}]">
                {{ k }}
                </el-button>
            </el-col>
        </el-row>
        <el-row v-else-if="Object.keys(mov_detail).length > 0">
            <p style="color: #999; text-align: center;">暂无播放链接</p>
        </el-row>
        
        <!-- 视频播放器 -->
        <el-row class="video-play" v-if="video_play" style="margin: 40px  0">
            <myVideoPlay :src="video_play_url"/>
        </el-row>

            <!-- 评论区域 -->
    <el-row class="comment-section" style="margin: 40px 0;">
      <el-col :span="24">
        <h3 style="margin-bottom: 20px;">评论</h3>
        <Comments :vod_id="actualVodId" />
      </el-col>
    </el-row>
    </div>
        
</template>

<script>
// 视频详情
import apiGetMovDetail from '../apis/getMovDetail'
import myVideoPlay from './VideoPlay.vue'
import { ElMessage } from 'element-plus'
import { ref } from 'vue'
import { useStore } from 'vuex'
import { isCollectVideo, addCollectVideo, removeCollectVideo } from '../apis/videoCollection'
import Comments from './Comments.vue'  // 导入评论组件

export default {
  name: 'MovDetail',

  setup() {
    const store = useStore()
    return {
        store
    }
  },

  components: {
    myVideoPlay,
    Comments
  },

  props: {
        vod_id: String
    },
  data() {
    return {
        actualVodId: null,
        mov_detail: {},
        video_play: false,
        video_play_url: '',
        activeName: '',
        isCollect: 0,
        loading: false,
        // 添加一个标志来跟踪视频ID是否已准备好
        isVodIdReady: false,
        // 添加计时器用于防抖
        collectCheckTimer: null
    }
  },

  methods: {
    initializeVodId() {
      let vodId = this.vod_id
      
      // 如果 prop 中没有有效的 ID，从 URL 中提取
      if (!vodId || vodId === 'undefined' || vodId === 'null' || vodId === 'NaN' || isNaN(parseInt(vodId))) {
        const path = window.location.pathname
        const match = path.match(/\/movdetail\/(\d+)/)
        if (match && match[1]) {
          vodId = match[1]
        }
      }
      
      // 验证 ID
      if (!vodId || isNaN(parseInt(vodId))) {
        console.error('❌ 无效的视频ID:', vodId)
        ElMessage.error('视频ID无效')
        this.isVodIdReady = false
        return null
      }
      
      this.actualVodId = parseInt(vodId)
      this.isVodIdReady = true
      console.log('✅ 最终使用的视频ID:', this.actualVodId)
      return this.actualVodId
    },

    getMovDetail() {
      const vodId = this.initializeVodId()
      
      if (!vodId) {
        this.loading = false
        return
      }
      
      this.loading = true
      
      const param = {
        vod_id: parseInt(vodId)
      }

      apiGetMovDetail(param).then((res) => {
        if (res.code == 200) {
          this.mov_detail = res.data || {}
          // 🎯 关键：在数据加载完成后检查收藏状态
          this.$nextTick(() => {
            this.showIsCollect()
          })
        } else {
          ElMessage.error('获取电影详情失败: ' + (res.msg || '未知错误'))
          this.mov_detail = {}
        }
      }).catch(error => {
        ElMessage.error('网络请求失败: ' + error.message)
        this.mov_detail = {}
      }).finally(() => {
        this.loading = false
      })
    },

    addCollect() {
    console.log('🎯 addCollect 被调用!!!')
    console.log('📺 视频ID:', this.actualVodId)
    console.log('🔑 登录状态:', this.store.state.appStore.isLogining)
    console.log('👤 用户信息:', this.store.state.appStore.user)
    
    if (this.store.state.appStore.isLogining) {
        const data = {  // 改为 data
            vod_id: parseInt(this.actualVodId)  // 确保是数字
        }
        
        console.log('📤 发送添加收藏请求，数据:', data)
        
        addCollectVideo(data).then(
            (res) => {
                console.log('📊 添加收藏API响应:', res)
                
                if (res.code == 200) {  // 直接使用 res.code
                    this.isCollect = 1
                    console.log('✅ 收藏成功，更新状态为:', this.isCollect)
                    ElMessage({
                        message: '收藏成功',
                        type: 'success',
                    })
                } else {
                    console.log('❌ 收藏失败:', res.message)
                    ElMessage({
                        message: res.message || '收藏失败',
                        type: 'warning',
                    })
                }
            }
        ).catch(error => {
            console.error('💥 添加收藏异常:', error)
            ElMessage.error('收藏失败: ' + error.message)
        })
    } else {
        ElMessage({
            message: '请先登录',
            type: 'warning',
        })
    }
},

removeCollect() {
    console.log('🗑️ removeCollect 被调用!!!')
    console.log('📺 视频ID:', this.actualVodId)
    console.log('🔑 登录状态:', this.store.state.appStore.isLogining)
    
    if (this.store.state.appStore.isLogining) {
        const data = {  // 改为 data
            vod_id: parseInt(this.actualVodId)  // 确保是数字
        }
        
        console.log('📤 发送取消收藏请求，数据:', data)
        
        removeCollectVideo(data).then(
            (res) => {
                console.log('📊 取消收藏API响应:', res)
                
                if (res.code == 200) {  // 直接使用 res.code
                    this.isCollect = 0
                    console.log('✅ 取消收藏成功，更新状态为:', this.isCollect)
                    ElMessage({
                        message: '取消收藏成功',
                        type: 'success',
                    })
                } else {
                    console.log('❌ 取消收藏失败:', res.message)
                    ElMessage({
                        message: res.message || '取消收藏失败',
                        type: 'warning',
                    })
                }
            }
        ).catch(error => {
            console.error('💥 取消收藏异常:', error)
            ElMessage.error('取消收藏失败: ' + error.message)
        })
    } else {
        console.log('⚠️ 用户未登录')
        ElMessage({
            message: '请先登录',
            type: 'warning',
        })
    }
},

showIsCollect() {
    // � 关键修复：添加严格的检查
    if (!this.isVodIdReady || !this.actualVodId || isNaN(this.actualVodId)) {
      console.log('⏸️ 视频ID未准备好，跳过收藏状态检查')
      return
    }
    
    if (!this.store.state.appStore.isLogining) {
      console.log('⏸️ 用户未登录，跳过收藏状态检查')
      return
    }

    const params = {
      vod_id: this.actualVodId
    }
    
    console.log('📤 发送检查收藏状态请求，参数:', params)
    
    isCollectVideo(params).then(
      (res) => {
        console.log('📊 检查收藏状态API响应:', res)
        if (res.code == 200) {
          this.isCollect = res.data
          console.log('✅ 收藏状态:', this.isCollect ? '已收藏' : '未收藏')
        }
      }
    ).catch(error => {
      console.error('💥 检查收藏状态异常:', error)
      // 静默处理，不显示错误信息
    })
},

    // 测试所有收藏API
    // 测试所有收藏API
testCollectAPIs() {
    console.log('🧪 ===== 开始测试收藏API =====')
    console.log('📺 视频ID:', this.actualVodId)
    console.log('🔑 登录状态:', this.store.state.appStore.isLogining)
    
    if (!this.store.state.appStore.isLogining) {
        ElMessage.warning('请先登录后再测试')
        return
    }
    
    // 测试参数 - 只需要 vod_id，不需要 user_id
    const testParams = { vod_id: parseInt(this.actualVodId) }
    const testData = { vod_id: parseInt(this.actualVodId) }
    
    console.log('测试参数:', testParams)
    
    // 1. 测试检查收藏状态
    console.log('\n1️⃣ 测试检查收藏状态API')
    isCollectVideo(testParams).then(res => {
        console.log('✅ 检查收藏状态响应:', res)
    }).catch(err => {
        console.error('❌ 检查收藏状态失败:', err)
    })
    
    // 2. 测试添加收藏
    setTimeout(() => {
        console.log('\n2️⃣ 测试添加收藏API')
        addCollectVideo(testData).then(res => {
            console.log('✅ 添加收藏响应:', res)
        }).catch(err => {
            console.error('❌ 添加收藏失败:', err)
        })
    }, 1000)
    
    // 3. 测试取消收藏
    setTimeout(() => {
        console.log('\n3️⃣ 测试取消收藏API')
        removeCollectVideo(testData).then(res => {
            console.log('✅ 取消收藏响应:', res)
        }).catch(err => {
            console.error('❌ 取消收藏失败:', err)
        })
    }, 2000)
    
    ElMessage.success('已开始测试，请查看控制台输出')
},

    videoPlay(playKey) {
        if (this.mov_detail.vod_play_url && this.mov_detail.vod_play_url[playKey]) {
            const play_url = this.mov_detail.vod_play_url[playKey]
            
            this.video_play = true
            this.video_play_url = play_url
            this.activeName = play_url
            
            ElMessage({
                message: '开始播放: ' + playKey,
                type: 'success',
            })
        } else {
            ElMessage({
                message: '播放链接无效',
                type: 'warning',
            })
        }
    },

    checkHtml(s) {
        if (typeof(s) == 'string') {
            if (s.indexOf('<p>')>-1) {
                return true
            } else if (s.indexOf('<span>')>-1) {
                return true
            } else {
                return false
            }
        } else {
            return false
        }
    },

    handleImageError(event) {
        event.target.src = '/api/imgs/default.jpg'
    }
  },

  watch: {
      moniterUser() {
        return this.store.state.appStore.user.id
      }
    },

    computed: {
      moniterUser() {
        // 🎯 只在视频ID准备好且用户登录时检查收藏状态
        if (this.isVodIdReady && this.store.state.appStore.isLogining) {
          // 使用防抖避免频繁调用
          clearTimeout(this.collectCheckTimer)
          this.collectCheckTimer = setTimeout(() => {
            this.showIsCollect()
          }, 500)
        }
        return this.store.state.appStore.user.id
      }
    },

  created() {
    console.log('🚀 MovDetail 组件创建')
    console.log('📺 接收到的 vod_id prop:', this.vod_id)
    
    // 只初始化视频ID，不立即检查收藏状态
    this.initializeVodId()
    this.getMovDetail()
  },

  mounted() {
    console.log('🎬 MovDetail 组件挂载完成')
    console.log('📺 实际使用的视频ID:', this.actualVodId)
    console.log('🔑 登录状态:', this.store.state.appStore.isLogining)
    
    // 🎯 延迟检查收藏状态，确保所有数据都已准备好
    setTimeout(() => {
      if (this.isVodIdReady) {
        this.showIsCollect()
      }
    }, 200)
  },

  beforeUnmount() {
    if (this.collectCheckTimer) {
      clearTimeout(this.collectCheckTimer)
    }
  }

}

</script>

<style>
div.vod-detail .el-row {
    margin: 0 0 10px;
}

span.des-name {
    line-height: 20px;
    margin: 0;
    color: #999;
    font-weight: 400;
    display: inline;
    text-align: left;
}

p.des-content {
    margin: 0;
    line-height: 20px;
    text-align: left;
    display: inline;
    color:black;
}

.el-col.vod-detail div.vod-detail {
    position: relative;
    width: 100%;
    height: 0;
    overflow: hidden;
    padding-bottom: 130%;
}

.el-col.vod-detail div img {
    width: 95%;
    height: auto;
    display: block;
    margin: 0 auto;
    object-fit: cover;
}

.el-button.vod-play-url.active {
  background-color: rgb(36, 184, 242);
  color: white;
  border-radius: 4px;
}
</style>