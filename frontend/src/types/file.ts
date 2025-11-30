/**
 * 檔案上傳相關類型定義
 */

export type FileCategory = 'pet_photo' | 'document' | 'avatar'

export interface FileMetadata {
  id: number | string
  filename: string
  original_filename?: string
  file_size: number
  mime_type?: string
  file_hash?: string
  storage_path?: string
  category: FileCategory
  related_id?: number
  uploaded_by?: number
  is_public?: boolean
  is_deleted?: boolean
  created_at?: string
  file_url?: string  // Direct URL to the file
  file_key?: string  // S3 key or storage identifier
  urls: {
    thumbnail?: string
    medium?: string
    large?: string
    original?: string
  }
}

export interface FileUploadResponse {
  success: boolean
  message: string
  files: FileMetadata[]
}

export interface FileListResponse {
  files: FileMetadata[]
  total: number
  page: number
  page_size: number
}

export interface FileStatsResponse {
  total_files: number
  total_size: number
  by_category: {
    [key: string]: {
      count: number
      size: number
    }
  }
}

export interface UploadProgress {
  id: string
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'processing' | 'success' | 'error'
  error?: string
  preview?: string
  result?: FileMetadata
}
