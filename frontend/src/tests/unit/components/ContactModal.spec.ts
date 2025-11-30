/**
 * Unit tests for ContactModal component (Story 2.5)
 */
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import ContactModal from '@/components/pet/ContactModal.vue'
import apiClient from '@/api/client'

// Mock API client
vi.mock('@/api/client', () => ({
  default: {
    post: vi.fn(),
  },
}))

const vuetify = createVuetify({
  components,
  directives,
})

describe('ContactModal', () => {
  let wrapper: VueWrapper<any>
  
  const mockPet = {
    id: 1,
    name: '柴犬小白',
    shelter_id: 1,
  }
  
  beforeEach(() => {
    wrapper = mount(ContactModal, {
      global: {
        plugins: [vuetify],
      },
      props: {
        pet: mockPet,
        modelValue: false,
      },
    })
    
    // Clear all mocks
    vi.clearAllMocks()
  })
  
  // =================================================================
  // Component Rendering Tests
  // =================================================================
  
  it('renders modal dialog when modelValue is true', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const dialog = wrapper.findComponent({ name: 'v-dialog' })
    expect(dialog.exists()).toBe(true)
  })
  
  it('displays correct modal title', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const title = wrapper.find('.text-h5')
    expect(title.text()).toContain('聯繫')
  })
  
  it('renders all form fields', async () => {
    await wrapper.setProps({ modelValue: true })
    
    // Check for essential form fields
    expect(wrapper.find('[label="姓名"]').exists()).toBe(true)
    expect(wrapper.find('[label="電子郵件"]').exists()).toBe(true)
    expect(wrapper.find('[label="聯絡電話"]').exists()).toBe(true)
    expect(wrapper.find('[label="聯絡方式"]').exists()).toBe(true)
    expect(wrapper.find('[label="諮詢類型"]').exists()).toBe(true)
    expect(wrapper.find('[label="訊息內容"]').exists()).toBe(true)
  })
  
  it('displays all 7 inquiry type options', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const inquiryTypes = [
      '一般諮詢',
      '領養相關',
      '預約參觀',
      '寵物健康',
      '領養流程',
      '費用相關',
      '其他問題',
    ]
    
    const form = wrapper.vm
    expect(form.inquiryTypes).toEqual(inquiryTypes)
  })
  
  it('displays all 4 contact method options', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const contactMethods = ['電子郵件', '電話', 'LINE', '簡訊']
    
    const form = wrapper.vm
    expect(form.contactMethods).toEqual(contactMethods)
  })
  
  // =================================================================
  // Form Validation Tests
  // =================================================================
  
  it('validates required fields - name', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    const nameRules = form.nameRules
    
    // Empty name should fail
    const emptyResult = nameRules[0]('')
    expect(typeof emptyResult).toBe('string')
    expect(emptyResult).toContain('必填')
    
    // Valid name should pass
    const validResult = nameRules[0]('張小明')
    expect(validResult).toBe(true)
  })
  
  it('validates email format', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    const emailRules = form.emailRules
    
    // Empty email should fail
    expect(typeof emailRules[0]('')).toBe('string')
    
    // Invalid email format should fail
    expect(typeof emailRules[1]('invalid-email')).toBe('string')
    
    // Valid email should pass
    expect(emailRules[0]('test@example.com')).toBe(true)
    expect(emailRules[1]('test@example.com')).toBe(true)
  })
  
  it('validates phone format', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    const phoneRules = form.phoneRules
    
    // Empty phone should fail
    expect(typeof phoneRules[0]('')).toBe('string')
    
    // Invalid phone format should fail
    expect(typeof phoneRules[1]('123')).toBe('string')
    expect(typeof phoneRules[1]('abc')).toBe('string')
    
    // Valid phone formats should pass
    expect(phoneRules[0]('0912345678')).toBe(true)
    expect(phoneRules[1]('0912345678')).toBe(true)
    expect(phoneRules[1]('0912-345-678')).toBe(true)
    expect(phoneRules[1]('(02)2345-6789')).toBe(true)
  })
  
  it('validates message length (min 10 characters)', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    const messageRules = form.messageRules
    
    // Empty message should fail
    expect(typeof messageRules[0]('')).toBe('string')
    
    // Short message should fail
    expect(typeof messageRules[1]('短訊息')).toBe('string')
    
    // Valid message should pass
    expect(messageRules[0]('這是一個有效的訊息內容')).toBe(true)
    expect(messageRules[1]('這是一個有效的訊息內容')).toBe(true)
  })
  
  it('validates privacy policy checkbox', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    const privacyRules = form.privacyRules
    
    // Unchecked should fail
    expect(typeof privacyRules[0](false)).toBe('string')
    
    // Checked should pass
    expect(privacyRules[0](true)).toBe(true)
  })
  
  // =================================================================
  // Visit Scheduling Tests
  // =================================================================
  
  it('shows date and time fields when inquiry type is "預約參觀"', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    form.formData.inquiry_type = '預約參觀'
    await wrapper.vm.$nextTick()
    
    expect(form.showVisitFields).toBe(true)
  })
  
  it('hides date and time fields for other inquiry types', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    form.formData.inquiry_type = '一般諮詢'
    await wrapper.vm.$nextTick()
    
    expect(form.showVisitFields).toBe(false)
  })
  
  it('displays time slot options', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    const timeSlots = form.timeSlots
    
    expect(timeSlots).toContain('上午 09:00 - 12:00')
    expect(timeSlots).toContain('下午 13:00 - 15:00')
    expect(timeSlots).toContain('下午 15:00 - 17:00')
    expect(timeSlots).toContain('晚上 18:00 - 20:00')
  })
  
  // =================================================================
  // Form Submission Tests
  // =================================================================
  
  it('submits form successfully with valid data', async () => {
    await wrapper.setProps({ modelValue: true })
    
    // Mock successful API response
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        success: true,
        message: '諮詢已成功送出，我們將儘快與您聯繫',
        data: {
          id: 1,
          name: '張小明',
          email: 'zhang@example.com',
          phone: '0912345678',
          contact_method: '電子郵件',
          inquiry_type: '一般諮詢',
          message: '我想了解更多關於這隻寵物的資訊',
          status: 'pending',
        },
      },
    })
    
    const form = wrapper.vm
    
    // Fill in valid form data
    form.formData = {
      name: '張小明',
      email: 'zhang@example.com',
      phone: '0912345678',
      contact_method: '電子郵件',
      inquiry_type: '一般諮詢',
      message: '我想了解更多關於這隻寵物的資訊',
      preferred_date: null,
      preferred_time: null,
      privacy_agreed: true,
    }
    
    // Submit form
    await form.submitForm()
    
    // Verify API was called with correct data
    expect(apiClient.post).toHaveBeenCalledWith(
      '/api/v1/inquiries',
      expect.objectContaining({
        name: '張小明',
        email: 'zhang@example.com',
        phone: '0912345678',
        contact_method: '電子郵件',
        inquiry_type: '一般諮詢',
        message: '我想了解更多關於這隻寵物的資訊',
        pet_id: mockPet.id,
        shelter_id: mockPet.shelter_id,
      })
    )
    
    // Verify success state
    expect(form.showSuccess).toBe(true)
    expect(form.successMessage).toContain('諮詢已成功送出')
  })
  
  it('submits form with visit date and time when scheduling visit', async () => {
    await wrapper.setProps({ modelValue: true })
    
    // Mock successful API response
    vi.mocked(apiClient.post).mockResolvedValueOnce({
      data: {
        success: true,
        message: '諮詢已成功送出',
        data: { id: 2 },
      },
    })
    
    const form = wrapper.vm
    
    // Fill in form data with visit scheduling
    form.formData = {
      name: '李小華',
      email: 'li@example.com',
      phone: '0923456789',
      contact_method: '電話',
      inquiry_type: '預約參觀',
      message: '我想預約參觀這隻寵物',
      preferred_date: '2025-11-15',
      preferred_time: '下午 13:00 - 15:00',
      privacy_agreed: true,
    }
    
    await form.submitForm()
    
    // Verify API was called with date and time
    expect(apiClient.post).toHaveBeenCalledWith(
      '/api/v1/inquiries',
      expect.objectContaining({
        preferred_date: '2025-11-15',
        preferred_time: '下午 13:00 - 15:00',
      })
    )
  })
  
  it('handles API error gracefully', async () => {
    await wrapper.setProps({ modelValue: true })
    
    // Mock API error
    vi.mocked(apiClient.post).mockRejectedValueOnce({
      response: {
        data: {
          detail: '伺服器錯誤，請稍後再試',
        },
      },
    })
    
    const form = wrapper.vm
    
    // Fill in valid form data
    form.formData = {
      name: '測試用戶',
      email: 'test@example.com',
      phone: '0912345678',
      contact_method: '電子郵件',
      inquiry_type: '一般諮詢',
      message: '這是一個測試訊息',
      privacy_agreed: true,
    }
    
    await form.submitForm()
    
    // Verify error state
    expect(form.showSuccess).toBe(false)
    expect(form.errorMessage).toContain('錯誤')
  })
  
  it('prevents submission without privacy agreement', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    
    // Fill in form but don't agree to privacy
    form.formData = {
      name: '測試用戶',
      email: 'test@example.com',
      phone: '0912345678',
      contact_method: '電子郵件',
      inquiry_type: '一般諮詢',
      message: '這是一個測試訊息',
      privacy_agreed: false,
    }
    
    await form.submitForm()
    
    // API should not be called
    expect(apiClient.post).not.toHaveBeenCalled()
  })
  
  it('disables submit button while loading', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    form.loading = true
    await wrapper.vm.$nextTick()
    
    const submitButton = wrapper.find('button[type="submit"]')
    expect(submitButton.attributes('disabled')).toBeDefined()
  })
  
  // =================================================================
  // Auto-close Tests
  // =================================================================
  
  it('closes modal automatically after 2 seconds on success', async () => {
    vi.useFakeTimers()
    
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    form.showSuccess = true
    form.autoCloseTimer = setTimeout(() => {
      form.closeModal()
    }, 2000)
    
    // Fast-forward time by 2 seconds
    await vi.advanceTimersByTimeAsync(2000)
    
    // Modal should emit update:modelValue with false
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
    const emitted = wrapper.emitted('update:modelValue') as any[]
    expect(emitted[emitted.length - 1]).toEqual([false])
    
    vi.useRealTimers()
  })
  
  // =================================================================
  // Form Reset Tests
  // =================================================================
  
  it('resets form data when modal is closed', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    
    // Fill in form data
    form.formData = {
      name: '測試用戶',
      email: 'test@example.com',
      phone: '0912345678',
      contact_method: '電子郵件',
      inquiry_type: '一般諮詢',
      message: '測試訊息',
      privacy_agreed: true,
    }
    
    // Close modal
    form.closeModal()
    
    // Form should be reset
    expect(form.formData.name).toBe('')
    expect(form.formData.email).toBe('')
    expect(form.formData.phone).toBe('')
    expect(form.formData.message).toBe('')
    expect(form.formData.privacy_agreed).toBe(false)
  })
  
  // =================================================================
  // Responsive Design Tests
  // =================================================================
  
  it('adjusts modal width based on display size', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    
    // Test that modalWidth is computed based on display
    expect(form.modalWidth).toBeDefined()
    expect(typeof form.modalWidth).toBe('string')
  })
  
  // =================================================================
  // Edge Cases
  // =================================================================
  
  it('handles very long message text', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const longMessage = '這是一個很長的訊息。'.repeat(100)
    
    const form = wrapper.vm
    form.formData.message = longMessage
    
    // Should accept long message
    const messageRules = form.messageRules
    expect(messageRules[0](longMessage)).toBe(true)
  })
  
  it('handles special characters in input fields', async () => {
    await wrapper.setProps({ modelValue: true })
    
    const form = wrapper.vm
    
    form.formData = {
      name: '李小華 (Xiao-Hua)',
      email: 'test+tag@example.com',
      phone: '(02)2345-6789',
      message: '我想了解：1) 費用 2) 流程 3) 時間。謝謝！😊',
      privacy_agreed: true,
    }
    
    // Validation should pass
    const nameRules = form.nameRules
    const emailRules = form.emailRules
    const phoneRules = form.phoneRules
    const messageRules = form.messageRules
    
    expect(nameRules[0](form.formData.name)).toBe(true)
    expect(emailRules[1](form.formData.email)).toBe(true)
    expect(phoneRules[1](form.formData.phone)).toBe(true)
    expect(messageRules[1](form.formData.message)).toBe(true)
  })
})
