import { createApp } from 'vue'
import './style.css'
import App from './App.vue'

// 引入 GitHub Markdown 样式和 Highlight.js 样式
import 'github-markdown-css/github-markdown-light.css'
import 'highlight.js/styles/atom-one-dark.css'

const app = createApp(App)
app.mount('#app')