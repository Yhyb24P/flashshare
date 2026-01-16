<template>
  <div 
    class="message-row" 
    :class="{ 'self': msg.sender === clientId, 'system': msg.type === 'expired' }"
  >
    <!-- 过期系统消息 -->
    <div v-if="msg.type === 'expired'" class="system-badge">
      <span>💨 此消息已随风而逝</span>
    </div>

    <!-- 正常消息 -->
    <template v-else>
      <div class="avatar">
        {{ msg.sender === clientId ? '我' : msg.sender.slice(0, 2).toUpperCase() }}
      </div>
      
      <div class="content-wrapper">
        <div class="meta">
          <span class="name">{{ msg.sender === clientId ? displayName : msg.sender.slice(0,6) }}</span>
          <span class="time">{{ formatTimeLeft(msg.expires_at) }}</span>
        </div>

        <div class="bubble">
          <!-- 文本 -->
          <div 
            v-if="msg.type === 'text'" 
            class="markdown-body" 
            v-html="renderContent(msg.content)"
          ></div>
          
          <!-- 文件 -->
          <div v-if="msg.type === 'file'" class="file-card">
            <div class="file-icon">📄</div>
            <div class="file-info">
              <div class="file-name" :title="msg.filename">{{ msg.filename }}</div>
              <div class="file-size">{{ formatSize(msg.file_size) }}</div>
            </div>
            <a :href="msg.download_url" download class="btn-dl">下载</a>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const props = defineProps(['msg', 'clientId', 'displayName', 'settings', 'now']);

const formatTimeLeft = (ts) => {
  const diff = ts - props.now;
  if (diff <= 0) return '即将销毁';
  const m = Math.floor(diff / 60);
  const s = Math.floor(diff % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
};

const formatSize = (b) => {
  if (!b) return '0B';
  const i = Math.floor(Math.log(b) / Math.log(1024));
  return (b / Math.pow(1024, i)).toFixed(1) + ['B', 'KB', 'MB', 'GB'][i];
};

const renderContent = (text) => {
  if (!props.settings?.enableMarkdown) return text;
  try {
    return DOMPurify.sanitize(marked.parse(text));
  } catch {
    return text;
  }
};
</script>

<style scoped>
.message-row { display: flex; gap: 12px; max-width: 85%; }
.message-row.self { align-self: flex-end; flex-direction: row-reverse; }
.message-row.system { align-self: center; width: 100%; justify-content: center; margin: 10px 0; }

.system-badge { background: var(--c-bg-hover); color: var(--c-text-light); padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; }

.avatar { width: 36px; height: 36px; border-radius: 8px; background: var(--c-bg-hover); color: var(--c-text-muted); display: flex; align-items: center; justify-content: center; font-size: 0.8rem; font-weight: bold; flex-shrink: 0; }
.self .avatar { background: var(--c-primary); color: white; }

.content-wrapper { display: flex; flex-direction: column; min-width: 0; }

.meta { display: flex; gap: 8px; font-size: 0.75rem; color: var(--c-text-light); margin-bottom: 4px; }
.self .meta { flex-direction: row-reverse; }

.bubble { background: var(--c-bubble-other); padding: 10px 14px; border-radius: var(--radius-lg); border-top-left-radius: 2px; box-shadow: var(--shadow-sm); color: var(--c-text-main); position: relative; word-wrap: break-word; }
.self .bubble { background: var(--c-bubble-self); border-top-left-radius: var(--radius-lg); border-top-right-radius: 2px; }

/* Markdown reset */
.markdown-body { background: transparent !important; font-size: 0.95rem; }
.markdown-body :deep(p) { margin: 0 0 0.5em; }
.markdown-body :deep(p:last-child) { margin: 0; }
.markdown-body :deep(pre) { background: rgba(0,0,0,0.05); padding: 8px; border-radius: 6px; }

/* File Card */
.file-card { display: flex; align-items: center; gap: 10px; background: rgba(255,255,255,0.5); padding: 8px; border-radius: 8px; border: 1px solid rgba(0,0,0,0.05); min-width: 200px; }
.file-icon { font-size: 1.5rem; }
.file-info { flex: 1; overflow: hidden; }
.file-name { font-weight: 600; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.file-size { font-size: 0.75rem; opacity: 0.7; }
.btn-dl { font-size: 0.8rem; color: var(--c-primary); text-decoration: none; padding: 4px 8px; background: rgba(14, 165, 233, 0.1); border-radius: 4px; }
</style>