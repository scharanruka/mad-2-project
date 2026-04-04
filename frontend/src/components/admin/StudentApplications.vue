<script setup>
import { Modal } from 'bootstrap'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted } from 'vue'

const authStore = useAuthStore()
const applications = ref([])
const applicationDetails = ref({})

const fetchApplications = async () => {
  const res = await fetch('http://localhost:5000/admin/applications', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  applications.value = await res.json()
}

const viewApplication = async (appl_id) => {
  const res = await fetch(`http://localhost:5000/admin/applications/${appl_id}/details`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  applicationDetails.value = await res.json()
  console.log(applicationDetails)

  const modalElement = document.getElementById('detailsModal')
  const modalInstance = new Modal(modalElement)
  modalInstance.show()
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('default', { dateStyle: 'long' }).format(date)
}

onMounted(() => {
  fetchApplications()
})
</script>

<template>
  <div class="card shadow-sm mb-4">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h5 class="mb-0">Student Applications</h5>
    </div>
    <div class="card-body p-0">
      <table class="table table-hover mb-0">
        <thead class="table-light">
          <tr>
            <th>Sr No.</th>
            <th>Name</th>
            <th>Drive</th>
            <th>Company</th>
            <th>Date</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="appl in applications" :key="appl.id">
            <td>{{ appl.id }}</td>
            <td>{{ appl.sname }}</td>
            <td>{{ appl.posting }}</td>
            <td>{{ appl.company }}</td>
            <td>{{ formatDate(appl.date_applied) }}</td>
            <td>
              <button class="btn btn-outline-primary btn-sm me-2" @click="viewApplication(appl.id)">
                View
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
          <h5 class="modal-title">Drive {{ applicationDetails.id }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <h3>Application Title: {{ applicationDetails.title }}</h3>
          <div>
            <!-- <p>{{ applicationDetails.description }}</p> -->
          </div>

          <!-- <h4>Salary : {{ applicationDetails.salary }}</h4> -->
        </div>
      </div>
    </div>
  </div>
</template>
