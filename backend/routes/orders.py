"""
Routes cho quản lý đơn hàng (COD)
"""
from flask import Blueprint, request, jsonify, session
from business.services.order_service import OrderService
from utils.helpers import login_required

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """
    Lấy lịch sử đơn hàng của user hiện tại
    """
    try:
        user_id = session['user_id']
        
        # Call business service
        orders, error = OrderService.get_orders(user_id)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy lịch sử đơn hàng: {str(e)}'}), 500

@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """
    Tạo đơn hàng COD (chỉ cần shipping_address)
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        shipping_address = data.get('shipping_address', '').strip()
        
        # Call business service
        order_dto, error = OrderService.create_order(user_id, shipping_address)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Đơn hàng đã được đặt thành công! Bạn sẽ thanh toán khi nhận hàng.',
            'order': order_dto.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi tạo đơn hàng: {str(e)}'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """
    Lấy chi tiết đơn hàng
    """
    try:
        user_id = session['user_id']
        
        # Call business service
        order_dto, error = OrderService.get_order(user_id, order_id)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 500
            return jsonify({'error': error}), status_code
        
        return jsonify({'order': order_dto.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy chi tiết đơn hàng: {str(e)}'}), 500
