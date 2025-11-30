"""
File: routes/orders.py

Mục đích:
Xử lý các route liên quan đến quản lý đơn hàng (tạo đơn, xem lịch sử, chi tiết)

Các endpoint trong file này:
- GET /api/orders: Lấy lịch sử đơn hàng của user hiện tại
- POST /api/orders: Tạo đơn hàng mới (checkout) - có transaction
- GET /api/orders/<id>: Lấy chi tiết đơn hàng

Dependencies:
- models.Order: Model cho bảng orders
- models.OrderItem: Model cho bảng order_items
- models.Cart: Model cho bảng cart
- models.Book: Model cho bảng books (để validate stock)
- utils.helpers: login_required decorator
"""
from flask import Blueprint, request, jsonify, session
from models import Order, OrderItem, Cart, Book, db
from utils.helpers import login_required
from decimal import Decimal

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """
    Lấy lịch sử đơn hàng của user hiện tại
    
    Flow:
    1. Lấy user_id từ session (đã được kiểm tra bởi @login_required)
    2. Query tất cả orders của user, sắp xếp theo created_at giảm dần
    3. Trả về danh sách orders (mỗi order đã có order_items từ relationship)
    
    Returns:
        - 200: Danh sách orders
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Query tất cả orders của user
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
        
        # Bước 3: Trả về danh sách orders
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy lịch sử đơn hàng: {str(e)}'}), 500

@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """
    Tạo đơn hàng mới (checkout) - Sử dụng TRANSACTION để đảm bảo tính nhất quán
    
    Flow chi tiết:
    1. Lấy user_id từ session (đã login)
    2. Lấy shipping_address từ request body
    3. Validate shipping_address không rỗng
    4. BẮT ĐẦU TRANSACTION (db.session.begin())
    5. Lấy tất cả items trong giỏ hàng của user
    6. Kiểm tra giỏ hàng không rỗng
    7. Với mỗi item trong giỏ:
       - Lấy thông tin sách từ database
       - Kiểm tra sách có tồn tại không
       - Kiểm tra stock còn đủ không (stock >= quantity)
       - Tính tiền (price * quantity)
       - Cộng vào tổng tiền
    8. Tạo Order mới với:
       - user_id
       - total_amount
       - shipping_address
       - status = 'pending'
       - payment_status = 'pending'
    9. Với mỗi item trong giỏ:
       - Tạo OrderItem (lưu giá tại thời điểm mua)
       - Giảm stock của sách (stock = stock - quantity)
    10. Xóa tất cả items trong giỏ hàng
    11. COMMIT TRANSACTION (lưu tất cả thay đổi)
    12. Trả về thông tin đơn hàng
    
    Nếu có lỗi ở bất kỳ bước nào (4-11):
    - ROLLBACK TRANSACTION (hủy tất cả thay đổi)
    - Trả về lỗi
    
    Returns:
        - 201: Tạo đơn hàng thành công
        - 400: Giỏ hàng rỗng, không đủ stock, hoặc địa chỉ không hợp lệ
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Lấy shipping_address từ request
        data = request.get_json()
        shipping_address = data.get('shipping_address', '').strip()
        
        # Bước 3: Validate shipping_address
        if not shipping_address:
            return jsonify({'error': 'Vui lòng nhập địa chỉ giao hàng'}), 400
        
        if len(shipping_address) < 10:
            return jsonify({'error': 'Địa chỉ giao hàng phải có ít nhất 10 ký tự'}), 400
        
        # Bước 4: BẮT ĐẦU TRANSACTION
        # SQLAlchemy tự động quản lý transaction, nhưng ta cần đảm bảo rollback khi có lỗi
        
        # Bước 5: Lấy tất cả items trong giỏ hàng
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        
        # Bước 6: Kiểm tra giỏ hàng không rỗng
        if not cart_items:
            return jsonify({'error': 'Giỏ hàng trống'}), 400
        
        # Bước 7: Validate stock và tính tổng tiền
        total_amount = Decimal('0')
        order_items_data = []
        
        for cart_item in cart_items:
            # Lấy thông tin sách
            book = Book.query.get(cart_item.book_id)
            if not book:
                db.session.rollback()
                return jsonify({'error': f'Sách với ID {cart_item.book_id} không tồn tại'}), 400
            
            # Kiểm tra stock còn đủ không
            if book.stock < cart_item.quantity:
                db.session.rollback()
                return jsonify({'error': f'Sách "{book.title}" không đủ số lượng (còn {book.stock} cuốn)'}), 400
            
            # Tính tiền
            item_price = Decimal(str(book.price))
            item_total = item_price * cart_item.quantity
            total_amount += item_total
            
            # Lưu thông tin để tạo order items sau
            order_items_data.append({
                'book_id': book.id,
                'quantity': cart_item.quantity,
                'price': item_price
            })
        
        # Bước 8: Tạo Order mới
        new_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='pending',
            payment_status='pending'
        )
        db.session.add(new_order)
        db.session.flush()  # Để lấy new_order.id
        
        # Bước 9: Tạo OrderItems và giảm stock
        for item_data in order_items_data:
            # Tạo OrderItem (lưu giá tại thời điểm mua)
            new_order_item = OrderItem(
                order_id=new_order.id,
                book_id=item_data['book_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(new_order_item)
            
            # Giảm stock của sách
            book = Book.query.get(item_data['book_id'])
            book.stock -= item_data['quantity']
        
        # Bước 10: Xóa tất cả items trong giỏ hàng
        Cart.query.filter_by(user_id=user_id).delete()
        
        # Bước 11: COMMIT TRANSACTION (lưu tất cả thay đổi)
        db.session.commit()
        
        # Bước 12: Trả về thông tin đơn hàng
        return jsonify({
            'message': 'Đơn hàng đã được đặt thành công! Bạn sẽ thanh toán khi nhận hàng.',
            'order': new_order.to_dict()
        }), 201
        
    except Exception as e:
        # Nếu có lỗi, rollback transaction
        db.session.rollback()
        return jsonify({'error': f'Lỗi tạo đơn hàng: {str(e)}'}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order(order_id):
    """
    Lấy chi tiết đơn hàng
    
    Flow:
    1. Lấy user_id từ session
    2. Query order theo order_id và user_id (đảm bảo user chỉ xem được đơn của mình)
    3. Kiểm tra order có tồn tại không
    4. Trả về thông tin order (đã có order_items từ relationship)
    
    Returns:
        - 200: Chi tiết order
        - 404: Order không tồn tại hoặc không thuộc về user
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session['user_id']
        
        # Bước 2: Query order theo order_id và user_id
        order = Order.query.filter_by(id=order_id, user_id=user_id).first()
        
        # Bước 3: Kiểm tra order có tồn tại không
        if not order:
            return jsonify({'error': 'Đơn hàng không tồn tại'}), 404
        
        # Bước 4: Trả về thông tin order
        return jsonify({'order': order.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy chi tiết đơn hàng: {str(e)}'}), 500
