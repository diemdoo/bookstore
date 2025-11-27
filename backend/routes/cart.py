"""
Routes cho quản lý giỏ hàng
"""
from flask import Blueprint, request, jsonify, session
from business.services.cart_service import CartService
from utils.helpers import login_required

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart', methods=['GET'])
@login_required
def get_cart():
    """
    Lấy giỏ hàng của user hiện tại
    """
    try:
        user_id = session['user_id']
        
        # Call business service
        cart_items, total_items = CartService.get_cart(user_id)
        
        return jsonify({
            'cart': [item.to_dict() for item in cart_items],
            'total_items': total_items
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy giỏ hàng: {str(e)}'}), 500

@cart_bp.route('/cart', methods=['POST'])
@login_required
def add_to_cart():
    """
    Thêm sách vào giỏ hàng
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        book_id = data.get('book_id')
        quantity = data.get('quantity', 1)
        
        if not book_id:
            return jsonify({'error': 'Thiếu book_id'}), 400
        
        # Call business service
        cart_dto, error = CartService.add_to_cart(user_id, book_id, quantity)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'message': 'Thêm vào giỏ hàng thành công',
            'cart_item': cart_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi thêm vào giỏ hàng: {str(e)}'}), 500

@cart_bp.route('/cart/<int:cart_id>', methods=['PUT'])
@login_required
def update_cart_item(cart_id):
    """
    Cập nhật số lượng sách trong giỏ hàng
    """
    try:
        user_id = session['user_id']
        data = request.get_json()
        quantity = data.get('quantity')
        
        if quantity is None:
            return jsonify({'error': 'Thiếu quantity'}), 400
        
        # Call business service
        cart_dto, error = CartService.update_cart_item(user_id, cart_id, quantity)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'message': 'Cập nhật giỏ hàng thành công',
            'cart_item': cart_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi cập nhật giỏ hàng: {str(e)}'}), 500

@cart_bp.route('/cart/<int:cart_id>', methods=['DELETE'])
@login_required
def remove_from_cart(cart_id):
    """
    Xóa sách khỏi giỏ hàng
    """
    try:
        user_id = session['user_id']
        
        # Call business service
        success, error = CartService.remove_from_cart(user_id, cart_id)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({'message': 'Xóa khỏi giỏ hàng thành công'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi xóa khỏi giỏ hàng: {str(e)}'}), 500
