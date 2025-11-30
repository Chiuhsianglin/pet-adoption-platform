<template>
  <button
    class="favorite-button"
    :class="[variant, { 'is-favorite': isFavorite, 'is-loading': loading }]"
    :disabled="loading || disabled"
    @click="handleClick"
    :title="isFavorite ? '取消收藏' : '加入收藏'"
  >
    <i 
      class="mdi" 
      :class="isFavorite ? 'mdi-heart' : 'mdi-heart-outline'"
    ></i>
    <span v-if="showText" class="button-text">
      {{ isFavorite ? '已收藏' : '收藏' }}
    </span>
    
    <!-- Loading Spinner -->
    <div v-if="loading" class="loading-spinner"></div>
  </button>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useFavoritesStore } from '@/stores/favorites'
import { useAuthStore } from '@/stores/auth'

interface FavoriteButtonProps {
  petId: number
  variant?: 'icon' | 'text' | 'floating'
  showText?: boolean
  disabled?: boolean
}

const props = withDefaults(defineProps<FavoriteButtonProps>(), {
  variant: 'icon',
  showText: false,
  disabled: false
})

const favoritesStore = useFavoritesStore()
const authStore = useAuthStore()
const router = useRouter()

// State
const loading = ref(false)
const animating = ref(false)

// Computed
const isFavorite = computed(() => favoritesStore.isFavoriteForCurrentUser
  ? favoritesStore.isFavoriteForCurrentUser(props.petId)
  : favoritesStore.isFavorite(props.petId)
)

// Methods
const handleClick = async (event: Event) => {
  event.preventDefault()
  event.stopPropagation()

  if (loading.value || props.disabled) return

  // If user not authenticated, redirect to login
  if (!authStore.isAuthenticated) {
    router.push({ path: '/auth/login', query: { redirect: window.location.pathname } })
    return
  }

  loading.value = true
  animating.value = true

  try {
    if (isFavorite.value) {
      await favoritesStore.removeFavorite(props.petId)
    } else {
      await favoritesStore.addFavorite(props.petId)
      // Trigger animation
      setTimeout(() => {
        animating.value = false
      }, 600)
    }
  } catch (error) {
    console.error('Failed to toggle favorite:', error)
    // You could emit an error event here if needed
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.favorite-button {
  position: relative;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem;
  border-radius: 50%;
}

.favorite-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.favorite-button .mdi {
  font-size: 1.5rem;
  transition: all 0.3s ease;
  color: #999;
}

.favorite-button.is-favorite .mdi {
  color: #e91e63;
  animation: heartBeat 0.6s ease-in-out;
}

.favorite-button:hover:not(:disabled) .mdi {
  transform: scale(1.2);
}

.favorite-button.is-favorite:hover:not(:disabled) .mdi {
  color: #c2185b;
}

.button-text {
  font-size: 0.95rem;
  font-weight: 600;
  color: #2c3e50;
  white-space: nowrap;
}

.favorite-button.is-favorite .button-text {
  color: #e91e63;
}

/* Loading Spinner */
.loading-spinner {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 20px;
  height: 20px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #e91e63;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.favorite-button.is-loading .mdi {
  opacity: 0;
}

@keyframes spin {
  0% { transform: translate(-50%, -50%) rotate(0deg); }
  100% { transform: translate(-50%, -50%) rotate(360deg); }
}

@keyframes heartBeat {
  0%, 100% {
    transform: scale(1);
  }
  10%, 30% {
    transform: scale(0.9);
  }
  20%, 40%, 60%, 80% {
    transform: scale(1.3);
  }
  50%, 70% {
    transform: scale(1.2);
  }
}

/* Variant: Icon (Default) */
.favorite-button.icon {
  width: 40px;
  height: 40px;
  padding: 0;
}

.favorite-button.icon:hover:not(:disabled) {
  background: rgba(233, 30, 99, 0.1);
}

/* Variant: Text */
.favorite-button.text {
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  background: white;
  border: 2px solid #e0e0e0;
}

.favorite-button.text:hover:not(:disabled) {
  border-color: #e91e63;
  background: rgba(233, 30, 99, 0.05);
}

.favorite-button.text.is-favorite {
  border-color: #e91e63;
  background: rgba(233, 30, 99, 0.1);
}

.favorite-button.text .mdi {
  font-size: 1.3rem;
}

/* Variant: Floating */
.favorite-button.floating {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 44px;
  height: 44px;
  padding: 0;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 10;
}

.favorite-button.floating:hover:not(:disabled) {
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transform: scale(1.1);
}

.favorite-button.floating.is-favorite {
  background: rgba(233, 30, 99, 0.95);
}

.favorite-button.floating.is-favorite .mdi {
  color: white;
}

.favorite-button.floating.is-favorite:hover:not(:disabled) {
  background: #e91e63;
}

/* Responsive Design */
@media (max-width: 768px) {
  .favorite-button.icon {
    width: 36px;
    height: 36px;
  }

  .favorite-button.text {
    padding: 0.625rem 1.25rem;
  }

  .favorite-button .mdi {
    font-size: 1.3rem;
  }

  .favorite-button.text .mdi {
    font-size: 1.2rem;
  }

  .button-text {
    font-size: 0.9rem;
  }

  .favorite-button.floating {
    width: 40px;
    height: 40px;
    top: 10px;
    right: 10px;
  }
}
</style>
