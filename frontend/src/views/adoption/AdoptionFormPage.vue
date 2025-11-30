<template>
  <v-container class="adoption-form-page">
    <v-row justify="center">
      <v-col cols="12" md="10" lg="8">
        <h1 class="text-h4 mb-6">領養申請表單</h1>

        <FormProgressIndicator :current-step="currentStep" />

        <v-card>
          <v-card-text>
            <!-- Step 1: Personal Info -->
            <FormStep1PersonalInfo
              v-if="currentStep === 1"
              ref="step1Ref"
              v-model="formData.personal_info"
              @validate="autoSave"
            />

            <!-- Step 2: Living Environment -->
            <FormStep2LivingEnvironment
              v-if="currentStep === 2"
              ref="step2Ref"
              v-model="formData.living_environment"
              @validate="autoSave"
            />

            <!-- Step 3: Pet Experience -->
            <FormStep3PetExperience
              v-if="currentStep === 3"
              ref="step3Ref"
              v-model="formData.pet_experience"
              @validate="autoSave"
            />

            <!-- Step 4: Review -->
            <FormStep4Review
              v-if="currentStep === 4"
              ref="step4Ref"
              :data="formData"
              :pet="petData"
            />
          </v-card-text>

          <v-card-actions class="pa-4">
            <v-btn
              variant="text"
              prepend-icon="mdi-close"
              @click="goBack"
            >
              取消
            </v-btn>

            <v-spacer></v-spacer>
            
            <v-btn
              v-if="currentStep > 1"
              variant="text"
              color="grey"
              prepend-icon="mdi-arrow-left"
              @click="previousStep"
            >
              上一步
            </v-btn>

            <v-btn
              v-if="currentStep < 4"
              color="primary"
              @click="nextStep"
              :loading="validating"
            >
              下一步
              <v-icon>mdi-arrow-right</v-icon>
            </v-btn>

            <v-btn
              v-else
              color="success"
              @click="submitApplication"
              :loading="submitting"
            >
              提交申請
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- Auto-save indicator -->
        <v-snackbar v-model="showSaveNotification" :timeout="2000" color="success">
          草稿已自動儲存
        </v-snackbar>

        <!-- Submit Success Dialog -->
        <v-dialog v-model="submitSuccessDialog" max-width="500" persistent>
          <v-card>
            <v-card-text class="text-center py-8">
              <v-icon 
                icon="mdi-check-circle" 
                color="success" 
                size="80"
                class="mb-4"
              />
              <div class="text-h5 mb-3">申請表單已提交！</div>
              <div class="text-body-1 text-medium-emphasis mb-4">
                接下來請上傳必要文件以完成申請流程
              </div>
              <v-alert type="info" variant="tonal" density="compact">
                您將被導向至文件上傳頁面
              </v-alert>
            </v-card-text>
            <v-card-actions class="pa-4">
              <v-spacer />
              <v-btn
                color="primary"
                variant="elevated"
                size="large"
                @click="goToDocumentUpload"
              >
                <v-icon icon="mdi-file-upload" start />
                前往上傳文件
              </v-btn>
              <v-spacer />
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Validation Warning Dialog -->
        <v-dialog v-model="validationWarningDialog" max-width="500">
          <v-card>
            <v-card-text class="text-center py-8">
              <v-icon 
                icon="mdi-alert-circle" 
                color="warning" 
                size="80"
                class="mb-4"
              />
              <div class="text-h5 mb-3">請確認所有資料</div>
              <div class="text-body-1 text-medium-emphasis mb-4">
                請確認您已填寫完整資訊並同意服務條款
              </div>
              <v-alert type="warning" variant="tonal" density="compact">
                提交前請仔細檢查所有資訊是否正確
              </v-alert>
            </v-card-text>
            <v-card-actions class="pa-4">
              <v-spacer />
              <v-btn
                color="warning"
                variant="elevated"
                size="large"
                @click="validationWarningDialog = false"
              >
                <v-icon icon="mdi-check" start />
                我知道了
              </v-btn>
              <v-spacer />
            </v-card-actions>
          </v-card>
        </v-dialog>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { adoptionApi } from '@/api/adoption'
import { petService } from '@/services/pet'
import type { Pet } from '@/types/pet'
import type { 
  FormStep, 
  AdoptionApplicationCreate
} from '@/types/adoption'

import FormProgressIndicator from './components/FormProgressIndicator.vue'
import FormStep1PersonalInfo from './components/FormStep1PersonalInfo.vue'
import FormStep2LivingEnvironment from './components/FormStep2LivingEnvironment.vue'
import FormStep3PetExperience from './components/FormStep3PetExperience.vue'
import FormStep4Review from './components/FormStep4Review.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const currentStep = ref<FormStep>(1)
const saving = ref(false)
const validating = ref(false)
const submitting = ref(false)
const showSaveNotification = ref(false)
const submitSuccessDialog = ref(false)
const validationWarningDialog = ref(false)

const step1Ref = ref()
const step2Ref = ref()
const step3Ref = ref()
const step4Ref = ref()

const petId = parseInt(route.params.petId as string)
const applicationId = ref<number | null>(null)
const petData = ref<Pet | null>(null)

const goBack = () => {
  router.push(`/pets`)
}

// Fetch pet data
const fetchPetData = async () => {
  try {
    petData.value = await petService.getPetById(petId)
  } catch (error) {
    console.error('Failed to fetch pet data:', error)
  }
}

// Form data with default values
const formData = ref<AdoptionApplicationCreate>({
  pet_id: petId,
  personal_info: {
    name: '',
    phone: '',
    email: '',
    address: '',
    id_number: '',
    occupation: '',
    monthly_income: 0
  },
  living_environment: {
    housing_type: 'apartment',
    space_size: 0,
    has_yard: false,
    family_members: 1,
    has_allergies: false,
    other_pets: []
  },
  pet_experience: {
    previous_experience: '',
    pet_knowledge: '',
    care_schedule: '',
    veterinarian_info: '',
    emergency_fund: 0
  }
})

// Auto-save interval
let autoSaveInterval: NodeJS.Timeout | null = null

const startAutoSave = () => {
  autoSaveInterval = setInterval(() => {
    autoSave()
  }, 30000) // Auto-save every 30 seconds
}

const stopAutoSave = () => {
  if (autoSaveInterval) {
    clearInterval(autoSaveInterval)
    autoSaveInterval = null
  }
}

const autoSave = async () => {
  try {
    if (applicationId.value) {
      await adoptionApi.updateApplication(applicationId.value, formData.value)
    } else {
      const result = await adoptionApi.createApplication(formData.value)
      applicationId.value = result.id
    }
    // Save to localStorage as backup with user ID to prevent cross-user data
    const userId = authStore.user?.id
    if (userId) {
      localStorage.setItem(`adoption_draft_${userId}_${petId}`, JSON.stringify(formData.value))
    }
  } catch (error) {
    console.error('Auto-save failed:', error)
  }
}

const saveDraft = async () => {
  saving.value = true
  try {
    if (applicationId.value) {
      await adoptionApi.updateApplication(applicationId.value, formData.value)
    } else {
      const result = await adoptionApi.createApplication(formData.value)
      applicationId.value = result.id
    }
    showSaveNotification.value = true
    const userId = authStore.user?.id
    if (userId) {
      localStorage.setItem(`adoption_draft_${userId}_${petId}`, JSON.stringify(formData.value))
    }
  } catch (error: any) {
    alert('儲存失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    saving.value = false
  }
}

const nextStep = async () => {
  validating.value = true
  try {
    let isValid = false

    switch (currentStep.value) {
      case 1:
        isValid = await step1Ref.value?.validate()
        break
      case 2:
        isValid = await step2Ref.value?.validate()
        break
      case 3:
        isValid = await step3Ref.value?.validate()
        break
    }

    if (isValid) {
      currentStep.value = (currentStep.value + 1) as FormStep
      await autoSave()
    }
  } finally {
    validating.value = false
  }
}

const previousStep = () => {
  currentStep.value = (currentStep.value - 1) as FormStep
}

const submitApplication = async () => {
  if (!step4Ref.value?.validate()) {
    validationWarningDialog.value = true
    return
  }

  submitting.value = true
  try {
    if (!applicationId.value) {
      const result = await adoptionApi.createApplication(formData.value)
      applicationId.value = result.id
    }

    await adoptionApi.submitApplication(applicationId.value)
    
    // Clear draft from localStorage
    const userId = authStore.user?.id
    if (userId) {
      localStorage.removeItem(`adoption_draft_${userId}_${petId}`)
    }
    
    // Show success dialog
    submitSuccessDialog.value = true
  } catch (error: any) {
    alert('提交失敗: ' + (error.response?.data?.detail || error.message))
  } finally {
    submitting.value = false
  }
}

const goToDocumentUpload = () => {
  submitSuccessDialog.value = false
  router.push(`/applications/${applicationId.value}/documents`)
}

// Load draft on mount
onMounted(async () => {
  // Fetch pet data first
  await fetchPetData()
  
  // Load draft only for current user
  const userId = authStore.user?.id
  if (userId) {
    const savedDraft = localStorage.getItem(`adoption_draft_${userId}_${petId}`)
    if (savedDraft) {
      try {
        const parsed = JSON.parse(savedDraft)
        formData.value = { ...formData.value, ...parsed }
      } catch (error) {
        console.error('Failed to load draft:', error)
      }
    }
  }
  
  startAutoSave()
})

onUnmounted(() => {
  stopAutoSave()
})
</script>

<style scoped>
.adoption-form-page {
  padding: 2rem 0;
}

.text-h4 {
  color: #FF6B6B;
  font-weight: 600;
}
</style>
