import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([
    {
      id: 1, role: 'assistant',
      content: '您好！我是 FogTraffic AI 助手 🤖\n\n我可以帮您进行交通目标智能检测分析。您可以：\n- 📷 上传图片进行单图检测\n- 📦 上传ZIP包进行批量检测\n- 💬 用自然语言描述您的需求',
      time: '09:00'
    }
  ])
  const isTyping = ref(false)

  function addMessage(msg) {
    messages.value.push({ id: Date.now(), time: new Date().toLocaleTimeString('zh-CN',{hour:'2-digit',minute:'2-digit'}), ...msg })
  }
  function clear() {
    messages.value = [messages.value[0]]
  }
  return { messages, isTyping, addMessage, clear }
})
