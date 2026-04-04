<script setup>
import { useAuthStore } from './stores/auth'
import router from '@/router'

const store = useAuthStore()
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
      <a class="navbar-brand" href="/">Placement Portal</a>
      <div>
        <button
          v-if="store.role"
          @click="router.push(`/${store.role}`)"
          class="btn btn-outline-light btn-sm me-3"
        >
          Dashboard
        </button>
        <button v-if="store.token" class="btn btn-outline-light btn-sm me-3" @click="store.logout">
          Logout
        </button>
        <button
          v-if="!store.token"
          class="btn btn-outline-light btn-sm me-3"
          @click="router.push('/login')"
        >
          Login
        </button>
      </div>
    </div>
  </nav>
  <router-view />
</template>
