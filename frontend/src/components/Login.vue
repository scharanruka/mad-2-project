<template>
  <div class="container mt-5">
    <div class="card p-4 shadow-sm mx-auto" style="max-width: 400px;">
      <h2>Login</h2>
      <form @submit.prevent="handleLogin">
        <div class="mb-3">
          <label>Email</label>
          <input v-model="email" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label>Password</label>
          <input v-model="password" type="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-primary w-100">Login</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const email = ref('')
const password = ref('')
const router = useRouter()

const handleLogin = async () => {
  const res = await fetch('http://localhost:5000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.value, password: password.value })
  })
  const data = await res.json()
  if (res.ok) {
    localStorage.setItem('token', data.access_token)
    localStorage.setItem('userRole', data.role)
    // Redirect based on role
    router.push(`/${data.role}`)
  } else {
    alert(data.msg)
  }
}
</script>