<script setup>
import BaseModal from '@/components/base/BaseModal.vue'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted } from 'vue'

const authStore = useAuthStore()
const applications = ref([])
const applicationDetails = ref({})
const isModalOpen = ref(false)

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
              <button
                class="btn btn-outline-primary btn-sm me-2"
                @click="
                  () => {
                    isModalOpen = true
                    viewApplication(appl.id)
                  }
                "
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
  <BaseModal v-model="isModalOpen" title="Student Application details">
    <template #body>
      <div>
        <h5>Student Name: {{ applicationDetails.sname }}</h5>
        <h5>Branch: {{ applicationDetails.branch }}</h5>
        <h5>Drive: {{ applicationDetails.posting_id }}</h5>
        <h5>Title: {{ applicationDetails.posting_title }}</h5>
      </div>
    </template>
  </BaseModal>
  <!-- <div class="modal fade" id="detailsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">Drive {{ applicationDetails.id }}</h5>
          <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
        </div>
        <div class="modal-body">
          <h3>Application Title: {{ applicationDetails.title }}</h3>
          <div>
            <p>{{ applicationDetails.description }}</p>
          </div>

          <h4>Date Applied : {{ applicationDetails.date_applied }}</h4>
        </div>
      </div>
    </div>
  </div> -->
</template>
