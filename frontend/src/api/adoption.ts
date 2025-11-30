/**
 * Adoption API
 */
import apiClient from './client'
import type {
  AdoptionApplicationCreate,
  AdoptionApplicationUpdate,
  AdoptionApplication,
  AdoptionApplicationList
} from '@/types/adoption'

const BASE_URL = '/adoptions'

export const adoptionApi = {
  /**
   * Create new adoption application
   */
  async createApplication(data: AdoptionApplicationCreate): Promise<AdoptionApplication> {
    const response = await apiClient.post(`${BASE_URL}/applications`, data)
    return response.data
  },

  /**
   * Update adoption application
   */
  async updateApplication(
    applicationId: number,
    data: AdoptionApplicationUpdate
  ): Promise<AdoptionApplication> {
    const response = await apiClient.put(`${BASE_URL}/applications/${applicationId}`, data)
    return response.data
  },

  /**
   * Get adoption application by ID
   */
  async getApplication(applicationId: number): Promise<AdoptionApplication> {
    const response = await apiClient.get(`${BASE_URL}/applications/${applicationId}`)
    return response.data
  },

  /**
   * Submit application for review
   */
  async submitApplication(applicationId: number): Promise<AdoptionApplication> {
    const response = await apiClient.post(`${BASE_URL}/applications/${applicationId}/submit`)
    return response.data
  },

  /**
   * Delete draft application
   */
  async deleteApplication(applicationId: number): Promise<{ message: string }> {
    const response = await apiClient.delete(`${BASE_URL}/applications/${applicationId}`)
    return response.data
  },

  /**
   * Get user's adoption applications
   */
  async getUserApplications(skip = 0, limit = 10): Promise<AdoptionApplicationList> {
    const response = await apiClient.get(`${BASE_URL}/applications`, {
      params: { skip, limit }
    })
    return response.data
  }
}
