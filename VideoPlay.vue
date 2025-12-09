<template>
  <div class="video-player-container">
    <video 
      ref="videoPlayer" 
      controls 
      autoplay
      style="width: 100%; height: 100%;"
    ></video>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import Hls from 'hls.js'

export default {
  name: 'VideoPlay',
  props: {
    videoUrl: String,
    src: String  // 兼容旧的 prop 名称
  },
  setup(props) {
    const videoPlayer = ref(null)
    let hls = null

    // 获取实际的视频URL
    const getVideoUrl = () => {
      return props.videoUrl || props.src
    }

    const initPlayer = () => {
      const url = getVideoUrl()
      
      if (!url) {
        console.error('❌ 视频URL为空')
        return
      }

      console.log('🎬 初始化播放器，URL:', url)

      // 如果已有实例，先销毁
      if (hls) {
        console.log('🧹 销毁旧的HLS实例')
        hls.destroy()
        hls = null
      }

      if (Hls.isSupported()) {
        console.log('✅ HLS.js 支持当前浏览器')
        
        hls = new Hls({
          debug: true,  // 开启调试
          enableWorker: true,
          lowLatencyMode: true,
          backBufferLength: 90
        })
        
        hls.loadSource(url)
        hls.attachMedia(videoPlayer.value)
        
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
          console.log('✅ 媒体清单解析完成，开始播放')
          videoPlayer.value.play().catch(e => {
            console.error('❌ 自动播放失败:', e)
          })
        })
        
        hls.on(Hls.Events.ERROR, (event, data) => {
          console.error('❌ HLS 错误:', data)
          if (data.fatal) {
            switch (data.type) {
              case Hls.ErrorTypes.NETWORK_ERROR:
                console.log('🔄 网络错误，尝试重新加载')
                hls.startLoad()
                break
              case Hls.ErrorTypes.MEDIA_ERROR:
                console.log('� 媒体错误，尝试恢复')
                hls.recoverMediaError()
                break
              default:
                console.log('💥 不可恢复的错误')
                hls.destroy()
                break
            }
          }
        })
        
        hls.on(Hls.Events.LEVEL_LOADED, (event, data) => {
          console.log('📊 级别加载:', data)
        })
        
      } else if (videoPlayer.value.canPlayType('application/vnd.apple.mpegurl')) {
        // 原生HLS支持（Safari）
        console.log('✅ 浏览器原生支持HLS')
        videoPlayer.value.src = url
        videoPlayer.value.addEventListener('loadedmetadata', () => {
          console.log('✅ 元数据加载完成，开始播放')
          videoPlayer.value.play().catch(e => {
            console.error('❌ 自动播放失败:', e)
          })
        })
      } else {
        console.error('❌ 浏览器不支持HLS播放')
      }
    }

    // 监听 URL 变化
    watch(() => getVideoUrl(), (newUrl, oldUrl) => {
      if (newUrl && newUrl !== oldUrl) {
        console.log('🔄 视频URL变化:', newUrl)
        initPlayer()
      }
    })

    onMounted(() => {
      console.log('🚀 VideoPlay 组件挂载')
      const url = getVideoUrl()
      if (url) {
        // 延迟初始化，确保DOM已渲染
        setTimeout(() => {
          initPlayer()
        }, 100)
      }
    })

    onUnmounted(() => {
      console.log('👋 VideoPlay 组件卸载')
      if (hls) {
        hls.destroy()
        hls = null
      }
    })

    return {
      videoPlayer
    }
  }
}
</script>

<style scoped>
.video-player-container {
  width: 100%;
  height: 500px;
  background: #000;
}

video {
  outline: none;
}
</style>