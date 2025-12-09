<template>  
  <div class="home-card" v-show="contentshow">
    <el-row style="margin: 15px 0 0 0">
        <span class="home-card-type">{{ type_id_names[movtype] }}</span>
        <router-link :to="'/movtype/'+ movtype" class="home-card-type" style="text-decoration: none; color:black;">
          &nbsp; 更多>
        </router-link>
    </el-row>
    
    <el-row alignment="flex-start">
      <el-col 
        v-for="o in movieList"
        :key="o.vod_id"
        :xs="8" :sm="4" :md="4" 
        style="padding: 9px;">
        <router-link :to="'/movdetail/'+ o.vod_id" style="text-decoration: none;">   
        <el-card
        class="box-card" 
        @click="selectMovie"
        shadow="hover"
        :body-style="{ padding: '8px 5px' }">
        <div class="card-div">
          <img :src="o.vod_pic" class="card-image" @error="handleImageError"/>
          <span class="card-remark">{{ o.vod_remarks }}</span>
        </div>
      
        <div style="padding: 0px;">
          <span style="line-height: 26px; font-size: 15px; color:#777; display: flex; margin-top: 4px; text-overflow: ellipsis; overflow: hidden; width: 80%; white-space: nowrap;">
            <el-tooltip class="box-item" effect="dark" :content="o.vod_name" placement="bottom-end" :show-after="1000">
            {{ o.vod_name }}
            </el-tooltip>
          </span>
        </div>
      
      </el-card>
      </router-link>
      </el-col>
   </el-row>
  </div>
</template>

<script>
import apiGetMovList from '../apis/getMovInfo'
import SakuraBigImg from './SakuraBigImg.vue'
import { useStore } from 'vuex'

export default {
    name: "MovLimitCard",
    props: {
        movtype: Number
    },
    components: {
      SakuraBigImg,
    },

    setup() {
      const store = useStore()
      // 修正分类映射 - 与后端一致
      const type_id_names = {
        1: "动漫",
        2: "电影", 
        3: "电视剧",
        4: "综艺"
      }
      return {
            store,
            type_id_names
        }
    },

    data() {
      return {
        page: 1,
        contentshow: true,
        movieList: []
      }
    },

    methods: {
        selectMovie(h) {
            console.log(h)
        },

        handleImageError(event) {
            event.target.src = '/api/imgs/default.jpg'
        },

        getMovList() {
          console.log('=== 🎯 MovLimitCard 调试信息 ===')
          console.log('接收到的 movtype:', this.movtype)
          console.log('分类名称:', this.type_id_names[this.movtype])
          
          const param =  { 
              page: this.page,
              movtype: this.movtype
          }

          console.log('API请求参数:', param)

          apiGetMovList(param).then(
            (res) => { 
              console.log('=== 📦 API响应 ===')
              console.log('分类:', this.type_id_names[this.movtype])
              console.log('获取到数据条数:', res.data ? res.data.length : 0)
              
              if (res.data && res.data.length > 0) {
                  console.log('前3条数据:')
                  res.data.slice(0, 3).forEach((item, index) => {
                    console.log(`[${index + 1}] ${item.vod_name}`)
                  })
                  
                  this.movieList = res.data
                  this.contentshow = true
              } else {
                console.log('❌ 没有获取到数据')
                this.contentshow = false
              }
             }
          ).catch(
            (error) => {
                console.error('💥 请求错误:', error)
                this.contentshow = false
            }
          )
        }
   },

   created() {
    console.log('🚀 MovLimitCard 创建，movtype:', this.movtype)
    this.getMovList()
   }

}
</script>

<style>
span.home-card-type {
    float: left;
    margin: 10px;
    font-size: 20px; 
    font-weight: bold;
    line-height: 20px;
}

.home-card-type {
    float: left;
    margin: 10px;
    line-height: 20px;
}

a.home-card-type:hover {
    color:rgb(36, 184, 242) !important;
}

.card-div {
  position: relative;
  width: 100%;
  height: 0;
  padding-bottom: 140%;
  overflow: hidden;
}

.card-image {
  position: absolute;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-remark {
  position: absolute;
  bottom: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  font-size: 12px;
  border-radius: 4px 0 0 0;
}
</style>