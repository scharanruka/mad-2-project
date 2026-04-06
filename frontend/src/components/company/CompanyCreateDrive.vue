<script setup>
import { ref } from 'vue'
import BaseModal from '@/components/base/BaseModal.vue'

const emit = defineEmits(['fetchJobs'])
const newJob = ref({ title: '', salary: '', min_cgpa: '', description: '' })
const isModalOpen = ref(false)

const postJob = async () => {
  const res = await fetch('http://localhost:5000/company/jobs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${localStorage.getItem('token')}`,
    },
    body: JSON.stringify(newJob.value),
  })
  if (res.ok) {
    alert('Job posted!')
    isModalOpen.value = false
    emit('fetchJobs')
  }
}
</script>

<template>
  <button type="submit" @click="isModalOpen = true" class="btn btn-primary">Create Drive</button>

  <BaseModal v-model="isModalOpen" title="Create a Drive">
    <template #body>
      <div class="">
        <form @submit.prevent="postJob" class="row g-3">
          <div class="col-md-6">
            <input v-model="newJob.title" placeholder="Job Title" class="form-control" required />
          </div>
          <div class="col-md-3">
            <input
              v-model="newJob.salary"
              placeholder="Salary (e.g. 12 LPA)"
              class="form-control"
            />
          </div>
          <div class="col-md-3">
            <input
              v-model="newJob.min_cgpa"
              type="number"
              step="0.1"
              placeholder="Min CGPA"
              class="form-control"
            />
          </div>
          <div class="col-md-3">
            <input
              v-model="newJob.deadline"
              type="date"
              :min="new Date().toISOString().split('T')[0]"
              placeholder="Deadline"
              class="form-control"
            />
          </div>
          <div class="col-12">
            <textarea
              v-model="newJob.description"
              placeholder="Job Description"
              class="form-control"
            ></textarea>
          </div>
          <div class="col-12">
            <button type="submit" class="btn btn-success">Submit</button>
          </div>
        </form>
      </div>
    </template>
  </BaseModal>
</template>
