import api from '@/services/api'

export interface VaccinationResponse {
  id: number
  pet_id: number
  administered_by: number | null
  vaccine_name: string
  vaccine_type: 'core' | 'non_core' | 'optional'
  batch_number: string | null
  manufacturer: string | null
  administration_date: string | null
  scheduled_date: string | null
  status: 'completed' | 'scheduled' | 'overdue' | 'cancelled'
  clinic_name: string | null
  veterinarian_name: string | null
  veterinarian_license: string | null
  next_due_date: string | null
  notes: string | null
  adverse_reactions: string | null
  created_at: string
  updated_at: string
}

export interface VaccinationSummary {
  total_count: number
  completed_count: number
  scheduled_count: number
  overdue_count: number
  cancelled_count: number
  next_due_date: string | null
}

export interface ApiResponse<T> {
  success: boolean
  message: string
  data: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/**
 * 獲取寵物的疫苗接種記錄
 */
export const getVaccinations = async (petId: number, page = 1, pageSize = 10) => {
  const response = await api.get<ApiResponse<PaginatedResponse<VaccinationResponse>>>(
    `/vaccinations/pets/${petId}/vaccinations`,
    {
      params: { page, page_size: pageSize }
    }
  )
  return response.data
}

/**
 * 獲取疫苗接種摘要統計
 */
export const getVaccinationSummary = async (petId: number) => {
  const response = await api.get<ApiResponse<VaccinationSummary>>(
    `/vaccinations/pets/${petId}/vaccinations/summary`
  )
  return response.data
}

export default {
  getVaccinations,
  getVaccinationSummary
}
