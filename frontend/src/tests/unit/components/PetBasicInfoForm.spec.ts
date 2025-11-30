/**
 * Unit tests for PetBasicInfoForm component
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import PetBasicInfoForm from '@/components/pet/PetBasicInfoForm.vue'
import type { PetFormData } from '@/types/pet'

const vuetify = createVuetify({
  components,
  directives,
})

describe('PetBasicInfoForm', () => {
  let wrapper: VueWrapper<any>
  
  const mockPetData: PetFormData = {
    name: '',
    species: null,
    breed: '',
    age_months: null,
    gender: null,
    size: null,
    color: '',
    description: '',
    health_status: '',
    vaccination_status: false,
    sterilized: false,
    special_needs: '',
    adoption_fee: null,
    location: '',
    photos: []
  }
  
  beforeEach(() => {
    wrapper = mount(PetBasicInfoForm, {
      global: {
        plugins: [vuetify],
      },
      props: {
        modelValue: { ...mockPetData },
      },
    })
  })
  
  it('renders form fields correctly', () => {
    expect(wrapper.find('input[placeholder*="名稱"]').exists()).toBe(true)
    expect(wrapper.find('[label="寵物種類"]').exists()).toBe(true)
  })
  
  it('emits update:modelValue when name changes', async () => {
    const nameInput = wrapper.find('input[placeholder*="名稱"]')
    await nameInput.setValue('測試寵物')
    
    expect(wrapper.emitted('update:modelValue')).toBeTruthy()
  })
  
  it('validates required fields', async () => {
    const form = wrapper.vm
    
    // Trigger validation
    const isValid = await form.validate()
    
    // Should fail validation with empty required fields
    expect(isValid).toBe(false)
  })
  
  it('displays species options correctly', () => {
    const speciesSelect = wrapper.findComponent({ name: 'v-select' })
    expect(speciesSelect.exists()).toBe(true)
  })
  
  it('accepts valid pet data', async () => {
    const validData: PetFormData = {
      name: '柴犬小白',
      species: 'dog',
      breed: '柴犬',
      age_months: 12,
      gender: 'male',
      size: 'medium',
      color: '棕色',
      description: '友善活潑',
      health_status: '健康',
      vaccination_status: true,
      sterilized: true,
      special_needs: '',
      adoption_fee: 3000,
      location: '台北市',
      photos: []
    }
    
    await wrapper.setProps({ modelValue: validData })
    
    const form = wrapper.vm
    const isValid = await form.validate()
    
    expect(isValid).toBe(true)
  })
})
