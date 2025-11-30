<template>
  <v-card class="form-step">
    <v-card-title>確認資料</v-card-title>
    <v-card-text>
      <v-alert type="info" variant="tonal" class="mb-4">
        請仔細檢查您填寫的資料，確認無誤後即可提交申請。
      </v-alert>

      <!-- Pet Info Summary -->
      <div v-if="pet" class="review-section">
        <h3 class="text-h6 mb-3">申請領養的寵物</h3>
        <v-card  class="pet-info-card">
          <v-row no-gutters>
            <v-col cols="12" sm="4" md="3">
              <v-img
                :src="pet.primary_photo_url || (pet.photos && pet.photos[0]?.file_url) || '/placeholder-pet.jpg'"
                aspect-ratio="1"
                cover
                class="pet-photo"
              >
                <template #placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular indeterminate color="grey-lighten-5" />
                  </v-row>
                </template>
              </v-img>
            </v-col>
            <v-col cols="12" sm="8" md="9">
              <v-card-text>
                <h4 class="text-h5 mb-3">{{ pet.name }}</h4>
                <v-row dense>
                  <v-col cols="6" md="3">
                    <div class="text-caption text-medium-emphasis">品種</div>
                    <div class="text-body-1">{{ pet.breed }}</div>
                  </v-col>
                  <v-col cols="6" md="3">
                    <div class="text-caption text-medium-emphasis">年齡</div>
                    <div class="text-body-1">{{ calculateAge(pet.age_years, pet.age_months) }}</div>
                  </v-col>
                  <v-col cols="6" md="3">
                    <div class="text-caption text-medium-emphasis">性別</div>
                    <div class="text-body-1">{{ genderLabel(pet.gender) }}</div>
                  </v-col>
                  <v-col cols="6" md="3">
                    <div class="text-caption text-medium-emphasis">體型</div>
                    <div class="text-body-1">{{ sizeLabel(pet.size) }}</div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-col>
          </v-row>
        </v-card>
      </div>

      <v-divider class="my-4"></v-divider>

      <!-- Personal Info Summary -->
      <div class="review-section">
        <h3 class="text-h6 mb-3">個人資訊</h3>
        <v-row dense>
          <v-col cols="6" md="3"><strong>姓名:</strong></v-col>
          <v-col cols="6" md="3">{{ data.personal_info.name }}</v-col>
          <v-col cols="6" md="3"><strong>電話:</strong></v-col>
          <v-col cols="6" md="3">{{ data.personal_info.phone }}</v-col>
          <v-col cols="6" md="3"><strong>Email:</strong></v-col>
          <v-col cols="6" md="9">{{ data.personal_info.email }}</v-col>
          <v-col cols="6" md="3"><strong>身份證:</strong></v-col>
          <v-col cols="6" md="3">{{ data.personal_info.id_number }}</v-col>
          <v-col cols="6" md="3"><strong>職業:</strong></v-col>
          <v-col cols="6" md="3">{{ data.personal_info.occupation }}</v-col>
          <v-col cols="6" md="3"><strong>月收入:</strong></v-col>
          <v-col cols="6" md="9">NT$ {{ data.personal_info.monthly_income.toLocaleString() }}</v-col>
          <v-col cols="12"><strong>地址:</strong> {{ data.personal_info.address }}</v-col>
        </v-row>
      </div>

      <v-divider class="my-4"></v-divider>

      <!-- Living Environment Summary -->
      <div class="review-section">
        <h3 class="text-h6 mb-3">居住環境</h3>
        <v-row dense>
          <v-col cols="6" md="3"><strong>住宅類型:</strong></v-col>
          <v-col cols="6" md="3">{{ housingTypeLabel }}</v-col>
          <v-col cols="6" md="3"><strong>空間大小:</strong></v-col>
          <v-col cols="6" md="3">{{ data.living_environment.space_size }}  坪</v-col>
          <v-col cols="6" md="3"><strong>院子/陽台:</strong></v-col>
          <v-col cols="6" md="3">{{ data.living_environment.has_yard ? '有' : '無' }}</v-col>
          <v-col cols="6" md="3"><strong>家庭成員:</strong></v-col>
          <v-col cols="6" md="3">{{ data.living_environment.family_members }} 人</v-col>
          <v-col cols="6" md="3"><strong>過敏史:</strong></v-col>
          <v-col cols="6" md="9">{{ data.living_environment.has_allergies ? '有' : '無' }}</v-col>
          <v-col cols="12" v-if="data.living_environment.other_pets.length > 0">
            <strong>其他寵物:</strong>
            <ul>
              <li v-for="(pet, idx) in data.living_environment.other_pets" :key="idx">
                {{ pet.species }} ({{ pet.age }} 歲) - {{ pet.vaccinated ? '已施打疫苗' : '未施打疫苗' }}
              </li>
            </ul>
          </v-col>
          
          <!-- 居住環境照片 -->
          <v-col cols="12" v-if="data.living_environment.environment_photos && data.living_environment.environment_photos.length > 0">
            <strong class="d-block mb-2">居住環境照片:</strong>
            <v-row>
              <v-col
                v-for="(photo, idx) in data.living_environment.environment_photos"
                :key="idx"
                cols="6"
                sm="4"
                md="3"
              >
                <v-img
                  :src="photo.file_url || photo.url"
                  aspect-ratio="1"
                  cover
                  class="rounded"
                >
                  <template #placeholder>
                    <v-row
                      class="fill-height ma-0"
                      align="center"
                      justify="center"
                    >
                      <v-progress-circular indeterminate color="grey-lighten-5" />
                    </v-row>
                  </template>
                </v-img>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </div>

      <v-divider class="my-4"></v-divider>

      <!-- Pet Experience Summary -->
      <div class="review-section">
        <h3 class="text-h6 mb-3">養寵經驗</h3>
        <div class="mb-2">
          <strong>過往經驗:</strong>
          <p class="mt-1">{{ data.pet_experience.previous_experience }}</p>
        </div>
        <div class="mb-2">
          <strong>寵物了解:</strong>
          <p class="mt-1">{{ data.pet_experience.pet_knowledge }}</p>
        </div>
        <div class="mb-2">
          <strong>照護計劃:</strong>
          <p class="mt-1">{{ data.pet_experience.care_schedule }}</p>
        </div>
        <div class="mb-2">
          <strong>獸醫資訊:</strong> {{ data.pet_experience.veterinarian_info }}
        </div>
        <div>
          <strong>緊急費用:</strong> NT$ {{ data.pet_experience.emergency_fund.toLocaleString() }}
        </div>
      </div>

      <v-divider class="my-4"></v-divider>

      <v-checkbox
        v-model="agreedToTerms"
        label="我確認以上資料正確無誤，並同意相關條款"
        :rules="[v => !!v || '請確認資料並同意條款']"
      ></v-checkbox>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { AdoptionApplicationCreate } from '@/types/adoption'
import type { Pet } from '@/types/pet'
import { calculateAge } from '@/utils/ageCalculator'

interface Props {
  data: AdoptionApplicationCreate
  pet: Pet | null
}

const props = defineProps<Props>()

const agreedToTerms = ref(false)

const housingTypeLabel = computed(() => {
  const types: Record<string, string> = {
    apartment: '公寓',
    house: '獨棟住宅',
    rental: '租屋',
    owned: '自有'
  }
  return types[props.data.living_environment.housing_type] || props.data.living_environment.housing_type
})

const genderLabel = (gender: string | undefined) => {
  if (!gender) return '未知'
  const labels: Record<string, string> = {
    male: '男生',
    female: '女生',
    unknown: '未知'
  }
  return labels[gender] || gender
}

const sizeLabel = (size: string | undefined) => {
  if (!size) return '未知'
  const labels: Record<string, string> = {
    small: '小型',
    medium: '中型',
    large: '大型'
  }
  return labels[size] || size
}

const validate = () => {
  return agreedToTerms.value
}

defineExpose({ validate })
</script>

<style scoped>
.form-step {
  margin-bottom: 1.5rem;
}

.review-section {
  padding: 1rem 0;
}

.review-section p {
  white-space: pre-wrap;
  color: #616161;
}

.pet-info-card {
  overflow: hidden;
}

.pet-photo {
  border-radius: 8px 0 0 8px;
  max-height: 180px; /* 調整為更小的尺寸 */
  object-fit: cover;
}

@media (max-width: 599px) {
  .pet-photo {
    border-radius: 8px 8px 0 0;
    max-height: 150px; /* 手機版的大小 */
  }
}
</style>
