import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  base: './',
  server: {
    proxy: {
      // 代理 /api/vod_list 到 /vod/vod_list
      '/api/vod_list': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/vod_list/, '/vod/vod_list')
      },
      // 代理 /api/vod_detail 到 /vod/vod_detail
      '/api/vod_detail': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/vod_detail/, '/vod/vod_detail')
      },
      // 代理 /api/auth 到 /auth
      '/api/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/auth/, '/auth')
      },
      // 代理 /api/show 到 /comments/show
      '/api/show': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
  rewrite: (path) => path.replace(/^\/api\/show/, '/show')
      },
      // 代理 /api/collection 到 /collection
      '/api/collection': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/collection/, '/collection')
      },
      // 代理 /api/publish 到 /comments/publish
      '/api/publish': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/publish/, '/publish')
      },
      // 代理 /api/reply 到 /comments/reply
      '/api/reply': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/reply/, '/reply')
      },
      // 代理 /api/delete 到 /delete
      '/api/delete': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/delete/, '/delete')
      },
      // 代理 /api/imgs 到 /vod/imgs
      '/api/imgs': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/imgs/, '/vod/imgs')
      },
      // 代理 /api/live 到 /live
      '/api/live': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/live/, '/live')
      },
      '/api/proxy/m3u8': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api\/proxy\/m3u8/, '/vod/proxy/m3u8')
      },
       '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
      
    }
  }
})