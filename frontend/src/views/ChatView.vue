<script setup lang="ts">
import { nextTick, onMounted, ref, useTemplateRef, watch } from 'vue'
import gsap from 'gsap'
import ChatMessageItem from '../components/ChatMessageItem.vue'
import { useChat } from '../composables/useChat'

const { messages, isStreaming, error, sendMessage } = useChat()
const input = ref('')

const cardRef = useTemplateRef<HTMLElement>('card')
const messagesRef = useTemplateRef<HTMLElement>('messagesList')

onMounted(() => {
  gsap.from(cardRef.value, {
    opacity: 0,
    y: 24,
    scale: 0.97,
    duration: 0.6,
    ease: 'power3.out',
  })
})

watch(
  () => messages.value.length,
  async () => {
    await nextTick()
    const el = messagesRef.value
    const last = el?.lastElementChild
    if (last) {
      gsap.from(last, { opacity: 0, y: 14, duration: 0.35, ease: 'power2.out' })
    }
    el?.scrollTo({ top: el.scrollHeight, behavior: 'smooth' })
  },
)

// Sigue el scroll mientras llegan tokens en streaming (el largo de `messages`
// no cambia durante el streaming, solo el contenido del ultimo mensaje).
watch(
  () => messages.value.reduce((total, m) => total + m.content.length, 0),
  async () => {
    await nextTick()
    const el = messagesRef.value
    if (el) el.scrollTop = el.scrollHeight
  },
)

function handleSubmit(): void {
  const question = input.value.trim()
  if (!question || isStreaming.value) return
  input.value = ''
  void sendMessage(question)
}
</script>

<template>
  <main class="chat">
    <section ref="card" class="chat__card">
      <header class="chat__header">
        <h1>Copiloto de Kardex</h1>
        <p>Preguntá en lenguaje natural sobre el estado del inventario</p>
      </header>

      <div ref="messagesList" class="chat__messages">
        <p v-if="messages.length === 0" class="chat__empty">
          Probá preguntando, por ejemplo: "¿Qué productos están agotados?"
        </p>
        <ChatMessageItem v-for="(message, index) in messages" :key="index" :message="message" />
      </div>

      <p v-if="error" class="chat__error">{{ error }}</p>

      <form class="chat__form" @submit.prevent="handleSubmit">
        <input
          v-model="input"
          type="text"
          placeholder="Escribí tu pregunta..."
          :disabled="isStreaming"
        />
        <button type="submit" :disabled="isStreaming || !input.trim()">
          {{ isStreaming ? 'Pensando…' : 'Enviar' }}
        </button>
      </form>
    </section>
  </main>
</template>

<style scoped>
.chat {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100svh;
  padding: 24px 16px;
}

.chat__card {
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 720px;
  height: min(760px, calc(100svh - 48px));
  padding: 24px;
  border-radius: 20px;
  background: var(--glass-bg);
  border: 1px solid var(--glass-border);
  box-shadow:
    0 8px 32px var(--glass-shadow),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
  backdrop-filter: blur(18px) saturate(160%);
  -webkit-backdrop-filter: blur(18px) saturate(160%);
}

.chat__header {
  text-align: left;
  margin-bottom: 16px;
}

.chat__header h1 {
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 0 0 4px;
  color: var(--text-h);
}

.chat__header p {
  color: var(--text);
  opacity: 0.8;
}

.chat__messages {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px 4px;
}

.chat__empty {
  color: var(--text);
  opacity: 0.6;
  text-align: left;
}

.chat__error {
  color: #dc2626;
  text-align: left;
  margin: 8px 0;
}

.chat__form {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--glass-border);
}

.chat__form input {
  flex: 1;
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg-strong);
  color: var(--text-h);
  font: inherit;
}

.chat__form input:focus {
  outline: 2px solid var(--accent-border);
  outline-offset: 1px;
}

.chat__form button {
  padding: 10px 20px;
  border-radius: 999px;
  border: 1px solid var(--glass-border);
  background: var(--glass-bg-strong);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  color: var(--text-h);
  font: inherit;
  font-weight: 600;
  cursor: pointer;
  transition:
    transform 0.15s ease,
    box-shadow 0.15s ease,
    background 0.15s ease,
    color 0.15s ease;
}

.chat__form button:hover:not(:disabled) {
  transform: translateY(-1px);
  background: var(--accent);
  color: var(--bg);
  box-shadow: 0 4px 14px var(--glass-shadow);
}

.chat__form button:active:not(:disabled) {
  transform: translateY(0);
}

.chat__form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
