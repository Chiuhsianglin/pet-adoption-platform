<template>
  <AppHeader />
  
  <!-- Fixed Filter Panel -->
  <v-card
    class="filter-panel"
    elevation="3"
    style="margin-top: 30px;"
  >
    <v-card-text class="pa-3">
      <v-btn
        color="primary"
        block
        class="mb-3"
        @click="showCreateDialog = true"
      >
        <v-icon start>mdi-plus</v-icon>
        發布貼文
      </v-btn>
      
      <v-text-field
        v-model="searchQuery"
        label="搜尋貼文"
        prepend-inner-icon="mdi-magnify"
        variant="outlined"
        density="compact"
        clearable
        hide-details
        class="mb-3"
        @update:model-value="handleSearch"
      />
      
      <v-select
        v-model="selectedType"
        :items="typeOptions"
        label="貼文類型"
        variant="outlined"
        density="compact"
        hide-details
        class="mb-3"
        @update:model-value="handleFilter"
      />
      
      <v-checkbox
        v-model="showMyPosts"
        label="只顯示我的貼文"
        hide-details
        @update:model-value="handleFilter"
      />
    </v-card-text>
  </v-card>

  <v-container fluid class="px-10 py-4" >
    <v-row class="mb-4" >
      <v-col cols="12" class="d-flex align-center justify-space-between">
      </v-col>
    </v-row>

    <v-row class="mb-4" justify="center">
      <v-col cols="12" md="8" lg="6">
        <!-- Empty row for spacing -->
      </v-col>
    </v-row>

    <v-row justify="center">
      <v-col cols="12" md="8" lg="6">
        <div v-if="loading && posts.length === 0">
          <v-card v-for="i in 3" :key="i" class="mb-4">
            <v-card-text>
              <div class="d-flex align-center mb-3">
                <v-skeleton-loader type="avatar" class="mr-3" />
                <div class="flex-grow-1">
                  <v-skeleton-loader type="text" width="150" />
                  <v-skeleton-loader type="text" width="100" />
                </div>
              </div>
              <v-skeleton-loader type="paragraph" />
              <v-skeleton-loader type="image" height="200" class="mt-3" />
            </v-card-text>
          </v-card>
        </div>

        <div v-else-if="posts.length === 0" class="text-center py-8">
          <v-icon size="64" color="grey">mdi-forum-outline</v-icon>
          <p class="text-h6 mt-4">目前還沒有貼文</p>
        </div>

        <div v-else>
          <post-card
            v-for="post in posts"
            :key="post.id"
            :post="post"
            class="mb-4"
            @like="handleLike"
            @click="goToDetail(post.id)"
          />

          <div v-if="hasMore" ref="scrollTrigger" class="text-center py-4">
            <v-progress-circular v-if="loading" indeterminate color="primary" />
          </div>

          <div v-if="!hasMore && posts.length > 0" class="text-center text-grey py-4">
            已顯示全部貼文
          </div>
        </div>
      </v-col>
    </v-row>

    <create-post-dialog
      v-model="showCreateDialog"
      @created="handlePostCreated"
    />

    <!-- Post Detail Dialog -->
    <v-dialog
      v-model="postDetailDialog"
      max-width="900"
      max-height="90vh"
      scrollable
      persistent
    >
      <v-card>
        <v-card-title class="d-flex align-center">
          <v-btn
            icon="mdi-close"
            variant="text"
            @click="closePostDialog"
          />
          <span class="ml-2">貼文詳情</span>
        </v-card-title>
        
        <v-card-text class="pa-4" style="max-height: calc(90vh - 80px); overflow-y: auto;">
          <post-detail-content
            v-if="postDetailDialog && selectedPostId"
            :post-id="selectedPostId"
            @close="closePostDialog"
            @deleted="handlePostDeleted"
            @updated="handlePostUpdated"
          />
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { getPosts, togglePostLike, type Post, PostType } from '@/api/community'
import PostCard from '@/components/community/PostCard.vue'
import CreatePostDialog from '@/components/community/CreatePostDialog.vue'
import PostDetailContent from '@/components/community/PostDetailContent.vue'
import AppHeader from '@/components/layout/AppHeader.vue'

const postDetailDialog = ref(false)
const selectedPostId = ref<number | null>(null)

const posts = ref<Post[]>([])
const loading = ref(false)
const hasMore = ref(false)
const skip = ref(0)
const limit = 20
const searchQuery = ref('')
const selectedType = ref<PostType | 'all'>('all')
const showMyPosts = ref(false)
const showCreateDialog = ref(false)
const scrollTrigger = ref<HTMLElement | null>(null)

const typeOptions = [
  { title: '全部', value: 'all' },
  { title: '問題', value: PostType.QUESTION },
  { title: '分享', value: PostType.SHARE }
]

const loadPosts = async (append = false) => {
  if (loading.value) return
  
  loading.value = true
  try {
    const skipVal = append ? skip.value : 0
    
    let response
    if (showMyPosts.value) {
      // 載入我的貼文
      const { getMyPosts } = await import('@/api/community')
      response = await getMyPosts(skipVal, limit)
    } else {
      // 載入所有貼文（包含篩選）
      const postTypeVal = selectedType.value !== 'all' ? selectedType.value : undefined
      const searchVal = searchQuery.value || undefined
      response = await getPosts(skipVal, limit, postTypeVal, searchVal)
    }
    
    if (append) {
      posts.value.push(...response.posts)
    } else {
      posts.value = response.posts
      skip.value = 0
    }
    
    skip.value += response.posts.length
    hasMore.value = response.hasMore
  } catch (error) {
    console.error('載入貼文失敗:', error)
  } finally {
    loading.value = false
  }
}

let searchTimeout: NodeJS.Timeout | null = null
const handleSearch = () => {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    skip.value = 0
    loadPosts(false)
  }, 300) // Reduced from 500ms to 300ms for faster response
}

const handleFilter = () => {
  skip.value = 0
  loadPosts(false)
}

const handleLike = async (postId: number) => {
  const post = posts.value.find(p => p.id === postId)
  if (!post) return

  // 樂觀更新 UI
  const wasLiked = post.is_liked
  const previousCount = post.like_count
  post.is_liked = !wasLiked
  post.like_count = wasLiked ? previousCount - 1 : previousCount + 1

  try {
    const response = await togglePostLike(postId, wasLiked)
    // 使用 API 返回的實際值
    post.is_liked = response.isLiked
    post.like_count = response.likeCount
  } catch (error) {
    // 失敗時回滾
    post.is_liked = wasLiked
    post.like_count = previousCount
    console.error('按讚失敗:', error)
  }
}

const handlePostCreated = (newPost: Post) => {
  posts.value.unshift(newPost)
  showCreateDialog.value = false
}

const goToDetail = (postId: number) => {
  selectedPostId.value = postId
  postDetailDialog.value = true
}

const closePostDialog = () => {
  postDetailDialog.value = false
  selectedPostId.value = null
}

const handlePostDeleted = () => {
  // 重新載入貼文列表
  skip.value = 0
  loadPosts(false)
}

const handlePostUpdated = (updatedPost: Post) => {
  // 更新列表中的貼文
  const index = posts.value.findIndex(p => p.id === updatedPost.id)
  if (index !== -1) {
    posts.value[index] = updatedPost
  }
}

let observer: IntersectionObserver | null = null

const setupInfiniteScroll = () => {
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0].isIntersecting && hasMore.value && !loading.value) {
        loadPosts(true)
      }
    },
    { threshold: 0.5 }
  )
}

watch(scrollTrigger, (newTrigger) => {
  if (observer && newTrigger) {
    observer.observe(newTrigger)
  }
})

onMounted(async () => {
  await loadPosts(false)
  setupInfiniteScroll()
})

onUnmounted(() => {
  if (observer) {
    observer.disconnect()
  }
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
})
</script>

<style scoped>
.filter-panel {
  position: fixed;
  top: 80px;
  left: 20px;
  width: 280px;
  z-index: 100;
  max-height: calc(100vh - 100px);
  overflow-y: auto;
}

@media (max-width: 960px) {
  .filter-panel {
    position: relative;
    top: 0;
    left: 0;
    width: 100%;
    margin: 70px 20px 20px 20px;
  }
}
</style>
