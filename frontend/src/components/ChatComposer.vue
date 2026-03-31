<template>
  <footer 
    class="composer" 
    :class="{ 'dragging': isDragging }"
    @dragover.prevent="isDragging = true" 
    @dragleave.prevent="isDragging = false"
    @drop.prevent="onDrop"
  >
    <div class="input-container">
      <input ref="fileInput" type="file" multiple style="display:none" @change="onPickFile" />
      
      <button class="btn-tool" @click="fileInput?.click()" title="上传文件 (支持拖拽)">
        📎
      </button>
      
      <textarea
        ref="textarea"
        :value="modelValue"
        class="input-area"
        placeholder="输入消息... (Ctrl+Enter 发送)"
        :disabled="disabled"
        rows="1"
        @input="onInput"
        @keydown.enter.exact.prevent="emitSend"
        @keydown.enter.ctrl.prevent="emitSend"
      ></textarea>
      
      <button class="btn-send" :disabled="disabled || !modelValue.trim()" @click="emitSend">
        ➤
      </button>
    </div>

    <!-- 拖拽遮罩 -->
    <div v-if="isDragging" class="drop-mask">
      <div class="drop-content">
        <span class="icon">📂</span>
        <span>松开鼠标以上传文件</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, nextTick } from 'vue';

const props = defineProps(['modelValue', 'disabled']);
const emit = defineEmits(['update:modelValue', 'send', 'uploadFiles']);

const isDragging = ref(false);
const textarea = ref(null);
const fileInput = ref(null);

const onInput = (e) => {
  emit('update:modelValue', e.target.value);
  adjustHeight();
};

const adjustHeight = () => {
  const el = textarea.value;
  if (!el) return;
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 150) + 'px';
};

const emitSend = () => {
  const text = props.modelValue.trim();
  if (!text || props.disabled) return;
  emit('send', text);
  emit('update:modelValue', '');
  nextTick(adjustHeight);
};

const onPickFile = (e) => {
  const files = Array.from(e.target.files || []);
  if (files.length) emit('uploadFiles', files);
  e.target.value = '';
};

const onDrop = (e) => {
  isDragging.value = false;
  const files = Array.from(e.dataTransfer?.files || []);
  if (files.length) emit('uploadFiles', files);
};
</script>

<style scoped>
.composer {
  padding: 16px 20px;
  background: var(--c-bg-panel);
  border-top: 1px solid var(--c-border);
  position: relative;
}

.input-container {
  display: flex;
  align-items: flex-end;
  gap: 12px;
  background: var(--c-bg-app);
  border: 1px solid var(--c-border);
  border-radius: 16px;
  padding: 8px 12px;
  transition: border-color .2s;
}
.input-container:focus-within { border-color: var(--c-primary); box-shadow: 0 0 0 2px rgba(14, 165, 233, 0.1); }

.input-area {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  resize: none;
  max-height: 150px;
  padding: 8px 0;
  font-family: inherit;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--c-text-main);
}

.btn-tool {
  background: transparent; border: none; font-size: 1.2rem; cursor: pointer; padding: 6px; border-radius: 8px; color: var(--c-text-muted); transition: .2s; flex-shrink: 0;
}
.btn-tool:hover { background: var(--c-bg-panel); color: var(--c-text-main); }

.btn-send {
  background: var(--c-primary); color: white; border: none; min-width: 36px; height: 36px; border-radius: 10px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: .2s; flex-shrink: 0;
}
.btn-send:hover { background: var(--c-primary-hover); }
.btn-send:disabled { background: var(--c-text-light); cursor: not-allowed; }

/* Mobile: ensure buttons don't shrink */
@media (max-width: 480px) {
  .btn-tool, .btn-send { min-width: 36px; height: 36px; }
  .composer { padding: 12px 10px; }
}

.drop-mask {
  position: absolute; inset: 0; background: rgba(255,255,255,0.9); z-index: 10; display: flex; align-items: center; justify-content: center; backdrop-filter: blur(2px);
}
.drop-content { display: flex; flex-direction: column; align-items: center; font-weight: bold; color: var(--c-primary); }
.drop-content .icon { font-size: 2rem; margin-bottom: 8px; }

/* Dark mode adjustment */
:global(.dark) .drop-mask { background: rgba(15, 23, 42, 0.9); }
</style>