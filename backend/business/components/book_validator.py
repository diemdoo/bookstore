"""
Book Business Validator
"""
from typing import Dict, Optional, Tuple, List
from decimal import Decimal


class BookValidator:
    """Business rules validator for Book operations"""
    
    REQUIRED_FIELDS = ['title', 'author', 'category', 'price', 'stock']
    
    @staticmethod
    def validate_create(data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate book creation data
        Returns: (is_valid, error_message)
        """
        # Check required fields
        for field in BookValidator.REQUIRED_FIELDS:
            if field not in data or not data[field]:
                return False, f'Thiếu trường {field}'
        
        # Validate title
        title = data.get('title', '').strip()
        if not title or len(title) < 1:
            return False, 'Tiêu đề sách không được để trống'
        if len(title) > 200:
            return False, 'Tiêu đề sách không được vượt quá 200 ký tự'
        
        # Validate author
        author = data.get('author', '').strip()
        if not author or len(author) < 1:
            return False, 'Tác giả không được để trống'
        if len(author) > 100:
            return False, 'Tên tác giả không được vượt quá 100 ký tự'
        
        # Validate category
        category = data.get('category', '').strip()
        if not category or len(category) < 1:
            return False, 'Thể loại không được để trống'
        if len(category) > 50:
            return False, 'Thể loại không được vượt quá 50 ký tự'
        
        # Validate price
        try:
            price = float(data.get('price', 0))
            if price < 0:
                return False, 'Giá sách phải lớn hơn hoặc bằng 0'
        except (ValueError, TypeError):
            return False, 'Giá sách không hợp lệ'
        
        # Validate stock
        try:
            stock = int(data.get('stock', 0))
            if stock < 0:
                return False, 'Số lượng tồn kho phải lớn hơn hoặc bằng 0'
        except (ValueError, TypeError):
            return False, 'Số lượng tồn kho không hợp lệ'
        
        # Validate optional fields
        if 'pages' in data and data['pages']:
            try:
                pages = int(data['pages'])
                if pages < 0:
                    return False, 'Số trang phải lớn hơn hoặc bằng 0'
            except (ValueError, TypeError):
                return False, 'Số trang không hợp lệ'
        
        if 'weight' in data and data['weight']:
            try:
                weight = int(data['weight'])
                if weight < 0:
                    return False, 'Trọng lượng phải lớn hơn hoặc bằng 0'
            except (ValueError, TypeError):
                return False, 'Trọng lượng không hợp lệ'
        
        return True, None
    
    @staticmethod
    def validate_update(data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Validate book update data
        Returns: (is_valid, error_message)
        """
        # Validate title if provided
        if 'title' in data:
            title = data.get('title', '').strip()
            if title and len(title) > 200:
                return False, 'Tiêu đề sách không được vượt quá 200 ký tự'
        
        # Validate author if provided
        if 'author' in data:
            author = data.get('author', '').strip()
            if author and len(author) > 100:
                return False, 'Tên tác giả không được vượt quá 100 ký tự'
        
        # Validate category if provided
        if 'category' in data:
            category = data.get('category', '').strip()
            if category and len(category) > 50:
                return False, 'Thể loại không được vượt quá 50 ký tự'
        
        # Validate price if provided
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return False, 'Giá sách phải lớn hơn hoặc bằng 0'
            except (ValueError, TypeError):
                return False, 'Giá sách không hợp lệ'
        
        # Validate stock if provided
        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    return False, 'Số lượng tồn kho phải lớn hơn hoặc bằng 0'
            except (ValueError, TypeError):
                return False, 'Số lượng tồn kho không hợp lệ'
        
        # Validate optional fields
        if 'pages' in data and data['pages']:
            try:
                pages = int(data['pages'])
                if pages < 0:
                    return False, 'Số trang phải lớn hơn hoặc bằng 0'
            except (ValueError, TypeError):
                return False, 'Số trang không hợp lệ'
        
        if 'weight' in data and data['weight']:
            try:
                weight = int(data['weight'])
                if weight < 0:
                    return False, 'Trọng lượng phải lớn hơn hoặc bằng 0'
            except (ValueError, TypeError):
                return False, 'Trọng lượng không hợp lệ'
        
        return True, None
    
    @staticmethod
    def validate_stock_available(book_stock: int, requested_quantity: int) -> Tuple[bool, Optional[str]]:
        """
        Validate if requested quantity is available in stock
        Returns: (is_available, error_message)
        """
        if requested_quantity <= 0:
            return False, 'Số lượng phải lớn hơn 0'
        
        if book_stock < requested_quantity:
            return False, f'Số lượng sách không đủ (còn {book_stock} cuốn)'
        
        return True, None

