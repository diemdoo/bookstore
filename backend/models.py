"""
SQLAlchemy Models cho database
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    """Model cho bảng Users"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='customer', nullable=False)  # admin hoặc customer
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    customer_code = db.Column(db.String(20), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='user', lazy=True, cascade='all, delete-orphan')
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
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
        """Generate next customer code (KH001, KH002, ...)"""
        last_customer = User.query.filter(
            User.customer_code.isnot(None)
        ).order_by(User.customer_code.desc()).first()
        
        if last_customer and last_customer.customer_code:
            last_num = int(last_customer.customer_code[2:])
            new_num = last_num + 1
        else:
            new_num = 1
        
        return f'KH{new_num:03d}'
    

class Book(db.Model):
    """Model cho bảng Books"""
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Will reference Category.key
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    image_url = db.Column(db.String(500), nullable=True)
    
    # Thông tin chi tiết
    publisher = db.Column(db.String(200), nullable=True)  # Nhà xuất bản
    publish_date = db.Column(db.String(20), nullable=True)  # Ngày xuất bản (format: DD/MM/YYYY)
    distributor = db.Column(db.String(200), nullable=True)  # Nhà phát hành
    dimensions = db.Column(db.String(100), nullable=True)  # Kích thước (cm)
    pages = db.Column(db.Integer, nullable=True)  # Số trang
    weight = db.Column(db.Integer, nullable=True)  # Trọng lượng (gram)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='book', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='book', lazy=True)
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'author': self.author,
            'category': self.category,
            'description': self.description,
            'price': float(self.price),
            'stock': self.stock,
            'image_url': self.image_url,
            'publisher': self.publisher,
            'publish_date': self.publish_date,
            'distributor': self.distributor,
            'dimensions': self.dimensions,
            'pages': self.pages,
            'weight': self.weight,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Category(db.Model):
    """Model cho bảng Categories"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 'Sach_Tieng_Viet'
    name = db.Column(db.String(100), nullable=False)  # e.g., 'Sách Tiếng Việt'
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0)  # Order of display in UI
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Cart(db.Model):
    """Model cho bảng Cart"""
    __tablename__ = 'cart'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'book': self.book.to_dict() if self.book else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Order(db.Model):
    """Model cho bảng Orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)  # pending/confirmed/cancelled/completed
    payment_status = db.Column(db.String(20), default='pending', nullable=False)  # pending/paid
    shipping_address = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'total_amount': float(self.total_amount),
            'status': self.status,
            'payment_status': self.payment_status,
            'shipping_address': self.shipping_address,
            'order_items': [item.to_dict() for item in self.order_items],
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class OrderItem(db.Model):
    """Model cho bảng OrderItems"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # Giá tại thời điểm mua
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'book_id': self.book_id,
            'quantity': self.quantity,
            'price': float(self.price),
            'book': self.book.to_dict() if self.book else None
        }

class Banner(db.Model):
    """Model cho bảng Banners"""
    __tablename__ = 'banners'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500), nullable=False)
    link = db.Column(db.String(500))  # Optional link when clicking banner
    bg_color = db.Column(db.String(50), default='#6366f1')  # Background color
    text_color = db.Column(db.String(50), default='#ffffff')  # Text color
    position = db.Column(db.String(20), default='main')  # main, side_top, side_bottom
    display_order = db.Column(db.Integer, default=0)  # Order of display
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Chuyển đổi model thành dictionary"""
        return {
            'id': self.id,
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

