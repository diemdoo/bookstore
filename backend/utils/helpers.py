"""
Các hàm tiện ích cho ứng dụng
"""
import bcrypt
import re
import unicodedata
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
    Validate password với các yêu cầu:
    - Tối thiểu 8 ký tự
    - Ít nhất 1 chữ cái thường
    - Ít nhất 1 chữ cái in hoa
    - Ít nhất 1 chữ số
    - Ít nhất 1 ký tự đặc biệt
    """
    if len(password) < 8:
        return False, 'Mật khẩu phải có ít nhất 8 ký tự'
    
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
    
    if not has_lower:
        return False, 'Mật khẩu phải có ít nhất 1 chữ cái thường'
    if not has_upper:
        return False, 'Mật khẩu phải có ít nhất 1 chữ cái in hoa'
    if not has_digit:
        return False, 'Mật khẩu phải có ít nhất 1 chữ số'
    if not has_special:
        return False, 'Mật khẩu phải có ít nhất 1 ký tự đặc biệt'
    
    return True, None

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
    Chỉ admin mới được truy cập
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        user_role = session.get('user_role')
        if user_role != 'admin':
            return jsonify({'error': 'Yêu cầu quyền admin'}), 403
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    """
    Decorator để yêu cầu quyền super admin
    Chỉ admin mới được truy cập
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        if session.get('user_role') != 'admin':
            return jsonify({'error': 'Yêu cầu quyền super admin'}), 403
        return f(*args, **kwargs)
    return decorated_function

def moderator_required(f):
    """
    Decorator để yêu cầu quyền moderator trở lên (moderator hoặc admin)
    Editor không được phép truy cập
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        user_role = session.get('user_role')
        if user_role not in ['admin', 'moderator']:
            return jsonify({'error': 'Yêu cầu quyền moderator trở lên'}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_slug(text):
    """Tạo slug từ text tiếng Việt có dấu"""
    if not text:
        return ''
    
    # Replace đ/Đ trước khi normalize (NFD không tách được chữ này)
    text = text.replace('đ', 'd').replace('Đ', 'd')
    
    # Normalize và loại bỏ dấu
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    
    # Chuyển lowercase, replace special chars, strip
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def generate_unique_slug(base_slug, model_class, exclude_id=None):
    """
    Tạo slug unique bằng cách append số nếu trùng
    
    Args:
        base_slug (str): Slug cơ bản
        model_class: Model class để check unique (ví dụ: Category)
        exclude_id (int): ID để exclude khi check (dùng khi update)
        
    Returns:
        str: Slug unique (có thể là base_slug hoặc base_slug-1, base_slug-2, ...)
    """
    slug = base_slug
    counter = 1
    
    while True:
        query = model_class.query.filter_by(slug=slug)
        if exclude_id:
            query = query.filter(model_class.id != exclude_id)
        
        if not query.first():
            return slug
        
        slug = f"{base_slug}-{counter}"
        counter += 1

def generate_category_key(name):
    """
    Tự động generate key từ name cho category
    
    Args:
        name (str): Tên category
        
    Returns:
        str: Key dạng UPPERCASE_WITH_UNDERSCORES
    """
    if not name:
        return ''
    
    # Chuyển thành uppercase và thay space bằng underscore
    key = name.upper().strip()
    key = re.sub(r'[^\w\s]', '', key)  # Loại bỏ ký tự đặc biệt
    key = re.sub(r'\s+', '_', key)     # Thay space bằng underscore
    key = re.sub(r'_+', '_', key)      # Loại bỏ underscore liên tiếp
    key = key.strip('_')
    
    return key

def generate_unique_category_key(base_key, model_class, exclude_id=None):
    """
    Tạo category key unique bằng cách append số nếu trùng
    
    Args:
        base_key (str): Key cơ bản (UPPERCASE_WITH_UNDERSCORES)
        model_class: Model class để check unique (Category)
        exclude_id (int): ID để exclude khi check (dùng khi update)
        
    Returns:
        str: Key unique (có thể là base_key hoặc base_key_2, base_key_3, ...)
        
    Example:
        base_key = "SACH_THIEU_NHI"
        Nếu trùng, trả về "SACH_THIEU_NHI_2", "SACH_THIEU_NHI_3", ...
    """
    key = base_key
    counter = 2  # Start from 2 (base key is version 1)
    
    while True:
        # Query để check xem key đã tồn tại chưa
        query = model_class.query.filter_by(key=key)
        if exclude_id:
            query = query.filter(model_class.id != exclude_id)
        
        # Nếu key chưa tồn tại, return ngay
        if not query.first():
            return key
        
        # Nếu trùng, append số và thử lại
        key = f"{base_key}_{counter}"
        counter += 1

def generate_unique_book_slug(base_slug, model_class, exclude_id=None):
    """
    Tạo slug unique cho book bằng cách append số nếu trùng
    
    Args:
        base_slug (str): Slug cơ bản từ title
        model_class: Model class để check unique (Book)
        exclude_id (int): ID để exclude khi check (dùng khi update)
        
    Returns:
        str: Slug unique (có thể là base_slug hoặc base_slug-1, base_slug-2, ...)
    """
    slug = base_slug
    counter = 1
    
    while True:
        query = model_class.query.filter_by(slug=slug)
        if exclude_id:
            query = query.filter(model_class.id != exclude_id)
        
        if not query.first():
            return slug
        
        slug = f"{base_slug}-{counter}"
        counter += 1

def generate_book_code(Book):
    """
    Tạo mã sách tự động (MS000001, MS000002, ...)
    
    Flow:
    1. Query book code lớn nhất hiện tại (MS000001 → 1)
    2. Tăng lên 1
    3. Format thành MS + 6 số (zero-padded)
    4. Kiểm tra unique và retry nếu trùng
    
    Args:
        Book: Book model class
    
    Returns:
        str: Mã sách unique (VD: MS000001)
    """
    from app import db
    from sqlalchemy import func
    
    max_code = db.session.query(func.max(Book.book_code)).scalar()
    
    if max_code:
        # Extract number from MS000001 → 1
        number = int(max_code[2:]) + 1
    else:
        number = 1
    
    # Format: MS + 6 digits
    book_code = f'MS{number:06d}'
    
    # Kiểm tra unique (trong trường hợp race condition)
    while Book.query.filter_by(book_code=book_code).first():
        number += 1
        book_code = f'MS{number:06d}'
    
    return book_code

def generate_category_code(Category):
    """
    Tạo mã danh mục (DM000001, DM000002, ...)
    
    Flow:
    1. Query category code lớn nhất hiện tại
    2. Tăng lên 1
    3. Format thành DM + 6 số (zero-padded)
    4. Kiểm tra unique và retry nếu trùng
    
    Args:
        Category: Category model class
    
    Returns:
        str: Mã danh mục unique (VD: DM000001)
    """
    from app import db
    from sqlalchemy import func
    
    max_code = db.session.query(func.max(Category.category_code)).scalar()
    
    if max_code:
        number = int(max_code[2:]) + 1
    else:
        number = 1
    
    category_code = f'DM{number:06d}'
    
    while Category.query.filter_by(category_code=category_code).first():
        number += 1
        category_code = f'DM{number:06d}'
    
    return category_code

def generate_banner_code(Banner):
    """
    Tạo mã banner (BN000001, BN000002, ...)
    
    Flow:
    1. Query banner code lớn nhất hiện tại
    2. Tăng lên 1
    3. Format thành BN + 6 số (zero-padded)
    4. Kiểm tra unique và retry nếu trùng
    
    Args:
        Banner: Banner model class
    
    Returns:
        str: Mã banner unique (VD: BN000001)
    """
    from app import db
    from sqlalchemy import func
    
    max_code = db.session.query(func.max(Banner.banner_code)).scalar()
    
    if max_code:
        number = int(max_code[2:]) + 1
    else:
        number = 1
    
    banner_code = f'BN{number:06d}'
    
    while Banner.query.filter_by(banner_code=banner_code).first():
        number += 1
        banner_code = f'BN{number:06d}'
    
    return banner_code
