"""
Book Data Access Object
"""
from models import db, Book
from business.dto.book_dto import BookDTO
from typing import Optional, List, Tuple
from sqlalchemy import or_


class BookDAO:
    """Data Access Object for Book operations"""
    
    @staticmethod
    def get_by_id(book_id: int) -> Optional[Book]:
        """Get book by ID"""
        return Book.query.get(book_id)
    
    @staticmethod
    def get_all() -> List[Book]:
        """Get all books"""
        return Book.query.all()
    
    @staticmethod
    def search(page: int = 1, per_page: int = 12, search: str = '',
               category: str = '', author: str = '') -> Tuple[List[Book], int, int]:
        """
        Search books with pagination
        Returns: (books, total, pages)
        """
        query = Book.query
        
        # Search by title
        if search:
            query = query.filter(Book.title.ilike(f'%{search}%'))
        
        # Filter by category
        if category:
            query = query.filter(Book.category == category)
        
        # Filter by author
        if author:
            query = query.filter(Book.author.ilike(f'%{author}%'))
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return pagination.items, pagination.total, pagination.pages
    
    @staticmethod
    def create(title: str, author: str, category: str, price: float, stock: int,
               description: Optional[str] = None, image_url: Optional[str] = None,
               publisher: Optional[str] = None, publish_date: Optional[str] = None,
               distributor: Optional[str] = None, dimensions: Optional[str] = None,
               pages: Optional[int] = None, weight: Optional[int] = None) -> Book:
        """Create a new book"""
        new_book = Book(
            title=title.strip(),
            author=author.strip(),
            category=category.strip(),
            description=description.strip() if description else None,
            price=float(price),
            stock=int(stock),
            image_url=image_url.strip() if image_url else None,
            publisher=publisher.strip() if publisher else None,
            publish_date=publish_date.strip() if publish_date else None,
            distributor=distributor.strip() if distributor else None,
            dimensions=dimensions.strip() if dimensions else None,
            pages=int(pages) if pages else None,
            weight=int(weight) if weight else None
        )
        db.session.add(new_book)
        db.session.commit()
        return new_book
    
    @staticmethod
    def update(book_id: int, **kwargs) -> Optional[Book]:
        """Update book fields"""
        book = Book.query.get(book_id)
        if not book:
            return None
        
        # Update fields
        if 'title' in kwargs:
            book.title = kwargs['title'].strip()
        if 'author' in kwargs:
            book.author = kwargs['author'].strip()
        if 'category' in kwargs:
            book.category = kwargs['category'].strip()
        if 'description' in kwargs:
            book.description = kwargs['description'].strip() if kwargs['description'] else None
        if 'price' in kwargs:
            book.price = float(kwargs['price'])
        if 'stock' in kwargs:
            book.stock = int(kwargs['stock'])
        if 'image_url' in kwargs:
            book.image_url = kwargs['image_url'].strip() if kwargs['image_url'] else None
        if 'publisher' in kwargs:
            book.publisher = kwargs['publisher'].strip() if kwargs['publisher'] else None
        if 'publish_date' in kwargs:
            book.publish_date = kwargs['publish_date'].strip() if kwargs['publish_date'] else None
        if 'distributor' in kwargs:
            book.distributor = kwargs['distributor'].strip() if kwargs['distributor'] else None
        if 'dimensions' in kwargs:
            book.dimensions = kwargs['dimensions'].strip() if kwargs['dimensions'] else None
        if 'pages' in kwargs:
            book.pages = int(kwargs['pages']) if kwargs['pages'] else None
        if 'weight' in kwargs:
            book.weight = int(kwargs['weight']) if kwargs['weight'] else None
        
        db.session.commit()
        return book
    
    @staticmethod
    def delete(book_id: int) -> bool:
        """Delete a book"""
        book = Book.query.get(book_id)
        if book:
            db.session.delete(book)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def update_stock(book_id: int, quantity: int) -> Optional[Book]:
        """Update book stock (add or subtract)"""
        book = Book.query.get(book_id)
        if book:
            book.stock += quantity
            db.session.commit()
        return book
    
    @staticmethod
    def get_categories() -> List[str]:
        """Get all unique categories"""
        categories = db.session.query(Book.category).distinct().all()
        return [cat[0] for cat in categories]
    
    @staticmethod
    def get_authors() -> List[str]:
        """Get all unique authors"""
        authors = db.session.query(Book.author).distinct().all()
        return [author[0] for author in authors]

