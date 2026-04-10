<script setup>
import { ref, onMounted } from 'vue'
import CompanyCreateDrive from './CompanyCreateDrive.vue'
import CompanyPlacementDrives from './CompanyPlacementDrives.vue'
import { useAuthStore } from '@/stores/auth'
const authStore = useAuthStore()
const details = ref({})
const myJobs = ref([])

const fetchDetails = async () => {
  const res = await fetch('http://localhost:5000/company/details', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  details.value = await res.json()
}

const fetchJobs = async () => {
  console.log('Jobs fetched!')
  const res = await fetch('http://localhost:5000/company/jobs', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  myJobs.value = await res.json()
}

onMounted(() => {
  fetchDetails()
  fetchJobs()
})

const exportCompanyData = async () => {
  const res = await fetch('http://localhost:5000/company/export-history', {
    method: 'POST',
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  const { task_id } = await res.json()

  // Poll
  const interval = setInterval(async () => {
    const statusRes = await fetch(`http://localhost:5000/task-status/${task_id}`)
    const { status } = await statusRes.json()

    if (status === 'SUCCESS') {
      clearInterval(interval)

      const fileRes = await fetch(`http://localhost:5000/company/download-export/${task_id}`, {
        headers: { Authorization: `Bearer ${authStore.token}` },
      })
      const blob = await fileRes.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Company_Recruitment_Report.csv`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
    }
  }, 3000)
}
</script>

<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Welcome {{ details.name }}</h2>
      <CompanyCreateDrive @fetch-jobs="fetchJobs" />
    </div>
    <div class="d-flex justify-content-between align-items-center mb-3">
      <h4>Your Placement Drives</h4>
      <button @click="exportCompanyData" class="btn btn-outline-success btn-sm">
        <i class="bi bi-download"></i> Export Recruitment History
      </button>
    </div>
    <CompanyPlacementDrives />
  </div>
</template>
