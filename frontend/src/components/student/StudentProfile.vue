<script setup>
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted } from 'vue'

const authStore = useAuthStore()

const profile = ref({
  full_name: '',
  branch: '',
  skills: '',
  resume_path: '',
})
const selectedFile = ref(null)

// Function to fetch and prefill data
const fetchProfileData = async () => {
  const res = await fetch('http://localhost:5000/student/details', {
    method: 'GET',
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  if (res.ok) {
    const data = await res.json()
    profile.value = data
  } else {
    throw new Error(`Server error: ${res.status}`)
  }
}

const handleFileUpload = (e) => {
  selectedFile.value = e.target.files[0]
}

const saveProfile = async () => {
  const formData = new FormData()
  formData.append('full_name', profile.value.full_name)
  formData.append('branch', profile.value.branch)
  formData.append('skills', profile.value.skills)
  if (selectedFile.value) {
    formData.append('resume', selectedFile.value)
  }

  const res = await fetch('http://localhost:5000/student/profile', {
    method: 'PUT',
    headers: { Authorization: `Bearer ${authStore.token}` },
    body: formData,
  })

  if (res.ok) {
    alert('Profile Saved!')
    fetchProfileData() // Refresh to show updated resume path
  }
}

// Run on page load
onMounted(() => {
  fetchProfileData()
})
</script>

<template>
  <div class="tab-pane fade" id="profile">
    <div class="card shadow-sm p-4">
      <h4>Update Your Professional Profile</h4>
      <form @submit.prevent="saveProfile">
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">Full Name</label>
            <input v-model="profile.full_name" class="form-control" required />
          </div>
          <div class="col-md-6">
            <label class="form-label">Branch</label>
            <input v-model="profile.branch" class="form-control" placeholder="e.g. Data Science" />
          </div>
          <div class="col-12">
            <label class="form-label">Skills (Comma separated)</label>
            <textarea v-model="profile.skills" class="form-control" rows="2"></textarea>
          </div>
          <div class="col-12">
            <label class="form-label">Upload Resume (PDF only)</label>
            <input type="file" @change="handleFileUpload" class="form-control" accept=".pdf" />
            <small class="text-muted" v-if="profile.resume_path"
              >Current: {{ profile.resume_path.split('/').pop() }}</small
            >
          </div>
          <div class="col-12 mt-4">
            <button type="submit" class="btn btn-primary w-100">
              Save Profile & Upload Resume
            </button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>
