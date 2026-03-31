<template>
  <div class="layout" :class="{ 'dark': settings.darkMode }">
    <!-- 侧边栏 -->
    <Sidebar
      :is-open="isSidebarOpen"
      :is-mobile="isMobile"
      :joined="joined"
      :current-room-id="roomId"
      v-model:display-name="user.displayName"
      :client-id="user.clientId"
      :recent-rooms="history"
      v-model:settings="settings"
      @toggle="toggleSidebar"
      @join="handleJoin"
      @leave="handleLeave"
      @copy-id="copyToClipboard(user.clientId)"
    />

    <!-- 遮罩层 (移动端侧边栏打开时显示) -->
    <div 
      v-if="isMobile && isSidebarOpen" 
      class="mobile-overlay"
      @click="isSidebarOpen = false"
    ></div>

    <!-- 主内容区 -->
    <main class="main-content">
      <!-- 1. 顶部栏 -->
      <ChatHeader 
        :joined="joined"
        :room-id="roomId"
        :is-mobile="isMobile"
        @toggle-sidebar="toggleSidebar"
        @clear-screen="clearMessages"
      />

      <!-- 2. 消息区域 -->
      <div class="messages-area" ref="scrollContainer">
        <!-- 欢迎页/空状态 -->
        <div v-if="!joined" class="welcome-screen">
          <div class="brand-logo">⚡</div>
          <h1>FlashShare</h1>
          <p class="subtitle">阅后即焚</p>
          <div class="quick-start">
            <input 
              v-model="inputRoomId" 
              placeholder="输入房间号 (如 1001)" 
              @keyup.enter="handleJoin(inputRoomId)"
            />
            <button @click="handleJoin(inputRoomId)">进入房间</button>
          </div>
        </div>

        <div v-else-if="messages.length === 0" class="empty-room-hint">
          <p>🌟 房间已连接，开始聊天吧！</p>
          <small>消息将在 10 分钟后自动销毁</small>
        </div>

        <!-- 消息列表 -->
        <div class="message-list" v-else>
          <ChatMessage 
            v-for="msg in messages" 
            :key="msg.id" 
            :msg="msg" 
            :client-id="user.clientId"
            :display-name="user.displayName"
            :settings="settings"
            :now="now"
          />
        </div>
      </div>

      <!-- 3. 输入区 -->
      <ChatComposer 
        v-if="joined"
        v-model="inputText"
        :disabled="!joined"
        @send="sendMessage"
        @upload-files="handleFileUpload"
      />
    </main>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue';
import Sidebar from './components/Sidebar.vue';
import ChatHeader from './components/ChatHeader.vue';
import ChatMessage from './components/ChatMessage.vue';
import ChatComposer from './components/ChatComposer.vue';

// --- 状态管理 ---
const settings = reactive({
  darkMode: false,
  enableMarkdown: true,
});

const user = reactive({
  clientId: Math.random().toString(36).substring(7),
  displayName: 'User_' + Math.floor(Math.random() * 1000)
});

const history = ref([]); // 历史房间列表
const messages = ref([]);
const joined = ref(false);
const roomId = ref("");
const inputRoomId = ref("");
const inputText = ref("");
const isSidebarOpen = ref(true);
const isMobile = ref(window.innerWidth < 768);
const now = ref(Date.now() / 1000);

let ws = null;
let timer = null;
const scrollContainer = ref(null);

// --- 初始化与持久化 ---
onMounted(() => {
  // 1. 读取本地存储
  const savedSettings = localStorage.getItem('fs_settings');
  if (savedSettings) Object.assign(settings, JSON.parse(savedSettings));
  
  const savedUser = localStorage.getItem('fs_user');
  if (savedUser) Object.assign(user, JSON.parse(savedUser));
  
  const savedHistory = localStorage.getItem('fs_history');
  if (savedHistory) history.value = JSON.parse(savedHistory);

  // 2. 路由检测 (/room/1001)
  const path = window.location.pathname;
  const match = path.match(/\/room\/(\w+)/);
  if (match) {
    handleJoin(match[1]);
  }

  // 3. 响应式监听
  window.addEventListener('resize', handleResize);
  handleResize();
  
  // 4. 时钟
  timer = setInterval(() => { now.value = Date.now() / 1000 }, 1000);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  clearInterval(timer);
  if (ws) ws.close();
});

// 监听变动并保存
watch(settings, (val) => localStorage.setItem('fs_settings', JSON.stringify(val)));
watch(user, (val) => localStorage.setItem('fs_user', JSON.stringify(val)));
watch(history, (val) => localStorage.setItem('fs_history', JSON.stringify(val)));

// --- 交互逻辑 ---
const handleResize = () => {
  isMobile.value = window.innerWidth < 768;
  if (isMobile.value) isSidebarOpen.value = false;
};

const toggleSidebar = () => isSidebarOpen.value = !isSidebarOpen.value;

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text);
  // 可以加个简单的 Toast 提示
};

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight;
    }
  });
};

const clearMessages = () => messages.value = [];

// --- 配置 ---
// Cloudflare Tunnel 后端地址（外部访问用）
const BACKEND_URL = 'https://limits-dressed-heavily-belt.trycloudflare.com';

// --- 核心业务逻辑 ---

const handleJoin = (id) => {
  const targetId = id || inputRoomId.value;
  if (!targetId) return;
  
  if (ws) ws.close();
  
  roomId.value = targetId;
  inputRoomId.value = ""; // 清空输入框
  
  // 更新历史记录 (去重并置顶)
  history.value = [targetId, ...history.value.filter(h => h !== targetId)].slice(0, 10);
  
  // 更新 URL (HTML5 History API)
  window.history.pushState({}, '', `/room/${targetId}`);

  // WebSocket 连接
  // 外部访问时直连后端隧道 URL，绕过 Vite proxy
  const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
  const wsUrl = isLocal
    ? `ws://localhost:8000/ws/${targetId}/${user.clientId}`
    : `wss://limits-dressed-heavily-belt.trycloudflare.com/ws/${targetId}/${user.clientId}`;

  ws = new WebSocket(wsUrl);
  
  ws.onopen = () => {
    joined.value = true;
    messages.value = []; // 清屏
    if (isMobile.value) isSidebarOpen.value = false; // 移动端进入房间后自动收起侧边栏
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'expired') {
      const existing = messages.value.find(m => m.id === data.id);
      if (existing) existing.type = 'expired';
    } else {
      messages.value.push(data);
      scrollToBottom();
    }
  };
  
  ws.onclose = () => {
    joined.value = false;
  };
};

const handleLeave = () => {
  if (ws) ws.close();
  joined.value = false;
  roomId.value = "";
  window.history.pushState({}, '', '/');
};

const sendMessage = (text) => {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ content: text }));
    scrollToBottom();
  }
};

const handleFileUpload = async (files) => {
  if (!roomId.value) return;
  
  for (const file of files) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("room_id", roomId.value);
    formData.append("sender", user.clientId);
    
    // 乐观 UI：先推一个假消息占位 (可选，这里略过，直接等后端广播)
    try {
      const isLocal = ['localhost', '127.0.0.1'].includes(window.location.hostname);
      const uploadUrl = isLocal
        ? '/api/upload'
        : 'https://limits-dressed-heavily-belt.trycloudflare.com/api/upload';
      await fetch(uploadUrl, { method: "POST", body: formData });
    } catch (e) {
      console.error("Upload failed", e);
      alert("上传失败: " + file.name);
    }
  }
};
</script>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  background-color: var(--c-bg-app);
  color: var(--c-text-main);
  position: relative;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; /* 防止 Flex 子项溢出 */
  position: relative;
}

.messages-area {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
}

/* 遮罩层 */
.mobile-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 15;
}

/* 欢迎页 */
.welcome-screen {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--c-text-muted);
}
.brand-logo { font-size: 4rem; margin-bottom: 1rem; }
.welcome-screen h1 { margin: 0; color: var(--c-text-main); }
.subtitle { margin-top: 0.5rem; margin-bottom: 2rem; }

.quick-start {
  display: flex;
  gap: 8px;
  background: var(--c-bg-panel);
  padding: 8px;
  border-radius: 12px;
  box-shadow: var(--shadow-md);
  border: 1px solid var(--c-border);
  flex-wrap: wrap;
  justify-content: center;
  max-width: 90vw;
}
.quick-start input {
  border: none;
  background: transparent;
  outline: none;
  padding: 8px;
  font-size: 1rem;
  min-width: 0;
  flex: 1 1 150px;
  color: var(--c-text-main);
}
.quick-start button {
  background: var(--c-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  flex-shrink: 0;
}

.empty-room-hint {
  text-align: center;
  color: var(--c-text-light);
  margin-top: 20vh;
}
</style>