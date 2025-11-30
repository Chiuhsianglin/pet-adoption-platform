/**
 * Unit tests for Pet API Service
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { petApi } from '@/services/pet'
import axios from 'axios'

// Mock axios
vi.mock('axios')
const mockedAxios = axios as jest.Mocked<typeof axios>

describe('Pet API Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  describe('getPets', () => {
    it('fetches pets list successfully', async () => {
      const mockResponse = {
        data: {
          success: true,
          data: {
            pets: [
              { id: 1, name: '小白', species: 'dog' },
              { id: 2, name: '小黑', species: 'cat' },
            ],
            pagination: {
              page: 1,
              limit: 10,
              total: 2,
              pages: 1
            }
          }
        }
      }
      
      mockedAxios.get.mockResolvedValue(mockResponse)
      
      const result = await petApi.getPets({ page: 1, limit: 10 })
      
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/pets/my-pets', {
        params: { page: 1, limit: 10 }
      })
      expect(result.data.pets).toHaveLength(2)
    })
  })
  
  describe('createPet', () => {
    it('creates a new pet successfully', async () => {
      const petData = {
        name: '測試寵物',
        species: 'dog',
        breed: '柴犬',
        age_months: 12,
      }
      
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: 1,
            ...petData,
            status: 'draft'
          }
        }
      }
      
      mockedAxios.post.mockResolvedValue(mockResponse)
      
      const result = await petApi.createPet(petData)
      
      expect(mockedAxios.post).toHaveBeenCalledWith('/api/v1/pets', petData)
      expect(result.data.name).toBe('測試寵物')
    })
  })
  
  describe('updatePet', () => {
    it('updates a pet successfully', async () => {
      const petId = 1
      const updateData = {
        description: '更新描述',
        adoption_fee: 5000
      }
      
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: petId,
            ...updateData
          }
        }
      }
      
      mockedAxios.put.mockResolvedValue(mockResponse)
      
      const result = await petApi.updatePet(petId, updateData)
      
      expect(mockedAxios.put).toHaveBeenCalledWith(`/api/v1/pets/${petId}`, updateData)
      expect(result.data.description).toBe('更新描述')
    })
  })
  
  describe('submitForReview', () => {
    it('submits pet for review successfully', async () => {
      const petId = 1
      
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: petId,
            status: 'pending_review'
          }
        }
      }
      
      mockedAxios.post.mockResolvedValue(mockResponse)
      
      const result = await petApi.submitForReview(petId)
      
      expect(mockedAxios.post).toHaveBeenCalledWith(`/api/v1/pets/${petId}/submit-review`)
      expect(result.data.status).toBe('pending_review')
    })
  })
  
  describe('approvePet', () => {
    it('approves pet successfully', async () => {
      const petId = 1
      const reason = '審核通過'
      
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: petId,
            status: 'available'
          }
        }
      }
      
      mockedAxios.put.mockResolvedValue(mockResponse)
      
      const result = await petApi.approvePet(petId, reason)
      
      expect(mockedAxios.put).toHaveBeenCalledWith(`/api/v1/pets/${petId}/approve`, { reason })
      expect(result.data.status).toBe('available')
    })
  })
  
  describe('rejectPet', () => {
    it('rejects pet with reason', async () => {
      const petId = 1
      const reason = '照片品質不佳'
      
      const mockResponse = {
        data: {
          success: true,
          data: {
            id: petId,
            status: 'rejected'
          }
        }
      }
      
      mockedAxios.put.mockResolvedValue(mockResponse)
      
      const result = await petApi.rejectPet(petId, reason)
      
      expect(mockedAxios.put).toHaveBeenCalledWith(`/api/v1/pets/${petId}/reject`, { reason })
      expect(result.data.status).toBe('rejected')
    })
  })
  
  describe('deletePet', () => {
    it('deletes a pet successfully', async () => {
      const petId = 1
      
      mockedAxios.delete.mockResolvedValue({ data: { success: true } })
      
      await petApi.deletePet(petId)
      
      expect(mockedAxios.delete).toHaveBeenCalledWith(`/api/v1/pets/${petId}`)
    })
  })
})
