<template>
  <div class="container">
    <div class="header">
      <h2>⚡ FlashShare 瞬传</h2>
      <div v-if="!joined" class="join-box">
        <input v-model="roomId" placeholder="输入房间号 (如 1234)" @keyup.enter="joinRoom" />
        <button @click="joinRoom">进入房间</button>
      </div>
      <div v-else class="status-bar">
        <span>🟢 房间: {{ roomId }}</span>
        <span>ID: {{ clientId.slice(0, 4) }}</span>
      </div>
    </div>

    <div v-if="joined" class="chat-area" ref="chatBox">
      <div v-for="msg in messages" :key="msg.id" class="message-row" :class="{ 'my-msg': msg.sender === clientId }">
        
        <div v-if="msg.type === 'expired'" class="system-msg">
          🗑️ 消息/文件已过期销毁
        </div>

        <div v-else class="message-bubble" :class="msg.type">
          <div class="msg-meta">
            <span>{{ msg.sender.slice(0,4) }}</span>
            <span class="timer" v-if="msg.expires_at > now">
              ⏱️ {{ formatTime(msg.expires_at - now) }}
            </span>
            <span class="timer expired" v-else>已过期</span>
          </div>

          <div v-if="msg.type === 'text'" class="content">{{ msg.content }}</div>

          <div v-if="msg.type === 'file'" class="file-content">
            <div class="icon">📄</div>
            <div class="details">
              <div class="filename">{{ msg.filename }}</div>
              <a v-if="msg.expires_at > now" 
                 :href="getDownloadUrl(msg.download_url)" 
                 target="_blank" 
                 class="download-btn">
                 ⬇️ 点击下载
              </a>
              <span v-else>文件已失效</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="joined" class="input-area">
      <input type="file" ref="fileInput" @change="uploadFile" style="display: none" />
      <button class="icon-btn" @click="$refs.fileInput.click()">📎</button>
      <input v-model="inputText" placeholder="发送消息..." @keyup.enter="sendMessage" />
      <button @click="sendMessage">发送</button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue';

// --- 状态定义 ---
const roomId = ref("");
const clientId = ref(Math.random().toString(36).substring(7)); // 随机生成一个用户ID
const joined = ref(false);
const inputText = ref("");
const messages = ref([]);
const ws = ref(null);
const now = ref(Date.now() / 1000); // 当前时间戳(秒)
let timerInterval = null;

// --- WebSocket 逻辑 ---
const joinRoom = () => {
  if (!roomId.value) return alert("请输入房间号");
  
  // 连接后端 WebSocket (注意端口要对应后端 8000)
  const wsUrl = `ws://localhost:8000/ws/${roomId.value}/${clientId.value}`;
  ws.value = new WebSocket(wsUrl);

  ws.value.onopen = () => {
    joined.value = true;
    console.log("已连接 WebSocket");
  };

  ws.value.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    // 如果收到“已过期”的通知，更新对应消息的状态
    if (data.type === 'expired') {
      const target = messages.value.find(m => m.id === data.id);
      if (target) {
        target.type = 'expired'; // 标记为已过期，UI会自动变化
      }
    } else {
      messages.value.push(data);
      scrollToBottom();
    }
  };

  ws.value.onclose = () => {
    alert("连接已断开");
    joined.value = false;
  };
};

const sendMessage = () => {
  if (!inputText.value.trim()) return;
  ws.value.send(JSON.stringify({ content: inputText.value }));
  inputText.value = "";
};

// --- 文件上传逻辑 ---
const uploadFile = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);
  formData.append("room_id", roomId.value);
  formData.append("sender", clientId.value);

  try {
    // 发送 POST 请求给后端
    await fetch("http://localhost:8000/api/upload", {
      method: "POST",
      body: formData
    });
    // 上传成功不需要手动加消息，后端会广播 WebSocket 通知
  } catch (err) {
    alert("上传失败: " + err);
  }
};

// --- 辅助功能 ---
const getDownloadUrl = (path) => {
  return `http://localhost:8000${path}`;
};

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

// --- 生命周期 ---
onMounted(() => {
  // 每秒更新一次“当前时间”，触发倒计时刷新
  timerInterval = setInterval(() => {
    now.value = Date.now() / 1000;
  }, 1000);
});

onUnmounted(() => {
  if (timerInterval) clearInterval(timerInterval);
  if (ws.value) ws.value.close();
});
</script>

<style>
/* 简单样式，保持清爽 */
body { margin: 0; font-family: sans-serif; background: #f0f2f5; }
.container { max-width: 600px; margin: 0 auto; height: 100vh; display: flex; flex-direction: column; background: white; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
.header { padding: 15px; background: #007bff; color: white; display: flex; justify-content: space-between; align-items: center; }
.chat-area { flex: 1; padding: 20px; overflow-y: auto; background: #fafafa; }
.input-area { padding: 15px; border-top: 1px solid #ddd; display: flex; gap: 10px; }
.input-area input[type="text"] { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
.join-box { display: flex; gap: 10px; }
.message-row { display: flex; margin-bottom: 15px; }
.my-msg { justify-content: flex-end; }
.message-bubble { max-width: 70%; padding: 10px; border-radius: 8px; background: #e9ecef; position: relative; }
.my-msg .message-bubble { background: #007bff; color: white; }
.my-msg .message-bubble .timer { color: #e0e0e0; }
.msg-meta { font-size: 12px; margin-bottom: 5px; opacity: 0.7; display: flex; justify-content: space-between; gap: 10px;}
.file-content { display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.2); padding: 5px; border-radius: 4px; }
.download-btn { color: inherit; text-decoration: underline; font-weight: bold; cursor: pointer; }
.system-msg { width: 100%; text-align: center; color: #999; font-size: 12px; }
</style>