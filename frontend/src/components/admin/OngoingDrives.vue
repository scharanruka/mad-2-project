<script setup>
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted } from 'vue'

const authStore = useAuthStore()
const postings = ref([])
const postingDetails = ref({})

const fetchPostings = async () => {
  const res = await fetch('http://localhost:5000/admin/postings', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  postings.value = await res.json()
}

const markPostingComplete = async (posting_id) => {
  await fetch(`http://localhost:5000/admin/postings/${posting_id}/complete`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  fetchPostings()
}

const showDetails = async (posting_id) => {
  const res = await fetch(`http://localhost:5000/admin/postings/${posting_id}/details`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  postingDetails.value = await res.json()

  const modalElement = document.getElementById('detailsModal')
  const modalInstance = new Modal(modalElement)
  modalInstance.show()
}

onMounted(() => {
  fetchPostings()
})
</script>

<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Ongoing Drives</h5>
    </div>
    <div class="card-body p-0">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Sr No.</th>
            <th>Drive Name</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="posting in postings" :key="posting.id">
            <td>{{ posting.id }}</td>
            <td>{{ posting.title }}</td>
            <td>
              <button @click="showDetails(posting.id)" class="btn btn-outline-primary btn-sm me-2">
                View Details
              </button>
              <button
                @click="markPostingComplete(posting.id)"
                class="btn btn-outline-success btn-sm me-2"
              >
                Mark as complete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <div class="modal fade" id="detailsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Drive {{ postingDetails.id }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <h3>Job Title: {{ postingDetails.title }}</h3>
          <div>
            <h4>Job Description</h4>
            <p>{{ postingDetails.description }}</p>
          </div>

          <h4>Salary : {{ postingDetails.salary }}</h4>

          <!-- <table class="table">
            <thead>
              <tr>
                <th>Name</th>
                <th>CGPA</th>
                <th>Status</th>
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
                <td>
                  <div class="btn-group">
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
                  </div>
                </td>
              </tr>
            </tbody>
          </table> -->
        </div>
      </div>
    </div>
  </div>
</template>
