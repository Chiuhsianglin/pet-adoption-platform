<template>
  <v-dialog :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" max-width="600">
    <v-card>
      <v-card-title class="d-flex align-center">
        <span class="text-h6">發布貼文</span>
        <v-spacer />
        <v-btn icon="mdi-close" variant="text" @click="close" />
      </v-card-title>

      <v-card-text>
        <v-select
          v-model="postType"
          :items="typeOptions"
          label="貼文類型*"
          variant="outlined"
          class="mb-4"
        />

        <v-textarea
          v-model="content"
          label="內容*"
          placeholder="分享你的想法..."
          variant="outlined"
          rows="6"
          counter="5000"
          :rules="[rules.required, rules.maxLength]"
        />

        <!-- Photo Upload -->
        <div class="mb-4">
          <v-btn
            variant="outlined"
            prepend-icon="mdi-image"
            @click="triggerFileInput"
            :disabled="photos.length >= 5"
          >
            上傳照片 ({{ photos.length }}/5)
          </v-btn>
          <input
            ref="fileInput"
            type="file"
            accept="image/*"
            multiple
            style="display: none"
            @change="handleFileSelect"
          />
        </div>

        <!-- Photo Preview -->
        <v-row v-if="photos.length > 0" dense>
          <v-col
            v-for="(photo, index) in photos"
            :key="index"
            cols="4"
          >
            <div class="photo-preview">
              <v-img
                :src="photo.preview"
                aspect-ratio="1"
                cover
                class="rounded"
              />
              <v-btn
                icon="mdi-close"
                size="small"
                color="red"
                class="remove-btn"
                @click="removePhoto(index)"
              />
            </div>
          </v-col>
        </v-row>

        <v-alert v-if="error" type="error" class="mt-4">
          {{ error }}
        </v-alert>
      </v-card-text>

      <v-card-actions>
        <v-spacer />
        <v-btn @click="close">取消</v-btn>
        <v-btn
          color="primary"
          :loading="loading"
          :disabled="!isValid"
          @click="submit"
        >
          發布
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { createPost, PostType } from '@/api/community'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  created: [post: any]
}>()

// State
const postType = ref<PostType>(PostType.SHARE)
const content = ref('')
const photos = ref<{ file: File; preview: string }[]>([])
const loading = ref(false)
const error = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const typeOptions = [
  { title: '分享', value: PostType.SHARE },
  { title: '問題', value: PostType.QUESTION }
]

const rules = {
  required: (v: string) => !!v || '此欄位為必填',
  maxLength: (v: string) => v.length <= 5000 || '內容不能超過 5000 字'
}

const isValid = computed(() => {
  return content.value.length > 0 && content.value.length <= 5000
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  
  // Check total count
  const remainingSlots = 5 - photos.value.length
  const filesToAdd = files.slice(0, remainingSlots)
  
  // Validate and add
  for (const file of filesToAdd) {
    // Check file size (3MB)
    if (file.size > 3 * 1024 * 1024) {
      error.value = `照片 ${file.name} 超過 3MB 限制`
      continue
    }
    
    // Create preview
    const preview = URL.createObjectURL(file)
    photos.value.push({ file, preview })
  }
  
  // Clear input
  if (target) target.value = ''
}

const removePhoto = (index: number) => {
  URL.revokeObjectURL(photos.value[index].preview)
  photos.value.splice(index, 1)
  error.value = ''
}

const submit = async () => {
  if (!isValid.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const formData = new FormData()
    formData.append('post_type', postType.value)
    formData.append('content', content.value)
    photos.value.forEach(photo => {
      formData.append('photos', photo.file)
    })
    
    const newPost = await createPost(formData)
    
    emit('created', newPost)
    resetForm()
    close()
  } catch (err: any) {
    error.value = err.response?.data?.detail || '發布失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  postType.value = PostType.SHARE
  content.value = ''
  photos.value.forEach(p => URL.revokeObjectURL(p.preview))
  photos.value = []
  error.value = ''
}

const close = () => {
  emit('update:modelValue', false)
}
</script>

<style scoped>
.photo-preview {
  position: relative;
}

.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
}
</style>
