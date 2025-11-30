<template>
  <v-dialog v-model="internalShow" max-width="1200" scrollable>
    <v-card>
      <v-card-title class="d-flex justify-space-between align-center">
        <span>{{ title || '圖片預覽' }}</span>
        <v-btn icon variant="text" @click="close">
          <v-icon>mdi-close</v-icon>
        </v-btn>
      </v-card-title>

      <v-card-text class="pa-0">
        <div class="image-preview-container">
          <!-- 圖片顯示 -->
          <div
            class="image-wrapper"
            :style="{ transform: `scale(${scale}) rotate(${rotation}deg)` }"
          >
            <v-img
              :src="imageUrl"
              :alt="alt"
              contain
              class="image-preview"
              @error="handleImageError"
            >
              <template v-slot:placeholder>
                <div class="d-flex align-center justify-center fill-height">
                  <v-progress-circular indeterminate color="primary" />
                </div>
              </template>
            </v-img>
          </div>

          <!-- 控制按鈕 -->
          <div class="image-controls">
            <v-btn
              icon
              variant="elevated"
              size="small"
              @click="zoomOut"
              :disabled="scale <= 0.5"
            >
              <v-icon>mdi-magnify-minus</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="elevated"
              size="small"
              @click="resetZoom"
            >
              <v-icon>mdi-fit-to-screen</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="elevated"
              size="small"
              @click="zoomIn"
              :disabled="scale >= 3"
            >
              <v-icon>mdi-magnify-plus</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="elevated"
              size="small"
              @click="rotateLeft"
            >
              <v-icon>mdi-rotate-left</v-icon>
            </v-btn>

            <v-btn
              icon
              variant="elevated"
              size="small"
              @click="rotateRight"
            >
              <v-icon>mdi-rotate-right</v-icon>
            </v-btn>

            <v-btn
              v-if="downloadUrl"
              icon
              variant="elevated"
              size="small"
              :href="downloadUrl"
              :download="filename"
              target="_blank"
            >
              <v-icon>mdi-download</v-icon>
            </v-btn>
          </div>
        </div>
      </v-card-text>

      <v-card-text v-if="description" class="pt-4">
        <p class="text-body-2">{{ description }}</p>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

interface Props {
  show: boolean
  imageUrl: string
  title?: string
  alt?: string
  description?: string
  downloadUrl?: string
  filename?: string
}

const props = defineProps<Props>()

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'close'): void
}

const emit = defineEmits<Emits>()

// State
const internalShow = ref(props.show)
const scale = ref(1)
const rotation = ref(0)
const imageError = ref(false)

// Watch
watch(() => props.show, (newVal) => {
  internalShow.value = newVal
  if (newVal) {
    resetView()
  }
})

watch(internalShow, (newVal) => {
  emit('update:show', newVal)
  if (!newVal) {
    emit('close')
  }
})

// Methods
const close = () => {
  internalShow.value = false
}

const zoomIn = () => {
  if (scale.value < 3) {
    scale.value = Math.min(scale.value + 0.25, 3)
  }
}

const zoomOut = () => {
  if (scale.value > 0.5) {
    scale.value = Math.max(scale.value - 0.25, 0.5)
  }
}

const resetZoom = () => {
  scale.value = 1
  rotation.value = 0
}

const rotateLeft = () => {
  rotation.value = (rotation.value - 90) % 360
}

const rotateRight = () => {
  rotation.value = (rotation.value + 90) % 360
}

const resetView = () => {
  scale.value = 1
  rotation.value = 0
  imageError.value = false
}

const handleImageError = () => {
  imageError.value = true
}
</script>

<style scoped lang="scss">
.image-preview-container {
  position: relative;
  min-height: 400px;
  max-height: 70vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(0, 0, 0, 0.9);
  overflow: hidden;
}

.image-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.3s ease;
}

.image-preview {
  max-width: 100%;
  max-height: 70vh;
}

.image-controls {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 8px;
  background-color: rgba(255, 255, 255, 0.95);
  padding: 8px;
  border-radius: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
</style>
