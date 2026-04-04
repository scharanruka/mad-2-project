<script setup>
import { Modal } from 'bootstrap'

function showModal() {
  const modalElement = document.getElementById('detailsModal')
  const modalInstance = new Modal(modalElement)
  modalInstance.show()
}
</script>

<template>
  <div class="modal fade" id="detailsModal" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
      <div class="modal-content">
        <div class="modal-header">
          <slot> </slot>
        </div>
      </div>
    </div>
  </div>
</template>
