"""
Order Business Service
"""
from typing import Dict, Optional, Tuple, List
from data.order_dao import OrderDAO
from business.dto.order_dto import OrderDTO
from business.components.order_validator import OrderValidator
from business.workflows.order_workflow import OrderWorkflow
from models import db


class OrderService:
    """Business service for order operations"""
    
    @staticmethod
    def get_orders(user_id: int) -> Tuple[List[OrderDTO], Optional[str]]:
        """
        Get user's orders
        Returns: (orders, error_message)
        """
        try:
            orders = OrderDAO.get_by_user_id(user_id)
            order_dtos = [OrderDTO.from_model(order) for order in orders]
            return order_dtos, None
        except Exception as e:
            return [], f'Lỗi lấy lịch sử đơn hàng: {str(e)}'
    
    @staticmethod
    def get_order(user_id: int, order_id: int) -> Tuple[Optional[OrderDTO], Optional[str]]:
        """
        Get order by ID (for user)
        Returns: (OrderDTO, error_message)
        """
        try:
            order = OrderDAO.get_by_user_and_id(user_id, order_id)
            if not order:
                return None, 'Đơn hàng không tồn tại'
            
            return OrderDTO.from_model(order), None
            
        except Exception as e:
            return None, f'Lỗi lấy chi tiết đơn hàng: {str(e)}'
    
    @staticmethod
    def create_order(user_id: int, shipping_address: str) -> Tuple[Optional[OrderDTO], Optional[str]]:
        """
        Create a new order
        Returns: (OrderDTO, error_message)
        """
        order_dto, error = OrderWorkflow.create_order(user_id, shipping_address)
        if error:
            return None, error
        
        return order_dto, None
    
    @staticmethod
    def update_order_status(order_id: int, status: Optional[str] = None,
                           payment_status: Optional[str] = None) -> Tuple[Optional[OrderDTO], Optional[str]]:
        """
        Update order status (admin only)
        Returns: (OrderDTO, error_message)
        """
        try:
            # Validate
            is_valid, error = OrderValidator.validate_update_status(status, payment_status)
            if not is_valid:
                return None, error
            
            # Update order
            updated_order = OrderDAO.update_status(order_id, status, payment_status)
            if not updated_order:
                return None, 'Đơn hàng không tồn tại'
            
            return OrderDTO.from_model(updated_order), None
            
        except Exception as e:
            db.session.rollback()
            return None, f'Lỗi cập nhật trạng thái đơn hàng: {str(e)}'

