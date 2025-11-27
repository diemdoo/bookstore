"""
Routes cho quản lý admin
"""
from flask import Blueprint, request, jsonify
from business.services.admin_service import AdminService
from business.services.order_service import OrderService
from utils.helpers import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """
    Lấy danh sách tất cả users
    """
    try:
        # Call business service
        users, error = AdminService.get_all_users()
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách users: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """
    Khóa/mở tài khoản user
    """
    try:
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'Thiếu trường is_active'}), 400
        
        # Call business service
        user_dto, error = AdminService.update_user_status(user_id, bool(is_active))
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 500
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'message': 'Cập nhật trạng thái user thành công',
            'user': user_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi cập nhật trạng thái user: {str(e)}'}), 500

@admin_bp.route('/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """
    Lấy tất cả đơn hàng
    """
    try:
        # Call business service
        orders, error = AdminService.get_all_orders()
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách đơn hàng: {str(e)}'}), 500

@admin_bp.route('/admin/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """
    Cập nhật trạng thái đơn hàng và payment_status
    """
    try:
        data = request.get_json()
        status = data.get('status')
        payment_status = data.get('payment_status')
        
        # Call business service
        order_dto, error = OrderService.update_order_status(order_id, status, payment_status)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'message': 'Cập nhật trạng thái đơn hàng thành công',
            'order': order_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi cập nhật trạng thái đơn hàng: {str(e)}'}), 500

@admin_bp.route('/admin/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """
    Lấy thống kê (doanh thu, số đơn hàng, sách bán chạy)
    """
    try:
        # Call business service
        statistics, error = AdminService.get_statistics()
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy thống kê: {str(e)}'}), 500
