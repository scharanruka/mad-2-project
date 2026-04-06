<script setup>
import { useAuthStore } from './stores/auth'
import router from '@/router'
import { useNotificationStore } from './stores/notificationStore'

const store = useAuthStore()
const notifStore = useNotificationStore()
console.log(notifStore.notifications.length)
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">PlacementPortal</router-link>

      <div class="d-flex align-items-center">
        <div class="dropdown me-3">
          <button
            class="btn btn-outline-light position-relative"
            id="notifDrop"
            data-bs-toggle="dropdown"
          >
            <i class="bi bi-bell"></i>
            <span
              v-if="notifStore.notifications.length"
              class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
            >
              {{ notifStore.notifications.length }}
            </span>
          </button>
          <ul
            class="dropdown-menu dropdown-menu-end shadow"
            aria-labelledby="notifDrop"
            style="width: 300px"
          >
            <li class="dropdown-header">Notifications</li>
            <li v-for="n in notifStore.notifications" :key="n.id">
              <a class="dropdown-item small border-bottom" href="#">
                <strong>{{ n.type.toUpperCase() }}:</strong> {{ n.message }}
                <div class="text-muted" style="font-size: 0.75rem">{{ n.timestamp }}</div>
              </a>
            </li>
            <li
              v-if="!notifStore.notifications.length"
              class="dropdown-item text-center text-muted"
            >
              No new alerts
            </li>
            <li><hr class="dropdown-divider" /></li>
            <li>
              <button
                @click="notifStore.clearAll"
                class="dropdown-item text-center text-primary small"
              >
                Clear All
              </button>
            </li>
          </ul>
        </div>

        <router-link to="/profile" class="btn btn-outline-info btn-sm me-2"
          >Edit Profile</router-link
        >
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

<!-- <nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
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
  </nav> -->
