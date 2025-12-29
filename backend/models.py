"""
File: backend/models.py

Mục đích:
Định nghĩa các SQLAlchemy Models cho database, bao gồm User, Book, Category, Cart, Order, OrderItem, Banner.
Các models này đại diện cho cấu trúc dữ liệu và relationships trong database.

Các models trong file này:
- User: Quản lý thông tin người dùng (admin và customer)
- Book: Quản lý thông tin sách và tính toán số lượng đã bán
- Category: Quản lý danh mục sách
- Cart: Quản lý giỏ hàng của user
- Order: Quản lý đơn hàng
- OrderItem: Quản lý chi tiết từng item trong đơn hàng
- Banner: Quản lý banner quảng cáo

Dependencies:
- flask_sqlalchemy: ORM framework để tương tác với database
- sqlalchemy: Database operations (func, relationships)
- datetime: Quản lý timestamp (created_at, updated_at)
"""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

# Khởi tạo SQLAlchemy instance để sử dụng trong toàn bộ ứng dụng
db = SQLAlchemy()

class User(db.Model):
    """
    Model cho bảng Users
    
    Mục đích:
    Quản lý thông tin người dùng trong hệ thống, bao gồm admin và customer.
    
    Fields:
    - id: Primary key
    - username: Tên đăng nhập (unique)
    - email: Email (unique)
    - password_hash: Mật khẩu đã được hash bằng bcrypt
    - full_name: Tên đầy đủ
    - role: Vai trò (admin hoặc customer)
    - is_active: Trạng thái hoạt động
    - customer_code: Mã khách hàng (KH001, KH002, ...) - tự động generate
    - created_at: Thời gian tạo tài khoản
    
    Relationships:
    - cart_items: Danh sách items trong giỏ hàng (one-to-many)
    - orders: Danh sách đơn hàng của user (one-to-many)
    
    Methods:
    - to_dict(): Chuyển đổi model thành dictionary (không bao gồm password_hash)
    - generate_customer_code(): Tạo mã khách hàng mới theo format KH001, KH002, ...
    """
    __tablename__ = 'users'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Thông tin đăng nhập
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # Đã được hash bằng bcrypt
    
    # Thông tin cá nhân
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='customer', nullable=False)  # admin hoặc customer
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    customer_code = db.Column(db.String(20), unique=True, nullable=True)  # KH001, KH002, ...
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với tất cả fields (trừ password_hash)
        2. Convert datetime sang ISO format string
        3. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin user (không có password_hash)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role,
            'is_active': self.is_active,
            'customer_code': self.customer_code,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @staticmethod
    def generate_customer_code():
        """
        Tạo mã khách hàng mới theo format KH001, KH002, KH003, ...
        
        Flow:
        1. Query user có customer_code lớn nhất
        2. Lấy số cuối cùng từ customer_code (ví dụ: KH001 -> 1)
        3. Tăng lên 1 và format lại thành KH002, KH003, ...
        4. Nếu chưa có customer nào, bắt đầu từ KH001
        
        Returns:
            str: Mã khách hàng mới (ví dụ: "KH001", "KH002")
        """
        # Bước 1: Tìm customer có mã lớn nhất
        last_customer = User.query.filter(
            User.customer_code.isnot(None)
        ).order_by(User.customer_code.desc()).first()
        
        # Bước 2-3: Tăng số lên 1
        if last_customer and last_customer.customer_code:
            last_num = int(last_customer.customer_code[2:])  # Lấy số từ "KH001" -> 1
            new_num = last_num + 1
        else:
            # Bước 4: Nếu chưa có, bắt đầu từ 1
            new_num = 1
        
        # Format: KH001, KH002, ...
        return f'KH{new_num:03d}'
    

class Book(db.Model):
    """
    Model cho bảng Books
    
    Mục đích:
    Quản lý thông tin sách trong hệ thống, bao gồm thông tin cơ bản và chi tiết.
    Có thể tính toán số lượng đã bán từ OrderItem.
    
    Fields:
    - id: Primary key
    - title: Tên sách
    - author: Tác giả
    - category: Danh mục sách (reference đến Category.key)
    - description: Mô tả sách
    - price: Giá bán
    - stock: Số lượng tồn kho
    - image_url: URL hình ảnh sách
    - publisher: Nhà xuất bản
    - publish_date: Ngày xuất bản
    - distributor: Nhà phát hành
    - dimensions: Kích thước (cm)
    - pages: Số trang
    - weight: Trọng lượng (gram)
    - created_at, updated_at: Timestamps
    
    Relationships:
    - cart_items: Danh sách items trong giỏ hàng chứa sách này (one-to-many)
    - order_items: Danh sách order items chứa sách này (one-to-many)
    
    Methods:
    - get_sold_count(): Tính số lượng đã bán từ OrderItem (chỉ tính order completed)
    - to_dict(): Chuyển đổi model thành dictionary (bao gồm sold count)
    """
    __tablename__ = 'books'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Mã sách (MS000001, MS000002, ...)
    book_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Thông tin cơ bản
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)  # Slug dùng cho URL (e.g., 'cay-cam-ngot-cua-toi')
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Reference đến Category.key
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    
    # Thông tin chi tiết
    publisher = db.Column(db.String(200), nullable=True)  # Nhà xuất bản
    publish_date = db.Column(db.String(20), nullable=True)  # Ngày xuất bản (format: YYYY-MM-DD)
    distributor = db.Column(db.String(200), nullable=True)  # Nhà phát hành
    dimensions = db.Column(db.String(100), nullable=True)  # Kích thước (cm)
    pages = db.Column(db.Integer, nullable=True)  # Số trang
    weight = db.Column(db.Integer, nullable=True)  # Trọng lượng (gram)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='book', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    
    def get_sold_count(self):
        """
        Tính số lượng đã bán từ OrderItem (chỉ tính các order đã completed)
        
        Flow:
        1. Query OrderItem join với Order
        2. Filter theo book_id và order status = 'completed'
        3. Sum tổng quantity của tất cả OrderItem
        4. Trả về số lượng đã bán (0 nếu chưa có)
        
        Returns:
            int: Số lượng đã bán (tổng quantity từ các order completed)
        """
        # Import here to avoid circular dependency (OrderItem và Order được định nghĩa sau)
        from models import OrderItem, Order
        
        # Bước 1-3: Query và tính tổng
        total = db.session.query(func.sum(OrderItem.quantity)).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            OrderItem.book_id == self.id,
            Order.status == 'completed'
        ).scalar()
        
        # Bước 4: Trả về số lượng (0 nếu None)
        return int(total) if total else 0
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với tất cả fields
        2. Convert price từ Decimal sang float
        3. Tính số lượng đã bán bằng get_sold_count()
        4. Convert datetime sang ISO format string
        5. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin sách (bao gồm sold count)
        """
        return {
            'id': self.id,
            'book_code': self.book_code,
            'title': self.title,
            'slug': self.slug,
            'author': self.author,
            'category': self.category,
            'description': self.description,
            'price': float(self.price),  # Convert Decimal sang float
            'stock': self.stock,
            'image_url': self.image_url,
            'publisher': self.publisher,
            'publish_date': self.publish_date,
            'distributor': self.distributor,
            'dimensions': self.dimensions,
            'pages': self.pages,
            'weight': self.weight,
            'sold': self.get_sold_count(),  # Tính số lượng đã bán
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Category(db.Model):
    """
    Model cho bảng Categories
    
    Mục đích:
    Quản lý danh mục sách trong hệ thống (ví dụ: Sách Tiếng Việt, Văn Phòng Phẩm, ...).
    
    Fields:
    - id: Primary key
    - key: Key duy nhất của category (dùng trong URL, ví dụ: 'Sach_Tieng_Viet')
    - name: Tên hiển thị của category (ví dụ: 'Sách Tiếng Việt')
    - description: Mô tả category
    - display_order: Thứ tự hiển thị trong UI (số nhỏ hơn hiển thị trước)
    - is_active: Trạng thái hoạt động
    - created_at, updated_at: Timestamps
    
    Methods:
    - to_dict(): Chuyển đổi model thành dictionary
    """
    __tablename__ = 'categories'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Mã danh mục (DM000001, DM000002, ...)
    category_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Thông tin category
    key = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'SACH_TIENG_VIET' (định danh nội bộ)
    name = db.Column(db.String(100), nullable=False)  # e.g., 'Sách Tiếng Việt' (tên hiển thị)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # e.g., 'sach-tieng-viet' (dùng cho URL)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0)  # Thứ tự hiển thị trong UI (số nhỏ hơn hiển thị trước)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với tất cả fields
        2. Convert datetime sang ISO format string
        3. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin category
        """
        return {
            'id': self.id,
            'category_code': self.category_code,
            'key': self.key,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Cart(db.Model):
    """
    Model cho bảng Cart
    
    Mục đích:
    Quản lý giỏ hàng của user, lưu trữ các sách mà user muốn mua.
    
    Fields:
    - id: Primary key
    - user_id: Foreign key đến User (user sở hữu giỏ hàng)
    - book_id: Foreign key đến Book (sách trong giỏ hàng)
    - quantity: Số lượng sách
    - created_at: Thời gian thêm vào giỏ hàng
    
    Relationships:
    - user: User sở hữu cart item này (via backref)
    - book: Book trong cart item này (via backref)
    
    Methods:
    - to_dict(): Chuyển đổi model thành dictionary (bao gồm thông tin book)
    """
    __tablename__ = 'cart'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    # Thông tin cart item
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với các fields cơ bản
        2. Thêm thông tin book (nếu có) bằng cách gọi book.to_dict()
        3. Convert datetime sang ISO format string
        4. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin cart item (bao gồm book info)
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'book': self.book.to_dict() if self.book else None,  # Include book details
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
    """
    Model cho bảng Orders
    
    Mục đích:
    Quản lý đơn hàng của user, lưu trữ thông tin đơn hàng và trạng thái.
    
    Fields:
    - id: Primary key
    - user_id: Foreign key đến User (user đặt hàng)
    - total_amount: Tổng tiền đơn hàng
    - status: Trạng thái đơn hàng (pending/confirmed/cancelled/completed)
    - payment_status: Trạng thái thanh toán (pending/paid)
    - shipping_address: Địa chỉ giao hàng
    - created_at, updated_at: Timestamps
    
    Relationships:
    - user: User đặt đơn hàng này (via backref)
    - order_items: Danh sách items trong đơn hàng (one-to-many)
    
    Methods:
    - to_dict(): Chuyển đổi model thành dictionary (bao gồm order_items)
    """
    __tablename__ = 'orders'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign key
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Thông tin đơn hàng
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/confirmed/cancelled/completed
    payment_status = db.Column(db.String(20), default='pending', nullable=False)  # pending/paid
    shipping_address = db.Column(db.Text, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với các fields cơ bản
        2. Convert total_amount từ Decimal sang float
        3. Convert tất cả order_items sang dictionary
        4. Convert datetime sang ISO format string
        5. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin đơn hàng (bao gồm order_items)
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),  # Convert Decimal sang float
            'status': self.status,
            'payment_status': self.payment_status,
            'shipping_address': self.shipping_address,
            'order_items': [item.to_dict() for item in self.order_items],  # Convert all items
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderItem(db.Model):
    """
    Model cho bảng OrderItems
    
    Mục đích:
    Quản lý chi tiết từng item trong đơn hàng, lưu trữ thông tin sách và giá tại thời điểm mua.
    
    Fields:
    - id: Primary key
    - order_id: Foreign key đến Order (đơn hàng chứa item này)
    - book_id: Foreign key đến Book (sách trong item)
    - quantity: Số lượng sách
    - price: Giá bán tại thời điểm mua (lưu để không bị ảnh hưởng khi giá thay đổi sau)
    
    Relationships:
    - order: Order chứa item này (via backref)
    - book: Book trong item này (via backref)
    
    Methods:
    - to_dict(): Chuyển đổi model thành dictionary (bao gồm thông tin book)
    """
    __tablename__ = 'order_items'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Foreign keys
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    
    # Thông tin item
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Giá tại thời điểm mua (không thay đổi khi giá sách thay đổi)
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với các fields cơ bản
        2. Convert price từ Decimal sang float
        3. Thêm thông tin book (nếu có) bằng cách gọi book.to_dict()
        4. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin order item (bao gồm book info)
        """
        return {
            'id': self.id,
            'order_id': self.order_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'price': float(self.price),  # Convert Decimal sang float
            'book': self.book.to_dict() if self.book else None  # Include book details
        }

class Banner(db.Model):
    """
    Model cho bảng Banners
    
    Mục đích:
    Quản lý banner quảng cáo hiển thị trên trang chủ, có thể có link và custom colors.
    
    Fields:
    - id: Primary key
    - title: Tiêu đề banner
    - description: Mô tả banner
    - image_url: URL hình ảnh banner
    - link: Link khi click vào banner (optional, có thể là internal route hoặc external URL)
    - bg_color: Màu nền (hex color, default: #6366f1 - primary color)
    - text_color: Màu chữ (hex color, default: #ffffff - white)
    - position: Vị trí hiển thị (main, side_top, side_bottom)
    - display_order: Thứ tự hiển thị (số nhỏ hơn hiển thị trước)
    - is_active: Trạng thái hoạt động
    - created_at, updated_at: Timestamps
    
    Methods:
    - to_dict(): Chuyển đổi model thành dictionary
    """
    __tablename__ = 'banners'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True)
    
    # Mã banner (BN000001, BN000002, ...)
    banner_code = db.Column(db.String(20), unique=True, nullable=False)
    
    # Thông tin banner
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=True)  # Optional - can be empty for text-only banners
    link = db.Column(db.String(500))  # Optional link khi click vào banner (internal route hoặc external URL)
    
    # Styling
    bg_color = db.Column(db.String(50), default='#6366f1')  # Màu nền (hex color)
    text_color = db.Column(db.String(50), default='#ffffff')  # Màu chữ (hex color)
    
    # Display settings
    position = db.Column(db.String(20), default='main')  # Vị trí: main, side_top, side_bottom
    display_order = db.Column(db.Integer, default=0)  # Thứ tự hiển thị (số nhỏ hơn hiển thị trước)
    is_active = db.Column(db.Boolean, default=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        Chuyển đổi model thành dictionary để trả về JSON response
        
        Flow:
        1. Tạo dictionary với tất cả fields
        2. Convert datetime sang ISO format string
        3. Trả về dictionary
        
        Returns:
            dict: Dictionary chứa thông tin banner
        """
        return {
            'id': self.id,
            'banner_code': self.banner_code,
            'title': self.title,
            'description': self.description,
            'image_url': self.image_url,
            'link': self.link,
            'bg_color': self.bg_color,
            'text_color': self.text_color,
            'position': self.position,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

