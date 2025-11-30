import api from './api'
import type {
  FileUploadResponse,
  FileMetadata,
  FileListResponse,
  FileStatsResponse,
  FileCategory,
} from '@/types/file'

export interface FileUploadOptions {
  files: File[]
  category: FileCategory
  related_id?: number
  is_public?: boolean
  onProgress?: (progress: number) => void
}

/**
 * 檔案上傳服務
 */
export const fileService = {
  /**
   * 上傳檔案
   */
  async upload(options: FileUploadOptions): Promise<FileUploadResponse> {
    const formData = new FormData()
    
    // 添加檔案
    options.files.forEach(file => {
      formData.append('files', file)
    })
    
    // 添加分類
    formData.append('category', options.category)

    const response = await api.post<FileUploadResponse>('/files/upload', formData, {
      onUploadProgress: (progressEvent) => {
        if (options.onProgress && progressEvent.total) {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          options.onProgress(percentCompleted)
        }
      },
    })

    return response.data
  },

  /**
   * 獲取檔案資訊
   */
  async getFile(fileId: number): Promise<FileMetadata> {
    const response = await api.get<FileMetadata>(`/files/${fileId}`)
    return response.data
  },

  /**
   * 刪除檔案
   */
  async deleteFile(fileId: number): Promise<{ success: boolean; message: string }> {
    const response = await api.delete<{ success: boolean; message: string }>(
      `/files/${fileId}`
    )
    return response.data
  },

  /**
   * 獲取檔案列表
   */
  async listFiles(params?: {
    category?: FileCategory
    related_id?: number
    page?: number
    page_size?: number
  }): Promise<FileListResponse> {
    const response = await api.get<FileListResponse>('/files', { params })
    return response.data
  },

  /**
   * 獲取檔案統計
   */
  async getStats(): Promise<FileStatsResponse> {
    const response = await api.get<FileStatsResponse>('/files/stats/summary')
    return response.data
  },

  /**
   * 驗證檔案類型
   */
  validateFileType(file: File, allowedTypes: string[]): boolean {
    return allowedTypes.some(type => {
      if (type.endsWith('/*')) {
        return file.type.startsWith(type.replace('/*', ''))
      }
      return file.type === type
    })
  },

  /**
   * 驗證檔案大小
   */
  validateFileSize(file: File, maxSize: number): boolean {
    return file.size <= maxSize
  },

  /**
   * 格式化檔案大小
   */
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
  },
}
