/**
 * 領養確認 API Client (Story 3.6 - MVP)
 */
import client from './client'

/**
 * 確認狀態
 */
export type ConfirmationStatus = 'pending' | 'approved' | 'rejected' | 'completed'

/**
 * 交接狀態
 */
export type HandoverStatus = 'scheduled' | 'in_progress' | 'completed' | 'cancelled'

/**
 * 交接安排
 */
export interface HandoverSchedule {
  id: number
  confirmation_id: number
  handover_date: string
  handover_time?: string
  location: string
  contact_person?: string
  contact_phone?: string
  items_checklist?: string
  special_instructions?: string
  status: HandoverStatus
  completed_at?: string
  completed_notes?: string
  created_at: string
  updated_at: string
}

/**
 * 確認記錄
 */
export interface Confirmation {
  id: number
  application_id: number
  status: ConfirmationStatus
  approved_by?: number
  approved_at?: string
  approval_notes?: string
  conditions?: string
  requirements_met: boolean
  completed_at?: string
  created_at: string
  updated_at: string
}

/**
 * 確認 + 交接資訊
 */
export interface ConfirmationWithHandover {
  confirmation: Confirmation
  handover?: HandoverSchedule
}

/**
 * 創建確認請求
 */
export interface CreateConfirmationRequest {
  approval_notes?: string
  conditions?: string
}

/**
 * 核准確認請求
 */
export interface ApproveConfirmationRequest {
  approval_notes: string
  conditions?: string
}

/**
 * 創建交接安排請求
 */
export interface CreateHandoverRequest {
  handover_date: string
  handover_time?: string
  location: string
  contact_person?: string
  contact_phone?: string
  items_checklist?: string
  special_instructions?: string
}

/**
 * 更新交接安排請求
 */
export interface UpdateHandoverRequest {
  handover_date?: string
  handover_time?: string
  location?: string
  contact_person?: string
  contact_phone?: string
  items_checklist?: string
  special_instructions?: string
  status?: HandoverStatus
  completed_notes?: string
}

/**
 * API 回應
 */
interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

/**
 * 創建確認記錄
 */
export async function createConfirmation(
  applicationId: number,
  data: CreateConfirmationRequest
): Promise<Confirmation> {
  const response = await client.post<ApiResponse<Confirmation>>(
    `/applications/${applicationId}/confirmations`,
    data
  )
  return response.data.data
}

/**
 * 核准確認
 */
export async function approveConfirmation(
  confirmationId: number,
  data: ApproveConfirmationRequest
): Promise<Confirmation> {
  const response = await client.put<ApiResponse<Confirmation>>(
    `/confirmations/${confirmationId}/approve`,
    data
  )
  return response.data.data
}

/**
 * 取得確認資訊
 */
export async function getConfirmation(
  applicationId: number
): Promise<ConfirmationWithHandover> {
  const response = await client.get<ApiResponse<ConfirmationWithHandover>>(
    `/applications/${applicationId}/confirmations`
  )
  return response.data.data
}

/**
 * 創建交接安排
 */
export async function createHandover(
  confirmationId: number,
  data: CreateHandoverRequest
): Promise<HandoverSchedule> {
  const response = await client.post<ApiResponse<HandoverSchedule>>(
    `/confirmations/${confirmationId}/handover`,
    data
  )
  return response.data.data
}

/**
 * 更新交接安排
 */
export async function updateHandover(
  handoverId: number,
  data: UpdateHandoverRequest
): Promise<HandoverSchedule> {
  const response = await client.put<ApiResponse<HandoverSchedule>>(
    `/handovers/${handoverId}`,
    data
  )
  return response.data.data
}

/**
 * 完成確認
 */
export async function completeConfirmation(
  confirmationId: number
): Promise<Confirmation> {
  const response = await client.post<ApiResponse<Confirmation>>(
    `/confirmations/${confirmationId}/complete`
  )
  return response.data.data
}

/**
 * 取得確認狀態顯示名稱
 */
export function getConfirmationStatusDisplayName(status: ConfirmationStatus): string {
  const statusMap: Record<ConfirmationStatus, string> = {
    pending: '待核准',
    approved: '已核准',
    rejected: '已拒絕',
    completed: '已完成'
  }
  return statusMap[status] || status
}

/**
 * 取得確認狀態顏色
 */
export function getConfirmationStatusColor(status: ConfirmationStatus): string {
  const colorMap: Record<ConfirmationStatus, string> = {
    pending: 'warning',
    approved: 'success',
    rejected: 'error',
    completed: 'info'
  }
  return colorMap[status] || 'default'
}

/**
 * 取得交接狀態顯示名稱
 */
export function getHandoverStatusDisplayName(status: HandoverStatus): string {
  const statusMap: Record<HandoverStatus, string> = {
    scheduled: '已安排',
    in_progress: '進行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

/**
 * 取得交接狀態顏色
 */
export function getHandoverStatusColor(status: HandoverStatus): string {
  const colorMap: Record<HandoverStatus, string> = {
    scheduled: 'primary',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'error'
  }
  return colorMap[status] || 'default'
}

/**
 * 常用交接項目檢查表
 */
export const COMMON_HANDOVER_ITEMS = [
  '寵物本體',
  '疫苗接種紀錄',
  '健康檢查報告',
  '晶片登記證明',
  '飼養用品',
  '飼料樣品',
  '藥品 (如有)',
  '說明書/注意事項'
]
