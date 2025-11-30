<template>
  <div v-if="loading && !post">
    <v-card flat>
      <v-card-title class="d-flex align-center">
        <v-skeleton-loader type="avatar" class="mr-3" />
        <div class="flex-grow-1">
          <v-skeleton-loader type="text" width="150" />
          <v-skeleton-loader type="text" width="100" />
        </div>
      </v-card-title>
      <v-divider />
      <v-card-text>
        <v-skeleton-loader type="paragraph" />
        <v-skeleton-loader type="image" height="300" class="mt-3" />
      </v-card-text>
    </v-card>
  </div>

  <v-card v-else-if="post" flat>
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
      <div class="mx-2" />
          <v-menu v-if="canDelete">
            <template #activator="{ props }">
              <v-btn icon="mdi-dots-vertical" variant="text" v-bind="props" />
            </template>
            <v-list>
              <v-list-item @click="openEditDialog">
                <template #prepend>
                  <v-icon>mdi-pencil</v-icon>
                </template>
                <v-list-item-title>編輯貼文</v-list-item-title>
              </v-list-item>
              <v-list-item @click="deletePost">
                <template #prepend>
                  <v-icon>mdi-delete</v-icon>
                </template>
                <v-list-item-title>刪除貼文</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </v-card-title>

        <v-divider />

        <v-card-text class="post-content-area">
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
                lazy-src="/placeholder-pet.png"
              >
                <template v-slot:placeholder>
                  <v-skeleton-loader type="image" />
                </template>
              </v-img>
            </v-col>
          </v-row>
        </v-card-text>

        <v-divider />

        <v-card-actions class="px-4 py-3">
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

          <v-btn color="grey" variant="text" size="small" @click="handleShare">
            <v-icon start>mdi-share-variant</v-icon>
            分享
          </v-btn>

          <v-btn color="grey" variant="text" size="small" @click="openReportDialog">
            <v-icon start>mdi-flag</v-icon>
            檢舉
          </v-btn>
        </v-card-actions>
      </v-card>

  <!-- Comments Section -->
  <v-card v-if="post" flat class="mt-4">
    
    <v-divider />
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

  <div v-if="!loading && !post" class="text-center py-8">
    <v-icon size="64" color="grey">mdi-alert-circle-outline</v-icon>
    <p class="text-h6 mt-4">{{ errorMessage || '貼文不存在' }}</p>
  </div>

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

  <!-- Report Post Dialog -->
  <v-dialog v-model="reportDialog" max-width="500">
    <v-card>
      <v-card-title class="text-h6 d-flex align-center">
        <v-icon color="warning" class="mr-2">mdi-flag</v-icon>
        檢舉貼文
      </v-card-title>
      
      <v-card-text class="py-4">
        <p class="text-body-2 text-grey mb-4">請告訴我們檢舉的原因，我們會盡快處理。</p>
        <v-textarea
          v-model="reportReason"
          label="檢舉原因"
          placeholder="請描述您檢舉此貼文的原因..."
          rows="4"
          variant="outlined"
          counter="1000"
          :rules="[(v) => !!v || '請輸入檢舉原因', (v) => v.length <= 1000 || '超過字數限制']"
        />
      </v-card-text>
      
      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn
          variant="text"
          @click="reportDialog = false"
        >
          取消
        </v-btn>
        <v-btn
          color="warning"
          variant="flat"
          @click="submitReport"
          :disabled="!reportReason.trim()"
        >
          送出檢舉
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Report Success Dialog -->
  <v-dialog v-model="reportSuccessDialog" max-width="400">
    <v-card>
      <v-card-title class="text-h6 d-flex align-center">
        <v-icon color="success" class="mr-2">mdi-check-circle</v-icon>
        檢舉送出成功
      </v-card-title>
      
      <v-card-text class="py-4">
        <p class="text-body-1">您的檢舉已送出，管理員將會盡快處理。</p>
        <p class="text-body-2 text-grey mt-2">感謝您幫助我們維護社群環境。</p>
      </v-card-text>
      
      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn
          color="primary"
          variant="flat"
          @click="reportSuccessDialog = false"
        >
          確定
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Report Already Exists Dialog -->
  <v-dialog v-model="reportAlreadyExistsDialog" max-width="450">
    <v-card>
      <v-card-title class="text-h6 d-flex align-center">
        <v-icon color="info" class="mr-2">mdi-information</v-icon>
        已檢舉過此貼文
      </v-card-title>
      
      <v-card-text class="py-4">
        <p class="text-body-1">您已經檢舉過此貼文，請等待管理員處理。</p>
        <p class="text-body-2 text-grey mt-2">我們會盡快審核您的檢舉，感謝您的耐心等待。</p>
      </v-card-text>
      
      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn
          color="primary"
          variant="flat"
          @click="reportAlreadyExistsDialog = false"
        >
          確定
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Edit Post Dialog -->
  <v-dialog v-model="editDialog" max-width="600">
    <v-card>
      <v-card-title class="text-h6 d-flex align-center">
        <v-icon color="primary" class="mr-2">mdi-pencil</v-icon>
        編輯貼文
      </v-card-title>
      
      <v-card-text class="py-4">
        <v-select
          v-model="editPostType"
          :items="postTypeOptions"
          label="貼文類型"
          variant="outlined"
          class="mb-4"
        />
        <v-textarea
          v-model="editContent"
          label="貼文內容"
          placeholder="分享您的想法..."
          rows="6"
          variant="outlined"
          counter="2000"
          :rules="[(v) => !!v || '請輸入貼文內容', (v) => v.length <= 2000 || '超過字數限制']"
        />

        <!-- 現有圖片 -->
        <div v-if="editExistingPhotos.length > 0" class="mb-4">
          <div class="text-subtitle-2 mb-2">現有圖片</div>
          <v-row dense>
            <v-col
              v-for="photo in editExistingPhotos"
              :key="photo.id"
              cols="4"
            >
              <div class="photo-preview">
                <v-img
                  :src="photo.photo_url"
                  aspect-ratio="1"
                  cover
                  class="rounded"
                />
                <v-btn
                  icon="mdi-close"
                  size="small"
                  color="red"
                  class="remove-btn"
                  @click="markPhotoForDeletion(photo.id)"
                />
              </div>
            </v-col>
          </v-row>
        </div>

        <!-- 新增圖片 -->
        <div class="mb-4">
          <v-btn
            variant="outlined"
            prepend-icon="mdi-image"
            @click="triggerEditFileInput"
            :disabled="totalPhotoCount >= 5"
          >
            新增照片 ({{ totalPhotoCount }}/5)
          </v-btn>
          <input
            ref="editFileInput"
            type="file"
            accept="image/*"
            multiple
            style="display: none"
            @change="handleEditFileSelect"
          />
        </div>

        <!-- 新圖片預覽 -->
        <v-row v-if="editNewPhotos.length > 0" dense>
          <v-col
            v-for="(photo, index) in editNewPhotos"
            :key="'new-' + index"
            cols="4"
          >
            <div class="photo-preview">
              <v-img
                :src="photo.preview"
                aspect-ratio="1"
                cover
                class="rounded"
              />
              <v-btn
                icon="mdi-close"
                size="small"
                color="red"
                class="remove-btn"
                @click="removeNewPhoto(index)"
              />
            </div>
          </v-col>
        </v-row>
      </v-card-text>
      
      <v-card-actions class="px-4 pb-4">
        <v-spacer />
        <v-btn
          variant="text"
          @click="closeEditDialog"
        >
          取消
        </v-btn>
        <v-btn
          color="primary"
          variant="flat"
          @click="submitEdit"
          :disabled="!editContent.trim()"
        >
          儲存
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import {
  getPost,
  getComments,
  createComment,
  togglePostLike,
  toggleCommentLike,
  deletePost as deletePostApi,
  deleteComment as deleteCommentApi,
  updatePost,
  type Post,
  type Comment,
  type PostPhoto,
  PostType
} from '@/api/community'
import CommentList from '@/components/community/CommentList.vue'

interface Props {
  postId: number
}

interface Emits {
  (e: 'close'): void
  (e: 'deleted'): void
  (e: 'updated', post: Post): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const authStore = useAuthStore()
const notificationStore = useNotificationStore()

const post = ref<Post | null>(null)
const comments = ref<Comment[]>([])
const loading = ref(false)
const commentsLoading = ref(false)
const errorMessage = ref('')
const deleteCommentDialog = ref(false)
const deletePostDialog = ref(false)
const commentToDelete = ref<number | null>(null)
const reportDialog = ref(false)
const reportReason = ref('')
const reportSuccessDialog = ref(false)
const reportAlreadyExistsDialog = ref(false)
const editDialog = ref(false)
const editContent = ref('')
const editPostType = ref<PostType>(PostType.SHARE)
const editExistingPhotos = ref<PostPhoto[]>([])
const editPhotosToDelete = ref<number[]>([])
const editNewPhotos = ref<{ file: File; preview: string }[]>([])
const editFileInput = ref<HTMLInputElement | null>(null)

const postTypeOptions = [
  { title: '分享', value: PostType.SHARE },
  { title: '問題', value: PostType.QUESTION }
]

const totalPhotoCount = computed(() => {
  return editExistingPhotos.value.length + editNewPhotos.value.length
})

const userInitial = computed(() => {
  if (!post.value) return '?'
  const name = post.value.user.name || post.value.user.email
  return name.charAt(0).toUpperCase()
})

const postTypeColor = computed(() => {
  if (!post.value) return 'grey'
  switch (post.value.post_type) {
    case PostType.SHARE: return 'success'
    case PostType.QUESTION: return 'info'
    default: return 'grey'
  }
})

const postTypeText = computed(() => {
  if (!post.value) return ''
  switch (post.value.post_type) {
    case PostType.SHARE: return '分享'
    case PostType.QUESTION: return '問題'
    default: return ''
  }
})

const photoColSize = computed(() => {
  if (!post.value || post.value.photos.length === 0) return 12
  if (post.value.photos.length === 1) return 12
  if (post.value.photos.length === 2) return 6
  return 4
})

const canDelete = computed(() => {
  return authStore.user && post.value && authStore.user.id === post.value.user.id
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '剛剛'
  if (minutes < 60) return `${minutes} 分鐘前`
  if (hours < 24) return `${hours} 小時前`
  if (days < 7) return `${days} 天前`
  return date.toLocaleDateString('zh-TW')
}

const loadPost = async () => {
  loading.value = true
  errorMessage.value = ''
  
  try {
    post.value = await getPost(props.postId)
  } catch (error: any) {
    console.error('Failed to load post:', error)
    errorMessage.value = error.response?.data?.detail || '載入貼文失敗'
  } finally {
    loading.value = false
  }
}

const loadComments = async () => {
  commentsLoading.value = true
  
  try {
    const response = await getComments(props.postId)
    comments.value = response.comments
  } catch (error: any) {
    console.error('Failed to load comments:', error)
    notificationStore.error('載入留言失敗')
  } finally {
    commentsLoading.value = false
  }
}

// Parallel loading for faster performance
const loadAll = async () => {
  await Promise.all([loadPost(), loadComments()])
}

const handlePostLike = async () => {
  if (!post.value) return
  
  // 樂觀更新 UI
  const wasLiked = post.value.is_liked
  const previousCount = post.value.like_count
  post.value.is_liked = !wasLiked
  post.value.like_count = wasLiked ? previousCount - 1 : previousCount + 1

  try {
    const result = await togglePostLike(post.value.id, wasLiked)
    // 使用 API 返回的實際值
    post.value.is_liked = result.isLiked
    post.value.like_count = result.likeCount
  } catch (error: any) {
    // 失敗時回滾
    post.value.is_liked = wasLiked
    post.value.like_count = previousCount
    console.error('Failed to like post:', error)
    notificationStore.error('操作失敗')
  }
}

const handleSubmitComment = async (content: string) => {
  if (!post.value) return
  
  try {
    const newComment = await createComment(post.value.id, content)
    comments.value.unshift(newComment)
    post.value.comment_count++
    notificationStore.success('留言已發布')
    // 通知父組件更新貼文資料
    emit('updated', post.value)
  } catch (error: any) {
    console.error('Failed to create comment:', error)
    notificationStore.error('發布留言失敗')
  }
}

const handleCommentLike = async (commentId: number) => {
  try {
    const result = await toggleCommentLike(commentId)
    const comment = comments.value.find(c => c.id === commentId)
    if (comment) {
      comment.is_liked = result.isLiked
      comment.like_count = result.likeCount
    }
  } catch (error: any) {
    console.error('Failed to like comment:', error)
    notificationStore.error('操作失敗')
  }
}

const handleDeleteComment = (commentId: number) => {
  commentToDelete.value = commentId
  deleteCommentDialog.value = true
}

const confirmDeleteComment = async () => {
  if (commentToDelete.value === null || !post.value) return
  
  try {
    await deleteCommentApi(post.value.id, commentToDelete.value)
    comments.value = comments.value.filter(c => c.id !== commentToDelete.value)
    post.value.comment_count--
    notificationStore.success('留言已刪除')
    // 通知父組件更新貼文資料
    emit('updated', post.value)
  } catch (error: any) {
    console.error('Failed to delete comment:', error)
    notificationStore.error('刪除留言失敗')
  } finally {
    deleteCommentDialog.value = false
    commentToDelete.value = null
  }
}

const deletePost = async () => {
  if (!post.value) return
  deletePostDialog.value = true
}

const confirmDeletePost = async () => {
  if (!post.value) return
  
  try {
    await deletePostApi(post.value.id)
    notificationStore.success('貼文已刪除')
    emit('deleted')
    emit('close')
  } catch (error: any) {
    console.error('Failed to delete post:', error)
    notificationStore.error('刪除貼文失敗')
  } finally {
    deletePostDialog.value = false
  }
}

const openEditDialog = () => {
  if (!post.value) return
  console.log('Opening edit dialog, post:', post.value)
  console.log('Post photos:', post.value.photos)
  editContent.value = post.value.content
  editPostType.value = post.value.post_type
  // 複製現有圖片列表（確保是陣列）
  editExistingPhotos.value = post.value.photos ? [...post.value.photos] : []
  editPhotosToDelete.value = []
  editNewPhotos.value = []
  console.log('editExistingPhotos set to:', editExistingPhotos.value)
  console.log('editExistingPhotos length:', editExistingPhotos.value.length)
  editDialog.value = true
}

const closeEditDialog = () => {
  editDialog.value = false
  // 清理新圖片的預覽 URL
  editNewPhotos.value.forEach(photo => URL.revokeObjectURL(photo.preview))
  editNewPhotos.value = []
  editPhotosToDelete.value = []
}

const triggerEditFileInput = () => {
  editFileInput.value?.click()
}

const handleEditFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  
  // 檢查總數量限制
  const remainingSlots = 5 - totalPhotoCount.value
  const filesToAdd = files.slice(0, remainingSlots)
  
  for (const file of filesToAdd) {
    // 檢查檔案大小 (3MB)
    if (file.size > 3 * 1024 * 1024) {
      notificationStore.error(`照片 ${file.name} 超過 3MB 限制`)
      continue
    }
    
    // 建立預覽
    const preview = URL.createObjectURL(file)
    editNewPhotos.value.push({ file, preview })
  }
  
  // 清空 input
  if (target) target.value = ''
}

const markPhotoForDeletion = (photoId: number) => {
  // 從現有圖片列表中移除
  const index = editExistingPhotos.value.findIndex((p: PostPhoto) => p.id === photoId)
  if (index > -1) {
    editExistingPhotos.value.splice(index, 1)
    editPhotosToDelete.value.push(photoId)
  }
}

const removeNewPhoto = (index: number) => {
  URL.revokeObjectURL(editNewPhotos.value[index].preview)
  editNewPhotos.value.splice(index, 1)
}

const submitEdit = async () => {
  if (!post.value || !editContent.value.trim()) {
    notificationStore.error('請輸入貼文內容')
    return
  }
  
  try {
    const newPhotoFiles = editNewPhotos.value.map(p => p.file)
    const updatedPost = await updatePost(
      post.value.id, 
      editContent.value, 
      editPostType.value,
      editPhotosToDelete.value.length > 0 ? editPhotosToDelete.value : undefined,
      newPhotoFiles.length > 0 ? newPhotoFiles : undefined
    )
    post.value = updatedPost
    closeEditDialog()
    emit('updated', updatedPost)
    notificationStore.success('貼文已更新')
  } catch (error: any) {
    console.error('Failed to update post:', error)
    notificationStore.error('更新貼文失敗')
  }
}

const openReportDialog = () => {
  reportReason.value = ''
  reportDialog.value = true
}

const submitReport = async () => {
  if (!post.value || !reportReason.value.trim()) {
    notificationStore.error('請輸入檢舉原因')
    return
  }
  
  try {
    const { reportPost } = await import('@/api/community')
    await reportPost(post.value.id, reportReason.value)
    reportDialog.value = false
    reportSuccessDialog.value = true
  } catch (error: any) {
    console.error('Failed to report post:', error)
    reportDialog.value = false
    
    // 檢查是否為重複檢舉（400 錯誤）
    if (error.response?.status === 400 && error.response?.data?.detail?.includes('already reported')) {
      reportAlreadyExistsDialog.value = true
    } else {
      notificationStore.error('檢舉失敗，請稍後再試')
    }
  }
}

const handleShare = async () => {
  if (!post.value) return
  
  const postUrl = `${window.location.origin}/community/${post.value.id}`
  
  // 嘗試使用 Web Share API（移動裝置）
  if (navigator.share) {
    try {
      await navigator.share({
        title: '分享貼文',
        text: post.value.content.substring(0, 100) + '...',
        url: postUrl
      })
      notificationStore.success('分享成功')
      return
    } catch (error: any) {
      // 用戶取消分享或不支持
      if (error.name !== 'AbortError') {
        console.log('Share API not available, falling back to clipboard')
      } else {
        return // 用戶取消
      }
    }
  }
  
  // 備用方案：複製連結到剪貼簿
  try {
    await navigator.clipboard.writeText(postUrl)
    notificationStore.success('貼文連結已複製到剪貼簿')
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    notificationStore.error('分享失敗，請稍後再試')
  }
}

onMounted(async () => {
  // Parallel loading for faster performance
  await loadAll()
})
</script>

<style scoped>
.post-content {
  white-space: pre-wrap;
  word-wrap: break-word;
}

.photo-preview {
  position: relative;
}

.remove-btn {
  position: absolute;
  top: 4px;
  right: 4px;
}
</style>
