"""
File: routes/admin.py

Mục đích:
Xử lý các route liên quan đến quản lý admin (users, orders, statistics)

Các endpoint trong file này:
- POST /api/admin/login: Đăng nhập admin
- GET /api/admin/users: Lấy danh sách users (có query param role để filter)
    - role=customer: Chỉ admin
  - Không có role: Chỉ super admin (admin)
- POST /api/admin/users: Tạo admin mới (chỉ super admin)
- PUT /api/admin/users/<id>: Cập nhật thông tin admin (chỉ super admin)
- PUT /api/admin/users/<id>/status: Cập nhật trạng thái user
  - Nếu user là customer: Chỉ admin/moderator
  - Nếu user là admin/editor: Chỉ super admin
- GET /api/admin/orders: Lấy tất cả đơn hàng (chỉ admin, không cho editor)
- PUT /api/admin/orders/<id>/status: Cập nhật trạng thái đơn hàng
- GET /api/admin/statistics: Lấy thống kê (chỉ admin)

Dependencies:
- models.User: Model cho bảng users
- models.Order: Model cho bảng orders
- models.OrderItem: Model cho bảng order_items
- models.Book: Model cho bảng books
- utils.helpers: admin_required, moderator_required, super_admin_required decorators, check_password, hash_password, validate_email
- sqlalchemy: Để query và aggregate
"""
from flask import Blueprint, request, jsonify, session
from models import User, Order, OrderItem, Book, db
from utils.helpers import admin_required, super_admin_required, moderator_required, check_password, hash_password, validate_email
from sqlalchemy import func, desc
from sqlalchemy.orm import joinedload

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """
    Đăng nhập admin (chỉ cho phép tài khoản có role='admin')
    
    Flow:
    1. Nhận username và password từ request
    2. Validate dữ liệu (không được để trống)
    3. Tìm user trong database theo username
    4. Kiểm tra user có role='admin' không
    5. Kiểm tra password có khớp không
    6. Kiểm tra tài khoản có bị khóa không (is_active)
    7. Tạo session để lưu thông tin đăng nhập
    8. Trả về thông tin user
    
    Returns:
        - 200: Đăng nhập thành công
        - 400: Thiếu thông tin
        - 401: Username/password không đúng, không phải admin, hoặc tài khoản bị khóa
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy dữ liệu từ request
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Bước 2: Validate dữ liệu
        if not username or not password:
            return jsonify({'error': 'Vui lòng nhập username và password'}), 400
        
        # Bước 3: Tìm user trong database
        user = User.query.filter_by(username=username).first()
        
        # Log để debug
        import logging
        logger = logging.getLogger(__name__)
        if not user:
            logger.warning(f'Admin login attempt with non-existent username: {username}')
            return jsonify({'error': 'Username hoặc password không đúng'}), 401

        logger.info(f'Admin login attempt for user: {username}, role: {user.role}, is_active: {user.is_active}')

        # Bước 4: Kiểm tra user có role='admin' không
        if user.role != 'admin':
            logger.warning(f'Admin login attempt by non-admin user: {username} (role: {user.role})')
            return jsonify({'error': 'Chỉ admin mới được phép đăng nhập'}), 401
        
        # Bước 5: Kiểm tra password
        if not check_password(password, user.password_hash):
            return jsonify({'error': 'Username hoặc password không đúng'}), 401
        
        # Bước 6: Kiểm tra tài khoản có bị khóa không
        if not user.is_active:
            return jsonify({'error': 'Tài khoản đã bị khóa'}), 401
        
        # Bước 7: Tạo session để lưu thông tin đăng nhập
        session['user_id'] = user.id
        session['username'] = user.username
        session['user_role'] = user.role
        
        # Bước 8: Trả về thông tin user
        return jsonify({
            'message': 'Đăng nhập thành công',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi đăng nhập: {str(e)}'}), 500

@admin_bp.route('/admin/users', methods=['GET'])
def get_users():
    """
    Lấy danh sách users (admin) với pagination
    
    Query Parameters:
        - role (optional): Filter theo role ('customer', 'admin')
                          Nếu không có, mặc định trả về admin (chỉ super admin)
        - page (int): Số trang (default: 1)
        - per_page (int): Số items mỗi trang (default: 20)
    
    Flow:
    1. Lấy query parameters (role, page, per_page)
    2. Kiểm tra quyền truy cập:
       - Nếu role=customer: chỉ admin được phép
       - Nếu không có role: chỉ super admin được phép (super_admin_required)
    3. Query users theo role filter
    4. Sắp xếp theo created_at giảm dần (mới nhất trước)
    5. Thực hiện pagination
    6. Trả về danh sách users với thông tin pagination
    
    Returns:
        - 200: Danh sách users với pagination info
        - 403: Không có quyền truy cập
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy query parameters
        role_filter = request.args.get('role', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Bước 2: Kiểm tra quyền truy cập và tạo query
        if role_filter == 'customer':
            # Chỉ admin được phép xem customers
            if 'user_id' not in session:
                return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
            user_role = session.get('user_role')
            if user_role not in ['admin', 'moderator']:
                return jsonify({'error': 'Chỉ Admin và Moderator mới có quyền quản lý khách hàng'}), 403
            # Query customers
            query = User.query.filter_by(role='customer').order_by(User.created_at.desc())
        else:
            # Mặc định: chỉ trả về admin (chỉ super admin)
            if 'user_id' not in session:
                return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
            user_role = session.get('user_role')
            if user_role != 'admin':
                return jsonify({'error': 'Chỉ Super Admin mới có quyền xem danh sách admin'}), 403
            query = User.query.filter_by(role='admin').order_by(User.created_at.desc())
        # Bước 3: Thực hiện pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Bước 4: Trả về danh sách users với pagination info
        return jsonify({
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách users: {str(e)}'}), 500

@admin_bp.route('/admin/users', methods=['POST'])
@super_admin_required
def create_admin_user():
    """
    Tạo admin user mới (chỉ super admin)
    
    Flow:
    1. Lấy dữ liệu từ request (username, email, password, full_name)
    2. Validate dữ liệu
    3. Kiểm tra username và email đã tồn tại chưa
    4. Hash password
    5. Tạo user mới với role='admin'
    6. Lưu vào database
    7. Trả về thông tin user
    
    Returns:
        - 201: Tạo thành công
        - 400: Dữ liệu không hợp lệ hoặc username/email đã tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy dữ liệu từ request
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Bước 2: Validate dữ liệu
        if not username or not email or not password:
            return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Email không hợp lệ'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400
        
        # Chặn tạo admin nếu đã có 1 admin active
        existing_admin = User.query.filter_by(role='admin', is_active=True).first()
        if existing_admin:
            return jsonify({'error': 'Chỉ được phép có 1 Super Admin duy nhất trong hệ thống'}), 400
        
        # Bước 3: Kiểm tra username và email đã tồn tại chưa
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username đã tồn tại'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email đã tồn tại'}), 400
        
        # Bước 4: Hash password
        password_hash = hash_password(password)
        
        # Bước 5-6: Tạo user mới và lưu vào database
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name or username,
            role='admin',
            is_active=True
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Bước 7: Trả về thông tin user
        return jsonify({
            'message': 'Tạo admin thành công',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi tạo user: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@super_admin_required
def update_admin_user(user_id):
    """
    Cập nhật thông tin admin user (chỉ super admin)
    
    Flow:
    1. Lấy dữ liệu từ request (email, full_name, password optional)
    2. Validate dữ liệu
    3. Kiểm tra user có tồn tại không
    4. Kiểm tra email không trùng với user khác (trừ user hiện tại)
    5. Kiểm tra user phải là admin
    6. Update user và commit
    7. Trả về thông tin user đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Dữ liệu không hợp lệ hoặc email đã tồn tại
        - 404: User không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy dữ liệu từ request
        data = request.get_json()
        email = data.get('email', '').strip()
        full_name = data.get('full_name', '').strip()
        role = data.get('role', '').strip()
        password = data.get('password', '').strip()  # Optional
        
        # Bước 2: Validate dữ liệu
        if not email or not full_name:
            return jsonify({'error': 'Vui lòng điền đầy đủ thông tin'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Email không hợp lệ'}), 400
        
        # Validate password nếu có
        if password and len(password) < 6:
            return jsonify({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}), 400
        
        # Bước 3: Query user từ database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        # Chỉ cho phép update admin
        if user.role != 'admin':
            return jsonify({'error': 'Chỉ có thể cập nhật admin'}), 400
        
        # Bước 4: Kiểm tra email không trùng với user khác (trừ user hiện tại)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email đã tồn tại'}), 400
        
        # Bước 5: Update user
        user.email = email
        user.full_name = full_name
        
        # Update password nếu có
        if password:
            user.password_hash = hash_password(password)
        
        db.session.commit()
        
        # Bước 7: Trả về thông tin user đã cập nhật
        return jsonify({
            'message': 'Cập nhật user thành công',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật user: {str(e)}'}), 500

@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
def update_user_status(user_id):
    """
    Khóa/mở tài khoản user
    
    Quyền truy cập:
    - Nếu user là customer: Chỉ Admin được phép
    - Nếu user là admin: Chỉ Super Admin được phép
    
    Flow:
    1. Kiểm tra quyền đăng nhập
    2. Query user từ database
    3. Kiểm tra user có tồn tại không
    4. Kiểm tra quyền truy cập dựa trên role của user
    5. Lấy is_active từ request body
    6. Validate is_active không None
    7. Validate không cho phép vô hiệu hóa admin duy nhất
    8. Cập nhật is_active
    9. Lưu vào database
    10. Trả về thông tin user đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Thiếu trường is_active hoặc validation lỗi
        - 403: Không có quyền truy cập
        - 404: User không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1: Kiểm tra quyền đăng nhập
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        
        user_role = session.get('user_role')
        
        # Bước 2-3: Query và kiểm tra user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User không tồn tại'}), 404
        
        # Bước 4: Kiểm tra quyền truy cập dựa trên role của user
        if user.role == 'customer':
            # Chỉ admin được phép quản lý customers
            if user_role not in ['admin', 'moderator']:
                return jsonify({'error': 'Chỉ Admin và Moderator mới có quyền quản lý khách hàng'}), 403
        else:
            # Chỉ super admin được phép quản lý admin/moderator/editor
            if user_role != 'admin':
                return jsonify({'error': 'Chỉ Super Admin mới có quyền quản lý quản trị viên'}), 403
        
        # Bước 5-6: Lấy và validate is_active
        data = request.get_json()
        is_active = data.get('is_active')
        
        if is_active is None:
            return jsonify({'error': 'Thiếu trường is_active'}), 400
        
        # Bước 7: Validate không cho phép vô hiệu hóa admin duy nhất
        if user.role == 'admin' and not bool(is_active):
            # Đếm tổng số admin active trong hệ thống (TRƯỚC KHI vô hiệu hóa)
            total_active_admins = User.query.filter_by(role='admin', is_active=True).count()
            
            # Nếu chỉ có 1 admin active và đó là user đang bị vô hiệu hóa → reject
            if total_active_admins == 1:
                return jsonify({
                    'error': 'Không thể vô hiệu hóa admin duy nhất trong hệ thống. Vui lòng tạo thêm admin khác trước khi vô hiệu hóa tài khoản này.'
                }), 400
        
        # Bước 8-9: Cập nhật và lưu
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
@moderator_required
def get_all_orders():
    """
    Lấy tất cả đơn hàng (admin) với pagination
    
    Query Parameters:
        - page (int): Số trang (default: 1)
        - per_page (int): Số items mỗi trang (default: 20)
    
    Flow:
    1. Lấy query parameters (page, per_page)
    2. Query orders từ database với pagination
    3. Load thông tin user (JOIN) để hiển thị thông tin khách hàng
    4. Sắp xếp theo created_at giảm dần (mới nhất trước)
    5. Trả về danh sách orders với thông tin pagination (mỗi order đã có order_items từ relationship)
    
    Returns:
        - 200: Danh sách orders với pagination info
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Bước 2-4: Query orders với user info, sắp xếp và pagination
        query = Order.query.options(joinedload(Order.user)).order_by(Order.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Bước 5: Trả về danh sách orders với pagination info
        return jsonify({
            'orders': [order.to_dict() for order in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách đơn hàng: {str(e)}'}), 500

@admin_bp.route('/admin/orders/<int:order_id>/status', methods=['PUT'])
@moderator_required
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
@moderator_required
def get_statistics():
    """
    Lấy thống kê tổng quan (admin)
    
    Quyền truy cập: Chỉ Admin được phép
    
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
        - 403: Không có quyền truy cập
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
