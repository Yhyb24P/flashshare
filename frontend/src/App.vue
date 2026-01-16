<template>
  <div class="container">
    <div class="header">
      <div class="brand">
        <h2>⚡ FlashShare</h2>
        <span class="subtitle">瞬传 | 阅后即焚</span>
      </div>
      
      <!-- 登录/状态栏 -->
      <div v-if="!joined" class="join-box">
        <input v-model="roomId" placeholder="房间号 (如 1001)" @keyup.enter="joinRoom" />
        <button @click="joinRoom">进入</button>
      </div>
      <div v-else class="status-bar">
        <div class="status-item">🟢 房间: <strong>{{ roomId }}</strong></div>
        <div class="status-item">ID: {{ clientId.slice(0, 4) }}</div>
      </div>
    </div>

    <!-- 聊天主区域 -->
    <div v-if="joined" class="chat-area" ref="chatBox">
      <div v-if="messages.length === 0" class="empty-tip">
        👋 房间是空的，发送第一条消息吧！<br>
        支持 Markdown 语法和图片预览。
      </div>

      <div v-for="msg in messages" :key="msg.id" class="message-row" :class="{ 'my-msg': msg.sender === clientId }">
        
        <!-- 系统通知 -->
        <div v-if="msg.type === 'expired'" class="system-msg">
          🗑️ 消息或文件已过期销毁
        </div>

        <!-- 正常消息气泡 -->
        <div v-else class="message-bubble" :class="msg.type">
          <!-- 消息元数据 (发送者 + 倒计时) -->
          <div class="msg-meta">
            <span class="sender-name">{{ msg.sender.slice(0,4) }}</span>
            <span class="timer" v-if="msg.expires_at > now" :class="{'urgent': (msg.expires_at - now) < 60}">
              ⏱️ {{ formatTime(msg.expires_at - now) }}
            </span>
            <span class="timer expired" v-else>已过期</span>
          </div>

          <!-- A. Markdown 文本消息 -->
          <div v-if="msg.type === 'text'" 
               class="markdown-body" 
               v-html="renderMarkdown(msg.content)">
          </div>

          <!-- B. 文件/图片消息 -->
          <div v-if="msg.type === 'file'" class="file-card">
            
            <!-- 如果是图片且未过期，显示预览 -->
            <div v-if="isImage(msg.filename) && msg.expires_at > now" class="image-preview">
               <img :src="getDownloadUrl(msg.download_url)" alt="图片预览" @click="openImage(getDownloadUrl(msg.download_url))"/>
            </div>

            <!-- 文件信息栏 -->
            <div class="file-info">
              <div class="file-icon">{{ getFileIcon(msg.filename) }}</div>
              <div class="file-details">
                <div class="filename" :title="msg.filename">{{ msg.filename }}</div>
                <div class="filesize" v-if="msg.file_size">{{ formatFileSize(msg.file_size) }}</div>
              </div>
              
              <!-- 下载按钮 -->
              <a v-if="msg.expires_at > now" 
                 :href="getDownloadUrl(msg.download_url)" 
                 target="_blank" 
                 class="download-btn"
                 download>
                 ⬇️
              </a>
              <span v-else class="expired-text">❌</span>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- 底部输入区 -->
    <div v-if="joined" class="input-area">
      <!-- 隐藏的文件上传 Input -->
      <input type="file" ref="fileInput" @change="uploadFile" style="display: none" />
      
      <button class="tool-btn" @click="$refs.fileInput.click()" title="上传文件/图片">
        📎
      </button>
      
      <textarea 
        v-model="inputText" 
        placeholder="支持 Markdown (Enter 发送, Shift+Enter 换行)..." 
        @keydown.enter.exact.prevent="sendMessage"
        rows="1"
      ></textarea>
      
      <button class="send-btn" @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

// --- 状态定义 ---
const roomId = ref("");
const clientId = ref(Math.random().toString(36).substring(7));
const joined = ref(false);
const inputText = ref("");
const messages = ref([]);
const ws = ref(null);
const now = ref(Date.now() / 1000);
let timerInterval = null;

// --- 工具函数 ---

// 1. Markdown 解析 (带安全过滤)
const renderMarkdown = (text) => {
  if (!text) return "";
  // marked 解析 md -> html
  const rawHtml = marked.parse(text);
  // DOMPurify 过滤危险脚本 (防止 XSS 攻击)
  return DOMPurify.sanitize(rawHtml);
};

// 2. 判断是否为图片
const isImage = (filename) => {
  if (!filename) return false;
  const ext = filename.split('.').pop().toLowerCase();
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp'].includes(ext);
};

// 3. 根据后缀获取简单图标
const getFileIcon = (filename) => {
  if (isImage(filename)) return '🖼️';
  if (filename.endsWith('.pdf')) return '📕';
  if (filename.endsWith('.zip') || filename.endsWith('.rar')) return '📦';
  if (filename.endsWith('.py') || filename.endsWith('.js') || filename.endsWith('.html')) return '💻';
  return '📄';
};

const formatFileSize = (bytes) => {
  if (!bytes) return '';
  bytes = parseInt(bytes);
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
};

const openImage = (url) => {
  window.open(url, '_blank');
}

// --- WebSocket 与核心逻辑 ---

const joinRoom = () => {
  if (!roomId.value) return alert("请输入房间号");
  // 自动适配 wss/ws 和当前域名
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws/${roomId.value}/${clientId.value}`;
  
  ws.value = new WebSocket(wsUrl);

  ws.value.onopen = () => {
    joined.value = true;
    console.log("已连接 WebSocket");
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'expired') {
      const target = messages.value.find(m => m.id === data.id);
      if (target) target.type = 'expired';
    } else {
      messages.value.push(data);
      scrollToBottom();
    }
  };

  ws.value.onclose = () => {
    // 简单的断线处理
    if(joined.value) alert("连接已断开，请刷新页面重试");
    joined.value = false;
  };
};

const sendMessage = () => {
  if (!inputText.value.trim()) return;
  ws.value.send(JSON.stringify({ content: inputText.value }));
  inputText.value = "";
  // 重置 textarea 高度
  nextTick(() => {
    const textarea = document.querySelector('textarea');
    if(textarea) textarea.style.height = 'auto';
  });
};

const uploadFile = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("room_id", roomId.value);
  formData.append("sender", clientId.value);

  // 简单的上传 UI 反馈 (实际项目中可以做进度条)
  const originalText = inputText.value;
  inputText.value = `[正在上传 ${file.name}...]`;

  try {
    const res = await fetch("/api/upload", {
      method: "POST",
      body: formData
    });
    if (!res.ok) {
      const errData = await res.json();
      throw new Error(errData.detail || "上传失败");
    }
    inputText.value = originalText; // 恢复输入框
  } catch (err) {
    alert("上传出错: " + err.message);
    inputText.value = originalText;
  } finally {
    // 清空 input 允许重复上传同名文件
    event.target.value = '';
  }
};

const getDownloadUrl = (path) => path; // Nginx 代理，直接返回相对路径即可

const formatTime = (seconds) => {
  if (seconds <= 0) return "00:00";
  const m = Math.floor(seconds / 60).toString().padStart(2, '0');
  const s = Math.floor(seconds % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
};

const scrollToBottom = () => {
  nextTick(() => {
    const box = document.querySelector('.chat-area');
    if (box) box.scrollTop = box.scrollHeight;
  });
};

onMounted(() => {
  timerInterval = setInterval(() => { now.value = Date.now() / 1000; }, 1000);
});

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval);
  if (ws.value) ws.value.close();
});
</script>

<style>
/* 全局重置 */
* { box-sizing: border-box; }
body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: #f0f2f5; color: #333; }

.container { max-width: 800px; margin: 0 auto; height: 100vh; display: flex; flex-direction: column; background: white; box-shadow: 0 0 20px rgba(0,0,0,0.05); }

/* 头部 */
.header { padding: 15px 20px; background: #2c3e50; color: white; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.brand h2 { margin: 0; font-size: 1.2rem; }
.subtitle { font-size: 0.8rem; opacity: 0.8; }
.status-bar { display: flex; gap: 15px; font-size: 0.9rem; }
.join-box { display: flex; gap: 8px; }
.join-box input { padding: 6px 10px; border-radius: 4px; border: none; outline: none; }
.join-box button { padding: 6px 15px; background: #42b983; border: none; border-radius: 4px; color: white; cursor: pointer; font-weight: bold; }

/* 聊天区域 */
.chat-area { flex: 1; padding: 20px; overflow-y: auto; background: #f4f7f6; display: flex; flex-direction: column; gap: 15px; }
.empty-tip { text-align: center; color: #999; margin-top: 50px; line-height: 1.6; }

/* 消息行 */
.message-row { display: flex; width: 100%; }
.my-msg { justify-content: flex-end; }
.my-msg .message-bubble { background: #e3f2fd; border-top-right-radius: 2px; }
.message-bubble { max-width: 80%; padding: 10px 15px; border-radius: 12px; background: white; box-shadow: 0 1px 2px rgba(0,0,0,0.1); border-top-left-radius: 2px; position: relative; }

/* 消息元数据 */
.msg-meta { display: flex; justify-content: space-between; font-size: 0.75rem; color: #888; margin-bottom: 6px; gap: 15px; }
.timer { font-family: monospace; }
.timer.urgent { color: #ff5252; font-weight: bold; animation: pulse 1s infinite; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }

/* Markdown 内容样式 (模仿 GitHub) */
.markdown-body { font-size: 0.95rem; line-height: 1.5; overflow-wrap: break-word; }
.markdown-body p { margin: 0 0 8px 0; }
.markdown-body p:last-child { margin-bottom: 0; }
.markdown-body pre { background: #2d2d2d; color: #ccc; padding: 10px; border-radius: 6px; overflow-x: auto; margin: 8px 0; }
.markdown-body code { background: rgba(0,0,0,0.05); padding: 2px 4px; border-radius: 3px; font-family: monospace; font-size: 0.9em; }
.markdown-body pre code { background: none; padding: 0; color: inherit; }
.markdown-body blockquote { border-left: 3px solid #ccc; margin: 0; padding-left: 10px; color: #666; }
.markdown-body img { max-width: 100%; border-radius: 4px; }
.markdown-body a { color: #0366d6; text-decoration: none; }
.markdown-body a:hover { text-decoration: underline; }

/* 文件卡片样式 */
.file-card { background: rgba(0,0,0,0.03); border-radius: 8px; padding: 8px; border: 1px solid rgba(0,0,0,0.05); }
.image-preview { margin-bottom: 8px; text-align: center; }
.image-preview img { max-width: 100%; max-height: 300px; border-radius: 4px; cursor: zoom-in; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
.file-info { display: flex; align-items: center; gap: 10px; padding: 4px; }
.file-icon { font-size: 1.5rem; }
.file-details { flex: 1; overflow: hidden; }
.filename { font-size: 0.9rem; font-weight: bold; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.filesize { font-size: 0.75rem; color: #666; }
.download-btn { padding: 5px 10px; background: white; border-radius: 4px; text-decoration: none; border: 1px solid #ddd; font-size: 0.9rem; transition: all 0.2s; }
.download-btn:hover { background: #f0f0f0; border-color: #ccc; }

/* 输入区域 */
.input-area { padding: 15px; background: white; border-top: 1px solid #eee; display: flex; gap: 10px; align-items: flex-end; }
.tool-btn { font-size: 1.2rem; background: none; border: none; cursor: pointer; padding: 8px; color: #666; transition: color 0.2s; }
.tool-btn:hover { color: #2c3e50; background: #f5f5f5; border-radius: 50%; }
textarea { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 6px; resize: none; font-family: inherit; max-height: 120px; min-height: 40px; outline: none; transition: border 0.2s; }
textarea:focus { border-color: #42b983; }
.send-btn { padding: 0 20px; height: 40px; background: #2c3e50; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: background 0.2s; }
.send-btn:hover { background: #1a252f; }

/* 响应式 */
@media (max-width: 600px) {
  .message-bubble { max-width: 90%; }
  .header h2 { font-size: 1rem; }
  .status-bar { font-size: 0.8rem; }
}
</style>