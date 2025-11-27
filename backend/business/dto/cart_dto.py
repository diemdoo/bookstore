"""
Cart Data Transfer Object
"""
from datetime import datetime
from typing import Optional
from .book_dto import BookDTO


class CartDTO:
    """Data Transfer Object for Cart"""
    
    def __init__(self, id: int = None, user_id: int = None, book_id: int = None,
                 quantity: int = 1, book: Optional[BookDTO] = None,
                 created_at: Optional[datetime] = None):
        self.id = id
        self.user_id = user_id
        self.book_id = book_id
        self.quantity = quantity
        self.book = book
        self.created_at = created_at
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'book': self.book.to_dict() if self.book else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_model(cls, cart_model):
        """Create DTO from SQLAlchemy model"""
        return cls(
            id=cart_model.id,
            user_id=cart_model.user_id,
            book_id=cart_model.book_id,
            quantity=cart_model.quantity,
            book=BookDTO.from_model(cart_model.book) if cart_model.book else None,
            created_at=cart_model.created_at
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create DTO from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            book_id=data.get('book_id'),
            quantity=data.get('quantity', 1),
            book=BookDTO.from_dict(data['book']) if data.get('book') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None
        )

