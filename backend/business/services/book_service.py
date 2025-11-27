"""
Book Business Service
"""
from typing import Dict, Optional, Tuple, List
from data.book_dao import BookDAO
from business.dto.book_dto import BookDTO
from business.components.book_validator import BookValidator
from models import db


class BookService:
    """Business service for book operations"""
    
    @staticmethod
    def get_books(page: int = 1, per_page: int = 12, search: str = '',
                 category: str = '', author: str = '') -> Tuple[List[BookDTO], int, int]:
        """
        Get books with pagination and filters
        Returns: (books, total, pages)
        """
        try:
            books, total, pages = BookDAO.search(page, per_page, search, category, author)
            book_dtos = [BookDTO.from_model(book) for book in books]
            return book_dtos, total, pages
        except Exception as e:
            return [], 0, 0
    
    @staticmethod
    def get_book(book_id: int) -> Tuple[Optional[BookDTO], Optional[str]]:
        """
        Get book by ID
        Returns: (BookDTO, error_message)
        """
        try:
            book = BookDAO.get_by_id(book_id)
            if not book:
                return None, 'Sách không tồn tại'
            
            return BookDTO.from_model(book), None
            
        except Exception as e:
            return None, f'Lỗi lấy chi tiết sách: {str(e)}'
    
    @staticmethod
    def create_book(data: Dict) -> Tuple[Optional[BookDTO], Optional[str]]:
        """
        Create a new book
        Returns: (BookDTO, error_message)
        """
        try:
            # Validate data
            is_valid, error = BookValidator.validate_create(data)
            if not is_valid:
                return None, error
            
            # Create book
            new_book = BookDAO.create(
                title=data['title'],
                author=data['author'],
                category=data['category'],
                price=float(data['price']),
                stock=int(data['stock']),
                description=data.get('description'),
                image_url=data.get('image_url'),
                publisher=data.get('publisher'),
                publish_date=data.get('publish_date'),
                distributor=data.get('distributor'),
                dimensions=data.get('dimensions'),
                pages=data.get('pages'),
                weight=data.get('weight')
            )
            
            return BookDTO.from_model(new_book), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi tạo sách: {str(e)}'
    
    @staticmethod
    def update_book(book_id: int, data: Dict) -> Tuple[Optional[BookDTO], Optional[str]]:
        """
        Update book
        Returns: (BookDTO, error_message)
        """
        try:
            # Check if book exists
            book = BookDAO.get_by_id(book_id)
            if not book:
                return None, 'Sách không tồn tại'
            
            # Validate data
            is_valid, error = BookValidator.validate_update(data)
            if not is_valid:
                return None, error
            
            # Update book
            updated_book = BookDAO.update(book_id, **data)
            
            return BookDTO.from_model(updated_book), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi cập nhật sách: {str(e)}'
    
    @staticmethod
    def delete_book(book_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete book
        Returns: (success, error_message)
        """
        try:
            success = BookDAO.delete(book_id)
            if not success:
                return False, 'Sách không tồn tại'
            
            return True, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Lỗi xóa sách: {str(e)}'

