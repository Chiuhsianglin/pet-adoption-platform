"""
S3 file upload service with URL caching
"""
import boto3
import os
from typing import Optional, Dict
from pathlib import Path
import uuid
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.core.config import settings

class S3Service:
    """Service for uploading files to AWS S3 with URL caching"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.AWS_S3_BUCKET
        self.region = settings.AWS_REGION
        self.use_s3 = settings.USE_S3
        self.cloudfront_domain = settings.AWS_CLOUDFRONT_DOMAIN
        # OPTIMIZED: Cache presigned URLs to reduce AWS API calls
        self._url_cache: Dict[str, tuple] = {}  # {s3_key: (url, expiration_time)}
        
        print(f"🔧 S3Service 初始化:")
        print(f"   USE_S3: {self.use_s3}")
        print(f"   Bucket: {self.bucket_name}")
        print(f"   Region: {self.region}")
        print(f"   CloudFront: {self.cloudfront_domain or '未設置'}")
        print(f"   AWS_ACCESS_KEY_ID 是否存在: {bool(settings.AWS_ACCESS_KEY_ID)}")
        
        # Initialize S3 client if enabled
        if self.use_s3:
            try:
                print(f"   📡 正在初始化 S3 client...")
                self.s3_client = boto3.client(
                    's3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=self.region
                )
                print(f"   ✅ S3 client 初始化成功!")
            except Exception as e:
                print(f"   ⚠️  Failed to initialize S3 client: {e}")
                import traceback
                traceback.print_exc()
                self.use_s3 = False
        else:
            print(f"   ℹ️  S3 未啟用，將使用本地儲存")
    
    def generate_s3_key(self, category: str, filename: str) -> str:
        """Generate S3 object key"""
        ext = Path(filename).suffix.lower()
        unique_filename = f"{uuid.uuid4()}{ext}"
        return f"{category}/{unique_filename}"
    
    def upload_file(self, file_content: bytes, filename: str, category: str, content_type: str) -> dict:
        """
        Upload file to S3 or local storage
        
        Returns:
            dict with file_url and file_key
        """
        print(f"    🔧 S3 Service - USE_S3={self.use_s3}")
        
        if self.use_s3 and self.s3_client:
            print(f"    ☁️  使用 S3 上傳到 bucket: {self.bucket_name}")
            return self._upload_to_s3(file_content, filename, category, content_type)
        else:
            print(f"    💾 使用本地儲存")
            return self._upload_to_local(file_content, filename, category)
    
    def _upload_to_s3(self, file_content: bytes, filename: str, category: str, content_type: str) -> dict:
        """Upload file to S3"""
        try:
            s3_key = self.generate_s3_key(category, filename)
            print(f"      📤 上傳到 S3 - Key: {s3_key}")
            
            # Upload to S3 (private by default)
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=file_content,
                ContentType=content_type,
                CacheControl='max-age=31536000',  # Cache for 1 year
            )
            
            print(f"      ✅ S3 上傳成功!")
            
            # Generate presigned URL (valid for 7 days)
            file_url = self.generate_presigned_url(s3_key, expiration=604800)
            print(f"      🔗 生成預簽名 URL (有效期 7 天)")
            
            return {
                "file_url": file_url,
                "file_key": s3_key,
            }
        except ClientError as e:
            print(f"      ❌ S3 upload failed: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to upload to S3: {str(e)}")
    
    def generate_presigned_url(self, s3_key: str, expiration: int = 604800) -> str:
        """
        Generate a URL for an S3 object (CloudFront優先，回退到Presigned URL)
        
        Args:
            s3_key: S3 object key
            expiration: URL expiration time in seconds (default: 7 days)
        
        Returns:
            CloudFront URL or Presigned URL
        """
        # 優先使用 CloudFront（公開訪問，無過期時間）
        if self.cloudfront_domain:
            cloudfront_url = f"{self.cloudfront_domain.rstrip('/')}/{s3_key}"
            print(f"      🚀 使用 CloudFront URL: {cloudfront_url[:80]}...")
            return cloudfront_url
        
        # 回退到 Presigned URL（帶快取）
        if s3_key in self._url_cache:
            cached_url, cache_expiry = self._url_cache[s3_key]
            if datetime.now() < cache_expiry - timedelta(hours=1):
                return cached_url
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            
            self._url_cache[s3_key] = (url, datetime.now() + timedelta(seconds=expiration))
            print(f"      🔗 生成 Presigned URL (有效期 {expiration//86400} 天)")
            return url
        except ClientError as e:
            print(f"❌ Failed to generate presigned URL: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to generate presigned URL: {str(e)}")
    
    def _upload_to_local(self, file_content: bytes, filename: str, category: str) -> dict:
        """Upload file to local storage (fallback)"""
        try:
            # Create upload directory
            upload_dir = Path("uploads") / category
            upload_dir.mkdir(parents=True, exist_ok=True)
            print(f"      📁 本地儲存目錄: {upload_dir.absolute()}")
            
            # Generate unique filename
            ext = Path(filename).suffix.lower()
            unique_filename = f"{uuid.uuid4()}{ext}"
            file_path = upload_dir / unique_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)
            
            print(f"      💾 檔案已儲存: {file_path.absolute()}")
            
            # Generate URL
            base_url = settings.BACKEND_URL
            file_url = f"{base_url}/uploads/{category}/{unique_filename}"
            file_key = f"{category}/{unique_filename}"
            
            print(f"      🔗 本地 URL: {file_url}")
            
            return {
                "file_url": file_url,
                "file_key": file_key,
            }
        except Exception as e:
            print(f"      ❌ Local upload failed: {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_key: str) -> bool:
        """Delete file from S3 or local storage"""
        if self.use_s3 and self.s3_client:
            try:
                self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=file_key
                )
                return True
            except ClientError as e:
                print(f"❌ S3 delete failed: {e}")
                return False
        else:
            try:
                file_path = Path("uploads") / file_key
                if file_path.exists():
                    file_path.unlink()
                return True
            except Exception as e:
                print(f"❌ Local delete failed: {e}")
                return False
    
    def get_file_url(self, file_key: str, expiration: int = 604800) -> Optional[str]:
        """
        Get URL for a file (alias for generate_presigned_url)
        
        Args:
            file_key: S3 object key (e.g., 'pet_photo/abc.jpg')
            expiration: URL expiration time in seconds (default 3600 = 1 hour)
            
        Returns:
            Presigned URL string, or None if not using S3
        """
        if not self.use_s3:
            print(f"⚠️ S3 is disabled, returning None for {file_key}")
            return None
            
        if not self.s3_client:
            print(f"❌ S3 client not initialized, returning None for {file_key}")
            return None
            
        try:
            print(f"📡 Generating presigned URL for: {file_key}")
            print(f"   Bucket: {self.bucket_name}")
            print(f"   Region: {self.region}")
            print(f"   Expiration: {expiration}s")
            
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': file_key
                },
                ExpiresIn=expiration
            )
            
            print(f"✅ Presigned URL generated successfully")
            print(f"   URL preview: {presigned_url[:100]}...")
            return presigned_url
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = e.response.get('Error', {}).get('Message', str(e))
            print(f"❌ AWS ClientError generating presigned URL for {file_key}:")
            print(f"   Error Code: {error_code}")
            print(f"   Error Message: {error_msg}")
            print(f"   Full response: {e.response}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error generating presigned URL for {file_key}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_s3_url(self, url: str) -> bool:
        """Check if a URL is an S3 URL (either direct S3 or CloudFront)"""
        if not url:
            return False
        return (
            f"{self.bucket_name}.s3" in url or
            f"s3.{self.region}.amazonaws.com/{self.bucket_name}" in url or
            (settings.AWS_CLOUDFRONT_DOMAIN and settings.AWS_CLOUDFRONT_DOMAIN in url)
        )
    
    def extract_s3_key_from_url(self, url: str) -> Optional[str]:
        """Extract S3 key from S3 URL"""
        if not url or not self.is_s3_url(url):
            return None
            
        try:
            # CloudFront URL: https://cloudfront.domain/pet_photo/abc.jpg
            if settings.AWS_CLOUDFRONT_DOMAIN and settings.AWS_CLOUDFRONT_DOMAIN in url:
                return url.split(settings.AWS_CLOUDFRONT_DOMAIN + '/')[-1]
            
            # S3 URL: https://bucket.s3.region.amazonaws.com/pet_photo/abc.jpg
            if f"{self.bucket_name}.s3" in url:
                return url.split(f"{self.bucket_name}.s3.{self.region}.amazonaws.com/")[-1].split('?')[0]
            
            return None
        except Exception as e:
            print(f"❌ Failed to extract S3 key from {url}: {e}")
            return None


# Global S3 service instance
s3_service = S3Service()
