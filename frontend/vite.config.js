// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'

// // https://vite.dev/config/
// export default defineConfig({
//   plugins: [vue()],
// })



// 本地开发
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    // 代理配置：模拟生产环境 Nginx 的转发行为
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000', // 后端地址
        changeOrigin: true,
      },
      '/ws': {
        target: 'ws://127.0.0.1:8000', // 后端 WebSocket 地址
        ws: true, // 开启 WebSocket 代理支持
        changeOrigin: true,
      }
    }
  }
})