<script setup>
import { Modal } from 'bootstrap'
import { ref, onMounted } from 'vue'
import CompanyCreateDrive from './CompanyCreateDrive.vue'
import BaseDropdown from '../base/BaseDropdown.vue'

const details = ref({})
const myJobs = ref([])
// const newJob = ref({ title: '', salary: '', min_cgpa: '', description: '' })
const applicants = ref([])
const selectedJobTitle = ref('')
const actionItems = [
  {
    label: 'Edit Profile',
    action: () => {
      console.log('Test')
    },
  },
  { label: 'Delete', action: () => {}, class: 'text-danger', icon: 'bi-trash' },
]

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

const viewApplicants = async (jobId, title) => {
  selectedJobTitle.value = title
  const res = await fetch(`http://localhost:5000/company/job/${jobId}/applicants`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  applicants.value = await res.json()

  // Use the imported Modal class instead of the global 'bootstrap' object
  const modalElement = document.getElementById('applicantModal')
  const modalInstance = new Modal(modalElement)
  modalInstance.show()
}

const updateStatus = async (appId, newStatus) => {
  const res = await fetch(`http://localhost:5000/company/application/${appId}/status`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({ status: newStatus }),
  })
  if (res.ok) {
    alert(`Student ${newStatus}`)
    // Refresh the list
    applicants.value = applicants.value.map((a) =>
      a.application_id === appId ? { ...a, status: newStatus } : a,
    )
  }
}

const toggleJob = async (jobId) => {
  await fetch(`http://localhost:5000/company/job/${jobId}/toggle-status`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  fetchJobs() // Refresh the main job table
}

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

    <div class="row">
      <div class="col-md-12">
        <div class="card shadow-sm">
          <div class="card-header">Your Placement Drives</div>
          <div class="card-body p-0">
            <table class="table table-hover mb-0">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Status</th>
                  <th>Applicants</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="job in myJobs" :key="job.id">
                  <td>{{ job.title }}</td>
                  <td>
                    <span
                      :class="job.status === 'ongoing' ? 'badge bg-success' : 'badge bg-warning'"
                      >{{ job.status }}</span
                    >
                  </td>
                  <td>{{ job.applicant_count }}</td>
                  <td>
                    <button
                      @click="viewApplicants(job.id)"
                      class="btn btn-sm btn-outline-info me-2"
                    >
                      View Applicants
                    </button>
                    <button
                      v-if="job.status != 'closed'"
                      @click="toggleJob(job.id)"
                      class="btn btn-sm btn-outline-success"
                    >
                      Mark as Complete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div class="modal fade" id="applicantModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Applicants for {{ selectedJobTitle }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
          </div>
          <div class="modal-body">
            <table class="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>CGPA</th>
                  <th>Status</th>
                  <th>Resume</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applicants" :key="app.application_id">
                  <td>{{ app.student_name }}</td>
                  <td>{{ app.cgpa }}</td>
                  <td>
                    <span class="badge bg-secondary">{{ app.status }}</span>
                  </td>
                  <td><button class="btn btn-sm btn-outline-info">view resume</button></td>
                  <td>
                    <!-- <div class="btn-group">
                      <button
                        @click="updateStatus(app.application_id, 'Shortlisted')"
                        class="btn btn-sm btn-success"
                      >
                        Shortlist
                      </button>
                      <button
                        @click="updateStatus(app.application_id, 'Rejected')"
                        class="btn btn-sm btn-danger"
                      >
                        Reject
                      </button>
                    </div> -->
                    <BaseDropdown label="Actions" :items="actionItems">
                      <template #label> Actions Test </template>
                    </BaseDropdown>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
