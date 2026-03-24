<template>
  <div class="container mt-5">
    <div class="card p-4 shadow-sm mx-auto" style="max-width: 500px">
      <h3>Company Registration</h3>
      <form @submit.prevent="handleRegister">
        <div class="mb-3">
          <label class="form-label">Company Name</label>
          <input v-model="form.name" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Industry</label>
          <input
            v-model="form.industry"
            type="text"
            class="form-control"
            placeholder="e.g. IT, Finance"
            required
          />
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="text" class="form-control" required />
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input v-model="form.password" type="password" class="form-control" required />
        </div>
        <button type="submit" class="btn btn-primary w-100">Submit for Approval</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const form = ref({ name: '', industry: '', email: '', password: '' })

const handleRegister = async () => {
  const res = await fetch('http://localhost:5000/register/company', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value),
  })
  const data = await res.json()
  alert(data.msg)
  if (res.ok) router.push('/login')
}
</script>
