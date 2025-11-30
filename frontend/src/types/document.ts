export enum DocumentType {
  IDENTITY = 'identity',
  INCOME = 'income',
  RESIDENCE = 'residence',
  EXPERIENCE = 'experience',
  VETERINARY = 'veterinary',
  FAMILY_CONSENT = 'family_consent',
  LANDLORD_CONSENT = 'landlord_consent',
  OTHER = 'other'
}

export enum DocumentStatus {
  PENDING = 'pending',
  REVIEWING = 'reviewing',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  RESUBMISSION_REQUIRED = 'resubmission_required'
}

export interface DocumentUploadRequest {
  document_type: DocumentType
  description?: string
}

export interface DocumentResponse {
  id: number
  application_id: number
  document_type: DocumentType
  original_filename: string
  file_size: number
  mime_type: string
  status: DocumentStatus
  uploaded_at: string
  reviewed_at?: string
  review_notes?: string
  version: number
  is_current_version: boolean
  security_scan_status?: string
  is_safe?: boolean
  file_url?: string  // S3 URL for direct access
  preview_url?: string
  download_url?: string
  description?: string
}

export interface DocumentListResponse {
  documents: DocumentResponse[]
  required_documents: string[]
  completed_documents: string[]
  missing_documents: string[]
  total_size: number
  completion_percentage: number
}

export interface FileValidationResult {
  is_valid: boolean
  file_size: number
  mime_type: string
  detected_type: string
  errors: string[]
  warnings: string[]
}

export interface DocumentDeleteResponse {
  success: boolean
  message: string
  deleted_document_id: number
}

export interface DocumentReviewRequest {
  status: DocumentStatus
  review_notes?: string
}

export interface DocumentReviewResponse {
  id: number
  status: DocumentStatus
  reviewed_at: string
  review_notes?: string
  message: string
}

export interface UploadProgress {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  document?: DocumentResponse
}

// Display labels for document types (Chinese)
export const DocumentTypeLabels: Record<DocumentType, string> = {
  [DocumentType.IDENTITY]: '身分證明',
  [DocumentType.INCOME]: '收入證明',
  [DocumentType.RESIDENCE]: '居住證明',
  [DocumentType.EXPERIENCE]: '飼養經驗證明',
  [DocumentType.VETERINARY]: '獸醫聯繫資訊',
  [DocumentType.FAMILY_CONSENT]: '家庭同意書',
  [DocumentType.LANDLORD_CONSENT]: '房東同意書',
  [DocumentType.OTHER]: '其他文件'
}

// Display labels for document status (Chinese)
export const DocumentStatusLabels: Record<DocumentStatus, string> = {
  [DocumentStatus.PENDING]: '待審核',
  [DocumentStatus.REVIEWING]: '審核中',
  [DocumentStatus.APPROVED]: '已通過',
  [DocumentStatus.REJECTED]: '已拒絕',
  [DocumentStatus.RESUBMISSION_REQUIRED]: '需重新提交'
}

// Status colors for UI display
export const DocumentStatusColors: Record<DocumentStatus, string> = {
  [DocumentStatus.PENDING]: 'grey',
  [DocumentStatus.REVIEWING]: 'blue',
  [DocumentStatus.APPROVED]: 'green',
  [DocumentStatus.REJECTED]: 'red',
  [DocumentStatus.RESUBMISSION_REQUIRED]: 'orange'
}

// Required document types
export const REQUIRED_DOCUMENT_TYPES = [
  DocumentType.IDENTITY,
  DocumentType.INCOME,
  DocumentType.RESIDENCE
]

// Allowed file types and extensions
export const ALLOWED_FILE_TYPES = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'application/msword': ['.doc'],
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
  'text/plain': ['.txt']
}

export const MAX_FILE_SIZE = 10 * 1024 * 1024 // 10MB

// Helper functions
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

export function isImageFile(mimeType: string): boolean {
  return mimeType.startsWith('image/')
}

export function validateFileType(file: File): { valid: boolean; error?: string } {
  const allowedMimeTypes = Object.keys(ALLOWED_FILE_TYPES)
  
  if (!allowedMimeTypes.includes(file.type)) {
    return {
      valid: false,
      error: `不支援的檔案類型：${file.type}。允許的類型：PDF, JPG, PNG, DOC, DOCX, TXT`
    }
  }
  
  return { valid: true }
}

export function validateFileSize(file: File): { valid: boolean; error?: string } {
  if (file.size > MAX_FILE_SIZE) {
    return {
      valid: false,
      error: `檔案大小超過限制。最大允許：${formatFileSize(MAX_FILE_SIZE)}，當前：${formatFileSize(file.size)}`
    }
  }
  
  if (file.size === 0) {
    return {
      valid: false,
      error: '檔案大小為 0，無法上傳'
    }
  }
  
  return { valid: true }
}
