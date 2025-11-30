<template>
  <v-container class="py-8">
    <v-row justify="center">
      <v-col cols="12" lg="10">
        <v-card>
          <v-card-title class="text-h4 pa-6">
            <v-icon icon="mdi-plus-circle" class="mr-2" />
            發布新寵物
          </v-card-title>

          <v-divider />

          <!-- Stepper -->
          <v-stepper 
            v-model="currentStep" 
            :items="steps" 
            class="elevation-0"
            hide-actions
          >
            <!-- Step 1: Basic Information -->
            <template #item.1>
              <v-card flat>
                <v-card-text>
                  <PetBasicInfoForm
                    ref="basicFormRef"
                    v-model="petData"
                    @valid="(valid) => (stepsValid[0] = valid)"
                  />
                </v-card-text>

                <v-card-actions class="pa-6">
                  <v-btn
                    
                    size="large"
                    @click="$router.push('/pets/manage')"
                  >
                    取消
                  </v-btn>
                  <v-spacer />
                  <v-btn
                    color="primary"
                    variant="elevated"
                    size="large"
                    @click="nextStep"
                  >
                    下一步
                    <v-icon icon="mdi-chevron-right" end />
                  </v-btn>
                </v-card-actions>
              </v-card>
            </template>

            <!-- Step 2: Photo Upload -->
            <template #item.2>
              <v-card flat>
                <v-card-text>
                  <PetPhotoUpload
                    ref="photoUploadRef"
                    v-model="photos"
                  />
                </v-card-text>

                <v-card-actions class="pa-6">
                  <v-btn
                    variant="text"
                    size="large"
                    @click="prevStep"
                  >
                    <v-icon icon="mdi-chevron-left" start />
                    上一步
                  </v-btn>
                  <v-spacer />
                  <v-btn
                    color="primary"
                    variant="elevated"
                    size="large"
                    @click="nextStep"
                  >
                    下一步
                    <v-icon icon="mdi-chevron-right" end />
                  </v-btn>
                </v-card-actions>
              </v-card>
            </template>

            <!-- Step 3: Preview and Submit -->
            <template #item.3>
              <v-card flat>
                <v-card-text>
                  <PetPreview :pet-data="petData" :photos="photos" />
                </v-card-text>

                <v-card-actions class="pa-6">
                  <v-btn
                    variant="text"
                    size="large"
                    @click="prevStep"
                  >
                    <v-icon icon="mdi-chevron-left" start />
                    上一步
                  </v-btn>
                  <v-spacer />
                  <!--v-btn
                    color="grey"
                    variant="outlined"
                    size="large"
                    class="mr-2"
                    :loading="saving"
                    @click="saveDraft"
                  >
                    <v-icon icon="mdi-content-save" start />
                    儲存草稿
                  </v-btn-->
                  <v-btn
                    color="primary"
                    variant="elevated"
                    size="large"
                    :loading="submitting"
                    @click="submitForReview"
                  >
                    <v-icon icon="mdi-plus" start />
                    新增寵物
                  </v-btn>
                </v-card-actions>
              </v-card>
            </template>
          </v-stepper>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import PetBasicInfoForm from '@/components/pet/PetBasicInfoForm.vue'
import PetPhotoUpload from '@/components/pet/PetPhotoUpload.vue'
import PetPreview from '@/components/pet/PetPreview.vue'
import { petService } from '@/services/pet'
import { useNotificationStore } from '@/stores/notification'
import type { PetCreate } from '@/types/pet'

const router = useRouter()
const notificationStore = useNotificationStore()

const currentStep = ref(1)
const steps = [
  { title: '基本資料', value: 1 },
  { title: '照片上傳', value: 2 },
  { title: '預覽發布', value: 3 },
]

const petData = ref<Partial<PetCreate>>({
  vaccination_status: false,
  sterilized: false,
})

interface PhotoData {
  id?: number
  file_id?: number
  url?: string
  preview?: string
}

const photos = ref<PhotoData[]>([])
const stepsValid = ref<boolean[]>([false, true, true])

const basicFormRef = ref()
const photoUploadRef = ref()

const saving = ref(false)
const submitting = ref(false)

const nextStep = async () => {
  // Validate current step
  let isValid = true

  if (currentStep.value === 1 && basicFormRef.value) {
    isValid = await basicFormRef.value.validate()
  }

  if (!isValid) {
    notificationStore.error('請填寫所有必填欄位')
    return
  }

  if (currentStep.value < 4) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const saveDraft = async () => {
  if (!petData.value.name || !petData.value.species) {
    notificationStore.error('請至少填寫寵物名稱和種類')
    return
  }

  saving.value = true
  try {
    const createdPet = await petService.createPet(petData.value as PetCreate)
    
    // Upload photos if any
    if (photos.value.length > 0 && createdPet.id) {
      for (let i = 0; i < photos.value.length; i++) {
        const photo = photos.value[i]
        if (photo.file_id) {
          await petService.addPhoto(createdPet.id, photo.file_id, i)
        }
      }
    }

    notificationStore.success('草稿已儲存')
    router.push('/pets/manage')
  } catch (error) {
    console.error('Failed to save draft:', error)
    notificationStore.error('儲存失敗')
  } finally {
    saving.value = false
  }
}

const submitForReview = async () => {
  if (!petData.value.name || !petData.value.species) {
    notificationStore.error('請填寫所有必填欄位')
    return
  }

  submitting.value = true
  try {
    // Create pet
    const createdPet = await petService.createPet(petData.value as PetCreate)
    
    // Link uploaded photos to the pet
    if (photos.value.length > 0 && createdPet.id) {
      try {
        await petService.linkPhotos(createdPet.id, photos.value)
        console.log('✅ Photos linked successfully')
      } catch (error) {
        console.error('⚠️  Failed to link photos:', error)
        // Don't fail the entire operation if photo linking fails
      }
    }
    
    notificationStore.success('寵物已發布')
    router.push('/pets/manage')
  } catch (error) {
    console.error('Failed to create pet:', error)
    notificationStore.error('發布失敗')
  } finally {
    submitting.value = false
  }
}
</script>
