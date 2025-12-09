<template>
  <el-carousel :height="bannerHeight + 'px'" style="margin: 0 auto; width: 100%; border-radius: 4px" 
               indicator-position="outside">
    <el-carousel-item v-for="(img, index) in imgs" :key="index">
      <img :src="img" :style="imgStyle" @load="onImgLoad">
    </el-carousel-item>
  </el-carousel>
</template>

<script>
// 直接使用相对路径
export default {
    name: "SakuraBigImg",
    data() {
        return {
            bannerHeight: 400,
            imgs: [
                "/src/assets/bigImg/b1.webp",
                "/src/assets/bigImg/b2.webp",
                "/src/assets/bigImg/b3.webp", 
                "/src/assets/bigImg/b4.webp"
            ]
        }
    },
    computed: {
        imgStyle() {
            return {
                width: '100%',
                height: this.bannerHeight + 'px',
                objectFit: 'cover'
            }
        }
    },
    mounted() {
        this.setBannerHeight();
        window.addEventListener('resize', this.setBannerHeight);
    },
    beforeUnmount() {
        window.removeEventListener('resize', this.setBannerHeight);
    },
    methods: {
        onImgLoad() {
            this.setBannerHeight();
        },
        setBannerHeight() {
            this.$nextTick(() => {
                const imgElement = this.$el?.querySelector('img');
                if (imgElement && imgElement.height > 0) {
                    this.bannerHeight = imgElement.height;
                }
            });
        }
    }
}
</script>

<style scoped>
.el-carousel__item h3 {
  display: flex;
  color: #475669;
  opacity: 0.75;
  line-height: 300px;
  margin: 0;
}

.el-carousel__item:nth-child(2n) {
  background-color: white;
}

.el-carousel__item:nth-child(2n + 1) {
  background-color: white;
}
</style>