import { ref } from 'vue'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

const API_URL = (import.meta.env.VITE_API_URL as string | undefined) ?? 'http://localhost:8000'

function parseSseChunk(rawEvent: string): string | null {
  const dataLine = rawEvent.split('\n').find((line) => line.startsWith('data:'))
  if (!dataLine) return null
  try {
    const payload = JSON.parse(dataLine.slice('data:'.length).trim()) as { content?: string }
    return typeof payload.content === 'string' ? payload.content : null
  } catch {
    return null
  }
}

export function useChat() {
  const messages = ref<ChatMessage[]>([])
  const isStreaming = ref(false)
  const error = ref<string | null>(null)

  async function sendMessage(question: string): Promise<void> {
    error.value = null
    messages.value.push({ role: 'user', content: question })
    messages.value.push({ role: 'assistant', content: '' })
    const assistantIndex = messages.value.length - 1
    isStreaming.value = true

    try {
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      })
      if (!response.ok || !response.body) {
        throw new Error(`El servidor respondio con un error (${response.status})`)
      }

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const events = buffer.split('\n\n')
        buffer = events.pop() ?? ''

        for (const rawEvent of events) {
          const content = parseSseChunk(rawEvent)
          if (content) messages.value[assistantIndex].content += content
        }
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Error desconocido al conectar con el backend'
    } finally {
      isStreaming.value = false
    }
  }

  return { messages, isStreaming, error, sendMessage }
}
