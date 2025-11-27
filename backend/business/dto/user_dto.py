"""
User Data Transfer Object
"""
from datetime import datetime
from typing import Optional


class UserDTO:
    """Data Transfer Object for User"""
    
    def __init__(self, id: int = None, username: str = None, email: str = None,
                 full_name: Optional[str] = None, role: str = 'customer',
                 is_active: bool = True, created_at: Optional[datetime] = None,
                 customer_code: Optional[str] = None):
        self.id = id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role
        self.is_active = is_active
        self.customer_code = customer_code
        self.created_at = created_at
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'customer_code': self.customer_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_model(cls, user_model):
        """Create DTO from SQLAlchemy model"""
        return cls(
            id=user_model.id,
            username=user_model.username,
            email=user_model.email,
            full_name=user_model.full_name,
            role=user_model.role,
            is_active=user_model.is_active,
            customer_code=user_model.customer_code,
            created_at=user_model.created_at
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create DTO from dictionary"""
        return cls(
            id=data.get('id'),
            username=data.get('username'),
            email=data.get('email'),
            full_name=data.get('full_name'),
            role=data.get('role', 'customer'),
            is_active=data.get('is_active', True),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

