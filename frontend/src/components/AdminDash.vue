<template>
  <div class="container mt-4">
    <h2 class="mb-4">Admin Dashboard</h2>

    <div class="row mb-4">
      <div class="col-md-3" v-for="(val, key) in stats" :key="key">
        <div class="card shadow-sm text-center p-3">
          <h6 class="text-uppercase text-muted">{{ key.replace('_', ' ') }}</h6>
          <h2 class="fw-bold">{{ val }}</h2>
        </div>
      </div>
    </div>

    <div class="card shadow-sm">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Manage Companies</h5>
        <input
          v-model="searchQuery"
          @input="fetchCompanies"
          class="form-control w-25"
          placeholder="Search name/industry..."
        />
      </div>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Industry</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in companies" :key="company.id">
              <td>{{ company.name }}</td>
              <td>{{ company.industry }}</td>
              <td>
                <span :class="company.is_approved ? 'badge bg-success' : 'badge bg-warning'">
                  {{ company.is_approved ? 'Approved' : 'Pending' }}
                </span>
              </td>
              <td>
                <button
                  v-if="!company.is_approved"
                  @click="approve(company.id)"
                  class="btn btn-sm btn-outline-success me-2"
                >
                  Approve
                </button>
                <button @click="removeCompany(company.id)" class="btn btn-sm btn-outline-danger">
                  Remove
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const stats = ref({})
const companies = ref([])
const searchQuery = ref('')

const fetchStats = async () => {
  const res = await fetch('http://localhost:5000/admin/stats', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  stats.value = await res.json()
}

const fetchCompanies = async () => {
  const res = await fetch(`http://localhost:5000/admin/companies?search=${searchQuery.value}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  companies.value = await res.json()
}

const approve = async (id) => {
  await fetch(`http://localhost:5000/admin/approve-company/${id}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  fetchCompanies()
  fetchStats()
}

onMounted(() => {
  fetchStats()
  // fetchCompanies()
})
</script>
