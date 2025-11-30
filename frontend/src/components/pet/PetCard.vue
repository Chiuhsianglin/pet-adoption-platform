<template>
  <v-card
    class="pet-card"
    elevation="2"
    hover
    @click="$emit('click', pet.id)"
  >
    <!-- Pet Image -->
    <v-img
      :src="pet.primary_photo_url || '/placeholder-pet.png'"
      :alt="pet.name"
      aspect-ratio="1"
      cover
      class="pet-image"
    >
      <!-- Status Badge -->
      <v-chip
        :color="statusColor"
        variant="flat"
        size="small"
        class="status-badge"
      >
        {{ statusText }}
      </v-chip>

      <!-- Favorite Button -->
      <v-btn
        :icon="isFavorite ? 'mdi-heart' : 'mdi-heart-outline'"
        :color="isFavorite ? 'red' : 'white'"
        size="small"
        class="favorite-btn"
        disabled
        @click.stop.prevent="toggleFavorite"
      />
    </v-img>

    <!-- Pet Info -->
    <v-card-text class="pet-info">
      <!-- Name and Species -->
      <div class="d-flex align-center mb-2">
        <v-icon :icon="speciesIcon" size="small" class="mr-1" />
        <h3 class="text-h6 text-truncate">{{ pet.name }}</h3>
      </div>

      <!-- Breed -->
      <p v-if="pet.breed" class="text-body-2 text-medium-emphasis mb-1">
        {{ pet.breed }}
      </p>

      <!-- Details Row -->
      <div class="details-row">
        <!-- Age -->
        <v-chip
          v-if="pet.age_years && pet.age_months"
          size="x-small"
          variant="outlined"
          prepend-icon="mdi-calendar"
        >
          {{ ageText }}
        </v-chip>

        <!-- Gender -->
        <v-chip
          v-if="pet.gender"
          size="x-small"
          variant="outlined"
          :prepend-icon="genderIcon"
        >
          {{ genderText }}
        </v-chip>

        <!-- Size -->
        <v-chip
          v-if="pet.size"
          size="x-small"
          variant="outlined"
          prepend-icon="mdi-ruler"
        >
          {{ sizeText }}
        </v-chip>
      </div>

      <!-- Location -->
      <div v-if="pet.location" class="location mt-2">
        <v-icon icon="mdi-map-marker" size="small" />
        <span class="text-caption">{{ pet.location }}</span>
      </div>

      <!-- Tags -->
      <div class="tags mt-2">
        <v-chip
          v-if="pet.vaccination_status"
          size="x-small"
          color="green"
          variant="flat"
          class="mr-1"
        >
          <v-icon icon="mdi-needle" start size="x-small" />
          已疫苗
        </v-chip>
        <v-chip
          v-if="pet.sterilized"
          size="x-small"
          color="blue"
          variant="flat"
        >
          <v-icon icon="mdi-check-circle" start size="x-small" />
          已結紮
        </v-chip>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useFavoritesStore } from '@/stores/favorites'
import { calculateAge } from '@/utils/ageCalculator'

interface Pet {
  id: number
  name: string
  species: string
  breed: string | null
  age_years: number | null
  age_months: number | null
  gender: string | null
  size: string | null
  status: string
  location: string | null
  adoption_fee: number | null
  primary_photo_url: string | null
  vaccination_status: boolean
  sterilized: boolean
}

interface Props {
  pet: Pet
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [petId: number]
}>()

const favoritesStore = useFavoritesStore()

// Computed
const isFavorite = computed(() => {
  return favoritesStore.isFavoriteForCurrentUser
    ? favoritesStore.isFavoriteForCurrentUser(props.pet.id)
    : favoritesStore.isFavorite(props.pet.id)
})

const statusColor = computed(() => {
  const colors: Record<string, string> = {
    available: 'success',
    pending_review: 'warning',
    reserved: 'info',
    adopted: 'grey',
    unavailable: 'error'
  }
  return colors[props.pet.status] || 'grey'
})

const statusText = computed(() => {
  const texts: Record<string, string> = {
    available: '可領養',
    pending_review: '審核中',
    reserved: '已預約',
    adopted: '已領養',
    unavailable: '不可領養'
  }
  return texts[props.pet.status] || props.pet.status
})

const speciesIcon = computed(() => {
  const icons: Record<string, string> = {
    dog: 'mdi-dog',
    cat: 'mdi-cat',
    rabbit: 'mdi-rabbit',
    bird: 'mdi-bird',
    other: 'mdi-paw'
  }
  return icons[props.pet.species] || 'mdi-paw'
})

const ageText = computed(() => {
  return calculateAge(props.pet.age_years ?? undefined, props.pet.age_months ?? undefined)
})

const genderIcon = computed(() => {
  const icons: Record<string, string> = {
    male: 'mdi-gender-male',
    female: 'mdi-gender-female',
    unknown: 'mdi-help-circle'
  }
  return icons[props.pet.gender || 'unknown'] || 'mdi-help-circle'
})

const genderText = computed(() => {
  const texts: Record<string, string> = {
    male: '公',
    female: '母',
    unknown: '未知'
  }
  return texts[props.pet.gender || 'unknown'] || '未知'
})

const sizeText = computed(() => {
  const texts: Record<string, string> = {
    small: '小型',
    medium: '中型',
    large: '大型'
  }
  return texts[props.pet.size || ''] || ''
})

// Methods
const toggleFavorite = async () => {
  if (isFavorite.value) {
    await favoritesStore.removeFavorite(props.pet.id)
  } else {
    await favoritesStore.addFavorite(props.pet.id)
  }
}
</script>

<style scoped lang="scss">
.pet-card {
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  }

  .pet-image {
    position: relative;

    .status-badge {
      position: absolute;
      top: 8px;
      left: 8px;
      z-index: 1;
    }

    .favorite-btn {
      position: absolute;
      top: 8px;
      right: 8px;
      z-index: 1;
      background-color: rgba(255, 255, 255, 0.9);
    }
  }

  .pet-info {
    h3 {
      font-weight: 600;
    }

    .details-row {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }

    .location {
      display: flex;
      align-items: center;
      gap: 4px;
      color: rgba(0, 0, 0, 0.6);
    }

    .tags {
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }
  }
}
</style>
