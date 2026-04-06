<script setup>
import { onMounted, ref, watch } from 'vue'
import { Modal } from 'bootstrap'

const props = defineProps({
  modelValue: Boolean, // Controls visibility (v-model)
  title: String,
})

const emit = defineEmits(['update:modelValue', 'close'])

const modalRef = ref(null)
let modalInstance = null

onMounted(() => {
  modalInstance = new Modal(modalRef.value)

  // Sync Bootstrap's internal state with Vue if user clicks the 'X' or backdrop
  modalRef.value.addEventListener('hidden.bs.modal', () => {
    emit('update:modelValue', false)
    emit('close')
  })
})

// Watch the prop to show/hide the modal programmatically
watch(
  () => props.modelValue,
  (val) => {
    if (val) modalInstance.show()
    else modalInstance.hide()
  },
)
</script>

<template>
  <div class="modal fade" ref="modalRef" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg modal-dialog-scrollable">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ title }}</h5>
          <button
            type="button"
            class="btn-close"
            @click="$emit('update:modelValue', false)"
          ></button>
        </div>
        <div class="modal-body">
          <slot name="body"></slot>
        </div>
        <div class="modal-footer">
          <slot name="footer">
            <!-- <button class="btn btn-secondary" @click="$emit('update:modelValue', false)">
              Close
            </button> -->
          </slot>
        </div>
      </div>
    </div>
  </div>
</template>
