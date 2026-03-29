<script setup>
import { useAuthStore } from './stores/auth'

const store = useAuthStore()
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
    <div class="container">
      <a class="navbar-brand" href="#">Placement Portal</a>
      <button v-if="store.token" class="btn btn-outline-light btn-sm" @click="store.logout">
        Logout
      </button>
      <button
        v-if="!store.token"
        class="btn btn-outline-light btn-sm"
        @click="store.router.push('/login')"
      >
        Login
      </button>
    </div>
  </nav>
  <router-view />
</template>
