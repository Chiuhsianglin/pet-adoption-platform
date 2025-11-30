<template>
  <v-container class="py-8">
    <v-row justify="center">
      <v-col cols="12" lg="10">
        <v-card v-if="loading">
          <v-card-text class="text-center py-12">
            <v-progress-circular indeterminate color="primary" size="64" />
            <div class="mt-4">載入中...</div>
          </v-card-text>
        </v-card>

        <v-card v-else-if="pet">
          <v-card-title class="text-h4 pa-6 d-flex align-center">
            <v-icon icon="mdi-pencil" class="mr-2" />
            編輯寵物資訊
            <v-spacer />
            <PetStatusBadge :status="pet.status" size="large" />
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
                    @click="router.push('/pets/manage')"
                  >
                    <v-icon icon="mdi-close" start />
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
                    size="large"
                    @click="router.push('/pets/manage')"
                  >
                    <v-icon icon="mdi-close" start />
                    取消
                  </v-btn>                  
                  <v-spacer />
                  <v-btn
                    variant="text"
                    size="large"
                    @click="prevStep"
                  >
                    <v-icon icon="mdi-chevron-left" start />
                    上一步
                  </v-btn>
                  
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
                    size="large"
                    @click="router.push('/pets/manage')"
                  >
                    <v-icon icon="mdi-close" start />
                    取消
                  </v-btn>                 
                  <v-spacer />                  
                 <v-btn
                    variant="text"
                    size="large"
                    @click="prevStep"
                  >
                    <v-icon icon="mdi-chevron-left" start />
                    上一步
                  </v-btn>
                  <v-btn
                    color="primary"
                    variant="outlined"
                    size="large"
                    class="mr-2"
                    :loading="saving"
                    @click="saveChanges"
                  >
                    <v-icon icon="mdi-content-save" start />
                    儲存變更
                  </v-btn>
                  <v-btn
                    v-if="canSubmitForReview"
                    color="primary"
                    variant="elevated"
                    size="large"
                    :loading="submitting"
                    @click="submitForReview"
                  >
                    <v-icon icon="mdi-send" start />
                    提交審核
                  </v-btn>
                </v-card-actions>
              </v-card>
            </template>
          </v-stepper>
        </v-card>
      </v-col>
    </v-row>

    <!-- Success Dialog -->
    <v-dialog v-model="successDialog" max-width="400">
      <v-card>
        <v-card-text class="text-center py-3">
          <v-icon 
            icon="mdi-check-circle" 
            color="success" 
            size="64"
            class="mb-4"
          />
          <div class="text-h6 mb-2">編輯成功！</div>
          <div class="text-body-2 text-medium-emphasis">
            寵物資訊已更新
          </div>
        </v-card-text>
        <v-card-actions class="pa-4 d-flex justify-center">
          <v-btn
            color="primary"
            variant="outlined" 
            style="width: 150px"           
            @click="router.push({ path: `/pets/${pet?.id}`, query: { from: 'management' } })"
          >
            <v-icon icon="mdi-eye" start />
            查看詳情
          </v-btn>
          <v-btn
            color="primary"
            variant="elevated"
            style="width: 150px"           
            @click="router.push('/pets/manage')"
          >
            <v-icon icon="mdi-format-list-bulleted" start />
            返回列表
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import PetBasicInfoForm from '@/components/pet/PetBasicInfoForm.vue'
import PetPhotoUpload from '@/components/pet/PetPhotoUpload.vue'
import PetPreview from '@/components/pet/PetPreview.vue'
import PetStatusBadge from '@/components/pet/PetStatusBadge.vue'
import { petService } from '@/services/pet'
import { useNotificationStore } from '@/stores/notification'
import { PetStatus, type Pet, type PetUpdate } from '@/types/pet'

const route = useRoute()
const router = useRouter()
const notificationStore = useNotificationStore()

const currentStep = ref(1)
const steps = [
  { title: '基本資訊', value: 1 },
  { title: '照片上傳', value: 2 },
  { title: '預覽變更', value: 3 },
]

const pet = ref<Pet | null>(null)
const petData = ref<Partial<PetUpdate>>({})

interface PhotoData {
  id?: number
  file_id?: number
  url?: string
  file_url?: string
  file_key?: string
  preview?: string
}

const photos = ref<PhotoData[]>([])
const stepsValid = ref<boolean[]>([false, true, true])

const basicFormRef = ref()
const photoUploadRef = ref()

const loading = ref(false)
const saving = ref(false)
const submitting = ref(false)
const successDialog = ref(false)

const canSubmitForReview = computed(() => {
  return pet.value?.status === PetStatus.DRAFT || pet.value?.status === PetStatus.REJECTED
})

const fetchPet = async () => {
  const petId = parseInt(route.params.id as string)
  if (!petId) {
    notificationStore.error('無效的寵物 ID')
    router.push('/pets/manage')
    return
  }

  loading.value = true
  try {
    pet.value = await petService.getPetById(petId)
    console.log('📥 Loaded pet data:', pet.value)
    
    // Copy all pet data to form data
    petData.value = {
      name: pet.value.name,
      species: pet.value.species,
      breed: pet.value.breed,
      age_years: pet.value.age_years,
      age_months: pet.value.age_months,
      weight_kg: pet.value.weight_kg,
      gender: pet.value.gender,
      size: pet.value.size,
      color: pet.value.color,
      description: pet.value.description,
      behavioral_info: pet.value.behavioral_info,
      health_status: pet.value.health_status,
      vaccination_status: pet.value.vaccination_status,
      sterilized: pet.value.sterilized,
      special_needs: pet.value.special_needs,
      microchip_id: pet.value.microchip_id,
      house_trained: pet.value.house_trained,
      good_with_kids: pet.value.good_with_kids,
      good_with_pets: pet.value.good_with_pets,
      energy_level: pet.value.energy_level,
      adoption_fee: pet.value.adoption_fee,
    }
    
    console.log('📝 Form data initialized:', petData.value)
    
    // Load photos with proper field mapping
    if (pet.value.photos) {
      photos.value = pet.value.photos.map((photo) => ({
        id: photo.id,
        file_id: photo.file_id,
        url: photo.file_url || photo.url,
        file_url: photo.file_url || photo.url,
        file_key: photo.file_key,
        preview: photo.file_url || photo.url,
      }))
      console.log('📸 Loaded photos:', photos.value)
    }
  } catch (error) {
    console.error('Failed to fetch pet:', error)
    notificationStore.error('載入失敗')
    router.push('/pets/manage')
  } finally {
    loading.value = false
  }
}

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

  if (currentStep.value < 3) {
    currentStep.value++
  }
}

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

const saveChanges = async () => {
  if (!pet.value?.id) return

  saving.value = true
  try {
    // Update pet data
    await petService.updatePet(pet.value.id, petData.value)
    
    // Handle deleted photos (photos that were in original but not in current list)
    const originalPhotoIds = (pet.value.photos || []).map(p => p.id).filter(Boolean)
    const currentPhotoIds = photos.value.map(p => p.id).filter(Boolean)
    const deletedPhotoIds = originalPhotoIds.filter(id => !currentPhotoIds.includes(id))
    
    if (deletedPhotoIds.length > 0) {
      console.log('🗑️  Deleting photos:', deletedPhotoIds)
      for (const photoId of deletedPhotoIds) {
        try {
          await petService.deletePhoto(pet.value.id, photoId as number)
        } catch (error) {
          console.error(`⚠️  Failed to delete photo ${photoId}:`, error)
        }
      }
    }
    
    // Link any new photos (photos without an id are newly uploaded)
    const newPhotos = photos.value.filter(p => !p.id && (p.url || p.file_url))
    if (newPhotos.length > 0) {
      try {
        await petService.linkPhotos(pet.value.id, newPhotos)
        console.log('✅ New photos linked successfully')
      } catch (error) {
        console.error('⚠️  Failed to link photos:', error)
        // Don't fail the entire save operation
      }
    }
    
    // Show success message and redirect
    successDialog.value = true
  } catch (error) {
    console.error('Failed to save changes:', error)
    notificationStore.error('儲存失敗')
  } finally {
    saving.value = false
  }
}

const submitForReview = async () => {
  if (!pet.value?.id) return

  submitting.value = true
  try {
    // Save changes first
    await petService.updatePet(pet.value.id, petData.value)
    
    // Link any new photos
    const newPhotos = photos.value.filter(p => !p.id && (p.url || p.file_url))
    if (newPhotos.length > 0) {
      try {
        await petService.linkPhotos(pet.value.id, newPhotos)
        console.log('✅ New photos linked successfully')
      } catch (error) {
        console.error('⚠️  Failed to link photos:', error)
      }
    }
    
    // Submit for review
    await petService.submitForReview(pet.value.id)
    
    notificationStore.success('已提交審核')
    router.push('/pets/manage')
  } catch (error) {
    console.error('Failed to submit for review:', error)
    notificationStore.error('提交失敗')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // If called with a ?step=N query param, open that step directly
  const stepParam = route.query.step
  if (stepParam) {
    const s = parseInt(String(Array.isArray(stepParam) ? stepParam[0] : stepParam))
    if (!isNaN(s) && s >= 1 && s <= 3) {
      currentStep.value = s
    }
  }

  fetchPet()
})

// React to query changes so external navigation can change step
import { watch } from 'vue'
watch(
  () => route.query.step,
  (val) => {
    if (!val) return
    const s = parseInt(String(Array.isArray(val) ? val[0] : val))
    if (!isNaN(s) && s >= 1 && s <= 3) {
      currentStep.value = s
    }
  }
)
</script>
