<template>
  <v-form ref="formRef" v-model="valid" @submit.prevent>
    <v-container>
      <v-row>
        <!-- Section Title: Basic Info -->
        <v-col cols="12">
          <h3 class="text-h6 mb-2">寵物基本資料</h3>
          <v-divider class="mb-4" />
        </v-col>

        <!-- Pet Name -->
        <v-col cols="12" md="6">
          <v-text-field
            v-model="formData.name"
            label="寵物名稱 *"
            :rules="rules.name"
            variant="outlined"
            required
          />
        </v-col>

        <!-- Species -->
        <v-col cols="12" md="6">
          <v-select
            v-model="formData.species"
            label="種類 *"
            :items="speciesOptions"
            :rules="rules.species"
            variant="outlined"
            required
          />
        </v-col>

        <!-- Breed -->
        <v-col cols="12" md="6">
          <v-text-field
            v-model="formData.breed"
            label="品種"
            variant="outlined"
            hint="例如：柴犬、波斯貓"
          />
        </v-col>

        <!-- Birth Year -->
        <v-col cols="12" md="3">
          <v-select
            v-model.number="formData.age_years"
            label="出生年份"
            :items="birthYearOptions"
            :rules="rules.age_years"
            variant="outlined"
            hint="選擇出生年份"
          />
        </v-col>

        <!-- Birth Month -->
        <v-col cols="12" md="3">
          <v-select
            v-model.number="formData.age_months"
            label="出生月份"
            :items="birthMonthOptions"
            :rules="rules.age_months"
            variant="outlined"
            hint="選擇出生月份"
          />
        </v-col>

        <!-- Weight -->
        <v-col cols="12" md="6">
          <v-text-field
            v-model.number="formData.weight_kg"
            label="體重（公斤）"
            type="number"
            variant="outlined"
            hint="例如：5.5"
          />
        </v-col>

        <!-- Gender -->
        <v-col cols="12" md="4">
          <v-select
            v-model="formData.gender"
            label="性別"
            :items="genderOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Size -->
        <v-col cols="12" md="4">
          <v-select
            v-model="formData.size"
            label="體型"
            :items="sizeOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Color -->
        <v-col cols="12" md="4">
          <v-text-field
            v-model="formData.color"
            label="毛色"
            variant="outlined"
            hint="例如：黑色、棕白相間"
          />
        </v-col>



        <!-- Description -->
        <v-col cols="12">
          <v-textarea
            v-model="formData.description"
            label="寵物描述"
            variant="outlined"
            rows="4"
            hint="描述寵物的個性、習慣、喜好等"
          />
        </v-col>

        <!-- Behavioral Info -->
        <v-col cols="12">
          <v-textarea
            v-model="formData.behavioral_info"
            label="行為資訊"
            variant="outlined"
            rows="3"
            hint="描述寵物的行為特徵、訓練狀況等"
          />
        </v-col>

        <!-- Section Title: Health Info -->
        <v-col cols="12">
          <h3 class="text-h6 mb-2 mt-4">寵物健康狀況</h3>
          <v-divider class="mb-4" />
        </v-col>

        <!-- Health Status -->
        <v-col cols="12" md="6">
          <v-select
            v-model="formData.vaccination_status"
            label="疫苗注射狀態"
            :items="vaccinationOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Sterilized -->
        <v-col cols="12" md="6">
          <v-select
            v-model="formData.sterilized"
            label="絕育手術狀態"
            :items="sterilizedOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Health Status -->
        <v-col cols="12">
          <v-textarea
            v-model="formData.health_status"
            label="健康狀況"
            variant="outlined"
            rows="3"
            hint="描述寵物目前的健康狀態、病史等"
          />
        </v-col>

        <!-- Special Needs -->
        <v-col cols="12">
          <v-textarea
            v-model="formData.special_needs"
            label="特殊需求"
            variant="outlined"
            rows="3"
            hint="特殊照顧需求、疾病史、過敏等"
          />
        </v-col>

        <!-- Microchip ID -->
        <v-col cols="12" md="6">
          <v-text-field
            v-model="formData.microchip_id"
            label="晶片編號"
            variant="outlined"
            hint="如有植入晶片請填寫"
          />
        </v-col>

        <!-- Section Title: Behavioral Traits -->
        <v-col cols="12">
          <h3 class="text-h6 mb-2 mt-4">行為特徵</h3>
          <v-divider class="mb-4" />
        </v-col>

        <!-- House Trained -->
        <v-col cols="12" md="4">
          <v-select
            v-model="formData.house_trained"
            label="居家訓練"
            :items="booleanOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Good with Kids -->
        <v-col cols="12" md="4">
          <v-select
            v-model="formData.good_with_kids"
            label="適合有小孩家庭"
            :items="booleanOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Good with Pets -->
        <v-col cols="12" md="4">
          <v-select
            v-model="formData.good_with_pets"
            label="適合有其他寵物"
            :items="booleanOptions"
            variant="outlined"
          />
        </v-col>

        <!-- Energy Level -->
        <v-col cols="12" md="6">
          <v-select
            v-model="formData.energy_level"
            label="活動力"
            :items="energyLevelOptions"
            variant="outlined"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { PetSpecies, PetGender, PetSize, type PetCreate } from '@/types/pet'

interface Props {
  modelValue: Partial<PetCreate>
}

interface Emits {
  (e: 'update:modelValue', value: Partial<PetCreate>): void
  (e: 'valid', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref()
const valid = ref(false)
const formData = ref<Partial<PetCreate>>({ ...props.modelValue })

// Options
const speciesOptions = [
  { title: '狗', value: PetSpecies.DOG },
  { title: '貓', value: PetSpecies.CAT },
  //{ title: '兔子', value: PetSpecies.RABBIT },
  //{ title: '鳥類', value: PetSpecies.BIRD },
  //{ title: '其他', value: PetSpecies.OTHER },
]

const genderOptions = [
  { title: '公', value: PetGender.MALE },
  { title: '母', value: PetGender.FEMALE },
  //{ title: '未知', value: PetGender.UNKNOWN },
]

const sizeOptions = [
  { title: '小型', value: PetSize.SMALL },
  { title: '中型', value: PetSize.MEDIUM },
  { title: '大型', value: PetSize.LARGE },
]

const vaccinationOptions = [
  { title: '尚未完成', value: false },
  { title: '已完成', value: true },
]

const sterilizedOptions = [
  { title: '尚未完成', value: false },
  { title: '已完成', value: true },
]

const booleanOptions = [
  { title: '是', value: true },
  { title: '否', value: false },
]

const energyLevelOptions = [
  { title: '低', value: 'low' },
  { title: '中', value: 'medium' },
  { title: '高', value: 'high' },
]

// Generate birth year options (current year to 30 years ago)
const currentYear = new Date().getFullYear()
const birthYearOptions = Array.from({ length: 31 }, (_, i) => ({
  title: `${currentYear - i} 年`,
  value: currentYear - i,
}))

// Generate birth month options
const birthMonthOptions = Array.from({ length: 12 }, (_, i) => ({
  title: `${i + 1} 月`,
  value: i + 1,
}))

// Validation rules
const rules = {
  name: [
    (v: string) => !!v || '寵物名稱為必填',
    (v: string) => (v && v.length <= 100) || '名稱不能超過 100 字元',
  ],
  species: [(v: string) => !!v || '請選擇寵物種類'],
  age_years: [
    (v: number) => !v || (v >= 1990 && v <= currentYear) || '請選擇有效的出生年份',
  ],
  age_months: [
    (v: number) => !v || (v >= 1 && v <= 12) || '請選擇有效的出生月份 (1-12)',
  ],
}

// Watch form data changes and emit to parent
watch(
  formData,
  (newValue) => {
    emit('update:modelValue', newValue)
  },
  { deep: true }
)

// Watch valid state
watch(valid, (newValue) => {
  emit('valid', newValue)
})

// Initialize from props only on mount, not on every change
// This prevents the form from resetting while user is typing
onMounted(() => {
  if (props.modelValue) {
    formData.value = { ...props.modelValue }
  }
})

// Expose validate method
defineExpose({
  validate: async () => {
    const { valid } = await formRef.value.validate()
    return valid
  },
})
</script>

<style scoped>
/* Add any custom styles here */
</style>
