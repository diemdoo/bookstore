"""
Cart Business Service
"""
from typing import Dict, Optional, Tuple, List
from data.cart_dao import CartDAO
from data.book_dao import BookDAO
from business.dto.cart_dto import CartDTO
from business.components.cart_validator import CartValidator
from models import db


class CartService:
    """Business service for cart operations"""
    
    @staticmethod
    def get_cart(user_id: int) -> Tuple[List[CartDTO], int]:
        """
        Get user's cart
        Returns: (cart_items, total_items)
        """
        try:
            cart_items = CartDAO.get_by_user_id(user_id)
            cart_dtos = [CartDTO.from_model(item) for item in cart_items]
            total_items = CartDAO.get_total_items(user_id)
            return cart_dtos, total_items
        except Exception as e:
            return [], 0
    
    @staticmethod
    def add_to_cart(user_id: int, book_id: int, quantity: int = 1) -> Tuple[Optional[CartDTO], Optional[str]]:
        """
        Add item to cart
        Returns: (CartDTO, error_message)
        """
        try:
            # Validate
            is_valid, error = CartValidator.validate_add_to_cart(user_id, book_id, quantity)
            if not is_valid:
                return None, error
            
            # Check if item already exists in cart
            existing_cart = CartDAO.get_by_user_and_book(user_id, book_id)
            
            if existing_cart:
                # Update quantity
                new_quantity = existing_cart.quantity + quantity
                updated_cart = CartDAO.update_quantity(existing_cart.id, new_quantity)
                return CartDTO.from_model(updated_cart), None
            else:
                # Create new cart item
                new_cart = CartDAO.create(user_id, book_id, quantity)
                return CartDTO.from_model(new_cart), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi thêm vào giỏ hàng: {str(e)}'
    
    @staticmethod
    def update_cart_item(user_id: int, cart_id: int, quantity: int) -> Tuple[Optional[CartDTO], Optional[str]]:
        """
        Update cart item quantity
        Returns: (CartDTO, error_message)
        """
        try:
            # Validate
            is_valid, error = CartValidator.validate_update_quantity(user_id, cart_id, quantity)
            if not is_valid:
                return None, error
            
            # Update cart item
            updated_cart = CartDAO.update_quantity(cart_id, quantity)
            return CartDTO.from_model(updated_cart), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi cập nhật giỏ hàng: {str(e)}'
    
    @staticmethod
    def remove_from_cart(user_id: int, cart_id: int) -> Tuple[bool, Optional[str]]:
        """
        Remove item from cart
        Returns: (success, error_message)
        """
        try:
            # Validate
            is_valid, error = CartValidator.validate_remove_from_cart(user_id, cart_id)
            if not is_valid:
                return False, error
            
            # Delete cart item
            success = CartDAO.delete(cart_id)
            return success, None
            
        except Exception as e:
            db.session.rollback()
            return False, f'Lỗi xóa khỏi giỏ hàng: {str(e)}'

