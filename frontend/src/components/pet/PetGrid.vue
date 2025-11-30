<template>
  <div class="pet-grid">
    <!-- Loading State -->
    <v-row v-if="loading">
      <v-col
        v-for="i in skeletonCount"
        :key="`skeleton-${i}`"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <v-skeleton-loader
          type="card"
          elevation="2"
        />
      </v-col>
    </v-row>

    <!-- Empty State -->
    <v-row v-else-if="!pets.length" class="empty-state">
      <v-col cols="12" class="text-center py-16">
        <v-icon icon="mdi-emoticon-sad-outline" size="64" class="mb-4" color="grey" />
        <h3 class="text-h5 mb-2">{{ emptyMessage }}</h3>
        <p class="text-body-1 text-medium-emphasis">
          {{ emptySubMessage }}
        </p>
        <v-btn
          v-if="showResetButton"
          color="primary"
          class="mt-4"
          @click="$emit('reset-filters')"
        >
          重置篩選條件
        </v-btn>
      </v-col>
    </v-row>

    <!-- Pet Grid -->
    <v-row v-else>
      <v-col
        v-for="pet in pets"
        :key="pet.id"
        cols="12"
        sm="6"
        md="4"
        lg="3"
      >
        <PetCard :pet="pet" @click="$emit('pet-click', $event)" />
      </v-col>
    </v-row>
  </div>
</template>

<script setup lang="ts">
import PetCard from './PetCard.vue'

interface Pet {
  id: number
  name: string
  species: string
  breed: string | null
  age_years: number | null
  age_months: number | null
  gender: string | null
  status: string
  size: string | null
  adoption_fee: number | null
  vaccination_status: boolean
  sterilized: boolean
  primary_photo_url: string | null
  location: string | null
}

interface Props {
  pets: Pet[]
  loading?: boolean
  emptyMessage?: string
  emptySubMessage?: string
  showResetButton?: boolean
  skeletonCount?: number
}

withDefaults(defineProps<Props>(), {
  loading: false,
  emptyMessage: '沒有找到符合條件的寵物',
  emptySubMessage: '請嘗試調整篩選條件或稍後再試',
  showResetButton: false,
  skeletonCount: 8
})

defineEmits<{
  'reset-filters': []
  'pet-click': [petId: number]
}>()
</script>

<style scoped>
.pet-grid {
  width: 100%;
}

.empty-state {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
