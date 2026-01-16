// 云端开发

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0', // 允许公网访问
    port: 5173,
    proxy: {
      // 代理 API 请求到后端 8000 端口
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      // 代理 WebSocket 请求
      '/ws': {
        target: 'ws://127.0.0.1:8000',
        ws: true,
        changeOrigin: true,
      }
    }
  }
})



// // 本地开发
// import { defineConfig } from 'vite'
// import vue from '@vitejs/plugin-vue'

// // https://vitejs.dev/config/
// export default defineConfig({
//   plugins: [vue()],
//   server: {
//     // 代理配置：模拟生产环境 Nginx 的转发行为
//     proxy: {
//       '/api': {
//         target: 'http://127.0.0.1:8000', // 后端地址
//         changeOrigin: true,
//       },
//       '/ws': {
//         target: 'ws://127.0.0.1:8000', // 后端 WebSocket 地址
//         ws: true, // 开启 WebSocket 代理支持
//         changeOrigin: true,
//       }
//     }
//   }
// })