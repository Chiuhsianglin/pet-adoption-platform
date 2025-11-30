<template>
  <v-card class="post-card" @click="$emit('click')">
    <v-card-title class="d-flex align-center">
      <v-avatar color="primary" size="40" class="mr-3">
        <span class="text-h6">{{ userInitial }}</span>
      </v-avatar>
      <div class="flex-grow-1">
        <div class="font-weight-bold">{{ post.user.name || post.user.email }}</div>
        <div class="text-caption text-grey">{{ formatDate(post.created_at) }}</div>
      </div>
      <v-chip :color="postTypeColor" size="small" class="ml-2">
        {{ postTypeText }}
      </v-chip>
    </v-card-title>

    <v-card-text>
      <div class="post-content mb-3">{{ post.content }}</div>
      
      <!-- Photos -->
      <v-row v-if="post.photos.length > 0" dense>
        <v-col
          v-for="photo in post.photos"
          :key="photo.id"
          :cols="photoColSize"
        >
          <v-img
            :src="photo.photo_url"
            contain
            class="rounded"
            max-height="400"
            lazy-src="/placeholder-pet.png"
          >
            <template v-slot:placeholder>
              <v-skeleton-loader type="image" />
            </template>
          </v-img>
        </v-col>
      </v-row>
    </v-card-text>

    <v-card-actions class="px-4 pb-3">
      <v-btn
        :color="post.is_liked ? 'red' : 'grey'"
        variant="text"
        size="small"
        @click.stop="$emit('like', post.id)"
      >
        <v-icon start>{{ post.is_liked ? 'mdi-heart' : 'mdi-heart-outline' }}</v-icon>
        {{ post.like_count }}
      </v-btn>

      <v-btn color="grey" variant="text" size="small">
        <v-icon start>mdi-comment-outline</v-icon>
        {{ post.comment_count }}
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Post } from '@/api/community'
import { PostType } from '@/api/community'

const props = defineProps<{
  post: Post
}>()

defineEmits<{
  click: []
  like: [postId: number]
}>()

const userInitial = computed(() => {
  const name = props.post.user.name || props.post.user.email
  return name.charAt(0).toUpperCase()
})

const postTypeColor = computed(() => {
  return props.post.post_type === PostType.QUESTION ? 'orange' : 'blue'
})

const postTypeText = computed(() => {
  return props.post.post_type === PostType.QUESTION ? '問題' : '分享'
})

const photoColSize = computed(() => {
  const count = props.post.photos.length
  if (count === 1) return 12
  if (count === 2) return 6
  if (count === 3) return 4
  return 6 // 4+ photos
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const seconds = Math.floor(diff / 1000)
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  const days = Math.floor(hours / 24)

  if (days > 7) {
    return date.toLocaleDateString('zh-TW')
  }
  if (days > 0) return `${days} 天前`
  if (hours > 0) return `${hours} 小時前`
  if (minutes > 0) return `${minutes} 分鐘前`
  return '剛剛'
}
</script>

<style scoped>
.post-card {
  cursor: pointer;
  transition: all 0.2s;
}

.post-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.post-content {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
