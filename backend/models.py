from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import datetime

# Khởi tạo SQLAlchemy instance để sử dụng trong toàn bộ ứng dụng
db = SQLAlchemy()

class User(db.Model):
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
    order_items = db.relationship('OrderItem', backref='book', lazy=True, cascade='all, delete-orphan')
    
    def get_sold_count(self):
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
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'book': self.book.to_dict() if self.book else None,  # Include book details
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
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
        return {
            'id': self.id,
            'order_id': self.order_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'price': float(self.price),  # Convert Decimal sang float
            'book': self.book.to_dict() if self.book else None  # Include book details
        }

class Banner(db.Model):
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