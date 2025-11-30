<template>
  <v-card class="review-comments">
    <v-card-title class="d-flex justify-space-between align-center">
      <span>審核評論</span>
      <v-btn
        color="primary"
        size="small"
        prepend-icon="mdi-plus"
        @click="openAddDialog"
      >
        新增評論
      </v-btn>
    </v-card-title>

    <v-card-text>
      <!-- Filter Options -->
      <div class="mb-4">
        <v-chip-group v-model="selectedFilter" mandatory>
          <v-chip value="all" size="small">全部</v-chip>
          <v-chip value="unresolved" size="small" color="warning">未解決</v-chip>
          <v-chip value="resolved" size="small" color="success">已解決</v-chip>
          <v-chip value="required" size="small" color="error">需要處理</v-chip>
        </v-chip-group>
      </div>

      <!-- Comments List -->
      <v-expansion-panels v-if="filteredComments.length > 0" multiple>
        <v-expansion-panel
          v-for="comment in filteredComments"
          :key="comment.id"
        >
          <v-expansion-panel-title>
            <div class="d-flex align-center flex-grow-1">
              <!-- Comment Type Icon -->
              <v-icon :color="getCommentTypeColor(comment.comment_type)" class="mr-2">
                {{ getCommentTypeIcon(comment.comment_type) }}
              </v-icon>
              
              <!-- Comment Preview -->
              <div class="flex-grow-1">
                <div class="text-subtitle-2">
                  {{ comment.comment.substring(0, 50) }}{{ comment.comment.length > 50 ? '...' : '' }}
                </div>
                <div class="text-caption text-grey">
                  {{ formatDateTime(comment.created_at) }} · {{ comment.reviewer_name || '審核員' }}
                </div>
              </div>

              <!-- Status Badges -->
              <div class="d-flex gap-1">
                <v-chip
                  v-if="comment.is_internal"
                  size="x-small"
                  color="grey"
                  variant="flat"
                >
                  內部
                </v-chip>
                <v-chip
                  v-if="comment.is_required_action"
                  size="x-small"
                  color="error"
                  variant="flat"
                >
                  需處理
                </v-chip>
                <v-chip
                  v-if="comment.is_resolved"
                  size="x-small"
                  color="success"
                  variant="flat"
                >
                  已解決
                </v-chip>
              </div>
            </div>
          </v-expansion-panel-title>

          <v-expansion-panel-text>
            <v-card variant="flat" color="grey-lighten-5">
              <v-card-text>
                <div class="mb-3">
                  <div class="text-subtitle-2 mb-1">評論內容</div>
                  <div class="text-body-1">{{ comment.comment }}</div>
                </div>

                <v-divider class="my-3" />

                <div class="d-flex justify-space-between align-center text-caption text-grey">
                  <div>
                    <strong>類型:</strong> {{ getCommentTypeName(comment.comment_type) }}
                  </div>
                  <div v-if="comment.is_resolved && comment.resolved_at">
                    於 {{ formatDateTime(comment.resolved_at) }} 解決
                  </div>
                </div>

                <!-- Resolution Info -->
                <div v-if="comment.is_resolved && comment.resolution_comment" class="mt-3">
                  <v-alert color="success" variant="tonal" density="compact">
                    <div class="text-subtitle-2 mb-1">解決說明</div>
                    <div class="text-body-2">{{ comment.resolution_comment }}</div>
                    <div class="text-caption text-grey mt-1">
                      由 {{ comment.resolved_by_name || '管理員' }} 解決
                    </div>
                  </v-alert>
                </div>

                <!-- Resolve Button -->
                <div v-if="!comment.is_resolved && canResolve" class="mt-3">
                  <v-btn
                    color="success"
                    size="small"
                    prepend-icon="mdi-check"
                    @click="openResolveDialog(comment)"
                  >
                    標記為已解決
                  </v-btn>
                </div>
              </v-card-text>
            </v-card>
          </v-expansion-panel-text>
        </v-expansion-panel>
      </v-expansion-panels>

      <!-- Empty State -->
      <v-alert v-else type="info" variant="tonal">
        暫無評論
      </v-alert>

      <!-- Loading -->
      <v-skeleton-loader v-if="loading" type="list-item@3" class="mt-4" />

      <!-- Error -->
      <v-alert v-if="error" type="error" class="mt-4">
        {{ error }}
      </v-alert>
    </v-card-text>

    <!-- Add Comment Dialog -->
    <v-dialog v-model="addDialog" max-width="600">
      <v-card>
        <v-card-title>新增審核評論</v-card-title>
        <v-card-text>
          <v-form ref="addForm" v-model="formValid">
            <v-select
              v-model="newComment.comment_type"
              :items="commentTypes"
              label="評論類型"
              item-title="label"
              item-value="value"
              required
            />

            <v-textarea
              v-model="newComment.comment"
              label="評論內容"
              rows="4"
              required
              :rules="[v => !!v || '評論內容為必填']"
            />

            <v-switch
              v-model="newComment.is_internal"
              label="內部評論（不對申請人顯示）"
              color="primary"
            />

            <v-switch
              v-model="newComment.is_required_action"
              label="需要申請人處理"
              color="error"
            />
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="addDialog = false">取消</v-btn>
          <v-btn
            color="primary"
            :loading="submitting"
            :disabled="!formValid"
            @click="submitComment"
          >
            提交
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Resolve Comment Dialog -->
    <v-dialog v-model="resolveDialog" max-width="500">
      <v-card>
        <v-card-title>解決評論</v-card-title>
        <v-card-text>
          <v-textarea
            v-model="resolutionComment"
            label="解決說明（選填）"
            rows="3"
            placeholder="說明如何解決此評論..."
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn @click="resolveDialog = false">取消</v-btn>
          <v-btn
            color="success"
            :loading="submitting"
            @click="submitResolve"
          >
            確認解決
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-card>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { getReviewComments, addReviewComment, resolveReviewComment, type ReviewComment } from '@/api/application-status'

const props = defineProps<{
  applicationId: number
  canResolve?: boolean
  showInternal?: boolean
}>()

const emit = defineEmits<{
  commentAdded: []
  commentResolved: [commentId: number]
}>()

const comments = ref<ReviewComment[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const selectedFilter = ref('all')

// Add Comment Dialog
const addDialog = ref(false)
const formValid = ref(false)
const submitting = ref(false)
const newComment = ref({
  comment_type: 'general',
  comment: '',
  is_internal: false,
  is_required_action: false
})

// Resolve Dialog
const resolveDialog = ref(false)
const resolvingComment = ref<ReviewComment | null>(null)
const resolutionComment = ref('')

const commentTypes = [
  { label: '一般評論', value: 'general' },
  { label: '批准說明', value: 'approval' },
  { label: '拒絕原因', value: 'rejection' },
  { label: '請求補充資訊', value: 'request_info' }
]

const filteredComments = computed(() => {
  let filtered = comments.value

  switch (selectedFilter.value) {
    case 'unresolved':
      filtered = filtered.filter(c => !c.is_resolved)
      break
    case 'resolved':
      filtered = filtered.filter(c => c.is_resolved)
      break
    case 'required':
      filtered = filtered.filter(c => c.is_required_action && !c.is_resolved)
      break
  }

  return filtered
})

const fetchComments = async () => {
  loading.value = true
  error.value = null
  
  try {
    comments.value = await getReviewComments(props.applicationId, props.showInternal)
  } catch (err: any) {
    error.value = err.response?.data?.message || '加載評論失敗'
    console.error('Failed to fetch comments:', err)
  } finally {
    loading.value = false
  }
}

const openAddDialog = () => {
  newComment.value = {
    comment_type: 'general',
    comment: '',
    is_internal: false,
    is_required_action: false
  }
  addDialog.value = true
}

const submitComment = async () => {
  if (!formValid.value) return
  
  submitting.value = true
  error.value = null
  
  try {
    await addReviewComment(props.applicationId, newComment.value)
    addDialog.value = false
    await fetchComments()
    emit('commentAdded')
  } catch (err: any) {
    error.value = err.response?.data?.message || '提交評論失敗'
    console.error('Failed to add comment:', err)
  } finally {
    submitting.value = false
  }
}

const openResolveDialog = (comment: ReviewComment) => {
  resolvingComment.value = comment
  resolutionComment.value = ''
  resolveDialog.value = true
}

const submitResolve = async () => {
  if (!resolvingComment.value) return
  
  submitting.value = true
  error.value = null
  
  try {
    await resolveReviewComment(resolvingComment.value.id, resolutionComment.value)
    resolveDialog.value = false
    await fetchComments()
    emit('commentResolved', resolvingComment.value.id)
  } catch (err: any) {
    error.value = err.response?.data?.message || '解決評論失敗'
    console.error('Failed to resolve comment:', err)
  } finally {
    submitting.value = false
  }
}

const getCommentTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    general: 'mdi-comment-text',
    approval: 'mdi-check-circle',
    rejection: 'mdi-close-circle',
    request_info: 'mdi-information'
  }
  return icons[type] || 'mdi-comment'
}

const getCommentTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    general: 'grey',
    approval: 'success',
    rejection: 'error',
    request_info: 'warning'
  }
  return colors[type] || 'grey'
}

const getCommentTypeName = (type: string) => {
  const types: Record<string, string> = {
    general: '一般評論',
    approval: '批准說明',
    rejection: '拒絕原因',
    request_info: '請求補充資訊'
  }
  return types[type] || type
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchComments()
})
</script>

<style scoped>
.review-comments {
  max-height: 70vh;
  overflow-y: auto;
}
</style>
