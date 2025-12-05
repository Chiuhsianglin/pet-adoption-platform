# -*- coding: utf-8 -*-
"""
Community API E2E Tests
Test complete community flow: HTTP Request -> Controller -> Service -> Repository -> Database
"""
import pytest
from httpx import AsyncClient
from app.models.user import User
from app.models.community import CommunityPost, PostComment, PostLike, PostTypeEnum


# ==================== Create Post Tests ====================

@pytest.mark.asyncio
class TestCreatePostAPI:
    """Test create community post API"""
    
    async def test_create_post_success(
        self,
        async_client: AsyncClient,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully create a post"""
        post_data = {
            "content": "This is my first community post!",
            "post_type": "share"
        }
        
        response = await async_client.post(
            "/api/v2/community/posts",
            data=post_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "This is my first community post!"
        assert data["post_type"] == "share"
        assert data["user_id"] == test_adopter_user.id
        assert "id" in data
    
    async def test_create_post_question_type(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """Test create question type post"""
        post_data = {
            "content": "How to train my new puppy?",
            "post_type": "question"
        }
        
        response = await async_client.post(
            "/api/v2/community/posts",
            data=post_data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["post_type"] == "question"
    
    async def test_create_post_empty_content(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """Test create post with empty content"""
        post_data = {
            "content": "",
            "post_type": "share"
        }
        
        response = await async_client.post(
            "/api/v2/community/posts",
            data=post_data,
            headers=adopter_auth_headers
        )
        
        # Validation happens at service layer and returns 400
        # But if FastAPI validation fails first, returns 422
        assert response.status_code in [400, 422]
    
    async def test_create_post_unauthenticated(
        self,
        async_client: AsyncClient
    ):
        """Test unauthenticated cannot create post"""
        post_data = {
            "content": "Test post",
            "post_type": "share"
        }
        
        response = await async_client.post(
            "/api/v2/community/posts",
            data=post_data
        )
        
        assert response.status_code in [401, 403]


# ==================== Get Post Tests ====================

@pytest.mark.asyncio
class TestGetPostAPI:
    """Test get post details API"""
    
    async def test_get_post_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully get post details"""
        # Create test post
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Test post content",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.get(
            f"/api/v2/community/posts/{post.id}",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == post.id
        assert data["content"] == "Test post content"
    
    async def test_get_post_not_found(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """Test get non-existent post"""
        response = await async_client.get(
            "/api/v2/community/posts/99999",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_get_deleted_post(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test get deleted post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Deleted post",
            post_type=PostTypeEnum.share,
            is_deleted=True
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.get(
            f"/api/v2/community/posts/{post.id}",
            headers=adopter_auth_headers
        )
        
        # Should return 404 or show as deleted
        assert response.status_code in [200, 404]


# ==================== List Posts Tests ====================

@pytest.mark.asyncio
class TestListPostsAPI:
    """Test list posts API"""
    
    async def test_list_posts_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully list posts"""
        # Create test posts
        for i in range(3):
            post = CommunityPost(
                user_id=test_adopter_user.id,
                content=f"Test post {i+1}",
                post_type=PostTypeEnum.share
            )
            test_db.add(post)
        await test_db.commit()
        
        response = await async_client.get(
            "/api/v2/community/posts",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        # Response could be list or dict with posts/items key
        if isinstance(data, list):
            assert len(data) >= 3
        else:
            assert "posts" in data or "items" in data
    
    async def test_list_posts_with_type_filter(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test list posts with post_type filter"""
        # Create posts of different types
        post1 = CommunityPost(
            user_id=test_adopter_user.id,
            content="Question post",
            post_type=PostTypeEnum.question
        )
        post2 = CommunityPost(
            user_id=test_adopter_user.id,
            content="Share post",
            post_type=PostTypeEnum.share
        )
        test_db.add_all([post1, post2])
        await test_db.commit()
        
        response = await async_client.get(
            "/api/v2/community/posts?post_type=question",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
    
    async def test_list_my_posts(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test list current user's posts"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="My post",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        
        response = await async_client.get(
            "/api/v2/community/posts/my",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200


# ==================== Update Post Tests ====================

@pytest.mark.asyncio
class TestUpdatePostAPI:
    """Test update post API"""
    
    async def test_update_post_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully update own post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Original content",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.put(
            f"/api/v2/community/posts/{post.id}",
            data={"content": "Updated content"},
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["content"] == "Updated content"
    
    async def test_update_post_not_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        test_shelter_user: User,
        shelter_auth_headers: dict
    ):
        """Test cannot update other user's post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Original content",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.put(
            f"/api/v2/community/posts/{post.id}",
            data={"content": "Hacked content"},
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 403
    
    async def test_update_post_not_found(
        self,
        async_client: AsyncClient,
        adopter_auth_headers: dict
    ):
        """Test update non-existent post"""
        response = await async_client.put(
            "/api/v2/community/posts/99999",
            data={"content": "Updated"},
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 404


# ==================== Delete Post Tests ====================

@pytest.mark.asyncio
class TestDeletePostAPI:
    """Test delete post API"""
    
    async def test_delete_post_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully delete own post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="To be deleted",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.delete(
            f"/api/v2/community/posts/{post.id}",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
    
    async def test_delete_post_not_owner(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        shelter_auth_headers: dict
    ):
        """Test cannot delete other user's post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Protected post",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.delete(
            f"/api/v2/community/posts/{post.id}",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 403


# ==================== Comment Tests ====================

@pytest.mark.asyncio
class TestCommentAPI:
    """Test comment API"""
    
    async def test_create_comment_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        test_shelter_user: User,
        shelter_auth_headers: dict
    ):
        """Test successfully create comment"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Post with comment",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.post(
            f"/api/v2/community/posts/{post.id}/comments",
            json={"content": "Great post!"},
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["content"] == "Great post!"
        assert data["user_id"] == test_shelter_user.id
    
    async def test_get_comments(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        test_shelter_user: User,
        adopter_auth_headers: dict
    ):
        """Test get post comments"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Post with comments",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        # Add comments
        for i in range(3):
            comment = PostComment(
                post_id=post.id,
                user_id=test_shelter_user.id,
                content=f"Comment {i+1}"
            )
            test_db.add(comment)
        await test_db.commit()
        
        response = await async_client.get(
            f"/api/v2/community/posts/{post.id}/comments",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        if isinstance(data, list):
            assert len(data) >= 3
        else:
            assert "comments" in data or "items" in data
    
    async def test_delete_comment_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test successfully delete own comment"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Post",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        comment = PostComment(
            post_id=post.id,
            user_id=test_adopter_user.id,
            content="My comment"
        )
        test_db.add(comment)
        await test_db.commit()
        await test_db.refresh(comment)
        
        response = await async_client.delete(
            f"/api/v2/community/comments/{comment.id}",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200


# ==================== Like Tests ====================

@pytest.mark.asyncio
class TestLikeAPI:
    """Test like/unlike post API"""
    
    async def test_like_post_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        test_shelter_user: User,
        shelter_auth_headers: dict
    ):
        """Test successfully like a post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Likeable post",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        response = await async_client.post(
            f"/api/v2/community/posts/{post.id}/like",
            headers=shelter_auth_headers
        )
        
        assert response.status_code in [200, 201]
    
    async def test_unlike_post_success(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        test_shelter_user: User,
        shelter_auth_headers: dict
    ):
        """Test successfully unlike a post"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Post to unlike",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        # First like it
        like = PostLike(
            post_id=post.id,
            user_id=test_shelter_user.id
        )
        test_db.add(like)
        await test_db.commit()
        
        # Then unlike
        response = await async_client.delete(
            f"/api/v2/community/posts/{post.id}/like",
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
    
    async def test_like_post_twice(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        adopter_auth_headers: dict
    ):
        """Test liking same post twice (should be idempotent)"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Double like test",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        # First like
        response1 = await async_client.post(
            f"/api/v2/community/posts/{post.id}/like",
            headers=adopter_auth_headers
        )
        assert response1.status_code in [200, 201]
        
        # Second like (should not fail)
        response2 = await async_client.post(
            f"/api/v2/community/posts/{post.id}/like",
            headers=adopter_auth_headers
        )
        assert response2.status_code in [200, 201, 409]


# ==================== Post Stats Tests ====================

@pytest.mark.asyncio
class TestPostStatsAPI:
    """Test post statistics API"""
    
    async def test_get_post_stats(
        self,
        async_client: AsyncClient,
        test_db,
        test_adopter_user: User,
        test_shelter_user: User,
        adopter_auth_headers: dict
    ):
        """Test get post statistics"""
        post = CommunityPost(
            user_id=test_adopter_user.id,
            content="Stats test post",
            post_type=PostTypeEnum.share
        )
        test_db.add(post)
        await test_db.commit()
        await test_db.refresh(post)
        
        # Add some likes and comments
        like = PostLike(
            post_id=post.id,
            user_id=test_shelter_user.id
        )
        comment = PostComment(
            post_id=post.id,
            user_id=test_shelter_user.id,
            content="Test comment"
        )
        test_db.add_all([like, comment])
        await test_db.commit()
        
        response = await async_client.get(
            f"/api/v2/community/posts/{post.id}/stats",
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "like_count" in data or "likes" in data
        assert "comment_count" in data or "comments" in data
