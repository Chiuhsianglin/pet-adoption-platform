<template>
  <div class="comment-list">
    <div class="d-flex align-center mb-4">
      <h3 class="text-h6">留言 ({{ comments.length }})</h3>
    </div>

    <!-- Comments - 可滿動區域 -->
    <div v-if="loading" class="text-center py-4">
      <v-progress-circular indeterminate color="primary" />
    </div>

    <div v-else-if="comments.length === 0" class="text-center text-grey py-4">
      尚無留言
    </div>

    <div v-else class="comments-container mb-4">
      <v-card
        v-for="comment in comments"
        :key="comment.id"
        class="mb-3"
      >
        <v-card-text>
          <div class="d-flex align-start">
            <v-avatar color="primary" size="32" class="mr-3">
              <span class="text-caption">{{ getUserInitial(comment.user) }}</span>
            </v-avatar>
            
            <div class="flex-grow-1">
              <div class="d-flex align-center mb-1">
                <span class="font-weight-bold">{{ comment.user.name || comment.user.email }}</span>
                <span class="text-caption text-grey ml-2">{{ formatDate(comment.created_at) }}</span>
              </div>
              
              <div class="comment-content">{{ comment.content }}</div>
            </div>

            <v-btn
              v-if="canDelete(comment)"
              color="grey"
              variant="text"
              size="small"
              icon
              class="ml-2 align-self-center"
              @click="$emit('delete-comment', comment.id)"
            >
              <v-icon>mdi-delete-outline</v-icon>
            </v-btn>
          </div>

          <div class="mt-2">
          </div>
        </v-card-text>
      </v-card>
    </div>

    <!-- Comment Input - 固定在底部 -->
    <div class="comment-input-fixed">
      <v-textarea
        v-model="newComment"
        label="寫下你的留言..."
        variant="outlined"
        rows="3"
        density="compact"
        hide-details
      />
      <div class="d-flex justify-end mt-2">
        <v-btn
          color="primary"
          :disabled="!newComment.trim()"
          :loading="submitting"
          @click="submitComment"
        >
          送出留言
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'
import type { Comment, UserBasicInfo } from '@/api/community'

const props = defineProps<{
  comments: Comment[]
  loading?: boolean
}>()

const emit = defineEmits<{
  'submit-comment': [content: string]
  'like-comment': [commentId: number]
  'delete-comment': [commentId: number]
}>()

const userStore = useUserStore()
const newComment = ref('')
const submitting = ref(false)

const getUserInitial = (user: UserBasicInfo) => {
  const name = user.name || user.email
  return name.charAt(0).toUpperCase()
}

const canDelete = (comment: Comment) => {
  const currentUser = userStore.currentUser
  if (!currentUser) return false
  return (
    currentUser.id === comment.user_id ||
    currentUser.role === 'admin'
  )
}

const submitComment = async () => {
  if (!newComment.value.trim()) return
  
  submitting.value = true
  try {
    emit('submit-comment', newComment.value)
    newComment.value = ''
  } finally {
    submitting.value = false
  }
}

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
.comment-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.comments-container {
  max-height: 400px;
  overflow-y: auto;
  padding-right: 4px;
  margin-bottom: 16px;
}

/* 滿動條樣式 */
.comments-container::-webkit-scrollbar {
  width: 8px;
}

.comments-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.comments-container::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.comments-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.comment-input-fixed {
  position: sticky;
  bottom: 0;
  background: white;
  padding-top: 16px;
  border-top: 1px solid #e0e0e0;
}
</style>
