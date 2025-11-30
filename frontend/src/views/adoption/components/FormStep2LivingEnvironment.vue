<template>
  <v-card class="form-step">
    <v-card-title>居住環境</v-card-title>
    <v-card-text>
      <v-form ref="formRef">
        <v-row>
          <v-col cols="12" md="6">
            <v-select
              v-model="formData.housing_type"
              :items="housingTypes"
              label="住宅類型 *"
              :rules="[rules.required]"
            ></v-select>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="formData.space_size"
              label="居住空間 (坪) *"
              type="number"
              :rules="[rules.required, rules.minValue(1)]"
            ></v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-switch
              v-model="formData.has_yard"
              label="有院子或陽台"
              color="primary"
            ></v-switch>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              v-model.number="formData.family_members"
              label="家庭成員人數 *"
              type="number"
              :rules="[rules.required, rules.minValue(1)]"
            ></v-text-field>
          </v-col>

          <v-col cols="12">
            <v-switch
              v-model="formData.has_allergies"
              label="家庭成員有過敏史"
              color="warning"
            ></v-switch>
          </v-col>

          <v-col cols="12">
            <v-card variant="outlined">
              <v-card-title class="text-subtitle-1">
                居住環境照片 
                <v-chip size="x-small" color="error" class="ml-2">必填</v-chip>
              </v-card-title>
              <v-card-subtitle class="text-caption">
                請至少上傳一張居住環境照片（例如：客廳、院子、寵物活動空間等）
              </v-card-subtitle>
              <v-card-text>
                <div class="photo-upload-area">
                  <input
                    ref="fileInput"
                    type="file"
                    accept="image/*"
                    multiple
                    style="display: none"
                    @change="handleFileSelect"
                  />
                  
                  <v-row v-if="environmentPhotos.length > 0">
                    <v-col
                      v-for="(photo, index) in environmentPhotos"
                      :key="index"
                      cols="6"
                      sm="4"
                      md="3"
                    >
                      <v-card class="photo-card">
                        <v-img
                          :src="photo.preview || photo.file_url || photo.url"
                          aspect-ratio="1"
                          cover
                          class="photo-preview"
                        >
                          <template #placeholder>
                            <v-row
                              class="fill-height ma-0"
                              align="center"
                              justify="center"
                            >
                              <v-progress-circular
                                indeterminate
                                color="grey-lighten-5"
                              />
                            </v-row>
                          </template>
                        </v-img>
                        <v-card-actions class="pa-2">
                          <v-spacer />
                          <v-btn
                            icon="mdi-delete"
                            size="small"
                            color="error"
                            @click="removePhoto(index)"
                          />
                        </v-card-actions>
                      </v-card>
                    </v-col>
                  </v-row>

                  <v-btn
                    prepend-icon="mdi-camera-plus"
                    variant="outlined"
                    color="primary"
                    block
                    class="mt-4"
                    :loading="uploading"
                    @click="triggerFileInput"
                  >
                    {{ environmentPhotos.length > 0 ? '新增更多照片' : '上傳照片' }}
                  </v-btn>
                  
                  <div v-if="environmentPhotos.length > 0" class="text-caption text-medium-emphasis mt-2">
                    已上傳 {{ environmentPhotos.length }} 張照片
                  </div>
                  
                  <v-alert
                    v-if="showPhotoWarning && environmentPhotos.length === 0"
                    type="warning"
                    density="compact"
                    class="mt-4"
                    closable
                    @click:close="showPhotoWarning = false"
                  >
                    請至少上傳一張居住環境照片才能繼續
                  </v-alert>
                </div>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col cols="12">
            <v-card>
              <v-card-title class="text-subtitle-1">其他寵物</v-card-title>
              <v-card-text>
                <div v-for="(pet, index) in formData.other_pets" :key="index" class="mb-4">
                  <v-row>
                    <v-col cols="12" md="4">
                      <v-text-field
                        v-model="pet.species"
                        label="寵物種類"
                        dense
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" md="3">
                      <v-text-field
                        v-model.number="pet.age"
                        label="年齡"
                        type="number"
                        dense
                      ></v-text-field>
                    </v-col>
                    <v-col cols="12" md="3">
                      <v-switch
                        v-model="pet.vaccinated"
                        label="已施打疫苗"
                        dense
                      ></v-switch>
                    </v-col>
                    <v-col cols="12" md="2">
                      <v-btn
                        icon="mdi-delete"
                        size="small"
                        color="error"
                        @click="removePet(index)"
                      ></v-btn>
                    </v-col>
                  </v-row>
                </div>
                <v-btn
                  prepend-icon="mdi-plus"
                  @click="addPet"
                >
                  新增寵物
                </v-btn>
              </v-card-text>
            </v-card>
          </v-col>       
       
        </v-row>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { LivingEnvironment, EnvironmentPhoto } from '@/types/adoption'
import { fileService } from '@/services/file'
import { useNotificationStore } from '@/stores/notification'

interface Props {
  modelValue: LivingEnvironment
}

interface Emits {
  (e: 'update:modelValue', value: LivingEnvironment): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const notificationStore = useNotificationStore()
const formRef = ref()
const fileInput = ref<HTMLInputElement>()
const formData = ref<LivingEnvironment>({ ...props.modelValue })
const uploading = ref(false)
const showPhotoWarning = ref(false)

// Initialize environment_photos array if not present
if (!formData.value.environment_photos) {
  formData.value.environment_photos = []
}

const environmentPhotos = computed(() => formData.value.environment_photos || [])

const housingTypes = [
  { title: '公寓', value: 'apartment' },
  { title: '獨棟住宅', value: 'house' },
  { title: '租屋', value: 'rental' },
  { title: '自有', value: 'owned' }
]

const rules = {
  required: (v: any) => !!v || '此欄位為必填',
  minValue: (min: number) => (v: number) => v >= min || `數值不能小於 ${min}`
}

const addPet = () => {
  formData.value.other_pets.push({
    species: '',
    age: 0,
    vaccinated: false
  })
}

const removePet = (index: number) => {
  formData.value.other_pets.splice(index, 1)
}

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  
  if (!files || files.length === 0) return

  uploading.value = true
  
  try {
    const validFiles: File[] = []
    
    for (const file of Array.from(files)) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        notificationStore.error(`${file.name} 不是圖片檔案`)
        continue
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        notificationStore.error(`${file.name} 檔案過大，請選擇小於 5MB 的圖片`)
        continue
      }

      validFiles.push(file)
    }

    if (validFiles.length === 0) {
      uploading.value = false
      return
    }

    // Upload files
    const uploadResult = await fileService.upload({
      files: validFiles,
      category: 'pet_photo'
    })
    
    // Add to photos array
    if (!formData.value.environment_photos) {
      formData.value.environment_photos = []
    }

    // Add uploaded files to environment_photos
    if (uploadResult.files && Array.isArray(uploadResult.files)) {
      for (const uploadedFile of uploadResult.files) {
        // 只存 file_url 和 file_key，不存 base64 preview
        // preview 只用於前端顯示，不應該存入資料庫
        formData.value.environment_photos.push({
          file_url: uploadedFile.file_url,
          file_key: uploadedFile.file_key,
          url: uploadedFile.file_url
          // 移除 preview: 避免 base64 資料過大
        })
      }
    }

    notificationStore.success(`成功上傳 ${validFiles.length} 張照片`)
  } catch (error) {
    console.error('照片上傳失敗:', error)
    notificationStore.error('照片上傳失敗，請稍後再試')
  } finally {
    uploading.value = false
    // Reset file input
    if (target) {
      target.value = ''
    }
  }
}

const createPreview = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target?.result as string)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

const removePhoto = (index: number) => {
  if (formData.value.environment_photos) {
    formData.value.environment_photos.splice(index, 1)
  }
}

watch(formData, (newValue) => {
  emit('update:modelValue', newValue)
}, { deep: true })

const validate = async () => {
  // Validate form fields
  const { valid } = await formRef.value.validate()
  
  // Validate at least one photo uploaded
  if (!formData.value.environment_photos || formData.value.environment_photos.length === 0) {
    showPhotoWarning.value = true
    notificationStore.error('請至少上傳一張居住環境照片')
    return false
  }
  
  // Hide warning if photos exist
  showPhotoWarning.value = false
  
  return valid
}

defineExpose({ validate })
</script>

<style scoped>
.form-step {
  margin-bottom: 1.5rem;
}

.photo-upload-area {
  padding: 1rem 0;
}

.photo-card {
  position: relative;
  overflow: hidden;
}

.photo-preview {
  border-radius: 8px;
}

.photo-card .v-card-actions {
  position: absolute;
  top: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.5);
  padding: 4px;
}
</style>
