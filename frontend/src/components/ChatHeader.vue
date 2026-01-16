<template>
  <header class="chat-header">
    <div class="left">
      <button v-if="isMobile" class="btn-icon" @click="$emit('toggleSidebar')">☰</button>
      <div class="meta">
        <h2 class="title">{{ joined ? `房间 #${roomId}` : '未连接' }}</h2>
        <div class="status" :class="{ 'online': joined }">
          <span class="dot"></span>
          {{ joined ? '实时连接中' : '离线' }}
        </div>
      </div>
    </div>
    <div class="right">
      <button class="btn-icon" v-if="joined" @click="$emit('clearScreen')" title="清空屏幕">
        🧹
      </button>
    </div>
  </header>
</template>

<script setup>
defineProps(['isMobile', 'joined', 'roomId']);
defineEmits(['toggleSidebar', 'clearScreen']);
</script>

<style scoped>
.chat-header {
  height: 60px;
  background: var(--c-bg-panel);
  border-bottom: 1px solid var(--c-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  flex-shrink: 0;
}

.left { display: flex; align-items: center; gap: 12px; }
.title { font-size: 1.1rem; margin: 0; font-weight: 600; color: var(--c-text-main); }
.status { display: flex; align-items: center; gap: 6px; font-size: 0.75rem; color: var(--c-text-light); }
.status .dot { width: 6px; height: 6px; background: var(--c-text-light); border-radius: 50%; }
.status.online .dot { background: #22c55e; }
.status.online { color: #22c55e; }

.btn-icon {
  width: 36px; height: 36px;
  border: 1px solid var(--c-border);
  background: transparent;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: var(--c-text-muted);
  transition: .2s;
}
.btn-icon:hover { background: var(--c-bg-hover); color: var(--c-text-main); }
</style>