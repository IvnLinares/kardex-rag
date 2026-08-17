<script setup lang="ts">
import { ref } from 'vue'
import ChatMessageItem from '../components/ChatMessageItem.vue'
import { useChat } from '../composables/useChat'

const { messages, isStreaming, error, sendMessage } = useChat()
const input = ref('')

function handleSubmit(): void {
  const question = input.value.trim()
  if (!question || isStreaming.value) return
  input.value = ''
  void sendMessage(question)
}
</script>

<template>
  <main class="chat">
    <header class="chat__header">
      <h1>Copiloto de Kardex</h1>
      <p>Preguntá en lenguaje natural sobre el estado del inventario</p>
    </header>

    <div class="chat__messages">
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
  </main>
</template>

<style scoped>
.chat {
  display: flex;
  flex-direction: column;
  height: 100svh;
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 20px;
  box-sizing: border-box;
}

.chat__header {
  text-align: left;
  margin-bottom: 16px;
}

.chat__header h1 {
  font-size: 28px;
  margin: 0 0 4px;
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
  padding: 12px 0;
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
  border-top: 1px solid var(--border);
}

.chat__form input {
  flex: 1;
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--text-h);
  font: inherit;
}

.chat__form button {
  padding: 10px 18px;
  border-radius: 8px;
  border: none;
  background: var(--accent);
  color: #fff;
  font: inherit;
  cursor: pointer;
}

.chat__form button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
