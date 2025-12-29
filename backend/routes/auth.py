"""
File: routes/auth.py

Mục đích: 
Xử lý các route liên quan đến authentication (đăng ký, đăng nhập, đăng xuất)

Các endpoint trong file này:
- POST /api/register: Đăng ký tài khoản mới
- POST /api/login: Đăng nhập vào hệ thống
- POST /api/logout: Đăng xuất
- GET /api/me: Lấy thông tin user hiện tại
- PUT /api/profile: Cập nhật thông tin profile

Dependencies:
- models.User: Model cho bảng users
- utils.helpers: Các hàm helper (hash_password, check_password, validate_email, validate_password)
- flask.session: Quản lý session
"""
from flask import Blueprint, request, jsonify, session
from models import User, db
from utils.helpers import hash_password, check_password, validate_email, validate_password, login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản mới
    
    Flow:
    1. Nhận dữ liệu từ request (username, email, password, full_name)
    2. Validate dữ liệu (kiểm tra đầy đủ, email hợp lệ, password >= 6 ký tự)
    3. Kiểm tra username và email đã tồn tại chưa
    4. Hash password bằng bcrypt
    5. Tạo user mới trong database
    6. Tự động đăng nhập (tạo session)
    7. Trả về thông tin user (không có password)
    
    Returns:
        - 201: Đăng ký thành công
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
        
        password_valid, password_error = validate_password(password)
        if not password_valid:
            return jsonify({'error': password_error}), 400
        
        # Bước 3: Kiểm tra username và email đã tồn tại chưa
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username đã tồn tại'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email đã tồn tại'}), 400
        
        # Bước 4: Hash password trước khi lưu vào database
        password_hash = hash_password(password)
        
        # Bước 5: Tạo user mới
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            full_name=full_name or username,
            role='customer',
            is_active=True,
            customer_code=User.generate_customer_code()
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Bước 6: Tự động đăng nhập (tạo session)
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['user_role'] = new_user.role
        
        # Bước 7: Trả về thông tin user (không có password_hash)
        return jsonify({
            'message': 'Đăng ký thành công',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi đăng ký: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập vào hệ thống (chỉ cho phép customer, không cho phép admin)
    
    Flow:
    1. Nhận username và password từ request
    2. Validate dữ liệu (không được để trống)
    3. Tìm user trong database theo username
    4. Kiểm tra user có phải admin không (nếu là admin thì từ chối)
    5. Kiểm tra password có khớp không
    6. Kiểm tra tài khoản có bị khóa không (is_active)
    7. Tạo session để lưu thông tin đăng nhập
    8. Trả về thông tin user
    
    Returns:
        - 200: Đăng nhập thành công
        - 400: Thiếu thông tin
        - 401: Username/password không đúng, là admin, hoặc tài khoản bị khóa
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
        
        # Bước 4: Kiểm tra user có phải admin không (nếu là admin thì từ chối)
        if user and user.role == 'admin':
            return jsonify({'error': 'Tài khoản admin phải đăng nhập qua /admin/login'}), 401
        
        # Bước 5: Kiểm tra password
        if not user or not check_password(password, user.password_hash):
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

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Đăng xuất khỏi hệ thống
    
    Flow:
    1. Xóa tất cả thông tin trong session
    2. Trả về thông báo thành công
    
    Returns:
        - 200: Đăng xuất thành công
    """
    # Xóa tất cả thông tin trong session
    session.clear()
    return jsonify({'message': 'Đăng xuất thành công'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Lấy thông tin user hiện tại (đã đăng nhập)
    
    Flow:
    1. Kiểm tra user đã đăng nhập chưa (có session['user_id'] không)
    2. Lấy user từ database theo user_id trong session
    3. Kiểm tra user có tồn tại không
    4. Trả về thông tin user
    
    Returns:
        - 200: Lấy thông tin thành công
        - 401: Chưa đăng nhập
        - 404: User không tồn tại
        - 500: Lỗi server
    """
    # Bước 1: Kiểm tra user đã đăng nhập chưa
    if 'user_id' not in session:
        return jsonify({'error': 'Chưa đăng nhập'}), 401
    
    try:
        # Bước 2: Lấy user từ database
        user = User.query.get(session['user_id'])
        
        # Bước 3: Kiểm tra user có tồn tại không
        if not user:
            session.clear()
            return jsonify({'error': 'User không tồn tại'}), 404
        
        # Bước 4: Trả về thông tin user
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy thông tin user: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """
    Cập nhật thông tin profile của user (full_name, email)
    
    Flow:
    1. Lấy user_id từ session (đã được kiểm tra bởi @login_required)
    2. Lấy dữ liệu từ request (full_name, email)
    3. Validate dữ liệu (không được để trống, email hợp lệ)
    4. Kiểm tra email đã được sử dụng bởi user khác chưa
    5. Cập nhật thông tin user trong database
    6. Trả về thông tin user đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Dữ liệu không hợp lệ hoặc email đã được sử dụng
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy user_id từ session
        user_id = session.get('user_id')
        
        # Bước 2: Lấy dữ liệu từ request
        data = request.get_json()
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        
        # Bước 3: Validate dữ liệu
        if not full_name:
            return jsonify({'error': 'Họ tên không được để trống'}), 400
        
        if not email:
            return jsonify({'error': 'Email không được để trống'}), 400
        
        if not validate_email(email):
            return jsonify({'error': 'Email không hợp lệ'}), 400
        
        # Bước 4: Lấy user và kiểm tra email đã được sử dụng chưa
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Người dùng không tồn tại'}), 404
        
        # Kiểm tra email đã được sử dụng bởi user khác chưa
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email đã được sử dụng'}), 400
        
        # Bước 5: Cập nhật thông tin user
        user.full_name = full_name
        user.email = email
        db.session.commit()
        
        # Bước 6: Trả về thông tin user đã cập nhật
        return jsonify({
            'message': 'Cập nhật thành công',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật: {str(e)}'}), 500