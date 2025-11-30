import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
  AxiosResponse,
} from 'axios'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import router from '@/router'
import { getApiConfig } from '@/config/api'

// 使用 V2 API 配置
const apiConfig = getApiConfig()
const api: AxiosInstance = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor - 加上 token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const authStore = useAuthStore()
    if (authStore.token) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    }
    
    // 如果是 FormData，移除 Content-Type 讓瀏覽器自動設定（包含 boundary）
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type']
    }
    
    return config
  },
  (error: AxiosError) => Promise.reject(error)
)

// ✅ Response interceptor - 統一錯誤處理
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  async (error: AxiosError<any>) => {
    const notificationStore = useNotificationStore()
    const authStore = useAuthStore()

    if (error.response) {
      const status = error.response.status
      const errorData = error.response.data

      switch (status) {
        case 401:
          notificationStore.error('登入已過期，請重新登入')
          authStore.logout()
          router.push('/auth/login')
          break
        case 403:
          notificationStore.error('您沒有權限執行此操作')
          break
        case 404:
          notificationStore.error('請求的資源不存在')
          break
        case 422:
          notificationStore.error(errorData.error?.message || '資料驗證失敗')
          break
        case 500:
          notificationStore.error('伺服器錯誤，請稍後再試')
          break
        default:
          notificationStore.error(errorData.error?.message || '發生錯誤，請稍後再試')
      }
    } else if (error.request) {
      notificationStore.error('無法連接到伺服器')
    } else {
      notificationStore.error('發生未知錯誤')
    }

    return Promise.reject(error)
  }
)

export default api
