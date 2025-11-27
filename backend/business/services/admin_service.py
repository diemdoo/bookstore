"""
Admin Business Service
"""
from typing import Dict, Optional, Tuple, List
from data.user_dao import UserDAO
from data.order_dao import OrderDAO
from data.book_dao import BookDAO
from business.dto.user_dto import UserDTO
from business.dto.order_dto import OrderDTO
from models import db, Order, Book, OrderItem
from sqlalchemy import func, desc


class AdminService:
    """Business service for admin operations"""
    
    @staticmethod
    def get_all_users() -> Tuple[List[UserDTO], Optional[str]]:
        """
        Get all users
        Returns: (users, error_message)
        """
        try:
            users = UserDAO.get_all()
            user_dtos = [UserDTO.from_model(user) for user in users]
            return user_dtos, None
        except Exception as e:
            return [], f'Lỗi lấy danh sách users: {str(e)}'
    
    @staticmethod
    def update_user_status(user_id: int, is_active: bool) -> Tuple[Optional[UserDTO], Optional[str]]:
        """
        Update user active status
        Returns: (UserDTO, error_message)
        """
        try:
            updated_user = UserDAO.update_status(user_id, is_active)
            if not updated_user:
                return None, 'User không tồn tại'
            
            return UserDTO.from_model(updated_user), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi cập nhật trạng thái user: {str(e)}'
    
    @staticmethod
    def get_all_orders() -> Tuple[List[OrderDTO], Optional[str]]:
        """
        Get all orders
        Returns: (orders, error_message)
        """
        try:
            orders = OrderDAO.get_all()
            order_dtos = [OrderDTO.from_model(order) for order in orders]
            return order_dtos, None
        except Exception as e:
            return [], f'Lỗi lấy danh sách đơn hàng: {str(e)}'
    
    @staticmethod
    def get_statistics() -> Tuple[Optional[Dict], Optional[str]]:
        """
        Get admin statistics
        Returns: (statistics_dict, error_message)
        """
        try:
            # Total revenue (from completed and paid orders)
            total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
                Order.status == 'completed',
                Order.payment_status == 'paid'
            ).scalar() or 0
            
            # Total orders
            total_orders = Order.query.count()
            
            # Orders by status
            orders_by_status = db.session.query(
                Order.status,
                func.count(Order.id)
            ).group_by(Order.status).all()
            
            # Convert to dict for easy access
            orders_by_status_dict = {status: count for status, count in orders_by_status}
            
            # Individual order counts
            pending_orders = orders_by_status_dict.get('pending', 0)
            confirmed_orders = orders_by_status_dict.get('confirmed', 0)
            completed_orders = orders_by_status_dict.get('completed', 0)
            cancelled_orders = orders_by_status_dict.get('cancelled', 0)
            
            # Top selling books (top 10)
            top_books = db.session.query(
                Book.id,
                Book.title,
                Book.author,
                Book.image_url,
                func.sum(OrderItem.quantity).label('total_sold')
            ).join(OrderItem).join(Order).filter(
                Order.status == 'completed'
            ).group_by(Book.id, Book.title, Book.author, Book.image_url).order_by(
                desc('total_sold')
            ).limit(10).all()
            
            statistics = {
                'total_revenue': float(total_revenue),
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'confirmed_orders': confirmed_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'orders_by_status': orders_by_status_dict,
                'top_books': [
                    {
                        'id': book_id,
                        'title': title,
                        'author': author,
                        'image_url': image_url,
                        'total_sold': int(total_sold)
                    }
                    for book_id, title, author, image_url, total_sold in top_books
                ]
            }
            
            return statistics, None
            
        except Exception as e:
            return None, f'Lỗi lấy thống kê: {str(e)}'

