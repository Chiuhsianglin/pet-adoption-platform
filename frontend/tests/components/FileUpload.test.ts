import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import FileUpload from '@/components/common/FileUpload.vue'
import { fileService } from '@/services/file'

// Mock file service
vi.mock('@/services/file', () => ({
  fileService: {
    upload: vi.fn(),
    validateFileType: vi.fn(),
    validateFileSize: vi.fn(),
    formatFileSize: vi.fn((size: number) => `${size} bytes`),
  },
}))

const vuetify = createVuetify({
  components,
  directives,
})

describe('FileUpload.vue', () => {
  let wrapper: any

  const createWrapper = (props = {}) => {
    return mount(FileUpload, {
      props: {
        category: 'pet_photo',
        ...props,
      },
      global: {
        plugins: [vuetify],
      },
    })
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders upload drop zone', () => {
    wrapper = createWrapper()
    expect(wrapper.find('.drop-zone').exists()).toBe(true)
    expect(wrapper.text()).toContain('拖拽檔案至此處')
  })

  it('displays accept text correctly', () => {
    wrapper = createWrapper({
      accept: 'image/jpeg,image/png',
    })
    expect(wrapper.text()).toContain('支援 JPG, PNG')
  })

  it('displays max size text', () => {
    wrapper = createWrapper({
      maxSize: 10485760, // 10MB
    })
    expect(wrapper.text()).toContain('最大檔案大小')
  })

  it('handles file selection', async () => {
    wrapper = createWrapper()
    
    // Mock file validation
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    // Simulate file selection
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.uploadingFiles.length).toBeGreaterThan(0)
  })

  it('validates file type on selection', async () => {
    wrapper = createWrapper({
      accept: 'image/jpeg,image/png',
    })
    
    vi.mocked(fileService.validateFileType).mockReturnValue(false)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)

    const file = new File(['test'], 'test.txt', { type: 'text/plain' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    // Should emit error
    expect(wrapper.emitted('upload-error')).toBeTruthy()
  })

  it('validates file size on selection', async () => {
    wrapper = createWrapper({
      maxSize: 1024, // 1KB
    })
    
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(false)

    const file = new File(['x'.repeat(2000)], 'large.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    // Should emit error
    expect(wrapper.emitted('upload-error')).toBeTruthy()
  })

  it('enforces max files limit', async () => {
    wrapper = createWrapper({
      maxFiles: 2,
    })
    
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)

    const files = [
      new File(['1'], 'test1.jpg', { type: 'image/jpeg' }),
      new File(['2'], 'test2.jpg', { type: 'image/jpeg' }),
      new File(['3'], 'test3.jpg', { type: 'image/jpeg' }),
    ]
    
    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', {
      value: files,
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.emitted('upload-error')).toBeTruthy()
    expect(wrapper.emitted('upload-error')![0][0]).toContain('最多只能上傳 2 個檔案')
  })

  it('handles drag and drop', async () => {
    wrapper = createWrapper()
    
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)

    const dropZone = wrapper.find('.drop-zone')
    
    // Simulate drag over
    await dropZone.trigger('dragover')
    expect(wrapper.vm.isDragging).toBe(true)

    // Simulate drop
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const dataTransfer = {
      files: [file],
    }
    
    await dropZone.trigger('drop', { dataTransfer })
    expect(wrapper.vm.isDragging).toBe(false)
  })

  it('uploads files on auto upload', async () => {
    wrapper = createWrapper({
      autoUpload: true,
    })
    
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)
    vi.mocked(fileService.upload).mockResolvedValue({
      success: true,
      message: 'Upload successful',
      files: [
        {
          id: 1,
          filename: 'test.jpg',
          original_filename: 'test.jpg',
          file_size: 1024,
          mime_type: 'image/jpeg',
          file_hash: 'abc123',
          storage_path: 'pets/1/original/test.jpg',
          category: 'pet_photo',
          uploaded_by: 1,
          is_public: true,
          is_deleted: false,
          created_at: new Date().toISOString(),
          urls: {
            thumbnail: 'http://example.com/thumb.jpg',
            medium: 'http://example.com/medium.jpg',
            large: 'http://example.com/large.jpg',
            original: 'http://example.com/original.jpg',
          },
        },
      ],
    })

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()
    
    // Wait for upload to complete
    await new Promise(resolve => setTimeout(resolve, 100))

    expect(fileService.upload).toHaveBeenCalled()
    expect(wrapper.emitted('upload-success')).toBeTruthy()
  })

  it('removes file from list', async () => {
    wrapper = createWrapper({
      autoUpload: false,
    })
    
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    const initialCount = wrapper.vm.uploadingFiles.length
    expect(initialCount).toBeGreaterThan(0)

    // Remove first file
    const fileId = wrapper.vm.uploadingFiles[0].id
    wrapper.vm.removeFile(fileId)
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.uploadingFiles.length).toBe(initialCount - 1)
  })

  it('disables upload when disabled prop is true', () => {
    wrapper = createWrapper({
      disabled: true,
    })

    const dropZone = wrapper.find('.drop-zone')
    expect(dropZone.classes()).toContain('drop-zone--disabled')
    
    const input = wrapper.find('input[type="file"]')
    expect(input.element.disabled).toBe(true)
  })

  it('shows upload button when showUploadButton is true', async () => {
    wrapper = createWrapper({
      autoUpload: false,
      showUploadButton: true,
    })
    
    vi.mocked(fileService.validateFileType).mockReturnValue(true)
    vi.mocked(fileService.validateFileSize).mockReturnValue(true)

    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' })
    const input = wrapper.find('input[type="file"]')
    
    Object.defineProperty(input.element, 'files', {
      value: [file],
      writable: false,
    })
    
    await input.trigger('change')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('上傳')
  })

  it('exposes clearSuccessful method', async () => {
    wrapper = createWrapper()
    
    // Add some files with different statuses
    wrapper.vm.uploadingFiles = [
      { id: '1', status: 'success', file: new File(['1'], '1.jpg'), progress: 100 },
      { id: '2', status: 'pending', file: new File(['2'], '2.jpg'), progress: 0 },
      { id: '3', status: 'success', file: new File(['3'], '3.jpg'), progress: 100 },
    ]
    
    wrapper.vm.clearSuccessful()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.uploadingFiles.length).toBe(1)
    expect(wrapper.vm.uploadingFiles[0].status).toBe('pending')
  })

  it('exposes clearAll method', async () => {
    wrapper = createWrapper()
    
    wrapper.vm.uploadingFiles = [
      { id: '1', status: 'success', file: new File(['1'], '1.jpg'), progress: 100 },
      { id: '2', status: 'pending', file: new File(['2'], '2.jpg'), progress: 0 },
    ]
    
    wrapper.vm.clearAll()
    await wrapper.vm.$nextTick()

    expect(wrapper.vm.uploadingFiles.length).toBe(0)
  })
})
