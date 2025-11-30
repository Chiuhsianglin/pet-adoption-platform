<template>
  <div class="image-gallery">
    <!-- 圖片網格 -->
    <v-row>
      <v-col
        v-for="(image, index) in images"
        :key="image.id || index"
        :cols="cols"
        :sm="sm"
        :md="md"
        :lg="lg"
      >
        <v-card
          class="image-gallery-card"
          :elevation="hover ? 4 : 2"
          @click="openPreview(index)"
        >
          <v-img
            :src="image.url || image.urls?.medium || image.urls?.thumbnail"
            :alt="image.alt || image.original_filename"
            :aspect-ratio="aspectRatio"
            cover
            class="image-gallery-img"
          >
            <template v-slot:placeholder>
              <div class="d-flex align-center justify-center fill-height">
                <v-progress-circular indeterminate color="primary" />
              </div>
            </template>

            <!-- 操作按鈕覆蓋層 -->
            <div v-if="showActions" class="image-overlay">
              <v-btn
                icon
                size="small"
                variant="elevated"
                @click.stop="openPreview(index)"
              >
                <v-icon>mdi-eye</v-icon>
              </v-btn>

              <v-btn
                v-if="deletable"
                icon
                size="small"
                variant="elevated"
                color="error"
                @click.stop="handleDelete(image, index)"
              >
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </div>
          </v-img>

          <!-- 圖片標題 -->
          <v-card-text v-if="showTitle && image.title" class="pa-2">
            <p class="text-caption text-truncate mb-0">{{ image.title }}</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- 空狀態 -->
    <v-sheet
      v-if="images.length === 0"
      class="d-flex align-center justify-center"
      height="200"
      color="grey-lighten-4"
      rounded
    >
      <div class="text-center">
        <v-icon size="64" color="grey">mdi-image-off-outline</v-icon>
        <p class="text-body-1 text-grey mt-2">{{ emptyText }}</p>
      </div>
    </v-sheet>

    <!-- 圖片預覽對話框 -->
    <ImagePreview
      v-model:show="previewDialog"
      :image-url="currentPreviewImage?.url || currentPreviewImage?.urls?.large || ''"
      :title="currentPreviewImage?.title || currentPreviewImage?.original_filename"
      :description="currentPreviewImage?.description"
      :download-url="currentPreviewImage?.urls?.original"
      :filename="currentPreviewImage?.original_filename"
      @close="closePreview"
    />

    <!-- 導航按鈕 (在預覽模式下) -->
    <div v-if="previewDialog && images.length > 1" class="navigation-buttons">
      <v-btn
        icon
        size="large"
        variant="elevated"
        class="nav-btn nav-btn--prev"
        :disabled="currentPreviewIndex === 0"
        @click="previousImage"
      >
        <v-icon>mdi-chevron-left</v-icon>
      </v-btn>

      <v-btn
        icon
        size="large"
        variant="elevated"
        class="nav-btn nav-btn--next"
        :disabled="currentPreviewIndex === images.length - 1"
        @click="nextImage"
      >
        <v-icon>mdi-chevron-right</v-icon>
      </v-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import ImagePreview from './ImagePreview.vue'

interface GalleryImage {
  id?: number
  url?: string
  urls?: {
    thumbnail?: string
    medium?: string
    large?: string
    original?: string
  }
  title?: string
  alt?: string
  description?: string
  original_filename?: string
}

interface Props {
  images: GalleryImage[]
  cols?: string | number
  sm?: string | number
  md?: string | number
  lg?: string | number
  aspectRatio?: string | number
  showTitle?: boolean
  showActions?: boolean
  deletable?: boolean
  hover?: boolean
  emptyText?: string
}

const props = withDefaults(defineProps<Props>(), {
  cols: 12,
  sm: 6,
  md: 4,
  lg: 3,
  aspectRatio: 1,
  showTitle: false,
  showActions: true,
  deletable: false,
  hover: true,
  emptyText: '暫無圖片',
})

interface Emits {
  (e: 'delete', image: GalleryImage, index: number): void
  (e: 'preview', image: GalleryImage, index: number): void
}

const emit = defineEmits<Emits>()

// State
const previewDialog = ref(false)
const currentPreviewIndex = ref(0)

// Computed
const currentPreviewImage = computed(() => {
  return props.images[currentPreviewIndex.value]
})

// Methods
const openPreview = (index: number) => {
  currentPreviewIndex.value = index
  previewDialog.value = true
  emit('preview', props.images[index], index)
}

const closePreview = () => {
  previewDialog.value = false
}

const previousImage = () => {
  if (currentPreviewIndex.value > 0) {
    currentPreviewIndex.value--
  }
}

const nextImage = () => {
  if (currentPreviewIndex.value < props.images.length - 1) {
    currentPreviewIndex.value++
  }
}

const handleDelete = (image: GalleryImage, index: number) => {
  emit('delete', image, index)
}
</script>

<style scoped lang="scss">
.image-gallery {
  width: 100%;
}

.image-gallery-card {
  cursor: pointer;
  transition: all 0.3s ease;
  overflow: hidden;

  &:hover {
    transform: translateY(-4px);

    .image-overlay {
      opacity: 1;
    }
  }
}

.image-gallery-img {
  position: relative;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.navigation-buttons {
  .nav-btn {
    position: fixed;
    top: 50%;
    transform: translateY(-50%);
    z-index: 9999;

    &--prev {
      left: 24px;
    }

    &--next {
      right: 24px;
    }
  }
}
</style>
