<script setup>
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted } from 'vue'
import BaseModal from '@/components/base/BaseModal.vue'

const authStore = useAuthStore()
const postings = ref([])
const postingDetails = ref({})
const isModalOpen = ref(false)

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

const togglePostingStatus = async (posting_id) => {
  await fetch(`http://localhost:5000/admin/postings/${posting_id}/toggle_status`, {
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

  // const modalElement = document.getElementById('detailsModal')
  // const modalInstance = new Modal(modalElement)
  // modalInstance.show()
}

onMounted(() => {
  fetchPostings()
})
</script>

<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mt-2 mb-2">Ongoing Drives</h5>
    </div>
    <div class="card-body p-0">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Sr No.</th>
            <th>Drive Name</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="posting in postings" :key="posting.id">
            <td>{{ posting.id }}</td>
            <td>{{ posting.title }}</td>
            <td>{{ posting.status }}</td>
            <td>
              <button
                @click="
                  () => {
                    isModalOpen = true
                    showDetails(posting.id)
                  }
                "
                class="btn btn-outline-primary btn-sm me-2"
              >
                View Details
              </button>
              <button
                @click="markPostingComplete(posting.id)"
                class="btn btn-outline-success btn-sm me-2"
              >
                Mark as complete
              </button>
              <button
                @click="togglePostingStatus(posting.id)"
                class="btn btn-outline-danger btn-sm me-2"
              >
                {{ posting.status == 'ongoing' ? 'Reject' : 'Accept' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <BaseModal v-model="isModalOpen" title="Drive details">
    <template #body>
      <div class="">
        <div class="">
          <div class="modal-header">
            <h5 class="modal-title">Drive {{ postingDetails.id }}</h5>
          </div>
          <div class="modal-body">
            <h3>Job Title: {{ postingDetails.title }}</h3>
            <div>
              <h4>Job Description</h4>
              <p>{{ postingDetails.description }}</p>
            </div>

            <h4>Salary : {{ postingDetails.salary }}</h4>
          </div>
        </div>
      </div>
    </template>
  </BaseModal>
  <!-- <div class="modal fade" id="detailsModal" tabindex="-1" aria-hidden="true">
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
        </div>
      </div>
    </div>
  </div> -->
</template>
