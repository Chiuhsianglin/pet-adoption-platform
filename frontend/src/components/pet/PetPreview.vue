<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h5">
            預覽寵物資訊
          </v-card-title>

          <v-divider />

          <v-card-text>
            <!-- Photos -->
            <div v-if="photos && photos.length > 0" class="mb-6">
              <h3 class="text-h6 mb-3">照片</h3>
              <v-row>
                <v-col
                  v-for="(photo, index) in photos"
                  :key="index"
                  cols="6"
                  md="4"
                  lg="3"
                >
                  <v-img
                    :src="photo.url || photo.preview"
                    aspect-ratio="1"
                    cover
                    class="rounded"
                  />
                </v-col>
              </v-row>
            </div>

            <!-- Basic Information -->
            <div class="mb-6">
              <h3 class="text-h6 mb-3">基本資訊</h3>
              <v-row>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">名稱</div>
                  <div class="text-body-1">{{ petData.name || '-' }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">種類</div>
                  <div class="text-body-1">{{ getSpeciesLabel(petData.species) }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">品種</div>
                  <div class="text-body-1">{{ petData.breed || '-' }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">出生年月 / 年齡</div>
                  <div class="text-body-1">
                    <div v-if="petData.age_years && petData.age_months">
                      {{ petData.age_years }}年{{ petData.age_months }}月
                    </div>
                    <div v-if="petData.age_years && petData.age_months" class="text-caption text-grey">
                      ({{ calculateAge(petData.age_years, petData.age_months) }})
                    </div>
                    <div v-if="!petData.age_years || !petData.age_months">-</div>
                  </div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">性別</div>
                  <div class="text-body-1">{{ getGenderLabel(petData.gender) }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">體型</div>
                  <div class="text-body-1">{{ getSizeLabel(petData.size) }}</div>
                </v-col>
                <v-col cols="6" md="3">
                  <div class="text-caption text-grey">毛色</div>
                  <div class="text-body-1">{{ petData.color || '-' }}</div>
                </v-col>
                <!--<v-col cols="6" md="4">
                  <div class="text-caption text-grey">領養費用</div>
                  <div class="text-body-1">
                    {{ petData.adoption_fee ? `NT$ ${petData.adoption_fee}` : '-' }}
                  </div>
                </v-col>-->
              </v-row>
            </div>

            <!-- Description -->
            <div v-if="petData.description" class="mb-6">
              <v-row>
                <v-col>
                  <div class="text-caption text-grey">寵物描述</div>
                  <div class="text-body-1">{{ petData.description || '-' }}</div>
                </v-col>
              </v-row>
            </div>
            <!-- Behavioral Info -->
            <div v-if="petData.behavioral_info" class="mb-6">
              <v-row>
                <v-col>
                  <div class="text-caption text-grey">行為資訊</div>
                  <div class="text-body-1">{{ petData.behavioral_info || '-' }}</div>
                </v-col>
              </v-row>
            </div>
            <!-- Health Information -->
            <div class="mb-6">
              <h3 class="text-h6 mb-3">健康資訊</h3>
              <v-row>
                <v-col cols="12" md="6">
                  <v-chip
                    :color="petData.vaccination_status ? 'success' : 'default'"
                    size="small"
                    class="mr-2"
                  >
                    {{ petData.vaccination_status ? '✓ 已完成疫苗注射' : '尚未完成疫苗注射' }}
                  </v-chip>
                </v-col>
                <v-col cols="12" md="6">
                  <v-chip
                    :color="petData.sterilized ? 'success' : 'default'"
                    size="small"
                  >
                    {{ petData.sterilized ? '✓ 已完成絕育手術' : '尚未完成絕育手術' }}
                  </v-chip>
                </v-col>
                <v-col v-if="petData.health_status" cols="12">
                  <div class="text-caption text-grey">健康狀況</div>
                  <p class="text-body-1">{{ petData.health_status }}</p>
                </v-col>
                <v-col v-if="petData.special_needs" cols="12">
                  <div class="text-caption text-grey">特殊需求</div>
                  <p class="text-body-1">{{ petData.special_needs }}</p>
                </v-col>
              </v-row>
            </div>

            <!-- Warning if missing required fields -->
            <v-alert v-if="missingRequiredFields.length > 0" type="warning" variant="tonal">
              <strong>缺少必填欄位：</strong>
              <ul class="mt-2">
                <li v-for="field in missingRequiredFields" :key="field">{{ field }}</li>
              </ul>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { PetSpecies, PetGender, PetSize, type PetCreate } from '@/types/pet'
import { calculateAge } from '@/utils/ageCalculator'

interface PhotoData {
  url?: string
  preview?: string
}

interface Props {
  petData: Partial<PetCreate>
  photos?: PhotoData[]
}

const props = defineProps<Props>()

const getSpeciesLabel = (species?: PetSpecies) => {
  const labels = {
    [PetSpecies.DOG]: '狗',
    [PetSpecies.CAT]: '貓',
    [PetSpecies.RABBIT]: '兔子',
    [PetSpecies.BIRD]: '鳥類',
    [PetSpecies.OTHER]: '其他',
  }
  return species ? labels[species] : '-'
}

const getGenderLabel = (gender?: PetGender) => {
  const labels = {
    [PetGender.MALE]: '公',
    [PetGender.FEMALE]: '母',
    [PetGender.UNKNOWN]: '未知',
  }
  return gender ? labels[gender] : '-'
}

const getSizeLabel = (size?: PetSize) => {
  const labels = {
    [PetSize.SMALL]: '小型',
    [PetSize.MEDIUM]: '中型',
    [PetSize.LARGE]: '大型',
  }
  return size ? labels[size] : '-'
}

const missingRequiredFields = computed(() => {
  const missing: string[] = []
  if (!props.petData.name) missing.push('寵物名稱')
  if (!props.petData.species) missing.push('種類')
  return missing
})
</script>

<style scoped>
ul {
  padding-left: 20px;
}

li {
  margin: 4px 0;
}
</style>
