"""
Book Data Transfer Object
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal


class BookDTO:
    """Data Transfer Object for Book"""
    
    def __init__(self, id: int = None, title: str = None, author: str = None,
                 category: str = None, description: Optional[str] = None,
                 price: Optional[Decimal] = None, stock: int = 0,
                 image_url: Optional[str] = None, publisher: Optional[str] = None,
                 publish_date: Optional[str] = None, distributor: Optional[str] = None,
                 dimensions: Optional[str] = None, pages: Optional[int] = None,
                 weight: Optional[int] = None, created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = id
        self.title = title
        self.author = author
        self.category = category
        self.description = description
        self.price = price
        self.stock = stock
        self.image_url = image_url
        self.publisher = publisher
        self.publish_date = publish_date
        self.distributor = distributor
        self.dimensions = dimensions
        self.pages = pages
        self.weight = weight
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self) -> dict:
        """Convert DTO to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'description': self.description,
            'price': float(self.price) if self.price else None,
            'stock': self.stock,
            'image_url': self.image_url,
            'publisher': self.publisher,
            'publish_date': self.publish_date,
            'distributor': self.distributor,
            'dimensions': self.dimensions,
            'pages': self.pages,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def from_model(cls, book_model):
        """Create DTO from SQLAlchemy model"""
        return cls(
            id=book_model.id,
            title=book_model.title,
            author=book_model.author,
            category=book_model.category,
            description=book_model.description,
            price=book_model.price,
            stock=book_model.stock,
            image_url=book_model.image_url,
            publisher=book_model.publisher,
            publish_date=book_model.publish_date,
            distributor=book_model.distributor,
            dimensions=book_model.dimensions,
            pages=book_model.pages,
            weight=book_model.weight,
            created_at=book_model.created_at,
            updated_at=book_model.updated_at
        )
    
    @classmethod
    def from_dict(cls, data: dict):
        """Create DTO from dictionary"""
        return cls(
            id=data.get('id'),
            title=data.get('title'),
            author=data.get('author'),
            category=data.get('category'),
            description=data.get('description'),
            price=Decimal(str(data['price'])) if data.get('price') else None,
            stock=data.get('stock', 0),
            image_url=data.get('image_url'),
            publisher=data.get('publisher'),
            publish_date=data.get('publish_date'),
            distributor=data.get('distributor'),
            dimensions=data.get('dimensions'),
            pages=data.get('pages'),
            weight=data.get('weight'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else None
        )

