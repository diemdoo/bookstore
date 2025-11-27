"""
Order Data Transfer Objects
"""
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from .book_dto import BookDTO


class OrderItemDTO:
    """Data Transfer Object for OrderItem"""
    
    def __init__(self, id: int = None, order_id: int = None, book_id: int = None,
                 quantity: int = None, price: Optional[Decimal] = None,
                 book: Optional[BookDTO] = None):
        self.id = id
        self.order_id = order_id
        self.book_id = book_id
        self.quantity = quantity
        self.price = price
        self.book = book
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else None,
            'book': self.book.to_dict() if self.book else None
        }
    
    @classmethod
    def from_model(cls, order_item_model):
        """Create DTO from SQLAlchemy model"""
        return cls(
            id=order_item_model.id,
            order_id=order_item_model.order_id,
            book_id=order_item_model.book_id,
            quantity=order_item_model.quantity,
            price=order_item_model.price,
            book=BookDTO.from_model(order_item_model.book) if order_item_model.book else None
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create DTO from dictionary"""
        return cls(
            id=data.get('id'),
            order_id=data.get('order_id'),
            book_id=data.get('book_id'),
            quantity=data.get('quantity'),
            price=Decimal(str(data['price'])) if data.get('price') else None,
            book=BookDTO.from_dict(data['book']) if data.get('book') else None
        )


class OrderDTO:
    """Data Transfer Object for Order"""
    
    def __init__(self, id: int = None, user_id: int = None,
                 total_amount: Optional[Decimal] = None, status: str = 'pending',
                 payment_status: str = 'pending', shipping_address: str = None,
                 order_items: Optional[List[OrderItemDTO]] = None,
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None,
                 customer_code: Optional[str] = None,
                 customer_username: Optional[str] = None,
                 customer_full_name: Optional[str] = None):
        self.id = id
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status
        self.payment_status = payment_status
        self.shipping_address = shipping_address
        self.order_items = order_items or []
        self.created_at = created_at
        self.updated_at = updated_at
        self.customer_code = customer_code
        self.customer_username = customer_username
        self.customer_full_name = customer_full_name
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount) if self.total_amount else None,
            'status': self.status,
            'payment_status': self.payment_status,
            'shipping_address': self.shipping_address,
            'order_items': [item.to_dict() for item in self.order_items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'customer_code': self.customer_code,
            'customer_username': self.customer_username,
            'customer_full_name': self.customer_full_name
        }
    
    @classmethod
    def from_model(cls, order_model):
        """Create DTO from SQLAlchemy model"""
        # Access user relationship if available
        user = order_model.user if hasattr(order_model, 'user') and order_model.user else None
        
        return cls(
            id=order_model.id,
            user_id=order_model.user_id,
            total_amount=order_model.total_amount,
            status=order_model.status,
            payment_status=order_model.payment_status,
            shipping_address=order_model.shipping_address,
            order_items=[OrderItemDTO.from_model(item) for item in order_model.order_items],
            created_at=order_model.created_at,
            updated_at=order_model.updated_at,
            customer_code=user.customer_code if user else None,
            customer_username=user.username if user else None,
            customer_full_name=user.full_name if user else None
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create DTO from dictionary"""
        return cls(
            id=data.get('id'),
            user_id=data.get('user_id'),
            total_amount=Decimal(str(data['total_amount'])) if data.get('total_amount') else None,
            status=data.get('status', 'pending'),
            payment_status=data.get('payment_status', 'pending'),
            shipping_address=data.get('shipping_address'),
            order_items=[OrderItemDTO.from_dict(item) for item in data.get('order_items', [])],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None,
            customer_code=data.get('customer_code'),
            customer_username=data.get('customer_username'),
            customer_full_name=data.get('customer_full_name')
        )

