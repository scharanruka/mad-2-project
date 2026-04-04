<template>
  <div class="container mt-4">
    <h2 class="mb-4">Admin Dashboard</h2>

    <div class="row mb-4">
      <div class="col-md-3" v-for="(val, key) in stats" :key="key">
        <div class="card shadow-sm text-center p-3">
          <h6 class="text-uppercase text-muted">{{ key.replace('_', ' ') }}</h6>
          <h2 class="fw-bold">{{ val }}</h2>
        </div>
      </div>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Registered Companies</h5>
        <input
          v-model="companySearchQuery"
          @input="fetchCompanies"
          class="form-control w-25"
          placeholder="Search name/industry..."
        />
      </div>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Industry</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="company in companies" :key="company.id">
              <td>{{ company.name }}</td>
              <td>{{ company.industry }}</td>
              <td class="">
                <span
                  :class="company.is_approved ? 'badge bg-success px-3' : 'badge bg-danger px-3'"
                >
                  {{ company.is_approved ? 'Approved' : 'Pending' }}
                </span>
                <span :class="company.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                  {{ company.is_active ? 'Active' : 'Blacklisted' }}
                </span>
              </td>
              <td>
                <span>
                  <button
                    v-if="!company.is_approved"
                    @click="approve_company(company.id)"
                    :class="`btn btn-sm me-2  ${company.is_approved ? 'btn-outline-danger' : 'btn-outline-success'}`"
                  >
                    {{ company.is_approved ? 'Reject' : 'Approve' }}
                  </button>
                </span>
                <span>
                  <button
                    @click="toggle_blacklist(company.id)"
                    :class="`btn btn-sm me-2  ${company.is_active ? 'btn-outline-secondary' : 'btn-outline-success'}`"
                  >
                    {{ company.is_active ? 'Blacklist' : 'Enable' }}
                  </button>
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div class="card shadow-sm mb-4">
      <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="mb-0">Registered Students</h5>
        <input
          v-model="studentSearchQuery"
          @input="fetchStudents"
          class="form-control w-25"
          placeholder="Search name/ID..."
        />
      </div>
      <div class="card-body p-0">
        <table class="table table-hover mb-0">
          <thead class="table-light">
            <tr>
              <th>Name</th>
              <th>Branch</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="student in students" :key="student.id">
              <td>{{ student.name }}</td>
              <td>{{ student.branch }}</td>
              <td>
                <span :class="student.is_active ? 'badge bg-success' : 'badge bg-secondary'">
                  {{ student.is_active ? 'Active' : 'Blacklisted' }}
                </span>
              </td>
              <td>
                <button
                  @click="toggle_blacklist(student.id)"
                  :class="`btn btn-sm me-2  ${student.is_active ? 'btn-outline-secondary' : 'btn-outline-primary'}`"
                >
                  Blacklist
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <OngoingDrives />
    <StudentApplications />
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted, reactive } from 'vue'
import OngoingDrives from '@/components/admin/OngoingDrives.vue'
import StudentApplications from '@/components/admin/StudentApplications.vue'

const authStore = useAuthStore()

const stats = ref({})
const companies = ref([])
const students = ref([])

const applications = ref([])

const companySearchQuery = ref('')
const studentSearchQuery = ref('')

const fetchStats = async () => {
  const res = await fetch('http://localhost:5000/admin/stats', {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  stats.value = await res.json()
}

const fetchCompanies = async () => {
  const query = companySearchQuery.value ? `?search=${companySearchQuery.value}` : ''
  const res = await fetch(`http://localhost:5000/admin/companies${query}`, {
    // ?search=${searchQuery.value}
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  companies.value = await res.json()
}

const fetchStudents = async () => {
  const query = studentSearchQuery.value ? `?search=${studentSearchQuery.value}` : ''
  const res = await fetch(`http://localhost:5000/admin/students${query}`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  students.value = await res.json()
}

const approve_company = async (id) => {
  await fetch(`http://localhost:5000/admin/companies/approve?id=${id}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  fetchCompanies()
  fetchStats()
}

const toggle_blacklist = async (id) => {
  await fetch(`http://localhost:5000/admin/user/blacklist?id=${id}`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${authStore.token}` },
  })
  fetchCompanies()
  fetchStudents()
}

onMounted(() => {
  fetchStats()
  fetchCompanies()
  fetchStudents()
})
</script>
