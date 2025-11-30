<template>
  <div class="favorite-card">
    <div class="card-image">
      <img 
        :src="petImage" 
        :alt="favorite.pet_name"
        @error="handleImageError"
        loading="lazy"
        decoding="async"
      />
      <div class="status-badge" :class="`status-${favorite.pet_status}`">
        {{ statusText }}
      </div>
    </div>

    <div class="card-content">
      <h3 class="pet-name">{{ favorite.pet_name }}</h3>
      
      <div class="pet-info">
        <div class="info-item">
          <i class="mdi mdi-paw"></i>
          <span>{{ speciesText }}</span>
        </div>
        <div v-if="favorite.pet_breed" class="info-item">
          <i class="mdi mdi-tag"></i>
          <span>{{ favorite.pet_breed }}</span>
        </div>
      </div>

      <div class="favorite-date">
        <i class="mdi mdi-clock-outline"></i>
        <span>{{ formattedDate }}</span>
      </div>
    </div>

    <div class="card-actions">
      <button 
        @click="emit('view-details', favorite.pet_id)" 
        class="btn btn-view"
        title="查看詳情"
      >
        <i class="mdi mdi-eye"></i>
        查看詳情
      </button>
      <button 
        @click="handleRemove" 
        class="btn btn-remove"
        :disabled="removing"
        title="取消收藏"
      >
        <i class="mdi mdi-heart-off"></i>
        {{ removing ? '移除中...' : '取消收藏' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface FavoriteCardProps {
  favorite: {
    pet_id: number
    pet_name: string
    pet_species: string
    pet_breed: string | null
    pet_status: string
    pet_photo_url: string | null
    created_at: string
  }
}

const props = defineProps<FavoriteCardProps>()

const emit = defineEmits<{
  remove: [petId: number]
  'view-details': [petId: number]
}>()

// State
const removing = ref(false)
const imageError = ref(false)

// Computed
const petImage = computed(() => {
  if (imageError.value || !props.favorite.pet_photo_url) {
    // Default placeholder based on species using data URI
    const species = props.favorite.pet_species
    if (species === 'dog') {
      return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%23e91e63" width="400" height="300"/%3E%3Ctext fill="white" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E🐕 狗狗%3C/text%3E%3C/svg%3E'
    } else if (species === 'cat') {
      return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%239c27b0" width="400" height="300"/%3E%3Ctext fill="white" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E🐱 貓咪%3C/text%3E%3C/svg%3E'
    } else {
      return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect fill="%232196f3" width="400" height="300"/%3E%3Ctext fill="white" font-family="Arial" font-size="32" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E🐾 寵物%3C/text%3E%3C/svg%3E'
    }
  }
  return props.favorite.pet_photo_url
})

const speciesText = computed(() => {
  const speciesMap: Record<string, string> = {
    'dog': '狗',
    'cat': '貓',
    'other': '其他'
  }
  return speciesMap[props.favorite.pet_species] || props.favorite.pet_species
})

const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    'available': '可領養',
    'pending': '待審核',
    'adopted': '已領養',
    'unavailable': '不可領養'
  }
  return statusMap[props.favorite.pet_status] || props.favorite.pet_status
})

const formattedDate = computed(() => {
  const date = new Date(props.favorite.created_at)
  const now = new Date()
  const diffInMs = now.getTime() - date.getTime()
  const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24))

  if (diffInDays === 0) {
    return '今天加入收藏'
  } else if (diffInDays === 1) {
    return '昨天加入收藏'
  } else if (diffInDays < 7) {
    return `${diffInDays} 天前加入收藏`
  } else if (diffInDays < 30) {
    const weeks = Math.floor(diffInDays / 7)
    return `${weeks} 週前加入收藏`
  } else {
    return date.toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }
})

// Methods
const handleImageError = () => {
  imageError.value = true
}

const handleRemove = async () => {
  if (removing.value) return

  if (confirm(`確定要將 ${props.favorite.pet_name} 從收藏清單中移除嗎？`)) {
    removing.value = true
    try {
      emit('remove', props.favorite.pet_id)
    } finally {
      // Reset after a short delay even if parent handles the error
      setTimeout(() => {
        removing.value = false
      }, 1000)
    }
  }
}
</script>

<style scoped>
.favorite-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.favorite-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

/* Card Image */
.card-image {
  position: relative;
  width: 100%;
  padding-top: 75%; /* 4:3 Aspect Ratio */
  overflow: hidden;
  background: #f0f0f0;
}

.card-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.favorite-card:hover .card-image img {
  transform: scale(1.05);
}

.status-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  backdrop-filter: blur(10px);
}

.status-available {
  background: rgba(76, 175, 80, 0.9);
}

.status-pending {
  background: rgba(255, 152, 0, 0.9);
}

.status-adopted {
  background: rgba(158, 158, 158, 0.9);
}

.status-unavailable {
  background: rgba(244, 67, 54, 0.9);
}

/* Card Content */
.card-content {
  padding: 1.5rem;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pet-name {
  font-size: 1.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin: 0;
  line-height: 1.2;
}

.pet-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #7f8c8d;
  font-size: 0.95rem;
}

.info-item .mdi {
  color: #e91e63;
  font-size: 1.1rem;
}

.favorite-date {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #95a5a6;
  font-size: 0.85rem;
  margin-top: auto;
  padding-top: 0.5rem;
  border-top: 1px solid #ecf0f1;
}

.favorite-date .mdi {
  font-size: 1rem;
}

/* Card Actions */
.card-actions {
  padding: 1rem 1.5rem;
  background: #f8f9fa;
  display: flex;
  gap: 0.75rem;
  border-top: 1px solid #ecf0f1;
}

.btn {
  flex: 1;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn .mdi {
  font-size: 1.2rem;
}

.btn-view {
  background: #2196f3;
  color: white;
}

.btn-view:hover {
  background: #1976d2;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.3);
}

.btn-remove {
  background: #f44336;
  color: white;
}

.btn-remove:hover:not(:disabled) {
  background: #d32f2f;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.3);
}

.btn-remove:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Responsive Design */
@media (max-width: 768px) {
  .card-content {
    padding: 1rem;
  }

  .pet-name {
    font-size: 1.25rem;
  }

  .card-actions {
    flex-direction: column;
    padding: 1rem;
  }

  .btn {
    width: 100%;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .card-actions {
    gap: 0.5rem;
  }

  .btn {
    font-size: 0.85rem;
    padding: 0.625rem 0.75rem;
  }
}
</style>
