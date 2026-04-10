<script setup>
import { ref, onMounted } from 'vue'
import StudentProfile from '@/components/student/StudentProfile.vue'

const jobs = ref([])
const myApplications = ref([])
const searchQuery = ref('')
const studentDetails = ref({})

const fetchStudentDetails = async () => {
  const res = await fetch(`http://localhost:5000/student/profile`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  studentDetails.value = await res.json()
}

const fetchJobs = async () => {
  const res = await fetch(`http://localhost:5000/student/jobs?search=${searchQuery.value}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  jobs.value = await res.json()
}

const fetchMyApplications = async () => {
  const res = await fetch(`http://localhost:5000/student/applications`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  myApplications.value = await res.json()
}

const apply = async (jobId) => {
  const res = await fetch(`http://localhost:5000/student/apply/${jobId}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  const data = await res.json()
  alert(data.msg)
  fetchJobs()
}

onMounted(() => {
  fetchJobs()
  fetchMyApplications()
  fetchStudentDetails()
})

const handleOfferDownload = async (applId) => {
  console.log('clicked')
  const res = await fetch(`http://localhost:5000/student/applications/${applId}/generate-offer`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  const { task_id } = await res.json()

  // Poll for completion
  const interval = setInterval(async () => {
    const statusRes = await fetch(`http://localhost:5000/task-status/${task_id}`)
    const { status } = await statusRes.json()

    if (status === 'SUCCESS') {
      clearInterval(interval)
      const fileRes = await fetch(`http://localhost:5000/student/download-offer/${applId}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      })

      const blob = await fileRes.blob()

      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `Offer Letter.pdf`
      document.body.appendChild(a)
      a.click()

      //  Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    }
  }, 2000)
}

const triggerCSVExport = async () => {
  const res = await fetch('http://localhost:5000/student/export-applications', {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  const { task_id, msg } = await res.json()

  const interval = setInterval(async () => {
    const statusRes = await fetch(`http://localhost:5000/task-status/${task_id}`)
    const { status } = await statusRes.json()

    if (status === 'SUCCESS') {
      clearInterval(interval)

      // 1. Fetch the generated CSV using the Auth header
      const downloadRes = await fetch(`http://localhost:5000/student/download-export/${task_id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      })

      // 2. Convert the response to a Blob (Binary Large Object)
      const blob = await downloadRes.blob()

      // 3. Create a hidden <a> tag to trigger the browser's save dialog
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `Application_History_${new Date().toLocaleDateString()}.csv`)
      document.body.appendChild(link)
      link.click()

      // 4. Cleanup to prevent memory leaks
      link.parentNode.removeChild(link)
      window.URL.revokeObjectURL(url)
    }
  }, 3000)
}
</script>

<template>
  <div class="container mt-4">
    <header>
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
    </header>

    <div class="container mt-4 tab-content">
      <div class="tab-pane fade show active" id="jobs">
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
              <p class="small text-muted">
                Showing active placement drives approved by the Institute.
              </p>
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
                  <button
                    @click="apply(job.id)"
                    class="btn px-4 btn-sm"
                    :class="job.has_applied ? 'btn-secondary' : 'btn-primary'"
                    :disabled="job.has_applied"
                  >
                    {{ job.has_applied === true ? 'Applied' : 'Apply now' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="tab-content">
      <div class="tab-pane fade" id="history">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <p>Student Name: {{ studentDetails.full_name }}</p>
            <p>Branch: {{ studentDetails.branch }}</p>
          </div>
          <button @click="triggerCSVExport" class="btn btn-outline-success btn-sm">
            <i class="bi bi-file-earmark-spreadsheet"></i> Export History (CSV)
          </button>
        </div>

        <table class="table table-striped border-secondary">
          <thead>
            <tr>
              <th>Drive No.</th>
              <th>Job Title</th>
              <th>Company</th>
              <th>Status</th>
              <th>Remarks</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="myApplications" v-for="appl in myApplications" :key="appl.id">
              <td>{{ appl.id }}</td>
              <td>{{ appl.job_title }}</td>
              <td>{{ appl.company }}</td>
              <td>
                <span
                  class="badge"
                  :class="
                    appl.status == 'rejected'
                      ? `bg-danger`
                      : appl.status == 'selected'
                        ? `bg-success`
                        : `bg-warning`
                  "
                  >{{ appl.status }}</span
                >
              </td>
              <td>
                <details>
                  {{ appl.feedback ? appl.feedback : 'None' }}
                </details>
              </td>
              <td>
                <button
                  @click="handleOfferDownload(appl.id)"
                  v-if="appl.status == 'selected'"
                  class="btn btn-sm btn-success"
                >
                  Download Placement Letter
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <StudentProfile />
  </div>
</template>
