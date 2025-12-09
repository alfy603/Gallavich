<template>
  <div class="ai-search-container">
    <div class="search-header">
      <h1>🤖 AI 智能搜索</h1>
      <p>用自然语言提问，AI 帮你查询视频</p>
    </div>

    <!-- 搜索框 -->
    <div class="search-box">
      <el-input
        v-model="question"
        placeholder="试试问：最近更新的动漫有哪些？"
        size="large"
        @keyup.enter="handleSearch"
      >
        <template #prepend>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button type="primary" @click="handleSearch" :loading="searching">
            搜索
          </el-button>
        </template>
      </el-input>
    </div>

    <!-- 示例问题 -->
    <div class="example-questions" v-if="! hasSearched">
      <p>试试这些问题：</p>
      <el-tag
        v-for="(q, index) in exampleQuestions"
        :key="index"
        @click="question = q; handleSearch()"
        style="margin: 5px; cursor: pointer;"
      >
        {{ q }}
      </el-tag>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results" v-if="hasSearched">
      <!-- AI 解释 -->
      <el-card class="explanation-card" v-if="searchResult">
        <template #header>
          <span>💡 AI 理解</span>
        </template>
        <p><strong>你的问题：</strong>{{ searchResult.question }}</p>
        <p><strong>AI 解释：</strong>{{ searchResult.explanation }}</p>
        <p><strong>执行状态：</strong>
          <el-tag :type="searchResult.success ? 'success' : 'danger'">
            {{ searchResult.reflection }}
          </el-tag>
        </p>
        
        <!-- SQL展示（可折叠） -->
        <el-collapse style="margin-top: 10px;">
          <el-collapse-item title="查看生成的SQL">
            <div class="sql-display">
              <p><strong>最终SQL：</strong></p>
              <code>{{ searchResult.final_sql }}</code>
              
              <div v-if="searchResult.sql_v2" style="margin-top: 10px;">
                <p><strong>优化前SQL：</strong></p>
                <code>{{ searchResult. sql_v1 }}</code>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-card>

      <!-- 视频结果 -->
      <div class="video-results" v-if="searchResult && searchResult.data. length > 0">
        <h3>找到 {{ searchResult.data.length }} 个结果</h3>
        
        <div class="video-grid">
          <div 
            v-for="video in searchResult.data" 
            :key="video.id" 
            class="video-card"
            @click="goToDetail(video.id)"
          >
            <div class="video-poster">
              <img :src="video.vod_pic" :alt="video.vod_name" @error="handleImageError" />
              <div class="video-remarks" v-if="video.vod_remarks">
                {{ video.vod_remarks }}
              </div>
            </div>
            <div class="video-info">
              <h4 class="video-title">{{ video.vod_name }}</h4>
              <p class="video-type">{{ video.type_name }}</p>
              <p class="video-time" v-if="video.vod_time">
                {{ formatDate(video.vod_time) }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 无结果 -->
      <el-empty 
        v-else-if="searchResult && searchResult.data.length === 0"
        description="没有找到相关视频，试试换个问法"
      >
        <el-button type="primary" @click="resetSearch">重新搜索</el-button>
      </el-empty>

      <!-- 错误提示 -->
      <el-alert
        v-if="searchResult && searchResult.error"
        type="error"
        :title="searchResult.error"
        show-icon
        :closable="false"
      />
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { aiSearch } from '../apis/aiSearch'

export default {
  name: 'AISearch',
  components: {
    Search
  },
  setup() {
    const router = useRouter()
    const question = ref('')
    const searching = ref(false)
    const hasSearched = ref(false)
    const searchResult = ref(null)

    const exampleQuestions = [
      '最近更新的动漫有哪些？',
      '评论最多的电影',
      '2023年上映的电视剧',
      '日本动漫推荐',
      '最热门的综艺节目'
    ]

    const handleSearch = async () => {
      if (!question. value.trim()) {
        ElMessage.warning('请输入搜索问题')
        return
      }

      searching.value = true
      hasSearched.value = true

      try {
        const res = await aiSearch(question.value)
        console.log('AI搜索结果:', res)
        
        if (res.success) {
          searchResult.value = res
          ElMessage.success('搜索完成')
        } else {
          searchResult.value = res
          ElMessage.error(res.error || '搜索失败')
        }
      } catch (error) {
        console.error('搜索异常:', error)
        ElMessage.error('搜索失败，请重试')
      } finally {
        searching.value = false
      }
    }

    const resetSearch = () => {
      question.value = ''
      hasSearched.value = false
      searchResult.value = null
    }

    const goToDetail = (vodId) => {
      router. push(`/movdetail/${vodId}`)
    }

    const handleImageError = (event) => {
      event.target.src = '/api/imgs/default. jpg'
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('zh-CN')
    }

    return {
      question,
      searching,
      hasSearched,
      searchResult,
      exampleQuestions,
      handleSearch,
      resetSearch,
      goToDetail,
      handleImageError,
      formatDate
    }
  }
}
</script>

<style scoped>
. ai-search-container {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.search-header {
  text-align: center;
  margin-bottom: 40px;
}

.search-header h1 {
  font-size: 36px;
  margin: 0 0 10px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.search-header p {
  color: #666;
  font-size: 16px;
}

.search-box {
  max-width: 800px;
  margin: 0 auto 30px;
}

.example-questions {
  text-align: center;
  margin: 20px 0 40px;
}

.example-questions p {
  color: #999;
  font-size: 14px;
  margin-bottom: 10px;
}

.explanation-card {
  margin-bottom: 30px;
}

.sql-display {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 8px;
}

.sql-display code {
  display: block;
  background: #fff;
  padding: 10px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
  overflow-x: auto;
}

.video-results h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
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

.video-info {
  padding: 12px;
}

.video-title {
  margin: 0 0 6px 0;
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

. video-type {
  margin: 0 0 4px 0;
  color: #999;
  font-size: 12px;
}

.video-time {
  margin: 0;
  color: #ccc;
  font-size: 12px;
}
</style>