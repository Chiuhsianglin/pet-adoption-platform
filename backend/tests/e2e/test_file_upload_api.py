"""
File Upload API E2E Tests
æ¸¬è©¦æª”æ?ä¸Šå‚³?Ÿèƒ½?„ç«¯å°ç«¯?´æ™¯
"""
import pytest
from httpx import AsyncClient
from io import BytesIO


class TestFileUploadAPI:
    """æª”æ?ä¸Šå‚³ API æ¸¬è©¦"""
    
    @pytest.mark.asyncio
    async def test_upload_single_image_success(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦?å?ä¸Šå‚³?®å¼µ?–ç?"""
        # ?µå»ºæ¸¬è©¦?–ç?
        image_data = b"fake_image_content_jpg"
        files = {
            "files": ("test_pet.jpg", BytesIO(image_data), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert "uploaded_files" in result
        assert len(result["uploaded_files"]) == 1
        assert result["uploaded_files"][0]["category"] == "pet_photo"
        assert result["uploaded_files"][0]["filename"].endswith(".jpg")
        assert "url" in result["uploaded_files"][0]
    
    @pytest.mark.asyncio
    async def test_upload_multiple_images_success(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦?å?ä¸Šå‚³å¤šå¼µ?–ç?"""
        files = [
            ("files", ("pet1.jpg", BytesIO(b"image1"), "image/jpeg")),
            ("files", ("pet2.png", BytesIO(b"image2"), "image/png")),
            ("files", ("pet3.gif", BytesIO(b"image3"), "image/gif")),
        ]
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["uploaded_files"]) == 3
        filenames = [f["filename"] for f in result["uploaded_files"]]
        assert any("pet1.jpg" in f for f in filenames)
        assert any("pet2.png" in f for f in filenames)
        assert any("pet3.gif" in f for f in filenames)
    
    @pytest.mark.asyncio
    async def test_upload_document_success(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦?å?ä¸Šå‚³?‡ä»¶"""
        files = {
            "files": ("adoption_form.pdf", BytesIO(b"pdf_content"), "application/pdf")
        }
        data = {"category": "document"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["uploaded_files"]) == 1
        assert result["uploaded_files"][0]["category"] == "document"
        assert result["uploaded_files"][0]["filename"].endswith(".pdf")
    
    @pytest.mark.asyncio
    async def test_upload_profile_photo_success(
        self, async_client: AsyncClient, adopter_auth_headers: dict
    ):
        """æ¸¬è©¦?å?ä¸Šå‚³?‹äºº?­å?"""
        files = {
            "files": ("avatar.jpg", BytesIO(b"avatar_content"), "image/jpeg")
        }
        data = {"category": "profile"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=adopter_auth_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["uploaded_files"][0]["category"] == "profile"
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦ä¸Šå‚³ä¸å?è¨±ç?æª”æ?é¡å?"""
        files = {
            "files": ("malware.exe", BytesIO(b"executable"), "application/x-msdownload")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_upload_invalid_category(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦ä½¿ç”¨?¡æ??„å?é¡?""
        files = {
            "files": ("test.jpg", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "invalid_category"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_without_authentication(self, async_client: AsyncClient):
        """æ¸¬è©¦?ªè?è­‰ç”¨?¶ä??³æ?æ¡?""
        files = {
            "files": ("test.jpg", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data
        )
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_upload_empty_file(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦ä¸Šå‚³ç©ºæ?æ¡?""
        files = {
            "files": ("empty.jpg", BytesIO(b""), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        # ?‰è©²?å?ä½†å¯?½æ?è­¦å?ï¼Œæ??¹æ?å¯¦ä??’ç?
        # ?™è£¡?‡è¨­ç³»çµ±?è¨±ç©ºæ?æ¡ˆä???
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_upload_large_file(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦ä¸Šå‚³å¤§æ?æ¡ˆï?å¦‚æ??‰å¤§å°é??¶ï?"""
        # ?µå»º 11MB ?„æ?æ¡ˆï??‡è¨­?åˆ¶??10MBï¼?
        large_data = b"x" * (11 * 1024 * 1024)
        files = {
            "files": ("large.jpg", BytesIO(large_data), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        # ?¹æ?å¯¦ä?ï¼Œå¯?½æ??Ÿæ?å¤±æ?
        # ?™è£¡?‘å€‘åªé©—è?ç³»çµ±?‰è??†å¤§æª”æ??„èƒ½??
        assert response.status_code in [200, 400, 413]
    
    @pytest.mark.asyncio
    async def test_upload_mixed_valid_invalid_files(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦?Œæ?ä¸Šå‚³?‰æ??Œç„¡?ˆç?æª”æ?"""
        files = [
            ("files", ("valid.jpg", BytesIO(b"image"), "image/jpeg")),
            ("files", ("invalid.exe", BytesIO(b"exe"), "application/x-msdownload")),
        ]
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        # ?‰è©²?’ç??´å€‹è?æ±?
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_upload_file_with_special_characters_in_name(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦ä¸Šå‚³?…å«?¹æ?å­—å??„æ?æ¡ˆå?ç¨?""
        files = {
            "files": ("å¯µç‰©?§ç? (1).jpg", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        assert response.status_code == 200
        # ç³»çµ±?‰è©²?•ç??¹æ?å­—å?ï¼ˆå¯?½æ?æ¸…ç??–ç·¨ç¢¼ï?
        result = response.json()
        assert len(result["uploaded_files"]) == 1


class TestFileUploadSecurity:
    """æª”æ?ä¸Šå‚³å®‰å…¨?§æ¸¬è©?""
    
    @pytest.mark.asyncio
    async def test_upload_file_with_path_traversal_attempt(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦è·¯å??æ­·?»æ??²è­·"""
        files = {
            "files": ("../../../etc/passwd", BytesIO(b"hack"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        # ç³»çµ±?‰è©²æ¸…ç?æª”æ??ç¨±?–æ?çµ?
        if response.status_code == 200:
            result = response.json()
            # æª”æ??ç¨±ä¸æ?è©²å??«è·¯å¾‘é?æ­·å???
            assert "../" not in result["uploaded_files"][0]["filename"]
    
    @pytest.mark.asyncio
    async def test_upload_file_with_null_byte_injection(
        self, async_client: AsyncClient, shelter_auth_headers: dict
    ):
        """æ¸¬è©¦ null byte æ³¨å…¥?²è­·"""
        files = {
            "files": ("test.jpg\x00.exe", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_auth_headers
        )
        
        # ç³»çµ±?‰è©²æ¸…ç??–æ?çµ•å???null byte ?„æ?æ¡ˆå?ç¨?
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            result = response.json()
            assert "\x00" not in result["uploaded_files"][0]["filename"]
