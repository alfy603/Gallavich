<template>
  <div style="padding: 20px 10px 0 10px">
    <SakuraBigImgVue/>
  </div>
  
  <!-- 正确的分类顺序 -->
  <MovLimitCardVue :movtype="1" key="anime"/>  <!-- 动漫 -->
  <MovLimitCardVue :movtype="2" key="movie"/>  <!-- 电影 -->
  <MovLimitCardVue :movtype="3" key="tv"/>     <!-- 电视剧 -->
  <MovLimitCardVue :movtype="4" key="variety"/> <!-- 综艺 -->
  <el-backtop :right="50" :bottom="80" />
</template>

<script>
// 首页
import SakuraBigImgVue from '../components/SakuraBigImg.vue'
import MovLimitCardVue from '../components/MovLimitCard.vue'

export default {
  name: 'MovieHome',
  components: {
    MovLimitCardVue,
    SakuraBigImgVue
  }
}
</script>