<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
      <a class="navbar-brand" href="#">Placement Portal</a>
      <button v-if="isLoggedIn" class="btn btn-outline-light btn-sm" @click="logout">Logout</button>
    </div>
  </nav>
  <router-view />
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const isLoggedIn = computed(() => !!localStorage.getItem('token'))

const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>
