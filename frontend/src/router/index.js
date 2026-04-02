import { createRouter, createWebHistory } from 'vue-router'
import Login from '../components/Login.vue'
import AdminDash from '@/components/admin/AdminDash.vue'
import CompanyDash from '../components/CompanyDash.vue'
import StudentDash from '../components/StudentDash.vue'

import RegisterStudent from '@/components/RegisterStudent.vue'
import RegisterCompany from '@/components/RegisterCompany.vue'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: Login },
  { path: '/register/student', component: RegisterStudent },
  { path: '/register/company', component: RegisterCompany },
  { path: '/admin', component: AdminDash, meta: { role: 'admin' } },
  { path: '/company', component: CompanyDash, meta: { role: 'company' } },
  { path: '/student', component: StudentDash, meta: { role: 'student' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// router.beforeEach((to, from, next) => {
//   const authStore = useAuthStore()
//   if (!authStore.token) {
//     router.push('/login')
//   } else if (to.path === '/login' && authStore.token) {
//     // Redirect already logged-in users to their role dashboard
//     router.push(`/${authStore.role.toLowerCase()}`)
//   } else {
//     // next()
//   }
// })

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const role = authStore.role
  if (to.meta.role && to.meta.role !== role) {
    next('/login')
  } else {
    next()
  }
})

// router.beforeEach((to, from, next) => {
//   const role = localStorage.getItem('userRole')
//   const isAuthenticated = !!localStorage.getItem('token')

//   // 1. Allow access to Login and Registration without a token
//   if (to.path === '/login' || to.path === '/register-student') {
//     next()
//   }
//   // 2. If trying to access a protected route without being logged in
//   else if (!isAuthenticated) {
//     next('/login')
//   }
//   // 3. If logged in, check role-based access
//   else if (to.meta.role && to.meta.role !== role) {
//     // Redirect to their own dashboard if they try to access another role's page
//     next(`/${role}`)
//   }
//   else {
//     next()
//   }
// })

export default router
