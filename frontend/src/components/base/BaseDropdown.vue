<script setup>
import { Dropdown } from 'bootstrap'
import { ref, onMounted } from 'vue'

const props = defineProps({
  label: { type: String, default: 'Options' },
  items: { type: Array, required: true },
  // Expected structure: { label: 'Delete', action: () => {}, class: 'text-danger', icon: 'bi-trash' }
})
const dropdownRef = ref(null)

onMounted(() => {
  new Dropdown(dropdownRef.value)
})
</script>

<template>
  <div class="dropdown">
    <button
      ref="dropdownRef"
      class="btn dropdown-toggle btn-outline-primary"
      type="button"
      data-bs-toggle="dropdown"
      aria-expanded="false"
    >
      <slot name="label">{{ label }}</slot>
    </button>

    <ul class="dropdown-menu">
      <li v-for="(item, index) in items" :key="index">
        <hr v-if="item.divider" class="dropdown-divider" />
        <button v-else class="dropdown-item" type="button" @click="item.action">
          {{ item.label }}
        </button>
      </li>
    </ul>
  </div>
</template>
