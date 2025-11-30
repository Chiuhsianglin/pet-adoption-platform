/**
 * Application Status Tracking API Client (Story 3.3 MVP)
 */
import apiClient from './client'

export interface TimelineEvent {
  id: number
  status: string
  previous_status?: string
  created_at: string
  changed_by: string
  change_reason?: string
  notes?: string
  estimated_completion?: string
  actual_completion?: string
  is_milestone: boolean
  metadata?: Record<string, any>
}

export interface TimelineResponse {
  events: TimelineEvent[]
  current_status: string
  progress_percentage: number
  total_duration_days?: number
  estimated_completion?: string
  milestones_completed: number
  milestones_total: number
}

export interface ApplicationStatusResponse {
  current_status: string
  previous_status?: string
  changed_at: string
  changed_by: string
  progress_percentage: number
  estimated_completion?: string
  next_steps: string[]
  required_actions: string[]
}

export interface ReviewComment {
  id: number
  comment: string
  comment_type: string
  reviewer_name: string
  reviewer_role: string
  is_internal: boolean
  is_required_action: boolean
  is_resolved: boolean
  created_at: string
  updated_at: string
  resolved_at?: string
  resolved_by_name?: string
  resolution_comment?: string
}

export interface StatusUpdateRequest {
  status: string
  reason?: string
  notes?: string
  estimated_completion?: string
  notify_applicant?: boolean
}

export interface ReviewCommentCreate {
  comment: string
  comment_type?: string
  is_internal?: boolean
  is_required_action?: boolean
}

/**
 * Get current application status
 */
export const getApplicationStatus = async (
  applicationId: number
): Promise<ApplicationStatusResponse> => {
  const response = await apiClient.get(`/applications/${applicationId}/status`)
  return response.data.data
}

/**
 * Update application status
 */
export const updateApplicationStatus = async (
  applicationId: number,
  statusUpdate: StatusUpdateRequest
): Promise<ApplicationStatusResponse> => {
  const response = await apiClient.put(
    `/applications/${applicationId}/status`,
    statusUpdate
  )
  return response.data.data
}

/**
 * Get application timeline
 */
export const getApplicationTimeline = async (
  applicationId: number
): Promise<TimelineResponse> => {
  const response = await apiClient.get(`/applications/${applicationId}/timeline`)
  return response.data.data
}

/**
 * Add review comment
 */
export const addReviewComment = async (
  applicationId: number,
  comment: ReviewCommentCreate
): Promise<ReviewComment> => {
  const response = await apiClient.post(
    `/applications/${applicationId}/comments`,
    comment
  )
  return response.data.data
}

/**
 * Get review comments
 */
export const getReviewComments = async (
  applicationId: number,
  includeInternal: boolean = false
): Promise<ReviewComment[]> => {
  const response = await apiClient.get(
    `/applications/${applicationId}/comments`,
    { params: { include_internal: includeInternal } }
  )
  return response.data.data
}

/**
 * Resolve review comment
 */
export const resolveReviewComment = async (
  commentId: number,
  resolutionComment?: string
): Promise<ReviewComment> => {
  const response = await apiClient.put(
    `/comments/${commentId}/resolve`,
    { resolution_comment: resolutionComment }
  )
  return response.data.data
}

/**
 * Get status display name (Chinese)
 */
export const getStatusDisplayName = (status: string): string => {
  const statusNames: Record<string, string> = {
    draft: '草稿',
    submitted: '已提交',
    document_review: '文件審核中',
    document_incomplete: '文件不完整',
    background_check: '背景調查',
    interview_scheduled: '面試已安排',
    interview_completed: '面試已完成',
    home_visit_scheduled: '家訪已安排',
    home_visit_completed: '家訪已完成',
    under_review: '審核中',
    approved: '已通過',
    rejected: '已拒絕',
    withdrawn: '已撤回',
    paused: '已暫停',
    completed: '已完成'
  }
  return statusNames[status] || status
}

/**
 * Get status color
 */
export const getStatusColor = (status: string): string => {
  const colorMap: Record<string, string> = {
    draft: 'grey',
    submitted: 'blue',
    document_review: 'orange',
    document_incomplete: 'red',
    background_check: 'purple',
    interview_scheduled: 'indigo',
    interview_completed: 'teal',
    home_visit_scheduled: 'cyan',
    home_visit_completed: 'green',
    under_review: 'amber',
    approved: 'success',
    rejected: 'error',
    withdrawn: 'grey',
    paused: 'warning',
    completed: 'success'
  }
  return colorMap[status] || 'grey'
}

/**
 * Get status icon
 */
export const getStatusIcon = (status: string): string => {
  const iconMap: Record<string, string> = {
    draft: 'mdi-file-document-edit-outline',
    submitted: 'mdi-send',
    document_review: 'mdi-file-search',
    document_incomplete: 'mdi-file-alert',
    background_check: 'mdi-shield-search',
    interview_scheduled: 'mdi-calendar-account',
    interview_completed: 'mdi-account-check',
    home_visit_scheduled: 'mdi-home-search',
    home_visit_completed: 'mdi-home-check',
    under_review: 'mdi-clipboard-text-search',
    approved: 'mdi-check-circle',
    rejected: 'mdi-close-circle',
    withdrawn: 'mdi-undo',
    paused: 'mdi-pause-circle',
    completed: 'mdi-flag-checkered'
  }
  return iconMap[status] || 'mdi-circle'
}
