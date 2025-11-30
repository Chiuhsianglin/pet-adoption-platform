/**
 * Review System API Client (Story 3.4 MVP)
 */
import apiClient from './client'

// ==================== Types ====================

export interface ReviewDecision {
  id: number
  application_id: number
  reviewer_id: number
  decision: 'approved' | 'rejected' | 'needs_info' | 'pending'
  decision_reason?: string
  recommendations?: string
  overall_score?: number
  conditions?: string[]
  review_started?: string
  review_completed: string
  time_spent_minutes?: number
  is_final: boolean
  created_at: string
  updated_at: string
  reviewer_name?: string
}

export interface ApplicationQueueItem {
  id: number  // Story 3.5: Added for document requests
  application_id: number
  applicant_id: number
  applicant_name: string
  pet_id: number
  pet_name: string
  status: string
  submitted_at: string
  days_since_submitted: number
  priority: 'low' | 'medium' | 'high' | 'urgent'
  documents_complete: boolean
  total_documents: number
  latest_comment?: string
}

export interface ReviewQueueResponse {
  items: ApplicationQueueItem[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface ReviewStatistics {
  pending_count: number
  today_completed: number
  week_completed: number
  avg_processing_time_minutes: number
  approval_rate: number
}

export interface ReviewDashboardResponse {
  statistics: ReviewStatistics
  pending_reviews: ApplicationQueueItem[]
  last_updated: string
}

export interface ReviewDecisionCreate {
  decision: 'approved' | 'rejected' | 'needs_info' | 'pending'
  decision_reason?: string
  recommendations?: string
  overall_score?: number
  conditions?: string[]
  is_final?: boolean
}

// ==================== API Functions ====================

/**
 * Get review dashboard data
 */
export const getReviewDashboard = async (): Promise<ReviewDashboardResponse> => {
  const response = await apiClient.get('/review/dashboard')
  return response.data.data
}

/**
 * Get review queue with filtering and pagination
 */
export const getReviewQueue = async (
  statusFilter?: string,
  page: number = 1,
  perPage: number = 20
): Promise<ReviewQueueResponse> => {
  const params: any = { page, per_page: perPage }
  if (statusFilter && statusFilter !== 'all') {
    params.status_filter = statusFilter
  }
  
  const response = await apiClient.get('/review/queue', { params })
  return response.data.data
}

/**
 * Submit review decision
 */
export const submitReviewDecision = async (
  applicationId: number,
  decision: ReviewDecisionCreate,
  reviewStarted?: Date
): Promise<ReviewDecision> => {
  const params: any = {}
  if (reviewStarted) {
    params.review_started = reviewStarted.toISOString()
  }
  
  const response = await apiClient.post(
    `/review/applications/${applicationId}/decisions`,
    decision,
    { params }
  )
  return response.data.data
}

/**
 * Get review decision history for an application
 */
export const getReviewDecisionHistory = async (
  applicationId: number
): Promise<ReviewDecision[]> => {
  const response = await apiClient.get(`/review/applications/${applicationId}/decisions`)
  return response.data.data
}

// ==================== Helper Functions ====================

/**
 * Get priority color
 */
export const getPriorityColor = (priority: string): string => {
  const colors: Record<string, string> = {
    low: 'grey',
    medium: 'info',
    high: 'warning',
    urgent: 'error',
  }
  return colors[priority] || 'grey'
}

/**
 * Get priority icon
 */
export const getPriorityIcon = (priority: string): string => {
  const icons: Record<string, string> = {
    low: 'mdi-flag-outline',
    medium: 'mdi-flag',
    high: 'mdi-flag',
    urgent: 'mdi-alert',
  }
  return icons[priority] || 'mdi-flag-outline'
}

/**
 * Get decision display name
 */
export const getDecisionDisplayName = (decision: string): string => {
  const names: Record<string, string> = {
    approved: '批准',
    rejected: '拒絕',
    needs_info: '需補充資料',
    pending: '待定',
  }
  return names[decision] || decision
}

/**
 * Get decision color
 */
export const getDecisionColor = (decision: string): string => {
  const colors: Record<string, string> = {
    approved: 'success',
    rejected: 'error',
    needs_info: 'warning',
    pending: 'info',
  }
  return colors[decision] || 'grey'
}

/**
 * Format time duration in minutes
 */
export const formatDuration = (minutes: number): string => {
  if (minutes < 60) {
    return `${minutes} 分鐘`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours} 小時 ${mins} 分鐘` : `${hours} 小時`
}
