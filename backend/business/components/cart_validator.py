"""
Cart Business Validator
"""
from typing import Dict, Optional, Tuple
from data.book_dao import BookDAO
from data.cart_dao import CartDAO


class CartValidator:
    """Business rules validator for Cart operations"""
    
    @staticmethod
    def validate_add_to_cart(user_id: int, book_id: int, quantity: int) -> Tuple[bool, Optional[str]]:
        """
        Validate adding item to cart
        Returns: (is_valid, error_message)
        """
        # Validate quantity
        if quantity <= 0:
            return False, 'Số lượng phải lớn hơn 0'
        
        # Check if book exists
        book = BookDAO.get_by_id(book_id)
        if not book:
            return False, 'Sách không tồn tại'
        
        # Check current cart quantity
        existing_cart = CartDAO.get_by_user_and_book(user_id, book_id)
        current_quantity = existing_cart.quantity if existing_cart else 0
        total_quantity = current_quantity + quantity
        
        # Validate stock availability
        if book.stock < total_quantity:
            return False, f'Số lượng sách không đủ (còn {book.stock} cuốn)'
        
        return True, None
    
    @staticmethod
    def validate_update_quantity(user_id: int, cart_id: int, quantity: int) -> Tuple[bool, Optional[str]]:
        """
        Validate updating cart item quantity
        Returns: (is_valid, error_message)
        """
        # Validate quantity
        if quantity <= 0:
            return False, 'Số lượng phải lớn hơn 0'
        
        # Check if cart item exists and belongs to user
        cart_item = CartDAO.get_by_id(cart_id)
        if not cart_item:
            return False, 'Mục giỏ hàng không tồn tại'
        
        if cart_item.user_id != user_id:
            return False, 'Không có quyền cập nhật mục giỏ hàng này'
        
        # Check stock availability
        book = BookDAO.get_by_id(cart_item.book_id)
        if not book:
            return False, 'Sách không tồn tại'
        
        if book.stock < quantity:
            return False, f'Số lượng sách không đủ (còn {book.stock} cuốn)'
        
        return True, None
    
    @staticmethod
    def validate_remove_from_cart(user_id: int, cart_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validate removing item from cart
        Returns: (is_valid, error_message)
        """
        # Check if cart item exists and belongs to user
        cart_item = CartDAO.get_by_id(cart_id)
        if not cart_item:
            return False, 'Mục giỏ hàng không tồn tại'
        
        if cart_item.user_id != user_id:
            return False, 'Không có quyền xóa mục giỏ hàng này'
        
        return True, None

