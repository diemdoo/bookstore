"""
Order Data Access Object
"""
from models import db, Order, OrderItem
from business.dto.order_dto import OrderDTO, OrderItemDTO
from typing import Optional, List
from decimal import Decimal


class OrderDAO:
    """Data Access Object for Order operations"""
    
    @staticmethod
    def get_by_id(order_id: int) -> Optional[Order]:
        """Get order by ID"""
        return Order.query.get(order_id)
    
    @staticmethod
    def get_by_user_id(user_id: int) -> List[Order]:
        """Get all orders for a user"""
        return Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def get_by_user_and_id(user_id: int, order_id: int) -> Optional[Order]:
        """Get order by user ID and order ID"""
        return Order.query.filter_by(id=order_id, user_id=user_id).first()
    
    @staticmethod
    def get_all() -> List[Order]:
        """Get all orders with user relationship loaded"""
        from sqlalchemy.orm import joinedload
        return Order.query.options(joinedload(Order.user)).order_by(Order.created_at.desc()).all()
    
    @staticmethod
    def create(user_id: int, total_amount: Decimal, shipping_address: str,
               status: str = 'pending', payment_status: str = 'pending') -> Order:
        """Create a new order"""
        new_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status=status,
            payment_status=payment_status,
            shipping_address=shipping_address
        )
        db.session.add(new_order)
        db.session.flush()  # To get order.id
        return new_order
    
    @staticmethod
    def update_status(order_id: int, status: Optional[str] = None,
                     payment_status: Optional[str] = None) -> Optional[Order]:
        """Update order status and/or payment_status"""
        order = Order.query.get(order_id)
        if order:
            if status:
                order.status = status
            if payment_status:
                order.payment_status = payment_status
            db.session.commit()
        return order
    
    @staticmethod
    def commit():
        """Commit database session"""
        db.session.commit()


class OrderItemDAO:
    """Data Access Object for OrderItem operations"""
    
    @staticmethod
    def create(order_id: int, book_id: int, quantity: int, price: Decimal) -> OrderItem:
        """Create a new order item"""
        new_order_item = OrderItem(
            order_id=order_id,
            book_id=book_id,
            quantity=quantity,
            price=price
        )
        db.session.add(new_order_item)
        return new_order_item
    
    @staticmethod
    def get_by_order_id(order_id: int) -> List[OrderItem]:
        """Get all order items for an order"""
        return OrderItem.query.filter_by(order_id=order_id).all()

