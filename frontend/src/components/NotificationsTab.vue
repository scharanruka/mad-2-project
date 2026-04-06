<script setup>
import BaseDropdown from './base/BaseDropdown.vue'

const handleMarkAsRead = () => console.log('Notifications marked as read!')
const handleDeleteAccount = () => alert('Are you sure?')

const notificationItems = [
  { label: 'Mark all as read', action: handleMarkAsRead, icon: 'bi-check2-all' },
  { label: 'Clear History', action: () => console.log('Cleared'), icon: 'bi-eraser' },
  { divider: true },
  { label: 'Notification Settings', action: () => {}, icon: 'bi-gear' },
]

const actionItems = [
  { label: 'Edit Profile', action: () => {} },
  { label: 'Delete', action: handleDeleteAccount, class: 'text-danger', icon: 'bi-trash' },
]
</script>

<template>
  <div class="d-flex gap-3 p-4">
    <BaseDropdown label="Notifications" variant="btn-outline-primary" :items="notificationItems" />

    <BaseDropdown variant="btn-secondary" :items="actionItems" align-right>
      <template #label> <i class="bi bi-three-dots-vertical"></i> Actions </template>
    </BaseDropdown>
  </div>
</template>
