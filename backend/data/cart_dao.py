"""
Cart Data Access Object
"""
from models import db, Cart, Book
from business.dto.cart_dto import CartDTO
from typing import Optional, List


class CartDAO:
    """Data Access Object for Cart operations"""
    
    @staticmethod
    def get_by_user_id(user_id: int) -> List[Cart]:
        """Get all cart items for a user"""
        return Cart.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_by_id(cart_id: int) -> Optional[Cart]:
        """Get cart item by ID"""
        return Cart.query.get(cart_id)
    
    @staticmethod
    def get_by_user_and_book(user_id: int, book_id: int) -> Optional[Cart]:
        """Get cart item by user and book"""
        return Cart.query.filter_by(user_id=user_id, book_id=book_id).first()
    
    @staticmethod
    def create(user_id: int, book_id: int, quantity: int = 1) -> Cart:
        """Create a new cart item"""
        new_cart = Cart(
            user_id=user_id,
            book_id=book_id,
            quantity=quantity
        )
        db.session.add(new_cart)
        db.session.commit()
        return new_cart
    
    @staticmethod
    def update_quantity(cart_id: int, quantity: int) -> Optional[Cart]:
        """Update cart item quantity"""
        cart_item = Cart.query.get(cart_id)
        if cart_item:
            cart_item.quantity = quantity
            db.session.commit()
        return cart_item
    
    @staticmethod
    def delete(cart_id: int) -> bool:
        """Delete a cart item"""
        cart_item = Cart.query.get(cart_id)
        if cart_item:
            db.session.delete(cart_item)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def delete_by_user_id(user_id: int) -> int:
        """Delete all cart items for a user (returns count deleted)"""
        count = Cart.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return count
    
    @staticmethod
    def get_total_items(user_id: int) -> int:
        """Get total quantity of items in user's cart"""
        result = db.session.query(db.func.sum(Cart.quantity)).filter_by(user_id=user_id).scalar()
        return result or 0

