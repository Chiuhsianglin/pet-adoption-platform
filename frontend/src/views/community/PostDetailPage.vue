<template>
  <AppHeader />
  <v-container fluid class="pa-4" style="margin-top: 70px;">
    <v-row v-if="loading && !post">
      <v-col cols="12" class="text-center py-8">
        <v-progress-circular indeterminate color="primary" />
      </v-col>
    </v-row>

    <v-row v-else-if="post" justify="center">
      <v-col cols="auto" class="d-flex align-start pt-2">
        <v-btn icon="mdi-arrow-left" variant="text" @click="$router.back()" />
      </v-col>
      <v-col cols="12" md="8" lg="6" class="pl-0"> 
        <!-- Post Card -->
        <v-card class="mb-4">
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
            <v-menu v-if="canDelete">
              <template #activator="{ props }">
                <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
              </template>
              <v-list>
                <v-list-item @click="deletePost">
                  <template #prepend>
                    <v-icon>mdi-delete</v-icon>
                  </template>
                  <v-list-item-title>刪除貼文</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-title>

          <v-card-text>
            <div class="post-content mb-3">{{ post.content }}</div>
            
            <v-row v-if="post.photos.length > 0" dense>
              <v-col
                v-for="photo in post.photos"
                :key="photo.id"
                :cols="photoColSize"
              >
                <v-img
                  :src="photo.photo_url"
                  :aspect-ratio="1"
                  cover
                  class="rounded"
                />
              </v-col>
            </v-row>
          </v-card-text>

          <v-card-actions class="px-4 pb-3">
            <v-btn
              :color="post.is_liked ? 'red' : 'grey'"
              variant="text"
              size="small"
              @click="handlePostLike"
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

        <!-- Comments -->
        <v-card>
          <v-card-text>
            <comment-list
              :comments="comments"
              :loading="commentsLoading"
              @submit-comment="handleSubmitComment"
              @like-comment="handleCommentLike"
              @delete-comment="handleDeleteComment"
            />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row v-else>
      <v-col cols="12" class="text-center py-8">
        <v-icon size="64" color="grey">mdi-alert-circle-outline</v-icon>
        <p class="text-h6 mt-4">{{ errorMessage || '貼文不存在' }}</p>
        <v-btn color="primary" class="mt-4" @click="$router.push('/community')">
          返回社群
        </v-btn>
      </v-col>
    </v-row>

    <!-- Delete Comment Dialog -->
    <v-dialog v-model="deleteCommentDialog" max-width="400">
      <v-card>
        <v-card-title class="text-h6 d-flex align-center">
          <v-icon color="warning" class="mr-2">mdi-alert-circle</v-icon>
          刪除留言
        </v-card-title>
        
        <v-card-text class="py-4">
          <p class="text-body-1">確定要刪除這則留言嗎？</p>
          <p class="text-body-2 text-grey mt-2">此操作無法復原。</p>
        </v-card-text>
        
        <v-card-actions class="px-4 pb-4">
          <v-spacer />
          <v-btn
            variant="text"
            @click="deleteCommentDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            @click="confirmDeleteComment"
          >
            刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Delete Post Dialog -->
    <v-dialog v-model="deletePostDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6 d-flex align-center bg-error-lighten-4 pa-4">
          <v-icon color="error" size="28" class="mr-2">mdi-alert-circle-outline</v-icon>
          <span class="text-error">確認刪除貼文</span>
        </v-card-title>
        
        <v-card-text class="py-6 px-6">
          <p class="text-body-1 mb-3">確定要刪除這則貼文嗎？</p>
          <v-alert
            type="warning"
            variant="tonal"
            density="compact"
            icon="mdi-information-outline"
            class="text-body-2"
          >
            此操作無法復原，貼文及所有留言都會被永久刪除。
          </v-alert>
        </v-card-text>
        
        <v-card-actions class="px-6 pb-4">
          <v-spacer />
          <v-btn
            variant="text"
            size="large"
            @click="deletePostDialog = false"
          >
            取消
          </v-btn>
          <v-btn
            color="error"
            variant="flat"
            size="large"
            prepend-icon="mdi-delete"
            @click="confirmDeletePost"
          >
            確認刪除
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import {
  getPost,
  getComments,
  createComment,
  togglePostLike,
  toggleCommentLike,
  deletePost as deletePostApi,
  deleteComment as deleteCommentApi,
  type Post,
  type Comment,
  PostType
} from '@/api/community'
import CommentList from '@/components/community/CommentList.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const post = ref<Post | null>(null)
const comments = ref<Comment[]>([])
const loading = ref(false)
const commentsLoading = ref(false)
const errorMessage = ref<string>('')
const deleteCommentDialog = ref(false)
const deletePostDialog = ref(false)
const commentToDelete = ref<number | null>(null)

const postId = computed(() => parseInt(route.params.id as string))

const userInitial = computed(() => {
  if (!post.value) return ''
  const name = post.value.user.name || post.value.user.email
  return name.charAt(0).toUpperCase()
})

const postTypeColor = computed(() => {
  return post.value?.post_type === PostType.QUESTION ? 'orange' : 'blue'
})

const postTypeText = computed(() => {
  return post.value?.post_type === PostType.QUESTION ? '問題' : '分享'
})

const photoColSize = computed(() => {
  if (!post.value) return 12
  const count = post.value.photos.length
  if (count === 1) return 12
  if (count === 2) return 6
  if (count === 3) return 4
  return 6
})

const canDelete = computed(() => {
  const currentUser = userStore.currentUser
  if (!currentUser || !post.value) return false
  return (
    currentUser.id === post.value.user_id ||
    currentUser.role === 'admin'
  )
})

const loadPost = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    post.value = await getPost(postId.value)
  } catch (error: any) {
    console.error('載入貼文失敗:', error)
    if (error.response?.status === 404) {
      errorMessage.value = '貼文不存在或已刪除'
    } else if (error.response?.status === 401) {
      errorMessage.value = '請先登入'
    } else {
      errorMessage.value = `載入貼文失敗: ${error.response?.data?.detail || error.message || '未知錯誤'}`
    }
  } finally {
    loading.value = false
  }
}

const loadComments = async () => {
  commentsLoading.value = true
  try {
    const response = await getComments(postId.value)
    comments.value = response.comments
    if (post.value) {
      post.value.comment_count = response.total
    }
  } catch (error) {
    console.error('載入留言失敗:', error)
  } finally {
    commentsLoading.value = false
  }
}

const handlePostLike = async () => {
  if (!post.value) return
  
  // 樂觀更新 UI
  const wasLiked = post.value.is_liked
  const previousCount = post.value.like_count
  post.value.is_liked = !wasLiked
  post.value.like_count = wasLiked ? previousCount - 1 : previousCount + 1
  
  try {
    const response = await togglePostLike(post.value.id, wasLiked)
    // 使用 API 返回的實際值
    post.value.is_liked = response.isLiked
    post.value.like_count = response.likeCount
  } catch (error) {
    // 失敗時回滾
    post.value.is_liked = wasLiked
    post.value.like_count = previousCount
    console.error('按讚失敗:', error)
  }
}

const handleSubmitComment = async (content: string) => {
  try {
    const newComment = await createComment(postId.value, content)
    comments.value.push(newComment)
    if (post.value) {
      post.value.comment_count++
    }
  } catch (error) {
    console.error('送出留言失敗:', error)
  }
}

const handleCommentLike = async (commentId: number) => {
  try {
    const response = await toggleCommentLike(commentId)
    const comment = comments.value.find(c => c.id === commentId)
    if (comment) {
      comment.is_liked = response.isLiked
      comment.like_count = response.likeCount
    }
  } catch (error) {
    console.error('按讚失敗:', error)
  }
}

const handleDeleteComment = async (commentId: number) => {
  commentToDelete.value = commentId
  deleteCommentDialog.value = true
}

const confirmDeleteComment = async () => {
  if (!commentToDelete.value) return
  
  try {
    await deleteCommentApi(postId.value, commentToDelete.value)
    comments.value = comments.value.filter(c => c.id !== commentToDelete.value)
    if (post.value) {
      post.value.comment_count--
    }
    deleteCommentDialog.value = false
    commentToDelete.value = null
  } catch (error) {
    console.error('刪除留言失敗:', error)
  }
}

const deletePost = async () => {
  deletePostDialog.value = true
}

const confirmDeletePost = async () => {
  try {
    await deletePostApi(postId.value)
    router.push('/community')
  } catch (error) {
    console.error('刪除貼文失敗:', error)
  } finally {
    deletePostDialog.value = false
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

onMounted(async () => {
  await loadPost()
  await loadComments()
})
</script>

<style scoped>
.post-content {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
