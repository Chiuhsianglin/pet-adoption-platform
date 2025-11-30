import apiClient from './client'

export enum PostType {
  QUESTION = 'question',
  SHARE = 'share'
}

export interface UserBasicInfo {
  id: number
  name: string | null
  email: string
}

export interface PostPhoto {
  id: number
  post_id: number
  file_key: string
  display_order: number
  photo_url: string
  created_at: string
}

export interface Post {
  id: number
  user_id: number
  user: UserBasicInfo
  post_type: PostType
  content: string
  photos: PostPhoto[]
  like_count: number
  comment_count: number
  is_liked: boolean
  is_deleted: boolean
  created_at: string
  updated_at: string
}

export interface PostListResponse {
  total: number
  posts: Post[]
  hasMore: boolean
}

export interface Comment {
  id: number
  post_id: number
  user_id: number
  user: UserBasicInfo
  content: string
  like_count: number
  is_liked: boolean
  is_deleted: boolean
  created_at: string
}

export interface CommentListResponse {
  total: number
  comments: Comment[]
}

export interface LikeResponse {
  success: boolean
  isLiked: boolean
  likeCount: number
}

export async function getPosts(
  skip?: number,
  limit?: number,
  postType?: PostType,
  search?: string
): Promise<PostListResponse> {
  const params: any = {}
  if (skip !== undefined) params.skip = skip
  if (limit !== undefined) params.limit = limit
  if (postType) params.post_type = postType
  if (search) params.search = search
  
  const response = await apiClient.get('/community/posts', { params })
  return {
    total: response.data.total,
    posts: response.data.posts,
    hasMore: response.data.has_more
  }
}

export async function getMyPosts(
  skip?: number,
  limit?: number
): Promise<PostListResponse> {
  const params: any = {}
  if (skip !== undefined) params.skip = skip
  if (limit !== undefined) params.limit = limit
  
  const response = await apiClient.get('/community/posts/my', { params })
  return {
    total: response.data.total,
    posts: response.data.posts,
    hasMore: response.data.has_more
  }
}

export async function getPost(postId: number): Promise<Post> {
  const response = await apiClient.get(`/community/posts/${postId}`)
  return response.data
}

export async function createPost(formData: FormData): Promise<Post> {
  const response = await apiClient.post('/community/posts', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

export async function updatePost(
  postId: number, 
  content: string, 
  postType?: PostType,
  deletePhotoIds?: number[],
  newPhotos?: File[]
): Promise<Post> {
  const formData = new FormData()
  formData.append('content', content)
  if (postType) {
    formData.append('post_type', postType)
  }
  if (deletePhotoIds && deletePhotoIds.length > 0) {
    formData.append('delete_photo_ids', JSON.stringify(deletePhotoIds))
  }
  if (newPhotos && newPhotos.length > 0) {
    newPhotos.forEach(photo => {
      formData.append('photos', photo)
    })
  }
  
  const response = await apiClient.put(`/community/posts/${postId}`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response.data
}

export async function deletePost(postId: number): Promise<void> {
  await apiClient.delete(`/community/posts/${postId}`)
}

export async function getComments(postId: number): Promise<CommentListResponse> {
  const response = await apiClient.get(`/community/posts/${postId}/comments`)
  return response.data
}

export async function createComment(postId: number, content: string): Promise<Comment> {
  const response = await apiClient.post(`/community/posts/${postId}/comments`, {
    content
  })
  return response.data
}

export async function deleteComment(
  postId: number,
  commentId: number
): Promise<void> {
  await apiClient.delete(`/community/comments/${commentId}`)
}

export async function togglePostLike(postId: number, isCurrentlyLiked: boolean): Promise<LikeResponse> {
  const response = isCurrentlyLiked 
    ? await apiClient.delete(`/community/posts/${postId}/like`)
    : await apiClient.post(`/community/posts/${postId}/like`)
  return {
    success: response.data.success,
    isLiked: response.data.is_liked,
    likeCount: response.data.like_count
  }
}

export async function toggleCommentLike(commentId: number): Promise<LikeResponse> {
  const response = await apiClient.post(`/community/comments/${commentId}/like`)
  return {
    success: response.data.success,
    isLiked: response.data.is_liked,
    likeCount: response.data.like_count
  }
}

export async function reportPost(postId: number, reason: string): Promise<{ success: boolean; message: string }> {
  const response = await apiClient.post(`/community/posts/${postId}/report`, { reason })
  return response.data
}
