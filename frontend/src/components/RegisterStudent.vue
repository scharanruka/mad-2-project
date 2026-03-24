<template>
  <div class="container mt-5">
    <div class="card p-4 shadow-sm mx-auto" style="max-width: 500px;">
      <h3>Student Registration</h3>
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label">Full Name</label>
          <input v-model="form.full_name" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="form.password" type="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-success w-100">Register as Student</button>
        <p class="mt-3 text-center">
          Already have an account? <router-link to="/login">Login</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = ref({ full_name: '', email: '', password: '' })

const handleRegister = async () => {
  const res = await fetch('http://localhost:5000/register/student', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  })
  if (res.ok) {
    alert("Registration successful! Please login.")
    router.push('/login')
  } else {
    const data = await res.json()
    alert(data.msg)
  }
}
</script>