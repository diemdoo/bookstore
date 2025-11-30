"""
File: routes/admin.py

Mục đích:
Xử lý các route liên quan đến quản lý admin (users, orders, statistics)

Các endpoint trong file này:
- GET /api/admin/users: Lấy danh sách tất cả users (admin)
- PUT /api/admin/users/<id>/status: Cập nhật trạng thái user (admin)
- GET /api/admin/orders: Lấy tất cả đơn hàng (admin)
- PUT /api/admin/orders/<id>/status: Cập nhật trạng thái đơn hàng (admin)
- GET /api/admin/statistics: Lấy thống kê (admin)

Dependencies:
- models.User: Model cho bảng users
- models.Order: Model cho bảng orders
- models.OrderItem: Model cho bảng order_items
- models.Book: Model cho bảng books
- utils.helpers: admin_required decorator
- sqlalchemy: Để query và aggregate
"""
from flask import Blueprint, request, jsonify
from models import User, Order, OrderItem, Book, db
from utils.helpers import admin_required
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    """
    Lấy danh sách tất cả users (admin)
    
    Flow:
    1. Query tất cả users từ database
    2. Sắp xếp theo created_at giảm dần (mới nhất trước)
    3. Trả về danh sách users
    
    Returns:
        - 200: Danh sách users
        - 500: Lỗi server
    """
    try:
        # Bước 1-2: Query và sắp xếp users
        users = User.query.order_by(User.created_at.desc()).all()
        
        # Bước 3: Trả về danh sách users
        return jsonify({
            'users': [user.to_dict() for user in users]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách users: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
@admin_required
def update_user_status(user_id):
    """
    Khóa/mở tài khoản user (admin)
    
    Flow:
    1. Lấy user_id từ URL
    2. Lấy is_active từ request body
    3. Validate is_active không None
    4. Query user từ database
    5. Kiểm tra user có tồn tại không
    6. Cập nhật is_active
    7. Lưu vào database
    8. Trả về thông tin user đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Thiếu trường is_active
        - 404: User không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1-2: Lấy dữ liệu
        data = request.get_json()
        is_active = data.get('is_active')
        
        # Bước 3: Validate
        if is_active is None:
            return jsonify({'error': 'Thiếu trường is_active'}), 400
        
        # Bước 4-5: Query và kiểm tra user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        # Bước 6-7: Cập nhật và lưu
        user.is_active = bool(is_active)
        db.session.commit()
        
        # Bước 8: Trả về thông tin user
        return jsonify({
            'message': 'Cập nhật trạng thái user thành công',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật trạng thái user: {str(e)}'}), 500

@admin_bp.route('/admin/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """
    Lấy tất cả đơn hàng (admin)
    
    Flow:
    1. Query tất cả orders từ database
    2. Load thông tin user (JOIN) để hiển thị thông tin khách hàng
    3. Sắp xếp theo created_at giảm dần (mới nhất trước)
    4. Trả về danh sách orders (mỗi order đã có order_items từ relationship)
    
    Returns:
        - 200: Danh sách orders
        - 500: Lỗi server
    """
    try:
        # Bước 1-3: Query orders với user info và sắp xếp
        orders = Order.query.options(joinedload(Order.user)).order_by(Order.created_at.desc()).all()
        
        # Bước 4: Trả về danh sách orders
        return jsonify({
            'orders': [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách đơn hàng: {str(e)}'}), 500

@admin_bp.route('/admin/orders/<int:order_id>/status', methods=['PUT'])
@admin_required
def update_order_status(order_id):
    """
    Cập nhật trạng thái đơn hàng và payment_status (admin)
    
    Flow:
    1. Lấy order_id từ URL
    2. Lấy status và payment_status từ request body
    3. Validate status và payment_status (nếu có)
    4. Query order từ database
    5. Kiểm tra order có tồn tại không
    6. Cập nhật status và/hoặc payment_status
    7. Lưu vào database
    8. Trả về thông tin order đã cập nhật
    
    Valid status values: pending, confirmed, cancelled, completed
    Valid payment_status values: pending, paid
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Status không hợp lệ
        - 404: Order không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1-2: Lấy dữ liệu
        data = request.get_json()
        status = data.get('status')
        payment_status = data.get('payment_status')
        
        # Bước 3: Validate status và payment_status
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        valid_payment_statuses = ['pending', 'paid']
        
        if status and status not in valid_statuses:
            return jsonify({
                'error': f'Trạng thái không hợp lệ. Phải là một trong: {", ".join(valid_statuses)}'
            }), 400
        
        if payment_status and payment_status not in valid_payment_statuses:
            return jsonify({
                'error': f'Trạng thái thanh toán không hợp lệ. Phải là một trong: {", ".join(valid_payment_statuses)}'
            }), 400
        
        # Bước 4-5: Query và kiểm tra order
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Đơn hàng không tồn tại'}), 404
        
        # Bước 6-7: Cập nhật và lưu
        if status:
            order.status = status
        if payment_status:
            order.payment_status = payment_status
        db.session.commit()
        
        # Bước 8: Trả về thông tin order
        return jsonify({
            'message': 'Cập nhật trạng thái đơn hàng thành công',
            'order': order.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật trạng thái đơn hàng: {str(e)}'}), 500

@admin_bp.route('/admin/statistics', methods=['GET'])
@admin_required
def get_statistics():
    """
    Lấy thống kê tổng quan (admin)
    
    Flow:
    1. Tính tổng doanh thu từ các đơn hàng đã hoàn thành và đã thanh toán
    2. Đếm tổng số đơn hàng
    3. Đếm số đơn hàng theo từng trạng thái (pending, confirmed, completed, cancelled)
    4. Query top 10 sách bán chạy nhất (dựa trên số lượng đã bán trong các đơn đã hoàn thành)
    5. Trả về object thống kê
    
    Returns:
        - 200: Object thống kê với các thông tin:
            - total_revenue: Tổng doanh thu
            - total_orders: Tổng số đơn hàng
            - pending_orders: Số đơn chờ xác nhận
            - confirmed_orders: Số đơn đã xác nhận
            - completed_orders: Số đơn đã hoàn thành
            - cancelled_orders: Số đơn đã hủy
            - orders_by_status: Dict số đơn theo từng status
            - top_books: Top 10 sách bán chạy
        - 500: Lỗi server
    """
    try:
        # Bước 1: Tính tổng doanh thu (chỉ tính đơn đã hoàn thành và đã thanh toán)
        total_revenue = db.session.query(func.sum(Order.total_amount)).filter(
            Order.status == 'completed',
            Order.payment_status == 'paid'
        ).scalar() or 0
        
        # Bước 2: Đếm tổng số đơn hàng
        total_orders = Order.query.count()
        
        # Bước 3: Đếm số đơn hàng theo từng trạng thái
        orders_by_status = db.session.query(
            Order.status,
            func.count(Order.id)
        ).group_by(Order.status).all()
        
        # Chuyển đổi sang dict để dễ truy cập
        orders_by_status_dict = {status: count for status, count in orders_by_status}
        
        # Lấy số lượng từng loại đơn
        pending_orders = orders_by_status_dict.get('pending', 0)
        confirmed_orders = orders_by_status_dict.get('confirmed', 0)
        completed_orders = orders_by_status_dict.get('completed', 0)
        cancelled_orders = orders_by_status_dict.get('cancelled', 0)
        
        # Bước 4: Query top 10 sách bán chạy nhất
        # Chỉ tính các đơn đã hoàn thành
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
        
        # Bước 5: Trả về object thống kê
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
        
        return jsonify(statistics), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy thống kê: {str(e)}'}), 500
