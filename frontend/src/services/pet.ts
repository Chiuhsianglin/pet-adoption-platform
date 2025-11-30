/**
 * Pet API Service
 * Handles all pet-related API requests
 */

import api from './api'
import type {
  Pet,
  PetCreate,
  PetUpdate,
  PetListParams,
  PetListResponse,
  PetHistoryResponse,
  PetReviewSubmit,
  PetReviewAction,
  PetStatusUpdate,
} from '@/types/pet'

/**
 * Pet Management API
 */
export const petService = {
  /**
   * Get list of pets
   */
  async getPets(params?: PetListParams): Promise<PetListResponse> {
    const response = await api.get('/pets', { params })
    return response.data.data
  },

  /**
   * Get my pets (shelter admin)
   */
  async getMyPets(params?: PetListParams): Promise<PetListResponse> {
    const response = await api.get('/pets/my-pets', { params })
    // V2 API 直接返回數據，不包裝在 data 中
    return response.data
  },

  /**
   * Get pet by ID
   */
  async getPetById(id: number): Promise<Pet> {
    const response = await api.get(`/pets/${id}`)
    return response.data.data
  },

  /**
   * Create new pet
   */
  async createPet(data: PetCreate): Promise<Pet> {
    const response = await api.post('/pets', data)
    // V2 API 直接返回數據，不包裝在 data 中
    return response.data
  },

  /**
   * Update pet
   */
  async updatePet(id: number, data: PetUpdate): Promise<Pet> {
    const response = await api.put(`/pets/${id}`, data)
    // V2 API 直接返回數據，不包裝在 data 中
    return response.data
  },

  /**
   * Delete pet
   */
  async deletePet(id: number): Promise<void> {
    await api.delete(`/pets/${id}`)
  },

  /**
   * Update pet status
   */
  async updateStatus(id: number, data: PetStatusUpdate): Promise<Pet> {
    const response = await api.put(`/pets/${id}/status`, data)
    // V2 API 直接返回數據，不包裝在 data 中
    return response.data
  },

  /**
   * Submit pet for review
   */
  async submitForReview(id: number, data?: PetReviewSubmit): Promise<void> {
    await api.post(`/pets/${id}/submit-review`, data || {})
  },

  /**
   * Approve pet (admin only)
   */
  async approvePet(id: number, data: PetReviewAction): Promise<void> {
    await api.put(`/pets/${id}/approve`, data)
  },

  /**
   * Reject pet (admin only)
   */
  async rejectPet(id: number, data: PetReviewAction): Promise<void> {
    await api.put(`/pets/${id}/reject`, data)
  },

  /**
   * Get pet history
   */
  async getPetHistory(id: number, limit?: number): Promise<PetHistoryResponse> {
    const response = await api.get(`/pets/${id}/history`, {
      params: { limit },
    })
    return response.data.data
  },

  /**
   * Add photo to pet
   */
  async addPhoto(petId: number, fileId: number, displayOrder: number = 0): Promise<void> {
    await api.post(`/pets/${petId}/photos`, {
      file_id: fileId,
      display_order: displayOrder,
    })
  },

  /**
   * Link uploaded photos to pet
   */
  async linkPhotos(petId: number, photos: any[]): Promise<void> {
    await api.post(`/pets/${petId}/photos/link`, {
      photos: photos.map(p => ({
        url: p.url || p.file_url,
        file_url: p.url || p.file_url,
        file_key: p.file_key,
      })),
    })
  },

  /**
   * Set primary photo
   */
  async setPrimaryPhoto(petId: number, photoId: number): Promise<void> {
    await api.put(`/pets/${petId}/photos/${photoId}/primary`)
  },

  /**
   * Delete photo
   */
  async deletePhoto(petId: number, photoId: number): Promise<void> {
    await api.delete(`/pets/${petId}/photos/${photoId}`)
  },

  /**
   * Refresh photo URLs (for expired presigned URLs)
   */
  async refreshPhotoUrls(petId: number): Promise<any[]> {
    const response = await api.post(`/pets/${petId}/photos/refresh-urls`)
    return response.data.data || []
  },
}

export default petService
