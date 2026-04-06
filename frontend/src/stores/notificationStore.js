import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notifications', () => {
  let notifications = ref([
    { id: '001', message: 'Test 001', type: 'info', timestamp: new Date().toLocaleTimeString() },
  ])

  function addNotification(message, type = 'info') {
    notifications.value.unshift({
      id: Date.now(),
      message,
      type,
      timestamp: new Date().toLocaleTimeString(),
    })
  }
  function clearAll() {
    notifications.value = []
  }

  return { addNotification, clearAll, notifications }
})
