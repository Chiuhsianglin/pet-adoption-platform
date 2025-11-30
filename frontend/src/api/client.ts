/**
 * API Client - 統一的 API 請求客戶端
 * 使用 @/services/api 作為基礎
 */
import api from '@/services/api'

// 直接導出 api 實例作為 apiClient
export const apiClient = api

// 也提供 default export 以支持不同的 import 方式
export default api
