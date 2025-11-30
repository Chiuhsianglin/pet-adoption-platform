/**
 * Document Request API Client (Story 3.5 - Option C)
 */
import apiClient from './client'

// ===== Types =====

export interface DocumentRequest {
  id: number
  application_id: number
  requester_id: number
  requested_documents: string[]
  request_reason: string
  due_date: string | null
  status: 'pending' | 'submitted' | 'approved' | 'rejected'
  response_note: string | null
  created_at: string
  updated_at: string
  submitted_at: string | null
  reviewed_at: string | null
}

export interface DocumentRequestCreate {
  requested_documents: string[]
  request_reason: string
  due_date?: string
}

export interface DocumentRequestUpdate {
  status: 'pending' | 'submitted' | 'approved' | 'rejected'
  response_note?: string
}

export interface DocumentRequestListResponse {
  requests: DocumentRequest[]
  total: number
}

// ===== API Functions =====

/**
 * 創建文件補件請求
 */
export async function createDocumentRequest(
  applicationId: number,
  data: DocumentRequestCreate
): Promise<DocumentRequest> {
  const response = await apiClient.post(
    `/applications/${applicationId}/document-requests`,
    data
  )
  return response.data.data
}

/**
 * 取得申請的所有補件請求
 */
export async function getDocumentRequests(
  applicationId: number
): Promise<DocumentRequestListResponse> {
  const response = await apiClient.get(
    `/applications/${applicationId}/document-requests`
  )
  return response.data.data
}

/**
 * 更新補件請求狀態
 */
export async function updateDocumentRequestStatus(
  requestId: number,
  data: DocumentRequestUpdate
): Promise<DocumentRequest> {
  const response = await apiClient.put(
    `/document-requests/${requestId}/status`,
    data
  )
  return response.data.data
}

// ===== Helper Functions =====

/**
 * 取得狀態顯示名稱
 */
export function getStatusDisplayName(status: string): string {
  const statusMap: Record<string, string> = {
    pending: '待補件',
    submitted: '已提交',
    approved: '已通過',
    rejected: '已拒絕'
  }
  return statusMap[status] || status
}

/**
 * 取得狀態顏色
 */
export function getStatusColor(status: string): string {
  const colorMap: Record<string, string> = {
    pending: 'warning',
    submitted: 'info',
    approved: 'success',
    rejected: 'error'
  }
  return colorMap[status] || 'default'
}

/**
 * 常見文件類型選項
 */
export const COMMON_DOCUMENT_TYPES = [
  '身份證明',
  '收入證明',
  '居住證明',
  '飼養經驗證明',
  '獸醫聯繫資訊',
  '家庭同意書',
  '房東同意書'
]
