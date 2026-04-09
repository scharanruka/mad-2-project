<script setup>
import { ref, onMounted } from 'vue'
import CompanyCreateDrive from './CompanyCreateDrive.vue'
import CompanyPlacementDrives from './CompanyPlacementDrives.vue'

const details = ref({})
const myJobs = ref([])

const fetchDetails = async () => {
  const res = await fetch('http://localhost:5000/company/details', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  details.value = await res.json()
}

const fetchJobs = async () => {
  console.log('Jobs fetched!')
  const res = await fetch('http://localhost:5000/company/jobs', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  myJobs.value = await res.json()
}

// const updateStatus = async (appId, newStatus) => {
//   const res = await fetch(`http://localhost:5000/company/application/${appId}/status`, {
//     method: 'POST',
//     headers: {
//       'Content-Type': 'application/json',
//       Authorization: `Bearer ${localStorage.getItem('token')}`,
//     },
//     body: JSON.stringify({ status: newStatus }),
//   })
//   if (res.ok) {
//     alert(`Student ${newStatus}`)
//     // Refresh the list
//     applicants.value = applicants.value.map((a) =>
//       a.application_id === appId ? { ...a, status: newStatus } : a,
//     )
//   }
// }

onMounted(() => {
  fetchDetails()
  fetchJobs()
})
</script>

<template>
  <div class="container mt-4">
    <div>
      <h2>Welcome {{ details.name }}</h2>
      <CompanyCreateDrive @fetch-jobs="fetchJobs" />
    </div>

    <CompanyPlacementDrives />
  </div>
</template>
