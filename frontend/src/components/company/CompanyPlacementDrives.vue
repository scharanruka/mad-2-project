<script setup>
import { onMounted, ref } from 'vue'
import BaseModal from '../base/BaseModal.vue'

const myPostings = ref([])
const applicants = ref([])

const studentApplication = ref({})
const reviewForm = ref({
  application_id: null,
  feedback: '',
  interview_date: '',
  status: '',
})

const fetchJobs = async () => {
  const res = await fetch('http://localhost:5000/company/jobs', {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  myPostings.value = await res.json()
}

const viewApplicants = async (jobId) => {
  const res = await fetch(`http://localhost:5000/company/job/${jobId}/applicants`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  applicants.value = await res.json()
}

const fetchApplication = async (appl_id) => {
  const res = await fetch(`http://localhost:5000/company/application/${appl_id}/`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  studentApplication.value = await res.json()
}

//  MODALS ------------
const applicantsListModal = ref(false)
const applicantsActionModal = ref(false)

const openApplicantsListModal = async (posting_id) => {
  viewApplicants(posting_id)
  applicantsListModal.value = true
  applicantsActionModal.value = false
}
const openApplicantsActionModal = async (appl_id) => {
  fetchApplication(appl_id)
  applicantsListModal.value = false
  applicantsActionModal.value = true
}
// -------------------------------------------
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
    reviewForm.value = { application_id: null, feedback: '', interview_date: '', status: '' }
    applicantsListModal.value = false
    applicantsActionModal.value = false
  }
}
const toggleJob = async (jobId) => {
  await fetch(`http://localhost:5000/company/job/${jobId}/toggle-status`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
  })
  fetchJobs() // Refresh the main job table
}

const viewStudentResume = async (student_id) => {}

onMounted(() => {
  fetchJobs()
})
</script>

<template>
  <div class="row">
    <div class="col-md-12">
      <div class="card shadow-sm">
        <!-- <div class="card-header"><h3>Your Placement Drives</h3></div> -->
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
              <tr v-for="job in myPostings" :key="job.id">
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
                    @click="openApplicantsListModal(job.id)"
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
  <BaseModal v-model="applicantsListModal" title="Update Applications for the Posting">
    <template #body>
      <div>
        <h5>Received applications:</h5>
        <div class="container">
          <table class="table-hover">
            <tbody>
              <tr v-for="appl in applicants" :key="appl.application_id">
                <td>{{ appl.student_name }}</td>
                <td>
                  <button
                    class="btn btn-outline-primary"
                    @click="openApplicantsActionModal(appl.application_id)"
                  >
                    Review Application
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </BaseModal>
  <BaseModal v-model="applicantsActionModal" title="Student Application">
    <template #body>
      <div>
        <h4></h4>
        <p>Application ID: {{ studentApplication.application_id }}</p>
        <p>Student name: {{ studentApplication.student_name }}</p>
        <p>Branch: {{ studentApplication.branch }}</p>
        <p>Job Title: {{ studentApplication.job_title }}</p>
        <p>Status: {{ studentApplication.status }}</p>
        <div>
          <span><button class="btn btn-outline-primary btn-sm">view resume</button></span>

          <div class="row g-2">
            <div class="col-md-6">
              <label>Feedback:</label>
              <textarea
                v-model="reviewForm.feedback"
                class="form-control form-control-sm"
                placeholder="Enter feedback for student..."
              ></textarea>
            </div>
            <div class="col-md-4">
              <label>Interview Date:</label>
              <input
                v-model="reviewForm.interview_date"
                type="datetime-local"
                class="form-control form-control-sm"
              />
            </div>
            <div class="col-md-2 d-grid gap-1">
              <button
                @click="submitReview(studentApplication.application_id, 'Shortlisted')"
                class="btn btn-sm btn-warning"
              >
                Shortlist
              </button>
              <button
                @click="submitReview(studentApplication.application_id, 'Rejected')"
                class="btn btn-sm btn-danger"
              >
                Reject
              </button>
              <button
                @click="submitReview(studentApplication.application_id, 'Selected')"
                class="btn btn-sm btn-success"
              >
                Select/Offer
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </BaseModal>
</template>
