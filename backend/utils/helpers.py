"""
Các hàm tiện ích cho ứng dụng
"""
import bcrypt
import re
from functools import wraps
from flask import session, jsonify

def hash_password(password):
    """
    Hash password bằng bcrypt
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, password_hash):
    """
    Kiểm tra password có khớp với hash không
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def validate_email(email):
    """
    Validate định dạng email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """
    Validate password (ít nhất 6 ký tự)
    """
    return len(password) >= 6

def login_required(f):
    """
    Decorator để yêu cầu đăng nhập
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator để yêu cầu quyền admin
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        if session.get('user_role') != 'admin':
            return jsonify({'error': 'Yêu cầu quyền admin'}), 403
        return f(*args, **kwargs)
    return decorated_function

