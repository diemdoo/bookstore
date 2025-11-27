"""
Order Business Workflow
"""
from typing import Dict, Tuple, Optional
from decimal import Decimal
from data.cart_dao import CartDAO
from data.book_dao import BookDAO
from data.order_dao import OrderDAO, OrderItemDAO
from business.components.order_validator import OrderValidator
from business.dto.order_dto import OrderDTO, OrderItemDTO
from models import db


class OrderWorkflow:
    """Business workflow for order creation and processing"""
    
    @staticmethod
    def create_order(user_id: int, shipping_address: str) -> Tuple[Optional[OrderDTO], Optional[str]]:
        """
        Complete workflow for creating an order:
        1. Validate order data
        2. Get cart items
        3. Validate stock for each item
        4. Calculate total amount
        5. Create order
        6. Create order items
        7. Update book stock
        8. Clear cart
        9. Commit transaction
        
        Returns: (OrderDTO, error_message)
        """
        try:
            # Step 1: Validate order creation
            is_valid, error = OrderValidator.validate_create(user_id, shipping_address)
            if not is_valid:
                return None, error
            
            # Step 2: Get cart items
            cart_items = CartDAO.get_by_user_id(user_id)
            
            # Step 3 & 4: Calculate total and prepare order items data
            total_amount = Decimal('0')
            order_items_data = []
            
            for cart_item in cart_items:
                book = BookDAO.get_by_id(cart_item.book_id)
                if not book:
                    db.session.rollback()
                    return None, f'Sách với ID {cart_item.book_id} không tồn tại'
                
                # Validate stock (double check)
                if book.stock < cart_item.quantity:
                    db.session.rollback()
                    return None, f'Sách "{book.title}" không đủ số lượng (còn {book.stock} cuốn)'
                
                # Calculate item total
                item_price = Decimal(str(book.price))
                item_total = item_price * cart_item.quantity
                total_amount += item_total
                
                order_items_data.append({
                    'book_id': book.id,
                    'quantity': cart_item.quantity,
                    'price': item_price
                })
            
            # Step 5: Create order
            new_order = OrderDAO.create(
                user_id=user_id,
                total_amount=total_amount,
                shipping_address=shipping_address.strip(),
                status='pending',
                payment_status='pending'
            )
            
            # Step 6: Create order items and update stock
            for item_data in order_items_data:
                # Create order item
                OrderItemDAO.create(
                    order_id=new_order.id,
                    book_id=item_data['book_id'],
                    quantity=item_data['quantity'],
                    price=item_data['price']
                )
                
                # Step 7: Update book stock
                BookDAO.update_stock(item_data['book_id'], -item_data['quantity'])
            
            # Step 8: Clear cart
            CartDAO.delete_by_user_id(user_id)
            
            # Step 9: Commit transaction
            OrderDAO.commit()
            
            # Convert to DTO
            order_dto = OrderDTO.from_model(new_order)
            
            return order_dto, None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi tạo đơn hàng: {str(e)}'

