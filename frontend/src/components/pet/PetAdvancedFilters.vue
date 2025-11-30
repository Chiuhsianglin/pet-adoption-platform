<template>
  <v-card class="pet-advanced-filters" elevation="2">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>進階篩選</span>
      <v-chip 
        v-if="appliedFiltersCount > 0" 
        size="small" 
        color="primary"
      >
        {{ appliedFiltersCount }}
      </v-chip>
    </v-card-title>

    <v-divider />

    <v-card-text class="pa-4">
      <!-- Species Filter -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between w-100">
              <span>🐾 物種</span>
              <v-chip 
                v-if="selectedSpecies.length > 0" 
                size="x-small" 
                color="primary"
                class="mr-2"
              >
                {{ selectedSpecies.length }}
              </v-chip>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-checkbox
              v-for="species in speciesOptions"
              :key="species.value"
              v-model="selectedSpecies"
              :value="species.value"
              :label="species.label"
              density="compact"
              hide-details
              class="mb-1"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Gender Filter -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between w-100">
              <span>⚥ 性別</span>
              <v-chip 
                v-if="selectedGender && selectedGender !== 'all'" 
                size="x-small" 
                color="primary"
                class="mr-2"
              >
                1
              </v-chip>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-radio-group v-model="selectedGender" density="compact" hide-details>
              <v-radio value="all" label="全部" />
              <v-radio
                v-for="gender in genderOptions"
                :key="gender.value"
                :value="gender.value"
                :label="gender.label"
              />
            </v-radio-group>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Size Filter -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between w-100">
              <span>📏 體型</span>
              <v-chip 
                v-if="selectedSizes.length > 0" 
                size="x-small" 
                color="primary"
                class="mr-2"
              >
                {{ selectedSizes.length }}
              </v-chip>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-checkbox
              v-for="size in sizeOptions"
              :key="size.value"
              v-model="selectedSizes"
              :value="size.value"
              :label="size.label"
              density="compact"
              hide-details
              class="mb-1"
            />
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Age Range Filter -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between w-100">
              <span>🎂 年齡</span>
              <v-chip 
                v-if="ageRange[0] > 0 || ageRange[1] < 20" 
                size="x-small" 
                color="primary"
                class="mr-2"
              >
                1
              </v-chip>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <div class="px-2">
              <div class="text-caption mb-2">
                {{ ageRange[0] }}歲 - {{ ageRange[1] }}歲
              </div>
              <v-range-slider
                v-model="ageRange"
                :min="0"
                :max="20"
                :step="1"
                thumb-label
                hide-details
                color="primary"
              >
                <template #thumb-label="{ modelValue }">
                  {{ modelValue }}歲
                </template>
              </v-range-slider>
            </div>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Health & Behavior Filters -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between w-100">
              <span>💚 健康與行為</span>
              <v-chip 
                v-if="healthFiltersCount > 0" 
                size="x-small" 
                color="primary"
                class="mr-2"
              >
                {{ healthFiltersCount }}
              </v-chip>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-checkbox
              v-model="spayedNeutered"
              label="已絕育"
              density="compact"
              hide-details
              class="mb-1"
            />
            <v-checkbox
              v-model="goodWithKids"
              label="適合有小孩的家庭"
              density="compact"
              hide-details
              class="mb-1"
            />
            <v-checkbox
              v-model="goodWithPets"
              label="能與其他寵物相處"
              density="compact"
              hide-details
            />
          </v-expansion-panel-text>
        </v-expansion-panel> 
      </v-expansion-panels>

      <!-- Energy Level Filter -->
      <v-expansion-panels variant="accordion" class="mb-4">
        <v-expansion-panel>
          <v-expansion-panel-title>
            <div class="d-flex justify-space-between w-100">
              <span>⚡ 活力程度</span>
              <v-chip 
                v-if="selectedEnergyLevel" 
                size="x-small" 
                color="primary"
                class="mr-2"
              >
                1
              </v-chip>
            </div>
          </v-expansion-panel-title>
          <v-expansion-panel-text>
            <v-radio-group v-model="selectedEnergyLevel" density="compact" hide-details>
              <v-radio :value="null" label="不限" />
              <v-radio
                v-for="level in energyLevelOptions"
                :key="level.value"
                :value="level.value"
                :label="level.label"
              />
            </v-radio-group>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>
    </v-card-text>

    <v-divider />

    <!-- Action Buttons -->
    <v-card-actions class="px-4 py-3">
      <v-row dense no-gutters>
        <v-col cols="6" class="pr-1">
          <v-btn
            variant="outlined"
            color="error"
            block
            :disabled="appliedFiltersCount === 0"
            @click="handleReset"
          >
            <v-icon start>mdi-refresh</v-icon>
            重置篩選
          </v-btn>
        </v-col>
        <v-col cols="6" class="pl-1">
          <v-btn
            variant="flat"
            color="primary"
            block
            @click="handleApply"
          >
            <v-icon start>mdi-check</v-icon>
            套用篩選
          </v-btn>
        </v-col>
      </v-row>
    </v-card-actions>

  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import type { PetSearchFilters, FilterOptions } from '@/composables/useSearch'

interface Props {
  filters?: PetSearchFilters
  filterOptions?: FilterOptions | null
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  filters: () => ({}),
  filterOptions: null,
  loading: false
})

const emit = defineEmits<{
  'update:filters': [filters: PetSearchFilters]
  'apply': []
  'reset': []
}>()

// Local state for filters
const selectedSpecies = ref<string[]>([])
const selectedGender = ref<string>('all')
const selectedSizes = ref<string[]>([])
const ageRange = ref<[number, number]>([0, 20])
const spayedNeutered = ref(false)
const goodWithKids = ref(false)
const goodWithPets = ref(false)
const selectedEnergyLevel = ref<string | null>(null)

// 中文對照表
const speciesLabelMap: Record<string, string> = {
  'dog': '狗',
  'cat': '貓',
  'bird': '鳥',
  'rabbit': '兔子',
  'other': '其他'
}

const genderLabelMap: Record<string, string> = {
  'male': '公',
  'female': '母',
  'unknown': '未知'
}

const sizeLabelMap: Record<string, string> = {
  'small': '小型',
  'medium': '中型',
  'large': '大型',
  'extra_large': '超大型'
}

const energyLevelLabelMap: Record<string, string> = {
  'low': '低',
  'medium': '中',
  'high': '高'
}

// Filter options with Chinese labels
const speciesOptions = computed(() => {
  if (props.filterOptions?.species) {
    return props.filterOptions.species
      .filter(item => item.value === 'dog' || item.value === 'cat')
      .map(item => ({
        ...item,
        label: speciesLabelMap[item.value] || item.label
      }))
  }
  return [
    { value: 'dog', label: '狗', count: 0 },
    { value: 'cat', label: '貓', count: 0 }
  ]
})

const genderOptions = computed(() => {
  if (props.filterOptions?.genders) {
    return props.filterOptions.genders
      .filter(item => item.value !== 'unknown')
      .map(item => ({
        ...item,
        label: genderLabelMap[item.value] || item.label
      }))
  }
  return [
    { value: 'male', label: '公', count: 0 },
    { value: 'female', label: '母', count: 0 },
  ]
})

const sizeOptions = computed(() => {
  if (props.filterOptions?.sizes) {
    return props.filterOptions.sizes.map(item => ({
      ...item,
      label: sizeLabelMap[item.value] || item.label
    }))
  }
  return [
    { value: 'small', label: '小型', count: 0 },
    { value: 'medium', label: '中型', count: 0 },
    { value: 'large', label: '大型', count: 0 },
    { value: 'extra_large', label: '超大型', count: 0 }
  ]
})

const energyLevelOptions = computed(() => {
  if (props.filterOptions?.energy_levels) {
    return props.filterOptions.energy_levels.map(item => ({
      ...item,
      label: energyLevelLabelMap[item.value] || item.label
    }))
  }
  return [
    { value: 'low', label: '低', count: 0 },
    { value: 'medium', label: '中', count: 0 },
    { value: 'high', label: '高', count: 0 }
  ]
})

// Computed
const healthFiltersCount = computed(() => {
  let count = 0
  if (spayedNeutered.value) count++
  if (goodWithKids.value) count++
  if (goodWithPets.value) count++
  return count
})

const appliedFiltersCount = computed(() => {
  let count = 0
  if (selectedSpecies.value.length > 0) count += selectedSpecies.value.length
  if (selectedGender.value && selectedGender.value !== 'all') count++
  if (selectedSizes.value.length > 0) count += selectedSizes.value.length
  if (ageRange.value[0] > 0 || ageRange.value[1] < 20) count++
  if (spayedNeutered.value) count++
  if (goodWithKids.value) count++
  if (goodWithPets.value) count++
  if (selectedEnergyLevel.value) count++
  return count
})

// Initialize from props
onMounted(() => {
  syncFromProps()
})

watch(() => props.filters, () => {
  syncFromProps()
}, { deep: true })

const syncFromProps = () => {
  if (props.filters.species) selectedSpecies.value = [...props.filters.species]
  if (props.filters.gender) selectedGender.value = props.filters.gender
  if (props.filters.size) selectedSizes.value = [...props.filters.size]
  if (props.filters.min_age !== undefined || props.filters.max_age !== undefined) {
    ageRange.value = [props.filters.min_age ?? 0, props.filters.max_age ?? 20]
  }
  spayedNeutered.value = props.filters.spayed_neutered ?? false
  goodWithKids.value = props.filters.good_with_kids ?? false
  goodWithPets.value = props.filters.good_with_pets ?? false
  selectedEnergyLevel.value = props.filters.energy_level || null
}

const buildFilters = (): PetSearchFilters => {
  const filters: PetSearchFilters = {}
  
  if (selectedSpecies.value.length > 0) {
    filters.species = selectedSpecies.value
  }
  
  if (selectedGender.value && selectedGender.value !== 'all') {
    filters.gender = selectedGender.value
  }
  
  if (selectedSizes.value.length > 0) {
    filters.size = selectedSizes.value
  }
  
  if (ageRange.value[0] > 0) {
    filters.min_age = ageRange.value[0]
  }
  
  if (ageRange.value[1] < 20) {
    filters.max_age = ageRange.value[1]
  }
  
  if (spayedNeutered.value) {
    filters.spayed_neutered = true
  }
  
  if (goodWithKids.value) {
    filters.good_with_kids = true
  }
  
  if (goodWithPets.value) {
    filters.good_with_pets = true
  }
  
  if (selectedEnergyLevel.value) {
    filters.energy_level = selectedEnergyLevel.value
  }
  
  return filters
}

const handleApply = () => {
  const filters = buildFilters()
  emit('update:filters', filters)
  emit('apply')
}

const handleReset = () => {
  selectedSpecies.value = []
  selectedGender.value = 'all'
  selectedSizes.value = []
  ageRange.value = [0, 20]
  spayedNeutered.value = false
  goodWithKids.value = false
  goodWithPets.value = false
  selectedEnergyLevel.value = null
  
  emit('update:filters', {})
  emit('reset')
}
</script>

<style scoped>
.pet-advanced-filters {
  height: 100%;
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.pet-advanced-filters :deep(.v-expansion-panel-text__wrapper) {
  padding: 8px 16px;
}

.pet-advanced-filters :deep(.v-expansion-panel-title) {
  font-weight: 500;
}
</style>
