"""
Storage Service for handling file uploads to AWS S3
Provides methods for uploading, deleting, and generating presigned URLs for files
"""
import boto3
from botocore.exceptions import ClientError
from typing import BinaryIO, Optional
from datetime import datetime
import uuid
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
from PIL import Image
from io import BytesIO

from app.core.config import settings


class StorageService:
    """Service for managing file storage on AWS S3"""
    
    # Allowed file types
    ALLOWED_IMAGE_TYPES = {
        'image/jpeg': ['.jpg', '.jpeg'],
        'image/png': ['.png'],
        'image/webp': ['.webp'],
        'image/gif': ['.gif']
    }
    
    # File size limits (in bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        )
        self.bucket_name = settings.AWS_S3_BUCKET
    
    def validate_image_file(self, file: BinaryIO, filename: str) -> tuple[bool, Optional[str]]:
        """
        Validate image file
        
        Args:
            file: File object
            filename: Original filename
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > self.MAX_IMAGE_SIZE:
            return False, f"檔案大小超過限制 ({self.MAX_IMAGE_SIZE / 1024 / 1024}MB)"
        
        if file_size == 0:
            return False, "檔案為空"
        
        # Check MIME type using python-magic (if available)
        if HAS_MAGIC:
            try:
                file_content = file.read(2048)  # Read first 2KB for type detection
                file.seek(0)  # Reset
                
                mime_type = magic.from_buffer(file_content, mime=True)
                
                if mime_type not in self.ALLOWED_IMAGE_TYPES:
                    return False, f"不支援的檔案類型: {mime_type}"
            except Exception as e:
                return False, f"檔案類型檢測失敗: {str(e)}"
        
        # Validate it's a real image by opening with PIL
        try:
            file.seek(0)
            image = Image.open(file)
            image.verify()
            file.seek(0)
        except Exception as e:
            return False, f"無效的圖片檔案: {str(e)}"
        
        return True, None
    
    def optimize_image(self, file: BinaryIO, max_width: int = 1920, quality: int = 85) -> BytesIO:
        """
        Optimize image by resizing and compressing
        
        Args:
            file: Original image file
            max_width: Maximum width in pixels
            quality: JPEG quality (1-100)
            
        Returns:
            Optimized image as BytesIO
        """
        file.seek(0)
        image = Image.open(file)
        
        # Convert RGBA to RGB if necessary
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        
        # Resize if needed
        if image.width > max_width:
            ratio = max_width / image.width
            new_height = int(image.height * ratio)
            image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = BytesIO()
        image.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    
    def upload_pet_photo(
        self,
        file: BinaryIO,
        filename: str,
        pet_id: int,
        optimize: bool = True
    ) -> tuple[str, str]:
        """
        Upload pet photo to S3
        
        Args:
            file: Image file object
            filename: Original filename
            pet_id: Pet ID for organizing files
            optimize: Whether to optimize the image
            
        Returns:
            Tuple of (file_url, file_key)
            
        Raises:
            ValueError: If file validation fails
            Exception: If upload fails
        """
        # Validate file
        is_valid, error = self.validate_image_file(file, filename)
        if not is_valid:
            raise ValueError(error)
        
        # Optimize image if requested
        if optimize:
            file = self.optimize_image(file)
        else:
            file.seek(0)
        
        # Generate unique file key
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        file_extension = '.jpg' if optimize else filename.split('.')[-1]
        file_key = f"pets/{pet_id}/photos/{timestamp}_{unique_id}{file_extension}"
        
        # Determine content type
        if optimize:
            content_type = 'image/jpeg'
        elif HAS_MAGIC:
            file.seek(0)
            content_type = magic.from_buffer(file.read(2048), mime=True)
            file.seek(0)
        else:
            # Fallback to basic detection from extension
            content_type = 'image/jpeg' if file_extension in ['.jpg', '.jpeg'] else 'image/png'
        
        # Upload to S3
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file.read(),
                ContentType=content_type,
                CacheControl='max-age=31536000',  # Cache for 1 year
            )
            
            # Generate public URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
            
            return file_url, file_key
            
        except ClientError as e:
            raise Exception(f"S3 上傳失敗: {str(e)}")
    
    def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str = 'application/octet-stream',
        folder: str = 'documents'
    ) -> tuple[str, str]:
        """
        通用文件上傳方法（同步）
        
        Args:
            file_content: 文件內容（bytes）
            file_name: 文件名
            content_type: MIME 類型
            folder: S3 中的資料夾路徑
            
        Returns:
            tuple: (file_url, file_key)
        """
        try:
            # 生成唯一的文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{file_name}"
            file_key = f"{folder}/{unique_filename}"
            
            # 上傳到 S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_content,
                ContentType=content_type
            )
            
            # 生成 URL
            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
            
            return file_url, file_key
            
        except ClientError as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"❌ S3 上傳錯誤: {error_detail}")
            raise Exception(f"文件上傳失敗: {str(e)}")
    
    def delete_file(self, file_key: str) -> bool:
        """
        Delete file from S3
        
        Args:
            file_key: S3 object key
            
        Returns:
            True if successful
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=file_key
            )
            return True
        except ClientError as e:
            print(f"S3 刪除失敗: {str(e)}")
            return False
    
    def generate_presigned_url(self, file_key: str, expiration: int = 3600) -> str:
        """
        Generate presigned URL for private files
        
        Args:
            file_key: S3 object key
            expiration: URL expiration time in seconds
            
        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            raise Exception(f"生成 URL 失敗: {str(e)}")


# Global storage service instance
storage_service = StorageService()
