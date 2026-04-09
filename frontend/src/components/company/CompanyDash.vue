<script setup>
import { Modal } from 'bootstrap'
import { ref, onMounted } from 'vue'
import CompanyCreateDrive from './CompanyCreateDrive.vue'
import BaseDropdown from '../base/BaseDropdown.vue'
import CompanyPlacementDrives from './CompanyPlacementDrives.vue'

const details = ref({})
const myJobs = ref([])
// const newJob = ref({ title: '', salary: '', min_cgpa: '', description: '' })
const applicants = ref([])
const selectedJobTitle = ref('')
const reviewForm = ref({
  application_id: null,
  feedback: '',
  interview_date: '',
  status: '',
})

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
// Modals ---------------------------------
const selectedApplicant = ref(null) // Tracks the student for the second modal
const reviewModalInstance = ref(null)

const openReview = (app) => {
  selectedApplicant.value = app
  // Pre-fill the form with existing data if any
  reviewForm.value = {
    application_id: app.application_id,
    feedback: app.feedback || '',
    interview_date: app.interview_date || '',
    status: app.status,
  }

  const modalElement = document.getElementById('reviewModal')
  reviewModalInstance.value = new Modal(modalElement)
  reviewModalInstance.value.show()
}

const submitReview = async (appId, status) => {
  const res = await fetch(`http://localhost:5000/company/application/${appId}/process`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify({
      status: status,
      feedback: reviewForm.value.feedback,
      interview_date: reviewForm.value.interview_date,
    }),
  })

  if (res.ok) {
    alert(`Application updated to ${status}`)
    // Refresh only the specific applicant in the local list
    // applicants.value = applicants.value.map((a) =>
    //   a.application_id === appId ? { ...a, status: status } : a,
    // )
    // Reset form
    // reviewForm.value = { application_id: null, feedback: '', interview_date: '', status: '' }
    reviewModalInstance.value.hide()
    // viewApplicants(selectedJobId)
  }
}

const toggleJob = async (jobId) => {
  await fetch(`http://localhost:5000/company/job/${jobId}/toggle-status`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  fetchJobs() // Refresh the main job table
}

// onMounted(() => {
//   fetchDetails()
//   fetchJobs()
// })
</script>

<template>
  <div class="container mt-4">
    <div>
      <h2>Welcome {{ details.name }}</h2>
      <CompanyCreateDrive @fetch-jobs="fetchJobs" />
    </div>

    <CompanyPlacementDrives />

    <!-- <div class="row">
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
    </div> -->

    <!-- <div class="modal fade" id="applicantModal" tabindex="-1" aria-hidden="true">
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
                  <td colspan="5">
                    <div class="border rounded p-3 mb-2 bg-light">
                      <div class="d-flex justify-content-between align-items-center mb-2">
                        <strong>{{ app.student_name }} (CGPA: {{ app.cgpa }})</strong>
                        <span class="badge bg-secondary">{{ app.status }}</span>
                      </div>

                      <div class="row g-2">
                        <div class="col-md-6">
                          <textarea
                            v-model="reviewForm.feedback"
                            class="form-control form-control-sm"
                            placeholder="Enter feedback for student..."
                          ></textarea>
                        </div>
                        <div class="col-md-4">
                          <input
                            type="datetime-local"
                            v-model="reviewForm.interview_date"
                            class="form-control form-control-sm"
                          />
                        </div>
                        <div class="col-md-2 d-grid gap-1">
                          <button
                            @click="submitReview(app.application_id, 'Shortlisted')"
                            class="btn btn-sm btn-warning"
                          >
                            Shortlist
                          </button>
                          <button
                            @click="submitReview(app.application_id, 'Rejected')"
                            class="btn btn-sm btn-danger"
                          >
                            Reject
                          </button>
                          <button
                            @click="submitReview(app.application_id, 'Selected')"
                            class="btn btn-sm btn-success"
                          >
                            Select/Offer
                          </button>
                        </div>
                      </div>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div> -->
  </div>
</template>
