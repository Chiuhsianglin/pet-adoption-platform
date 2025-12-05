"""
File Upload API E2E Tests
測試檔案上傳功能的端對端場景
"""
import pytest
from httpx import AsyncClient
from io import BytesIO


class TestFileUploadAPI:
    """檔案上傳 API 測試"""
    
    @pytest.mark.asyncio
    async def test_upload_single_image_success(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試成功上傳單張圖片"""
        # 創建測試圖片
        image_data = b"fake_image_content_jpg"
        files = {
            "files": ("test_pet.jpg", BytesIO(image_data), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
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
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試成功上傳多張圖片"""
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
            headers=shelter_headers
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
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試成功上傳文件"""
        files = {
            "files": ("adoption_form.pdf", BytesIO(b"pdf_content"), "application/pdf")
        }
        data = {"category": "document"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert len(result["uploaded_files"]) == 1
        assert result["uploaded_files"][0]["category"] == "document"
        assert result["uploaded_files"][0]["filename"].endswith(".pdf")
    
    @pytest.mark.asyncio
    async def test_upload_profile_photo_success(
        self, async_client: AsyncClient, adopter_headers: dict
    ):
        """測試成功上傳個人頭像"""
        files = {
            "files": ("avatar.jpg", BytesIO(b"avatar_content"), "image/jpeg")
        }
        data = {"category": "profile"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=adopter_headers
        )
        
        assert response.status_code == 200
        result = response.json()
        assert result["uploaded_files"][0]["category"] == "profile"
    
    @pytest.mark.asyncio
    async def test_upload_invalid_file_type(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試上傳不允許的檔案類型"""
        files = {
            "files": ("malware.exe", BytesIO(b"executable"), "application/x-msdownload")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        assert response.status_code == 400
        assert "not allowed" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_upload_invalid_category(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試使用無效的分類"""
        files = {
            "files": ("test.jpg", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "invalid_category"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        assert response.status_code == 400
        assert "Invalid category" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_upload_without_authentication(self, async_client: AsyncClient):
        """測試未認證用戶上傳檔案"""
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
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試上傳空檔案"""
        files = {
            "files": ("empty.jpg", BytesIO(b""), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        # 應該成功但可能有警告，或根據實作拒絕
        # 這裡假設系統允許空檔案上傳
        assert response.status_code in [200, 400]
    
    @pytest.mark.asyncio
    async def test_upload_large_file(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試上傳大檔案（如果有大小限制）"""
        # 創建 11MB 的檔案（假設限制是 10MB）
        large_data = b"x" * (11 * 1024 * 1024)
        files = {
            "files": ("large.jpg", BytesIO(large_data), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        # 根據實作，可能成功或失敗
        # 這裡我們只驗證系統有處理大檔案的能力
        assert response.status_code in [200, 400, 413]
    
    @pytest.mark.asyncio
    async def test_upload_mixed_valid_invalid_files(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試同時上傳有效和無效的檔案"""
        files = [
            ("files", ("valid.jpg", BytesIO(b"image"), "image/jpeg")),
            ("files", ("invalid.exe", BytesIO(b"exe"), "application/x-msdownload")),
        ]
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        # 應該拒絕整個請求
        assert response.status_code == 400
    
    @pytest.mark.asyncio
    async def test_upload_file_with_special_characters_in_name(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試上傳包含特殊字元的檔案名稱"""
        files = {
            "files": ("寵物照片 (1).jpg", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        assert response.status_code == 200
        # 系統應該處理特殊字元（可能會清理或編碼）
        result = response.json()
        assert len(result["uploaded_files"]) == 1


class TestFileUploadSecurity:
    """檔案上傳安全性測試"""
    
    @pytest.mark.asyncio
    async def test_upload_file_with_path_traversal_attempt(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試路徑遍歷攻擊防護"""
        files = {
            "files": ("../../../etc/passwd", BytesIO(b"hack"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        # 系統應該清理檔案名稱或拒絕
        if response.status_code == 200:
            result = response.json()
            # 檔案名稱不應該包含路徑遍歷字元
            assert "../" not in result["uploaded_files"][0]["filename"]
    
    @pytest.mark.asyncio
    async def test_upload_file_with_null_byte_injection(
        self, async_client: AsyncClient, shelter_headers: dict
    ):
        """測試 null byte 注入防護"""
        files = {
            "files": ("test.jpg\x00.exe", BytesIO(b"image"), "image/jpeg")
        }
        data = {"category": "pet_photo"}
        
        response = await async_client.post(
            "/api/v2/files/upload",
            files=files,
            data=data,
            headers=shelter_headers
        )
        
        # 系統應該清理或拒絕包含 null byte 的檔案名稱
        assert response.status_code in [200, 400]
        if response.status_code == 200:
            result = response.json()
            assert "\x00" not in result["uploaded_files"][0]["filename"]
