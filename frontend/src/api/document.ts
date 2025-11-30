import api from '@/services/api'
import type {
  DocumentResponse,
  DocumentListResponse,
  DocumentDeleteResponse,
  DocumentReviewRequest,
  DocumentReviewResponse
} from '@/types/document'

/**
 * Upload a document for an application
 */
export async function uploadDocument(
  applicationId: number,
  file: File,
  documentType: string,
  description?: string,
  onProgress?: (progress: number) => void
): Promise<DocumentResponse> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('document_type', documentType)
  if (description) {
    formData.append('description', description)
  }

  const response = await api.post<DocumentResponse>(
    `/adoptions/applications/${applicationId}/documents`,
    formData,
    {
      onUploadProgress: (progressEvent: any) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(percentCompleted)
        }
      }
    }
  )

  return response.data
}

/**
 * Get list of documents for an application
 */
export async function getDocumentList(applicationId: number): Promise<DocumentListResponse> {
  const response = await api.get<DocumentListResponse>(
    `/adoptions/applications/${applicationId}/documents`
  )

  return response.data
}

/**
 * Delete a document
 */
export async function deleteDocument(
  applicationId: number,
  documentId: number
): Promise<DocumentDeleteResponse> {
  const response = await api.delete<DocumentDeleteResponse>(
    `/adoptions/applications/${applicationId}/documents/${documentId}`
  )

  return response.data
}

/**
 * Get download URL for a document
 */
export function getDocumentDownloadUrl(documentId: number): string {
  return `/documents/documents/${documentId}/download`
}

/**
 * Get preview URL for a document (images only)
 */
export function getDocumentPreviewUrl(documentId: number): string {
  return `/documents/documents/${documentId}/preview`
}

/**
 * Download a document
 */
export async function downloadDocument(documentId: number, filename?: string): Promise<void> {
  const response = await api.get(
    `/documents/documents/${documentId}/download`,
    {
      responseType: 'blob'
    }
  )

  // Get filename from response headers or use provided filename
  const contentDisposition = response.headers['content-disposition']
  let downloadFilename = filename || 'document'
  
  if (contentDisposition) {
    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/)
    if (filenameMatch) {
      downloadFilename = filenameMatch[1]
    }
  }

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', downloadFilename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

/**
 * Get version history for a document
 */
export async function getDocumentVersions(documentId: number): Promise<DocumentResponse[]> {
  const response = await api.get<DocumentResponse[]>(
    `/documents/documents/${documentId}/versions`
  )

  return response.data
}

/**
 * Review a document (admin/staff only)
 */
export async function reviewDocument(
  documentId: number,
  reviewData: DocumentReviewRequest
): Promise<DocumentReviewResponse> {
  const response = await api.put<DocumentReviewResponse>(
    `/documents/documents/${documentId}/review`,
    reviewData
  )

  return response.data
}

/**
 * Revert to a previous document version
 */
export async function revertDocumentVersion(
  documentId: number,
  versionId: number
): Promise<DocumentResponse> {
  const response = await api.put<DocumentResponse>(
    `/documents/documents/${documentId}/revert/${versionId}`,
    {}
  )

  return response.data
}
