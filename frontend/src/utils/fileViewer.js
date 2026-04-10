import { useAuthStore } from '@/stores/auth'

export const openResume = async (studentId) => {
  const authStore = useAuthStore()
  const res = await fetch(`http://localhost:5000/view-resume/${studentId}`, {
    headers: { Authorization: `Bearer ${authStore.token}` },
  })

  if (res.ok) {
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    window.open(url, '_blank') // Opens PDF in new tab
  } else {
    alert('You do not have permission to view this resume.')
  }
}
