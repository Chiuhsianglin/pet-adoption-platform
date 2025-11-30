import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Extend route meta type
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    requiresAuth?: boolean
    requiresRole?: string | string[]
    guest?: boolean
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomePage.vue'),
    meta: { title: '首頁' },
  },
  {
    path: '/auth/login',
    name: 'Login',
    component: () => import('@/views/auth/LoginPage.vue'),
    meta: { title: '登入', guest: true },
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: () => import('@/views/auth/RegisterPage.vue'),
    meta: { title: '註冊', guest: true },
  },
  {
    path: '/pets',
    name: 'PetBrowsing',
    component: () => import('@/views/pets/PetBrowsingPage.vue'),
    meta: { title: '瀏覽寵物' },
  },
  {
    path: '/pets/list',
    name: 'PetList',
    component: () => import('@/views/pets/PetListPage.vue'),
    meta: { title: '寵物列表 (舊版)' },
  },
  {
    path: '/pets/create',
    name: 'PetCreate',
    component: () => import('@/views/pets/PetCreatePage.vue'),
    meta: { title: '發布新寵物', requiresAuth: true },
  },
  {
    path: '/pets/manage',
    name: 'PetManage',
    component: () => import('@/views/pets/PetManagePage.vue'),
    meta: { title: '寵物管理', requiresAuth: true },
  },
  {
    path: '/pets/:id',
    name: 'PetDetail',
    component: () => import('@/views/pets/PetDetailPage.vue'),
    meta: { title: '寵物詳情' },
  },
  {
    path: '/pets/:id/edit',
    name: 'PetEdit',
    component: () => import('@/views/pets/PetEditPage.vue'),
    meta: { title: '編輯寵物', requiresAuth: true },
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('@/views/favorites/FavoritesPage.vue'),
    meta: { title: '我的收藏', requiresAuth: true },
  },
  {
    path: '/pets/:petId/adopt',
    name: 'AdoptionForm',
    component: () => import('@/views/adoption/AdoptionFormPage.vue'),
    meta: { title: '填寫領養申請', requiresAuth: true },
  },
  {
    path: '/applications',
    name: 'MyApplications',
    component: () => import('@/views/application/MyApplicationsPage.vue'),
    meta: { title: '我的領養申請', requiresAuth: true },
  },
  {
    path: '/applications/:applicationId/documents',
    name: 'DocumentUpload',
    component: () => import('@/views/application/DocumentUploadPage.vue'),
    meta: { title: '上傳申請文件', requiresAuth: true },
  },
  {
    path: '/applications/:applicationId/status',
    name: 'ApplicationStatus',
    component: () => import('@/views/application/StatusTrackingPage.vue'),
    meta: { title: '申請狀態追蹤', requiresAuth: true },
  },
  {
    path: '/adoptions/review',
    name: 'ApplicationReview',
    component: () => import('@/views/adoption/ApplicationReviewPage.vue'),
    meta: { title: '申請審核', requiresAuth: true, requiresRole: ['shelter', 'admin'] },
  },
  {
    path: '/adoptions/applications/:id',
    name: 'ApplicationDetail',
    component: () => import('@/views/adoption/ApplicationDetailPage.vue'),
    meta: { title: '申請詳情', requiresAuth: true },
  },
  {
    path: '/review/queue',
    name: 'ReviewQueue',
    component: () => import('@/views/review/ReviewQueuePage.vue'),
    meta: { title: '審核佇列', requiresAuth: true, requiresRole: ['shelter', 'admin'] },
  },
  {
    path: '/applications/:id/confirmation',
    name: 'ConfirmationPage',
    component: () => import('@/views/confirmation/ConfirmationPage.vue'),
    meta: { title: '領養確認', requiresAuth: true },
  },
  {
    path: '/chat',
    name: 'ChatList',
    component: () => import('@/views/chat/ChatListPage.vue'),
    meta: { title: '聊天室列表', requiresAuth: true },
  },
  {
    path: '/chat/:id',
    name: 'ChatRoom',
    component: () => import('@/views/chat/ChatRoomPage.vue'),
    meta: { title: '聊天對話', requiresAuth: true },
  },
  {
    path: '/chat/test',
    name: 'ChatTest',
    component: () => import('@/views/chat/ChatTestPage.vue'),
    meta: { title: '聊天測試', requiresAuth: true },
  },
  {
    path: '/notifications',
    name: 'Notifications',
    component: () => import('@/views/notifications/NotificationsPage.vue'),
    meta: { title: '通知中心', requiresAuth: true },
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('@/views/settings/UserSettingsPage.vue'),
    meta: { title: '使用者設定', requiresAuth: true },
  },
  {
    path: '/community',
    name: 'Community',
    component: () => import('@/views/community/CommunityPage.vue'),
    meta: { title: '社群分享', requiresAuth: true },
  },
  {
    path: '/community/my-posts',
    name: 'MyPosts',
    component: () => import('@/views/community/MyPostsPage.vue'),
    meta: { title: '我的貼文', requiresAuth: true },
  },
  {
    path: '/community/:id',
    name: 'PostDetail',
    component: () => import('@/views/community/PostDetailPage.vue'),
    meta: { title: '貼文詳情', requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/user/ProfilePage.vue'),
    meta: { title: '個人檔案', requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundPage.vue'),
    meta: { title: '找不到頁面' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_to, _from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - 寵物領養平台` : '寵物領養平台'
  
  // Check authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // Check guest routes
  if (to.meta.guest && authStore.isAuthenticated) {
    next({ name: 'Home' })
    return
  }
  
  // Check role-based access
  if (to.meta.requiresRole) {
    const requiredRoles = Array.isArray(to.meta.requiresRole) 
      ? to.meta.requiresRole 
      : [to.meta.requiresRole]
    
    if (!authStore.userRole || !requiredRoles.includes(authStore.userRole)) {
      // User doesn't have required role, redirect to home
      alert('您沒有權限訪問此頁面')
      next({ name: 'Home' })
      return
    }
  }
  
  next()
})

export default router
