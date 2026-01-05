from flask import Blueprint, request, jsonify, session
from models import Cart, Book, db
from utils.helpers import login_required

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart', methods=['GET'])
@login_required
def get_cart():
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Query tất cả cart items của user
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        
        # Bước 3: Tính tổng số lượng items
        total_items = sum(item.quantity for item in cart_items)
        
        # Bước 4: Trả về danh sách cart items
        return jsonify({
            'cart': [item.to_dict() for item in cart_items],
            'total_items': total_items
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy giỏ hàng: {str(e)}'}), 500

@cart_bp.route('/cart', methods=['POST'])
@login_required
def add_to_cart():
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Lấy dữ liệu từ request
        data = request.get_json()
        book_id = data.get('book_id')
        # Handle None case: if quantity is None or missing, default to 1
        quantity = data.get('quantity')
        if quantity is None:
            quantity = 1
        else:
            # Convert to int if it's a string or ensure it's an integer
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                return jsonify({'error': 'Số lượng phải là số nguyên hợp lệ'}), 400
        
        # Bước 3: Validate dữ liệu
        if not book_id:
            return jsonify({'error': 'Thiếu book_id'}), 400
        
        if quantity <= 0:
            return jsonify({'error': 'Số lượng phải lớn hơn 0'}), 400
        
        # Bước 4: Kiểm tra sách có tồn tại không
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Sách không tồn tại'}), 404
        
        # Bước 5: Kiểm tra sách đã có trong giỏ chưa
        existing_cart = Cart.query.filter_by(user_id=user_id, book_id=book_id).first()
        
        if existing_cart:
            # Bước 6: Cộng thêm quantity
            new_quantity = existing_cart.quantity + quantity
            
            # Bước 8: Validate stock
            if book.stock < new_quantity:
                return jsonify({'error': f'Số lượng sách không đủ (còn {book.stock} cuốn)'}), 400
            
            # Bước 9: Cập nhật quantity
            existing_cart.quantity = new_quantity
            db.session.commit()
            
            # Bước 10: Trả về thông tin cart item
            return jsonify({
                'message': 'Thêm vào giỏ hàng thành công',
                'cart_item': existing_cart.to_dict()
            }), 200
        else:
            # Bước 7: Tạo cart item mới
            # Bước 8: Validate stock
            if book.stock < quantity:
                return jsonify({'error': f'Số lượng sách không đủ (còn {book.stock} cuốn)'}), 400
            
            # Bước 9: Tạo cart item mới
            new_cart = Cart(
                user_id=user_id,
                book_id=book_id,
                quantity=quantity
            )
            db.session.add(new_cart)
            db.session.commit()
            
            # Bước 10: Trả về thông tin cart item
            return jsonify({
                'message': 'Thêm vào giỏ hàng thành công',
                'cart_item': new_cart.to_dict()
            }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi thêm vào giỏ hàng: {str(e)}'}), 500

@cart_bp.route('/cart/<int:cart_id>', methods=['PUT'])
@login_required
def update_cart_item(cart_id):
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Lấy dữ liệu từ request
        data = request.get_json()
        quantity = data.get('quantity')
        
        # Bước 3: Validate dữ liệu
        if quantity is None:
            return jsonify({'error': 'Thiếu quantity'}), 400
        
        if quantity <= 0:
            return jsonify({'error': 'Số lượng phải lớn hơn 0'}), 400
        
        # Bước 4: Kiểm tra cart item có tồn tại không
        cart_item = Cart.query.get(cart_id)
        if not cart_item:
            return jsonify({'error': 'Mục giỏ hàng không tồn tại'}), 404
        
        # Bước 5: Kiểm tra cart item có thuộc về user không
        if cart_item.user_id != user_id:
            return jsonify({'error': 'Không có quyền cập nhật mục giỏ hàng này'}), 403
        
        # Bước 6: Lấy thông tin sách
        book = Book.query.get(cart_item.book_id)
        if not book:
            return jsonify({'error': 'Sách không tồn tại'}), 404
        
        # Bước 7: Validate stock
        if book.stock < quantity:
            return jsonify({'error': f'Số lượng sách không đủ (còn {book.stock} cuốn)'}), 400
        
        # Bước 8 & 9: Cập nhật quantity và lưu
        cart_item.quantity = quantity
        db.session.commit()
        
        # Bước 10: Trả về thông tin cart item
        return jsonify({
            'message': 'Cập nhật giỏ hàng thành công',
            'cart_item': cart_item.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật giỏ hàng: {str(e)}'}), 500

@cart_bp.route('/cart/<int:cart_id>', methods=['DELETE'])
@login_required
def remove_from_cart(cart_id):
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Kiểm tra cart item có tồn tại không
        cart_item = Cart.query.get(cart_id)
        if not cart_item:
            return jsonify({'error': 'Mục giỏ hàng không tồn tại'}), 404
        
        # Bước 3: Kiểm tra cart item có thuộc về user không
        if cart_item.user_id != user_id:
            return jsonify({'error': 'Không có quyền xóa mục giỏ hàng này'}), 403
        
        # Bước 4: Xóa cart item
        db.session.delete(cart_item)
        db.session.commit()
        
        # Bước 5: Trả về thông báo thành công
        return jsonify({'message': 'Xóa khỏi giỏ hàng thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi xóa khỏi giỏ hàng: {str(e)}'}), 500
