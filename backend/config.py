"""
File: config.py

Mục đích:
Tập trung quản lý tất cả environment variables và cấu hình cho ứng dụng Flask

Tất cả environment variables được đọc từ .env file hoặc system environment,
và được định nghĩa ở đây để dễ quản lý và maintain.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Cấu hình chung cho ứng dụng Flask
    
    Tất cả environment variables được đọc từ .env file hoặc system environment.
    Đây là single source of truth cho tất cả cấu hình của ứng dụng.
    """
    # ==================== Database Configuration ====================
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://bookstore_user:bookstore_pass@localhost:5432/bookstore'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ==================== Security Configuration ====================
    # Secret key cho session encryption
    SECRET_KEY = os.getenv('SECRET_KEY', 'bookstore-secret-key-change-in-production')
    
    # Session config
    SESSION_COOKIE_SECURE = False  # Set True trong production với HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ==================== Cloudflare R2 Storage Configuration ====================
    # R2 Account ID (Cloudflare Account ID)
    R2_ACCOUNT_ID = os.getenv('R2_ACCOUNT_ID')
    
    # R2 Access Key ID (API Token)
    R2_ACCESS_KEY_ID = os.getenv('R2_ACCESS_KEY_ID')
    
    # R2 Secret Access Key (API Token Secret)
    R2_SECRET_ACCESS_KEY = os.getenv('R2_SECRET_ACCESS_KEY')
    
    # R2 Bucket Name (Tên bucket để lưu trữ files)
    R2_BUCKET_NAME = os.getenv('R2_BUCKET_NAME')
    
    # R2 Public Domain (Custom domain cho public URLs, ví dụ: cdn.duyne.me)
    R2_PUBLIC_DOMAIN = os.getenv('R2_PUBLIC_DOMAIN')
    
    # ==================== Logging Configuration ====================
    # Log level cho ứng dụng (debug, info, warning, error, critical)
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'info')
    
    # ==================== Gemini AI Configuration ====================
    # Google Gemini Pro API Key (để tích hợp chatbot thông minh)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

