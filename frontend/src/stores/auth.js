import { defineStore } from 'pinia'
import { ref } from 'vue'
import router from '@/router'

export const useAuthStore = defineStore('auth', () => {
  let token = ref(localStorage.getItem('token') || '')
  let role = ref(localStorage.getItem('role') || '')

  function setAuth(access_token, user_role) {
    token.value = access_token
    role.value = user_role

    localStorage.setItem('token', token.value)
    localStorage.setItem('role', role.value)
    router.push(`/${role.value}`)
  }

  function logout() {
    token.value = ''
    role.value = ''
    localStorage.clear()
    router.push(`/`)
  }

  return { token, role, setAuth, logout }
})
