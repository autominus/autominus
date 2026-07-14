import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('ft_token') || '')
  const user  = ref(JSON.parse(localStorage.getItem('ft_user') || 'null'))
  const isLoggedIn = computed(() => !!token.value)

  function login(username) {
    const u = { id: 1, username: username || '小明同学' }
    token.value = 'mock-' + Date.now()
    user.value  = u
    localStorage.setItem('ft_token', token.value)
    localStorage.setItem('ft_user',  JSON.stringify(u))
  }
  function logout() {
    token.value = ''; user.value = null
    localStorage.removeItem('ft_token')
    localStorage.removeItem('ft_user')
  }
  return { token, user, isLoggedIn, login, logout }
})
