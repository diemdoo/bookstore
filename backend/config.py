"""
Cấu hình cho ứng dụng Flask
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Cấu hình chung cho ứng dụng"""
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://bookstore_user:bookstore_pass@localhost:5432/bookstore'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key cho session
    SECRET_KEY = os.getenv('SECRET_KEY', 'bookstore-secret-key-change-in-production')
    
    # Session config
    SESSION_COOKIE_SECURE = False  # Set True trong production với HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

