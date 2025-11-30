<template>
  <v-app>
    <app-header />
    <v-main>
      <v-container class="py-8">
      <v-row>
        <!-- Filters Sidebar -->
        <v-col cols="12" md="3">
          <v-card>
            <v-card-title class="bg-primary">
              <v-icon icon="mdi-filter" class="mr-2" />
              篩選條件
            </v-card-title>
            <v-card-text>
              <v-text-field
                v-model="filters.search"
                label="搜尋"
                prepend-inner-icon="mdi-magnify"
                variant="outlined"
                density="compact"
                clearable
                class="mb-4"
              />

              <v-select
                v-model="filters.species"
                label="物種"
                :items="speciesOptions"
                variant="outlined"
                density="compact"
                clearable
                class="mb-4"
              />

              <v-select
                v-model="filters.age"
                label="年齡"
                :items="ageOptions"
                variant="outlined"
                density="compact"
                clearable
                class="mb-4"
              />

              <v-select
                v-model="filters.size"
                label="體型"
                :items="sizeOptions"
                variant="outlined"
                density="compact"
                clearable
                class="mb-4"
              />

              <v-btn
                color="primary"
                block
                @click="applyFilters"
              >
                套用篩選
              </v-btn>
            </v-card-text>
          </v-card>
        </v-col>

        <!-- Pet List -->
        <v-col cols="12" md="9">
          <v-row class="mb-4">
            <v-col>
              <h1 class="text-h4">瀏覽寵物</h1>
              <p class="text-body-1 text-grey">找到您的完美夥伴</p>
            </v-col>
          </v-row>

          <v-row v-if="loading">
            <v-col v-for="n in 6" :key="n" cols="12" sm="6" md="4">
              <v-skeleton-loader type="card" />
            </v-col>
          </v-row>

          <v-row v-else-if="pets.length === 0">
            <v-col cols="12">
              <v-alert type="info" variant="tonal">
                目前沒有符合條件的寵物
              </v-alert>
            </v-col>
          </v-row>

          <v-row v-else>
            <v-col
              v-for="pet in pets"
              :key="pet.id"
              cols="12"
              sm="6"
              md="4"
            >
              <v-card
                hover
                @click="goToPetDetail(pet.id)"
                class="pet-card"
              >
                <v-img
                  :src="pet.image || '/placeholder-pet.jpg'"
                  height="200"
                  cover
                >
                  <v-chip
                    class="ma-2"
                    :color="getStatusColor(pet.status)"
                    size="small"
                  >
                    {{ getStatusText(pet.status) }}
                  </v-chip>
                </v-img>

                <v-card-title>{{ pet.name }}</v-card-title>

                <v-card-text>
                  <div class="d-flex align-center mb-2">
                    <v-icon icon="mdi-paw" size="small" class="mr-2" />
                    <span>{{ pet.species }} - {{ pet.breed }}</span>
                  </div>
                  <div class="d-flex align-center mb-2">
                    <v-icon icon="mdi-clock" size="small" class="mr-2" />
                    <span>{{ pet.age }} 歲</span>
                  </div>
                  <div class="d-flex align-center">
                    <v-icon icon="mdi-map-marker" size="small" class="mr-2" />
                    <span>{{ pet.location }}</span>
                  </div>
                </v-card-text>

                <v-card-actions>
                  <v-btn
                    color="primary"
                    variant="text"
                    @click.stop="goToPetDetail(pet.id)"
                  >
                    查看詳情
                  </v-btn>
                  <v-spacer />
                  <v-btn
                    icon="mdi-heart-outline"
                    variant="text"
                    @click.stop="toggleFavorite(pet.id)"
                  />
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>

          <!-- Pagination -->
          <v-row v-if="totalPages > 1" class="mt-4">
            <v-col class="d-flex justify-center">
              <v-pagination
                v-model="currentPage"
                :length="totalPages"
                @update:modelValue="loadPets"
              />
            </v-col>
          </v-row>
        </v-col>
      </v-row>
    </v-container>
    </v-main>
  </v-app>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/layout/AppHeader.vue'

const router = useRouter()

const loading = ref(false)
const pets = ref<any[]>([])
const currentPage = ref(1)
const totalPages = ref(1)

const filters = ref({
  search: '',
  species: null,
  age: null,
  size: null,
})

const speciesOptions = ['狗', '貓', '兔子', '鳥類', '其他']
const ageOptions = ['幼年 (0-1歲)', '成年 (1-7歲)', '老年 (7歲以上)']
const sizeOptions = ['小型', '中型', '大型']

const loadPets = async () => {
  loading.value = true
  try {
    // TODO: Call API to load pets
    // Placeholder data
    pets.value = [
      {
        id: 1,
        name: '小白',
        species: '狗',
        breed: '柴犬',
        age: 2,
        size: '中型',
        location: '台北市',
        status: 'available',
        image: null,
      },
    ]
    totalPages.value = 1
  } catch (error) {
    console.error('Failed to load pets:', error)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  currentPage.value = 1
  loadPets()
}

const goToPetDetail = (id: number) => {
  router.push({ name: 'PetDetail', params: { id },  query: { from: 'pets' } })
}

const toggleFavorite = (id: number) => {
  console.log('Toggle favorite:', id)
}

const getStatusColor = (status: string) => {
  return status === 'available' ? 'success' : 'grey'
}

const getStatusText = (status: string) => {
  return status === 'available' ? '可領養' : '已領養'
}

onMounted(() => {
  loadPets()
})
</script>

<style scoped>
.pet-card {
  cursor: pointer;
  transition: transform 0.2s;
}

.pet-card:hover {
  transform: translateY(-4px);
}
</style>
