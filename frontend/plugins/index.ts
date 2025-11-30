import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
    meta: { layout: 'auth', guest: true },
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterPage.vue'),
    meta: { layout: 'auth', guest: true },
  },
  {
    path: '/pets',
    name: 'PetList',
    component: () => import('@/views/pets/PetListPage.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/pets/:id',
    name: 'PetDetail',
    component: () => import('@/views/pets/PetDetailPage.vue'),
    meta: { layout: 'default' },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/ProfilePage.vue'),
    meta: { layout: 'default', requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundPage.vue'),
    meta: { layout: 'empty' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    return { top: 0 }
  },
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const isGuest = to.matched.some((record) => record.meta.guest)

  // Set page title
  document.title = to.meta.title
    ? \\ - 寵物領養平台\
    : '寵物領養平台'

  // Check authentication
  if (requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (isGuest && authStore.isAuthenticated) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
