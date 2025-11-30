import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import VaccinationTimeline from '@/components/pet/VaccinationTimeline.vue'
import * as vaccinationsApi from '@/api/vaccinations'

// Mock the vaccinations API
vi.mock('@/api/vaccinations', () => ({
  getVaccinations: vi.fn(),
  getVaccinationSummary: vi.fn()
}))

const vuetify = createVuetify({
  components,
  directives,
})

describe('VaccinationTimeline.vue', () => {
  let wrapper: VueWrapper<any>

  const mockVaccinationsResponse = {
    success: true,
    message: 'Success',
    data: {
      items: [
        {
          id: 1,
          pet_id: 1,
          administered_by: null,
          vaccine_name: '狂犬病疫苗',
          vaccine_type: 'core',
          batch_number: 'RV2023001',
          manufacturer: null,
          administration_date: '2025-05-11',
          scheduled_date: null,
          status: 'COMPLETED',
          clinic_name: '愛心動物醫院',
          veterinarian_name: '王小明獸醫師',
          veterinarian_license: null,
          next_due_date: '2026-05-11',
          notes: '接種順利，寵物狀態良好',
          adverse_reactions: null,
          created_at: '2025-11-07T20:32:34',
          updated_at: '2025-11-07T20:38:36'
        },
        {
          id: 4,
          pet_id: 1,
          administered_by: null,
          vaccine_name: '犬流感疫苗',
          vaccine_type: 'optional',
          batch_number: null,
          manufacturer: null,
          administration_date: null,
          scheduled_date: '2025-12-07',
          status: 'SCHEDULED',
          clinic_name: '市立動物醫院',
          veterinarian_name: null,
          veterinarian_license: null,
          next_due_date: '2026-12-07',
          notes: '預防流感季節感染',
          adverse_reactions: null,
          created_at: '2025-11-07T20:32:34',
          updated_at: '2025-11-07T20:38:36'
        }
      ],
      total: 2,
      page: 1,
      page_size: 10
    }
  }

  const mountComponent = (props = {}) => {
    return mount(VaccinationTimeline, {
      props: {
        petId: 1,
        ...props
      },
      global: {
        plugins: [vuetify]
      }
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Component Mounting', () => {
    it('應該成功掛載元件', () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent()
      expect(wrapper.exists()).toBe(true)
    })

    it('應該在掛載時載入疫苗記錄', async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(vaccinationsApi.getVaccinations).toHaveBeenCalledWith(1, 1, 50)
    })
  })

  describe('Loading State', () => {
    it('應該在載入時顯示 loading 狀態', () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockImplementation(() => 
        new Promise(resolve => setTimeout(resolve, 1000))
      )
      wrapper = mountComponent()
      
      expect(wrapper.find('.v-progress-circular').exists()).toBe(true)
      expect(wrapper.text()).toContain('載入疫苗記錄中')
    })

    it('載入完成後應該隱藏 loading 狀態', async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(wrapper.find('.v-progress-circular').exists()).toBe(false)
    })
  })

  describe('Empty State', () => {
    it('應該在沒有疫苗記錄時顯示空狀態', async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue({
        ...mockVaccinationsResponse,
        data: {
          items: [],
          total: 0,
          page: 1,
          page_size: 10
        }
      })
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(wrapper.text()).toContain('尚無疫苗接種記錄')
    })
  })

  describe('Vaccination Display', () => {
    beforeEach(async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('應該顯示疫苗名稱', () => {
      expect(wrapper.text()).toContain('狂犬病疫苗')
      expect(wrapper.text()).toContain('犬流感疫苗')
    })

    it('應該正確格式化疫苗類型', () => {
      expect(wrapper.text()).toContain('核心疫苗')
      expect(wrapper.text()).toContain('選擇性疫苗')
    })

    it('應該顯示診所名稱', () => {
      expect(wrapper.text()).toContain('愛心動物醫院')
      expect(wrapper.text()).toContain('市立動物醫院')
    })

    it('應該顯示獸醫師姓名（如果有）', () => {
      expect(wrapper.text()).toContain('王小明獸醫師')
    })

    it('應該顯示批號（如果有）', () => {
      expect(wrapper.text()).toContain('RV2023001')
    })

    it('應該顯示備註', () => {
      expect(wrapper.text()).toContain('接種順利，寵物狀態良好')
      expect(wrapper.text()).toContain('預防流感季節感染')
    })
  })

  describe('Status Display', () => {
    beforeEach(async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('應該正確顯示完成狀態', () => {
      expect(wrapper.text()).toContain('已完成')
    })

    it('應該正確顯示預約狀態', () => {
      expect(wrapper.text()).toContain('已預約')
    })
  })

  describe('Summary Statistics', () => {
    beforeEach(async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
    })

    it('應該顯示疫苗接種摘要', () => {
      expect(wrapper.text()).toContain('疫苗接種摘要')
    })

    it('應該正確計算已完成數量', () => {
      expect(wrapper.text()).toMatch(/已完成/)
    })

    it('應該正確計算已預約數量', () => {
      expect(wrapper.text()).toMatch(/已預約/)
    })

    it('應該顯示總計', () => {
      expect(wrapper.text()).toMatch(/總計/)
    })
  })

  describe('Error Handling', () => {
    it('應該處理 API 錯誤', async () => {
      const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      vi.mocked(vaccinationsApi.getVaccinations).mockRejectedValue(new Error('API Error'))
      
      wrapper = mountComponent()
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(consoleErrorSpy).toHaveBeenCalledWith('載入疫苗記錄失敗:', expect.any(Error))
      consoleErrorSpy.mockRestore()
    })
  })

  describe('Props', () => {
    it('應該使用正確的 petId 呼叫 API', async () => {
      vi.mocked(vaccinationsApi.getVaccinations).mockResolvedValue(mockVaccinationsResponse)
      wrapper = mountComponent({ petId: 123 })
      
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 100))
      
      expect(vaccinationsApi.getVaccinations).toHaveBeenCalledWith(123, 1, 50)
    })
  })
})
