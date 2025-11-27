"""
Storage utility để upload ảnh lên Cloudflare R2
"""
import os
import boto3
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename
import uuid

class StorageService:
    """Service để quản lý upload ảnh lên Cloudflare R2
    
    Tất cả cấu hình được đọc từ environment variables:
    - R2_ACCOUNT_ID: Cloudflare Account ID
    - R2_ACCESS_KEY_ID: R2 Access Key ID
    - R2_SECRET_ACCESS_KEY: R2 Secret Access Key
    - R2_BUCKET_NAME: R2 Bucket name
    - R2_PUBLIC_DOMAIN: Custom domain cho public URLs (ví dụ: cdn.duynhne.me)
    """
    
    def __init__(self):
        """Khởi tạo R2 client từ environment variables"""
        # Đọc tất cả cấu hình từ environment variables (không hardcode)
        self.account_id = os.getenv('R2_ACCOUNT_ID')
        self.access_key_id = os.getenv('R2_ACCESS_KEY_ID')
        self.secret_access_key = os.getenv('R2_SECRET_ACCESS_KEY')
        self.bucket_name = os.getenv('R2_BUCKET_NAME')
        self.public_domain = os.getenv('R2_PUBLIC_DOMAIN')
        
        # Validate required env vars
        if not all([self.account_id, self.access_key_id, self.secret_access_key, self.bucket_name, self.public_domain]):
            raise ValueError(
                'Missing required R2 environment variables. '
                'Check R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME, R2_PUBLIC_DOMAIN'
            )
        
        # Build R2 endpoint
        endpoint_url = f'https://{self.account_id}.r2.cloudflarestorage.com'
        
        # Tạo boto3 S3 client với R2 endpoint
        self.client = boto3.client(
            's3',
            endpoint_url=endpoint_url,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key
        )
        
        # Tạo bucket nếu chưa có
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Đảm bảo bucket tồn tại"""
        try:
            # Kiểm tra bucket có tồn tại không
            self.client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            if error_code == '404':
                # Bucket không tồn tại, tạo mới
                try:
                    self.client.create_bucket(Bucket=self.bucket_name)
                    print(f'✅ Đã tạo bucket: {self.bucket_name}')
                except ClientError as create_error:
                    print(f'❌ Lỗi khi tạo bucket: {create_error}')
            else:
                print(f'❌ Lỗi khi kiểm tra bucket: {e}')
    
    def upload_file(self, file, folder='books'):
        """
        Upload file lên Cloudflare R2
        
        Args:
            file: File object từ request
            folder: Thư mục trong bucket (default: 'books')
        
        Returns:
            str: Public URL của file (sử dụng custom domain)
        """
        try:
            # Validate file
            if not file or not file.filename:
                raise ValueError('Không có file được upload')
            
            # Lấy extension
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
            
            # Validate extension
            allowed_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
            if ext not in allowed_extensions:
                raise ValueError(f'Định dạng file không được hỗ trợ. Chỉ chấp nhận: {", ".join(allowed_extensions)}')
            
            # Tạo tên file unique
            unique_filename = f"{uuid.uuid4()}.{ext}"
            object_name = f"{folder}/{unique_filename}" if folder else unique_filename
            
            # Upload file lên R2
            file.seek(0)  # Reset file pointer
            self.client.upload_fileobj(
                file,
                self.bucket_name,
                object_name,
                ExtraArgs={'ContentType': f'image/{ext}'}
            )
            
            # Tạo public URL sử dụng custom domain
            url = f"https://{self.public_domain}/{object_name}"
            
            return url
            
        except ClientError as e:
            raise Exception(f'Lỗi khi upload lên R2: {str(e)}')
        except Exception as e:
            raise Exception(f'Lỗi khi upload file: {str(e)}')
    
    def delete_file(self, object_name):
        """
        Xóa file khỏi Cloudflare R2
        
        Args:
            object_name: Tên object trong bucket (ví dụ: 'books/filename.jpg')
        """
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except ClientError as e:
            raise Exception(f'Lỗi khi xóa file: {str(e)}')

# Singleton instance
storage_service = StorageService()

