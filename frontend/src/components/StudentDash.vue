<script setup>
import { ref, onMounted } from 'vue'

const jobs = ref([])
const searchQuery = ref('')

const fetchJobs = async () => {
  const res = await fetch(`http://localhost:5000/student/jobs?search=${searchQuery.value}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  jobs.value = await res.json()
}

const apply = async (jobId) => {
  const res = await fetch(`http://localhost:5000/student/apply/${jobId}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  const data = await res.json()
  alert(data.msg)
}

onMounted(fetchJobs)
</script>

<!-- <template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-md-3">
        <div class="card p-3 shadow-sm">
          <h5>Filters</h5>
          <input
            v-model="searchQuery"
            @input="fetchJobs"
            class="form-control mb-3"
            placeholder="Search title or skills..."
          />
          <p class="small text-muted">Showing active placement drives approved by the Institute.</p>
        </div>
      </div>

      <div class="col-md-9">
        <h3 class="mb-4">Available Roles</h3>
        <div v-if="jobs.length === 0" class="alert alert-light">
          No jobs matching your criteria.
        </div>

        <div v-for="job in jobs" :key="job.id" class="card mb-3 shadow-sm border-0">
          <div class="card-body d-flex justify-content-between align-items-center">
            <div>
              <h5 class="card-title text-primary">{{ job.title }}</h5>
              <h6 class="card-subtitle mb-2 text-muted">
                {{ job.company_name }} | {{ job.salary }}
              </h6>
              <p class="card-text small">{{ job.description.substring(0, 100) }}...</p>
              <span class="badge bg-info text-dark">Min CGPA: {{ job.min_cgpa }}</span>
              <span class="badge bg-light text-dark ms-2">Deadline: {{ job.deadline }}</span>
            </div>
            <div>
              <button @click="apply(job.id)" class="btn btn-primary px-4">Apply Now</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template> -->

<template>
  <div class="container mt-4">
    <ul class="nav nav-pills mb-4">
      <li class="nav-item">
        <button class="nav-link active" data-bs-toggle="pill" data-bs-target="#jobs">
          Job Board
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" data-bs-toggle="pill" data-bs-target="#history">
          My Applications
        </button>
      </li>
      <li class="nav-item">
        <button class="nav-link" data-bs-toggle="pill" data-bs-target="#profile">Profile</button>
      </li>
    </ul>

    <div class="tab-content">
      <div class="tab-pane fade" id="history">
        <div v-for="app in myApplications" :key="app.id" class="card mb-2">
          <div class="card-body">
            <h6>{{ app.job_title }} at {{ app.company }}</h6>
            <span :class="getStatusClass(app.status)">{{ app.status }}</span>
            <p class="small mt-2">Feedback: {{ app.feedback }}</p>
          </div>
        </div>
      </div>

      <div class="tab-pane fade" id="profile">
        <form @submit.prevent="updateProfile" enctype="multipart/form-data">
          <div class="mb-3">
            <label>Resume (PDF)</label>
            <input type="file" @change="onFileChange" class="form-control" accept=".pdf" />
          </div>
          <button type="submit" class="btn btn-primary">Update Profile</button>
        </form>
      </div>
    </div>
  </div>
</template>
