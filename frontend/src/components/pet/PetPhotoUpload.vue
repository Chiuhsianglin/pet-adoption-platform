<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-alert v-if="photos.length === 0" type="info" variant="tonal" class="mb-4">
          <strong>照片上傳提示：</strong>
          <ul class="mt-2">
            <li>建議上傳至少 3 張寵物照片</li>
            <li>最多可上傳 10 張照片</li>
            <li>照片將自動壓縮和優化</li>
            <li>第一張照片將作為主要照片</li>
          </ul>
        </v-alert>

        <!-- File input -->
        <v-file-input
          v-model="selectedFiles"
          label="選擇照片"
          accept="image/*"
          multiple
          prepend-icon="mdi-camera"
          variant="outlined"
          :disabled="photos.length >= 10"
          @update:model-value="handleFileSelect"
        >
          <template #selection="{ fileNames }">
            <template v-for="(fileName, index) in fileNames" :key="fileName">
              <v-chip
                v-if="index < 2"
                color="primary"
                size="small"
                class="me-2"
              >
                {{ fileName }}
              </v-chip>

              <span
                v-else-if="index === 2"
                class="text-overline text-grey-darken-3 mx-2"
              >
                +{{ fileNames.length - 2 }} 個檔案
              </span>
            </template>
          </template>
        </v-file-input>

        <!-- Upload progress -->
        <v-progress-linear
          v-if="uploading"
          :model-value="uploadProgress"
          color="primary"
          height="6"
          class="mb-4"
        />

        <!-- Photo grid -->
        <v-row v-if="photos.length > 0">
          <v-col
            v-for="(photo, index) in photos"
            :key="photo.id || index"
            cols="6"
            md="4"
            lg="3"
          >
            <v-card>
              <v-img
                :src="photo.file_url || photo.url || photo.preview"
                aspect-ratio="1"
                cover
                class="photo-img"
                @error="() => handlePhotoError(photo, index)"
              >
                <template v-if="photo.loading" #placeholder>
                  <v-row class="fill-height ma-0" align="center" justify="center">
                    <v-progress-circular indeterminate color="grey-lighten-5" />
                  </v-row>
                </template>
              </v-img>

              <v-card-actions>
                <v-chip
                  v-if="index === 0"
                  size="small"
                  color="primary"
                  variant="flat"
                >
                  主要照片
                </v-chip>
                <v-spacer />
                <v-btn
                  icon="mdi-delete"
                  size="small"
                  variant="text"
                  @click="removePhoto(index)"
                />
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- Photo count -->
        <v-alert
          v-if="photos.length > 0"
          type="success"
          variant="tonal"
          class="mt-4"
        >
          已上傳 {{ photos.length }} / 10 張照片
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { fileService } from '@/services/file'
import { useNotificationStore } from '@/stores/notification'
import type { FileMetadata } from '@/types/file'

interface PhotoData {
  id?: number
  file_id?: number | string
  url?: string
  file_url?: string
  file_key?: string
  preview?: string
  file?: File
  loading?: boolean
}

interface Props {
  modelValue: PhotoData[]
}

interface Emits {
  (e: 'update:modelValue', value: PhotoData[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const notificationStore = useNotificationStore()

const selectedFiles = ref<File[]>([])
const photos = ref<PhotoData[]>([...props.modelValue])
const uploading = ref(false)
const uploadProgress = ref(0)

const handleFileSelect = async (files: File | File[] | null) => {
  if (!files) return
  
  const fileArray = Array.isArray(files) ? files : [files]
  if (fileArray.length === 0) return

  const remainingSlots = 10 - photos.value.length
  if (fileArray.length > remainingSlots) {
    notificationStore.error(`最多只能上傳 ${remainingSlots} 張照片`)
    return
  }

  uploading.value = true
  uploadProgress.value = 0

  try {
    // Upload files
    const response = await fileService.upload({
      files: fileArray,
      category: 'pet_photo',
      onProgress: (progress) => {
        uploadProgress.value = progress
      },
    })

    // Add uploaded photos
    const uploadedPhotos = response.files.map((file: FileMetadata) => ({
      file_id: file.id,
      url: file.file_url || file.urls?.original || '',
      file_url: file.file_url || file.urls?.original || '',
      file_key: file.file_key || '',
      preview: file.urls?.thumbnail || file.urls?.large || file.file_url || file.urls?.original || '',
    }))

    photos.value.push(...uploadedPhotos)
    emit('update:modelValue', photos.value)

    notificationStore.success('照片上傳成功')
  } catch (error) {
    console.error('Failed to upload photos:', error)
    notificationStore.error('照片上傳失敗')
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    selectedFiles.value = []
  }
}

const removePhoto = (index: number) => {
  photos.value.splice(index, 1)
  emit('update:modelValue', photos.value)
}

// Handle photo load error (for expired presigned URLs)
const handlePhotoError = async (photo: PhotoData, index: number) => {
  // Only retry once per photo
  if (photo.loading) return
  
  console.log(`⚠️  Photo load failed, will use fallback URL`)
  // For now, just mark as loading to prevent retry loop
  // In a real app, you could call petService.refreshPhotoUrls here
  photos.value[index] = { ...photo, loading: false }
}

// Watch props changes
watch(
  () => props.modelValue,
  (newValue) => {
    photos.value = [...newValue]
  },
  { deep: true }
)

// Expose validate method
defineExpose({
  validate: async () => {
    // Photos are optional but recommended
    return true
  },
})
</script>

<style scoped>
ul {
  padding-left: 20px;
}

li {
  margin: 4px 0;
}

.photo-img {
  cursor: pointer;
  transition: transform 0.2s;
}

.photo-img:hover {
  transform: scale(1.05);
}
</style>
