/**
 * API Configuration
 * 使用 V2 API
 */

export interface ApiConfig {
  baseURL: string
  timeout: number
}

/**
 * 取得完整的 API 基礎 URL
 */
export function getApiBaseURL(): string {
  const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  
  // 移除可能的版本號後綴
  const cleanBaseURL = baseURL.replace(/\/api\/v[12]$/, '')
  
  return `${cleanBaseURL}/api/v2`
}

/**
 * 取得完整的 API 配置
 */
export function getApiConfig(): ApiConfig {
  return {
    baseURL: getApiBaseURL(),
    timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
  }
}
