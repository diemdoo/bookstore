"""
Order Business Validator
"""
from typing import Dict, Optional, List, Tuple
from data.cart_dao import CartDAO
from data.book_dao import BookDAO


class OrderValidator:
    """Business rules validator for Order operations"""
    
    VALID_STATUSES = ['pending', 'confirmed', 'cancelled', 'completed']
    VALID_PAYMENT_STATUSES = ['pending', 'paid']
    
    @staticmethod
    def validate_create(user_id: int, shipping_address: str) -> Tuple[bool, Optional[str]]:
        """
        Validate order creation
        Returns: (is_valid, error_message)
        """
        # Validate shipping address
        if not shipping_address or not shipping_address.strip():
            return False, 'Vui lòng nhập địa chỉ giao hàng'
        
        if len(shipping_address.strip()) < 10:
            return False, 'Địa chỉ giao hàng phải có ít nhất 10 ký tự'
        
        # Check if cart is not empty
        cart_items = CartDAO.get_by_user_id(user_id)
        if not cart_items:
            return False, 'Giỏ hàng trống'
        
        # Validate stock for each cart item
        for cart_item in cart_items:
            book = BookDAO.get_by_id(cart_item.book_id)
            if not book:
                return False, f'Sách với ID {cart_item.book_id} không tồn tại'
            
            if book.stock < cart_item.quantity:
                return False, f'Sách "{book.title}" không đủ số lượng (còn {book.stock} cuốn)'
        
        return True, None
    
    @staticmethod
    def validate_status(status: str) -> Tuple[bool, Optional[str]]:
        """
        Validate order status
        Returns: (is_valid, error_message)
        """
        if status not in OrderValidator.VALID_STATUSES:
            return False, f'Trạng thái không hợp lệ. Phải là một trong: {", ".join(OrderValidator.VALID_STATUSES)}'
        return True, None
    
    @staticmethod
    def validate_payment_status(payment_status: str) -> Tuple[bool, Optional[str]]:
        """
        Validate payment status
        Returns: (is_valid, error_message)
        """
        if payment_status not in OrderValidator.VALID_PAYMENT_STATUSES:
            return False, f'Trạng thái thanh toán không hợp lệ. Phải là một trong: {", ".join(OrderValidator.VALID_PAYMENT_STATUSES)}'
        return True, None
    
    @staticmethod
    def validate_update_status(status: Optional[str] = None,
                              payment_status: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """
        Validate order status update
        Returns: (is_valid, error_message)
        """
        if status:
            is_valid, error = OrderValidator.validate_status(status)
            if not is_valid:
                return False, error
        
        if payment_status:
            is_valid, error = OrderValidator.validate_payment_status(payment_status)
            if not is_valid:
                return False, error
        
        return True, None

