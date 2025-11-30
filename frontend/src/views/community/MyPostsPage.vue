<template>
  <v-container fluid class="pa-4">
    <v-row class="mb-4">
      <v-col cols="12" class="d-flex align-center">
        <v-btn icon="mdi-arrow-left" variant="text" @click="$router.back()" class="mr-2" />
        <h1 class="text-h4">我的貼文</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <div v-if="loading && posts.length === 0" class="text-center py-8">
          <v-progress-circular indeterminate color="primary" />
        </div>

        <div v-else-if="posts.length === 0" class="text-center py-8">
          <v-icon size="64" color="grey">mdi-forum-outline</v-icon>
          <p class="text-h6 mt-4">你還沒有發布任何貼文</p>
          <v-btn color="primary" class="mt-4" @click="$router.push('/community')">
            前往社群
          </v-btn>
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
  </v-container>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { getMyPosts, togglePostLike, type Post } from '@/api/community'
import PostCard from '@/components/community/PostCard.vue'

const router = useRouter()

const posts = ref<Post[]>([])
const loading = ref(false)
const hasMore = ref(false)
const skip = ref(0)
const limit = 20
const scrollTrigger = ref<HTMLElement | null>(null)

const loadPosts = async (append = false) => {
  if (loading.value) return
  
  loading.value = true
  try {
    const skipVal = append ? skip.value : 0
    
    const response = await getMyPosts(skipVal, limit)
    
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

const goToDetail = (postId: number) => {
  router.push(`/community/${postId}`)
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
})
</script>
