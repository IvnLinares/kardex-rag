<script setup lang="ts">
import type { ChatMessage } from '../composables/useChat'

defineProps<{ message: ChatMessage }>()
</script>

<template>
  <div class="message" :class="`message--${message.role}`">
    <span class="message__role">{{ message.role === 'user' ? 'Vos' : 'Copiloto' }}</span>
    <p class="message__content">{{ message.content || '…' }}</p>
  </div>
</template>

<style scoped>
.message {
  max-width: 75%;
  padding: 10px 14px;
  border-radius: 12px;
  text-align: left;
}

.message--user {
  align-self: flex-end;
  background: var(--accent-bg);
  border: 1px solid var(--accent-border);
}

.message--assistant {
  align-self: flex-start;
  background: var(--code-bg);
  border: 1px solid var(--border);
}

.message__role {
  display: block;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: var(--text);
  opacity: 0.7;
  margin-bottom: 4px;
}

.message__content {
  white-space: pre-wrap;
  color: var(--text-h);
}
</style>
