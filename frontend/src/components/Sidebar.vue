<template>
  <aside 
    class="sidebar" 
    :class="{ 
      'collapsed': !isOpen && !isMobile, 
      'mobile-open': isMobile && isOpen 
    }"
  >
    <!-- A. 用户卡片 -->
    <div class="header">
      <div class="user-card">
        <div class="avatar" :style="{ backgroundColor: userColor }">
          {{ displayName.slice(0, 2).toUpperCase() }}
          <span class="status-dot" :class="{ 'connected': joined }"></span>
        </div>
        <div class="info" v-if="isOpen || isMobile">
          <input 
            :value="displayName"
            @input="$emit('update:displayName', $event.target.value)"
            class="input-name"
            title="点击修改昵称"
          />
          <div class="user-id" @click="$emit('copyId')" title="点击复制 ID">
            ID: {{ clientId.slice(0, 6) }} ❐
          </div>
        </div>
      </div>
      
      <!-- 折叠按钮 (仅桌面端) -->
      <button v-if="!isMobile" class="toggle-btn" @click="$emit('toggle')">
        <span class="icon">{{ isOpen ? '◀' : '▶' }}</span>
      </button>
    </div>

    <!-- B. 内容区 -->
    <div class="body" v-if="isOpen || isMobile">
      <!-- 搜索/过滤 -->
      <div class="search-box">
        <input v-model="searchQuery" placeholder="搜索最近的房间..." />
      </div>

      <!-- 历史列表 -->
      <div class="nav-section">
        <label>最近访问</label>
        <div class="room-list">
          <div v-if="filteredRooms.length === 0" class="empty-text">无记录</div>
          <div 
            v-for="r in filteredRooms" 
            :key="r" 
            class="room-item"
            :class="{ 'active': currentRoomId === r && joined }"
            @click="$emit('join', r)"
          >
            <span class="hash">#</span>
            <span class="name">{{ r }}</span>
            <span v-if="currentRoomId === r && joined" class="tag-live">LIVE</span>
          </div>
        </div>
      </div>
      
      <!-- 快捷操作 -->
      <div class="nav-section mt-auto">
        <button v-if="joined" class="btn-leave" @click="$emit('leave')">
          退出当前房间
        </button>
      </div>
    </div>

    <!-- C. 底部设置 -->
    <div class="footer" v-if="isOpen || isMobile">
      <div class="setting-item">
        <span>🌙 深色模式</span>
        <label class="switch">
          <input type="checkbox" :checked="settings.darkMode" @change="updateSetting('darkMode', $event.target.checked)">
          <span class="slider"></span>
        </label>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  isOpen: Boolean,
  isMobile: Boolean,
  joined: Boolean,
  displayName: String,
  clientId: String,
  recentRooms: Array,
  currentRoomId: String,
  settings: Object
});

const emit = defineEmits(['toggle', 'update:displayName', 'copyId', 'join', 'leave', 'update:settings']);

const searchQuery = ref("");

// 计算属性：生成用户头像颜色
const userColor = computed(() => {
  const colors = ['#0ea5e9', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444'];
  let hash = 0;
  if (props.clientId) {
    for (let i = 0; i < props.clientId.length; i++) hash += props.clientId.charCodeAt(i);
  }
  return colors[hash % colors.length];
});

// 计算属性：过滤房间列表
const filteredRooms = computed(() => {
  if (!searchQuery.value) return props.recentRooms;
  return props.recentRooms.filter(r => r.includes(searchQuery.value));
});

const updateSetting = (key, value) => {
  emit('update:settings', { ...props.settings, [key]: value });
};
</script>

<style scoped>
.sidebar {
  width: 280px;
  background: var(--c-bg-panel);
  border-right: 1px solid var(--c-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: all 0.3s ease;
  z-index: 20;
}

/* Mobile (< 768px): sidebar slides in as overlay */
@media (max-width: 767px) {
  .sidebar {
    width: 100%;
    max-width: 300px;
    position: absolute;
    height: 100%;
    box-shadow: var(--shadow-md);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
  }
  .sidebar.mobile-open {
    transform: translateX(0);
  }
  .sidebar.collapsed {
    width: 100%;
    max-width: 300px;
    transform: translateX(-100%);
  }
}

/* Tablet (768px - 1024px): narrower sidebar */
@media (min-width: 768px) and (max-width: 1024px) {
  .sidebar {
    width: 220px;
  }
  .sidebar.collapsed {
    width: 60px;
  }
}

/* Header */
.header { padding: 16px; border-bottom: 1px solid var(--c-border); position: relative; display: flex; align-items: center; height: 72px; }
.user-card { display: flex; align-items: center; gap: 12px; overflow: hidden; width: 100%; min-width: 0; }
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  position: relative;
  flex-shrink: 0;
  font-size: 0.85rem; /* prevent overflow on small screens */
}
.status-dot { width: 10px; height: 10px; background: var(--c-text-muted); border: 2px solid var(--c-bg-panel); border-radius: 50%; position: absolute; bottom: -2px; right: -2px; transition: .3s; }
.status-dot.connected { background: #22c55e; }

.info { display: flex; flex-direction: column; min-width: 0; overflow: hidden; }
.input-name { border: none; background: transparent; font-weight: 600; color: var(--c-text-main); width: 100%; padding: 0; outline: none; font-size: 1rem; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.input-name:focus { border-bottom: 1px solid var(--c-primary); }
.user-id { font-size: 0.75rem; color: var(--c-text-muted); cursor: pointer; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.toggle-btn { position: absolute; right: -12px; top: 50%; transform: translateY(-50%); width: 24px; height: 24px; border-radius: 50%; border: 1px solid var(--c-border); background: var(--c-bg-panel); color: var(--c-text-muted); display: flex; align-items: center; justify-content: center; cursor: pointer; z-index: 10; font-size: 0.6rem; }
.toggle-btn:hover { color: var(--c-primary); border-color: var(--c-primary); }

/* Body */
.body { flex: 1; padding: 16px; display: flex; flex-direction: column; overflow-y: auto; gap: 20px; }

.search-box input { width: 100%; padding: 8px 12px; background: var(--c-bg-hover); border: 1px solid transparent; border-radius: 8px; color: var(--c-text-main); outline: none; transition: .2s; }
.search-box input:focus { border-color: var(--c-primary); background: var(--c-bg-panel); }

.nav-section label { font-size: 0.75rem; font-weight: 700; color: var(--c-text-muted); text-transform: uppercase; margin-bottom: 8px; display: block; }
.room-item { padding: 10px; border-radius: 8px; color: var(--c-text-muted); display: flex; align-items: center; gap: 10px; cursor: pointer; transition: .2s; overflow: hidden; }
.room-item:hover { background: var(--c-bg-hover); color: var(--c-text-main); }
.room-item.active { background: var(--c-bubble-self); color: var(--c-primary-hover); font-weight: 500; }
.hash { opacity: 0.5; font-weight: bold; flex-shrink: 0; }
.name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; min-width: 0; }
.tag-live { flex-shrink: 0; font-size: 0.6rem; background: var(--c-primary); color: white; padding: 2px 6px; border-radius: 4px; }
.empty-text { font-size: 0.8rem; color: var(--c-text-light); font-style: italic; padding: 8px; }

.mt-auto { margin-top: auto; }
.btn-leave { width: 100%; padding: 10px; background: var(--c-bg-hover); color: var(--c-danger); border: none; border-radius: 8px; cursor: pointer; font-weight: 600; transition: .2s; }
.btn-leave:hover { background: #fee2e2; }

/* Footer */
.footer { padding: 16px; border-top: 1px solid var(--c-border); }
.setting-item { display: flex; justify-content: space-between; align-items: center; font-size: 0.9rem; color: var(--c-text-main); }
.switch { position: relative; width: 36px; height: 20px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; inset: 0; background-color: var(--c-text-light); border-radius: 20px; transition: .4s; }
.slider:before { position: absolute; content: ""; height: 16px; width: 16px; left: 2px; bottom: 2px; background-color: white; border-radius: 50%; transition: .4s; }
input:checked + .slider { background-color: var(--c-primary); }
input:checked + .slider:before { transform: translateX(16px); }
</style>