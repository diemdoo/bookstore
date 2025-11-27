"""
Authentication Business Service
"""
from typing import Dict, Optional, Tuple
from data.user_dao import UserDAO
from business.dto.user_dto import UserDTO
from utils.helpers import hash_password, check_password, validate_email, validate_password
from models import db


class AuthService:
    """Business service for authentication operations"""
    
    @staticmethod
    def register(username: str, email: str, password: str, full_name: Optional[str] = None) -> Tuple[Optional[UserDTO], Optional[str]]:
        """
        Register a new user
        Returns: (UserDTO, error_message)
        """
        try:
            # Validate input
            if not username or not email or not password:
                return None, 'Vui lòng điền đầy đủ thông tin'
            
            if not validate_email(email):
                return None, 'Email không hợp lệ'
            
            if not validate_password(password):
                return None, 'Mật khẩu phải có ít nhất 6 ký tự'
            
            # Check if username exists
            if UserDAO.exists_by_username(username):
                return None, 'Username đã tồn tại'
            
            # Check if email exists
            if UserDAO.exists_by_email(email):
                return None, 'Email đã tồn tại'
            
            # Create user
            password_hash = hash_password(password)
            new_user = UserDAO.create(
                username=username.strip(),
                email=email.strip(),
                password_hash=password_hash,
                full_name=full_name.strip() if full_name else None,
                role='user'
            )
            
            return UserDTO.from_model(new_user), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi đăng ký: {str(e)}'
    
    @staticmethod
    def login(username: str, password: str) -> Tuple[Optional[UserDTO], Optional[str]]:
        """
        Login user
        Returns: (UserDTO, error_message)
        """
        try:
            if not username or not password:
                return None, 'Vui lòng nhập username và password'
            
            # Find user
            user = UserDAO.get_by_username(username)
            
            if not user or not check_password(password, user.password_hash):
                return None, 'Username hoặc password không đúng'
            
            if not user.is_active:
                return None, 'Tài khoản đã bị khóa'
            
            return UserDTO.from_model(user), None
            
        except Exception as e:
            return None, f'Lỗi đăng nhập: {str(e)}'
    
    @staticmethod
    def get_current_user(user_id: int) -> Tuple[Optional[UserDTO], Optional[str]]:
        """
        Get current user by ID
        Returns: (UserDTO, error_message)
        """
        try:
            user = UserDAO.get_by_id(user_id)
            if not user:
                return None, 'User không tồn tại'
            
            return UserDTO.from_model(user), None
            
        except Exception as e:
            return None, f'Lỗi lấy thông tin user: {str(e)}'
    
    @staticmethod
    def update_profile(user_id: int, full_name: str, email: str) -> Tuple[Optional[UserDTO], Optional[str]]:
        """
        Update user profile (full_name and email)
        Returns: (UserDTO, error_message)
        """
        try:
            if not full_name:
                return None, 'Họ tên không được để trống'
            
            if not email:
                return None, 'Email không được để trống'
            
            if not validate_email(email):
                return None, 'Email không hợp lệ'
            
            user = UserDAO.get_by_id(user_id)
            if not user:
                return None, 'Người dùng không tồn tại'
            
            # Check email uniqueness (exclude current user)
            existing = UserDAO.get_by_email(email)
            if existing and existing.id != user_id:
                return None, 'Email đã được sử dụng'
            
            # Update
            updated_user = UserDAO.update_profile(user_id, full_name.strip(), email.strip())
            
            return UserDTO.from_model(updated_user), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi cập nhật profile: {str(e)}'

