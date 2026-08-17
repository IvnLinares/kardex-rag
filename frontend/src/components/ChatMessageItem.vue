<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessage } from '../composables/useChat'

const props = defineProps<{ message: ChatMessage }>()

interface Segment {
  text: string
  highlighted: boolean
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const segments = computed<Segment[]>(() => {
  const { content, sources } = props.message
  const names = [...new Set(sources.map((s) => s.nombre).filter(Boolean))].sort(
    (a, b) => b.length - a.length,
  )
  if (!content || names.length === 0) {
    return [{ text: content, highlighted: false }]
  }

  const pattern = new RegExp(`(${names.map(escapeRegExp).join('|')})`, 'gi')
  return content
    .split(pattern)
    .filter((part) => part !== '')
    .map((part) => ({
      text: part,
      highlighted: names.some((name) => name.toLowerCase() === part.toLowerCase()),
    }))
})
</script>

<template>
  <div class="message" :class="`message--${message.role}`">
    <span class="message__role">{{ message.role === 'user' ? 'Vos' : 'Copiloto' }}</span>
    <p class="message__content">
      <template v-if="message.content">
        <template v-for="(segment, index) in segments" :key="index">
          <mark v-if="segment.highlighted">{{ segment.text }}</mark>
          <template v-else>{{ segment.text }}</template>
        </template>
      </template>
      <span v-else>…</span>
    </p>
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

.message__content mark {
  background: var(--accent-border);
  color: inherit;
  border-radius: 3px;
  padding: 0 2px;
}
</style>
