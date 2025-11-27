"""
User Data Access Object
"""
from models import db, User
from business.dto.user_dto import UserDTO
from typing import Optional, List


class UserDAO:
    """Data Access Object for User operations"""
    
    @staticmethod
    def get_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def get_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_all() -> List[User]:
        """Get all users ordered by created_at desc"""
        return User.query.order_by(User.created_at.desc()).all()
    
    @staticmethod
    def create(username: str, email: str, password_hash: str,
               full_name: Optional[str] = None, role: str = 'user') -> User:
        """Create a new user"""
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name or username,
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    @staticmethod
    def update_status(user_id: int, is_active: bool) -> Optional[User]:
        """Update user active status"""
        user = User.query.get(user_id)
        if user:
            user.is_active = is_active
            db.session.commit()
        return user
    
    @staticmethod
    def update_profile(user_id: int, full_name: str, email: str) -> Optional[User]:
        """Update user profile (full_name and email)"""
        user = User.query.get(user_id)
        if user:
            user.full_name = full_name
            user.email = email
            db.session.commit()
        return user
    
    @staticmethod
    def exists_by_username(username: str) -> bool:
        """Check if username exists"""
        return User.query.filter_by(username=username).first() is not None
    
    @staticmethod
    def exists_by_email(email: str) -> bool:
        """Check if email exists"""
        return User.query.filter_by(email=email).first() is not None

