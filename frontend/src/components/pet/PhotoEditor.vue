<template>
  <div class="photo-editor">
    <v-card>
      <v-card-title class="d-flex align-center">
        <v-icon class="mr-2">mdi-image-multiple</v-icon>
        照片管理
        <v-spacer />
        <v-btn
          color="primary"
          prepend-icon="mdi-upload"
          @click="openUploadDialog"
        >
          上傳照片
        </v-btn>
      </v-card-title>

      <v-card-text>
        <!-- Photo Grid -->
        <v-row v-if="photos.length > 0">
          <v-col
            v-for="(photo, index) in photos"
            :key="photo.id"
            cols="12"
            sm="6"
            md="4"
          >
            <v-card class="photo-card" elevation="2">
              <!-- Photo Image -->
              <v-img
                :src="photo.file_url"
                :alt="photo.caption || `照片 ${index + 1}`"
                aspect-ratio="1"
                cover
                class="photo-image"
              >
                <!-- Primary Badge -->
                <v-chip
                  v-if="photo.is_primary"
                  color="primary"
                  size="small"
                  class="primary-badge"
                >
                  <v-icon start size="small">mdi-star</v-icon>
                  主要照片
                </v-chip>

                <!-- Actions Overlay -->
                <div class="photo-actions">
                  <v-btn
                    icon="mdi-arrow-left"
                    size="small"
                    variant="tonal"
                    :disabled="index === 0"
                    @click="movePhoto(index, -1)"
                  />
                  <v-btn
                    icon="mdi-arrow-right"
                    size="small"
                    variant="tonal"
                    :disabled="index === photos.length - 1"
                    @click="movePhoto(index, 1)"
                  />
                  <v-btn
                    v-if="!photo.is_primary"
                    icon="mdi-star-outline"
                    size="small"
                    variant="tonal"
                    @click="setPrimary(photo.id)"
                  />
                  <v-btn
                    icon="mdi-delete"
                    size="small"
                    variant="tonal"
                    color="error"
                    @click="confirmDelete(photo)"
                  />
                </div>
              </v-img>

              <!-- Caption Editor -->
              <v-card-text class="pa-2">
                <inline-editor
                  :pet-id="petId"
                  :field-name="`photo_${photo.id}_caption`"
                  :field-value="photo.caption"
                  field-type="text"
                  label="照片說明"
                  empty-text="點擊新增說明"
                  :can-edit="canEdit"
                  @updated="(value) => updateCaption(photo.id, value)"
                />
              </v-card-text>

              <!-- Order Badge -->
              <v-chip
                size="x-small"
                class="order-badge"
                variant="flat"
              >
                {{ index + 1 }}
              </v-chip>
            </v-card>
          </v-col>
        </v-row>

        <!-- Empty State -->
        <v-alert
          v-else
          type="info"
          variant="tonal"
          icon="mdi-image-off"
          class="mb-0"
        >
          尚無照片，請點擊「上傳照片」按鈕新增照片
        </v-alert>
      </v-card-text>
    </v-card>

    <!-- Upload Dialog -->
    <v-dialog v-model="uploadDialog" max-width="600">
      <v-card>
        <v-card-title>上傳照片</v-card-title>
        <v-card-text>
          <v-file-input
            v-model="uploadFiles"
            label="選擇照片"
            accept="image/*"
            multiple
            prepend-icon="mdi-camera"
            show-size
            counter
            :rules="fileRules"
          />
          <v-text-field
            v-model="uploadCaption"
            label="照片說明（選填）"
            hint="可以在上傳後為每張照片單獨編輯說明"
            persistent-hint
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="uploadDialog = false">取消</v-btn>
          <v-btn
            color="primary"
            :loading="uploading"
            :disabled="!uploadFiles || uploadFiles.length === 0"
            @click="uploadPhotos"
          >
            上傳
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="deleteDialog" max-width="400">
      <v-card>
        <v-card-title>確認刪除</v-card-title>
        <v-card-text>
          確定要刪除這張照片嗎？此操作無法復原。
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="deleteDialog = false">取消</v-btn>
          <v-btn
            color="error"
            :loading="deleting"
            @click="deletePhoto"
          >
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar"
      :color="snackbarColor"
      :timeout="3000"
    >
      {{ snackbarMessage }}
      <template #actions>
        <v-btn variant="text" @click="snackbar = false">關閉</v-btn>
      </template>
    </v-snackbar>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import apiClient from '@/services/api'
import InlineEditor from './InlineEditor.vue'

interface Photo {
  id: number
  pet_id: number
  file_url: string
  file_key: string
  caption: string | null
  is_primary: boolean
  upload_order: number
  created_at: string
}

interface Props {
  petId: number
  photos: Photo[]
  canEdit?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  canEdit: true
})

const emit = defineEmits<{
  (e: 'updated'): void
}>()

// State
const uploadDialog = ref(false)
const deleteDialog = ref(false)
const uploadFiles = ref<File[] | null>(null)
const uploadCaption = ref('')
const uploading = ref(false)
const deleting = ref(false)
const photoToDelete = ref<Photo | null>(null)

// Snackbar
const snackbar = ref(false)
const snackbarMessage = ref('')
const snackbarColor = ref<'success' | 'error'>('success')

// Validation rules
const fileRules = [
  (files: File[]) => !files || files.length <= 10 || '最多只能上傳 10 張照片',
  (files: File[]) => {
    if (!files) return true
    const maxSize = 5 * 1024 * 1024 // 5MB
    return files.every(f => f.size <= maxSize) || '每張照片大小不能超過 5MB'
  }
]

// Methods
const openUploadDialog = () => {
  uploadFiles.value = null
  uploadCaption.value = ''
  uploadDialog.value = true
}

const uploadPhotos = async () => {
  if (!uploadFiles.value || uploadFiles.value.length === 0) return

  uploading.value = true

  try {
    const formData = new FormData()
    uploadFiles.value.forEach(file => {
      formData.append('files', file)
    })
    if (uploadCaption.value) {
      formData.append('caption', uploadCaption.value)
    }

    await apiClient.post(`/pets/${props.petId}/photos`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    showSnackbar('照片上傳成功', 'success')
    uploadDialog.value = false
    emit('updated')
    
  } catch (error: any) {
    showSnackbar(error.response?.data?.detail || '上傳失敗', 'error')
  } finally {
    uploading.value = false
  }
}

const movePhoto = async (index: number, direction: number) => {
  const newPhotos = [...props.photos]
  const targetIndex = index + direction

  if (targetIndex < 0 || targetIndex >= newPhotos.length) return

  // Swap
  [newPhotos[index], newPhotos[targetIndex]] = [newPhotos[targetIndex], newPhotos[index]]

  // Update order on server
  const photoIds = newPhotos.map(p => p.id)
  
  try {
    await apiClient.post(`/pets/${props.petId}/photos/reorder`, {
      photo_ids: photoIds
    })

    emit('updated')
    
  } catch (error: any) {
    showSnackbar(error.response?.data?.detail || '重新排序失敗', 'error')
  }
}

const setPrimary = async (photoId: number) => {
  try {
    await apiClient.put(`/pets/${props.petId}/photos/${photoId}/primary`)
    
    showSnackbar('主要照片已更新', 'success')
    emit('updated')
    
  } catch (error: any) {
    showSnackbar(error.response?.data?.detail || '設定主要照片失敗', 'error')
  }
}

const updateCaption = async (photoId: number, caption: string) => {
  try {
    await apiClient.put(
      `/pets/${props.petId}/photos/${photoId}/caption`,
      { caption }
    )

    showSnackbar('照片說明已更新', 'success')
    emit('updated')
    
  } catch (error: any) {
    showSnackbar(error.response?.data?.detail || '更新說明失敗', 'error')
  }
}

const confirmDelete = (photo: Photo) => {
  photoToDelete.value = photo
  deleteDialog.value = true
}

const deletePhoto = async () => {
  if (!photoToDelete.value) return

  deleting.value = true

  try {
    await apiClient.delete(
      `/pets/${props.petId}/photos/${photoToDelete.value.id}`
    )

    showSnackbar('照片已刪除', 'success')
    deleteDialog.value = false
    photoToDelete.value = null
    emit('updated')
    
  } catch (error: any) {
    showSnackbar(error.response?.data?.detail || '刪除失敗', 'error')
  } finally {
    deleting.value = false
  }
}

const showSnackbar = (message: string, color: 'success' | 'error') => {
  snackbarMessage.value = message
  snackbarColor.value = color
  snackbar.value = true
}
</script>

<style scoped lang="scss">
.photo-editor {
  .photo-card {
    position: relative;
    transition: transform 0.2s;

    &:hover {
      transform: translateY(-4px);

      .photo-actions {
        opacity: 1;
      }
    }
  }

  .photo-image {
    position: relative;
  }

  .primary-badge {
    position: absolute;
    top: 8px;
    left: 8px;
    z-index: 1;
  }

  .photo-actions {
    position: absolute;
    bottom: 8px;
    right: 8px;
    display: flex;
    gap: 4px;
    opacity: 0;
    transition: opacity 0.2s;
    z-index: 1;
  }

  .order-badge {
    position: absolute;
    top: 8px;
    right: 8px;
    z-index: 1;
  }
}
</style>
