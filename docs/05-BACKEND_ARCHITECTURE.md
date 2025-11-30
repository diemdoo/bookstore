# 05 - Kiến Trúc Backend Chi Tiết

## 📦 Tổng Quan

Backend được xây dựng với Flask framework, theo cấu trúc **đơn giản và dễ hiểu** để phù hợp với dự án tốt nghiệp. Code được thiết kế để dễ đọc, dễ giải thích và dễ báo cáo.

**📊 Xem Class Diagram:** [`diagrams/backend-class-diagram.mmd`](diagrams/backend-class-diagram.mmd)

## 🏗 Cấu Trúc Backend

```
backend/
├── app.py                    # Flask application chính
├── config.py                 # Configuration management
├── models.py                 # SQLAlchemy ORM models
├── seed_data.py              # Database seeding script
├── requirements.txt          # Python dependencies
│
├── routes/                   # 🔷 ROUTES LAYER (HTTP + Business Logic)
│   ├── auth.py              # Authentication endpoints
│   ├── books.py             # Books CRUD endpoints
│   ├── cart.py              # Shopping cart endpoints
│   ├── orders.py            # Orders management
│   ├── admin.py             # Admin operations
│   ├── categories.py        # Category management
│   ├── banners.py           # Banner management
│   ├── chatbot.py           # Chatbot FAQ endpoint
│   └── upload.py            # File upload handling
│
└── utils/                    # 🔷 UTILS LAYER (Helper Functions)
    ├── helpers.py           # Password hashing, decorators, validation
    └── storage.py           # Cloudflare R2 storage utilities
```

## 🎯 Nguyên Tắc Thiết Kế

### 1. Đơn Giản và Dễ Hiểu

- **Không có layer trung gian**: Routes trực tiếp tương tác với Models
- **Self-contained**: Mỗi route file chứa toàn bộ logic cần thiết
- **Clear comments**: Mỗi hàm có comment giải thích flow như mã giả

### 2. Code Style

- **File-level comment**: Mô tả mục đích file và các endpoints
- **Function-level comment**: Mô tả flow chi tiết từng bước
- **Inline comments**: Giải thích các bước quan trọng trong code

### 3. Transaction Safety

- Các operations phức tạp (như tạo đơn hàng) sử dụng database transaction
- Quản lý transaction trực tiếp trong route: `db.session.begin()`, `commit()`, `rollback()`

## 📝 Comment Style Guide

### File-level Comment

```python
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
- utils.helpers: Các hàm helper (hash_password, check_password, validate_email)
- flask.session: Quản lý session
"""
```

### Function-level Comment

```python
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
    # Implementation...
```

## 🔑 1. Routes Layer

### backend/routes/auth.py

**Chức năng:** Xử lý authentication (đăng ký, đăng nhập, đăng xuất, profile)

**Endpoints:**
- `POST /api/register` - Đăng ký tài khoản mới
- `POST /api/login` - Đăng nhập
- `POST /api/logout` - Đăng xuất
- `GET /api/me` - Lấy thông tin user hiện tại
- `PUT /api/profile` - Cập nhật profile

**Flow ví dụ (register):**
1. Lấy dữ liệu từ request body
2. Validate input (username, email, password)
3. Kiểm tra username/email đã tồn tại chưa (query User model)
4. Hash password với `hash_password()` từ utils
5. Tạo User mới và lưu vào database
6. Tạo session (tự động đăng nhập)
7. Trả về thông tin user

### backend/routes/books.py

**Chức năng:** Quản lý sách (list, search, detail, CRUD)

**Endpoints:**
- `GET /api/books` - Lấy danh sách sách (pagination, search, filter)
- `GET /api/books/<id>` - Chi tiết sách
- `GET /api/books/bestsellers` - Sách bán chạy
- `POST /api/books` - Tạo sách mới (admin)
- `PUT /api/books/<id>` - Cập nhật sách (admin)
- `DELETE /api/books/<id>` - Xóa sách (admin)

**Flow ví dụ (get_books với pagination):**
1. Lấy query parameters (page, per_page, search, category, etc.)
2. Build SQLAlchemy query với filters
3. Sử dụng `.paginate()` để phân trang
4. Trả về danh sách books với metadata (total, pages)

### backend/routes/cart.py

**Chức năng:** Quản lý giỏ hàng

**Endpoints:**
- `GET /api/cart` - Lấy giỏ hàng
- `POST /api/cart` - Thêm vào giỏ
- `PUT /api/cart/<id>` - Cập nhật số lượng
- `DELETE /api/cart/<id>` - Xóa khỏi giỏ

**Flow ví dụ (add_to_cart):**
1. Lấy user_id từ session
2. Lấy book_id và quantity từ request
3. Validate book tồn tại và còn stock
4. Kiểm tra đã có trong giỏ chưa (query Cart model)
5. Nếu có: cập nhật quantity
6. Nếu chưa: tạo Cart item mới
7. Trả về cart item

### backend/routes/orders.py

**Chức năng:** Quản lý đơn hàng (quan trọng nhất, có transaction)

**Endpoints:**
- `GET /api/orders` - Lấy lịch sử đơn hàng
- `POST /api/orders` - Tạo đơn hàng (checkout)
- `GET /api/orders/<id>` - Chi tiết đơn hàng

**Flow chi tiết (create_order - có transaction):**
1. Lấy user_id từ session
2. Lấy shipping_address từ request
3. **Bắt đầu transaction** (`db.session.begin()`)
4. Query tất cả Cart items của user (JOIN với Book)
5. Validate cart không rỗng
6. Với mỗi cart item:
   - Validate stock còn đủ
   - Tính tiền (price * quantity)
   - Cộng vào tổng tiền
7. Tạo Order mới
8. Với mỗi cart item:
   - Tạo OrderItem (lưu giá tại thời điểm mua)
   - Giảm stock của Book
9. Xóa tất cả Cart items
10. **Commit transaction** (`db.session.commit()`)
11. Trả về thông tin đơn hàng

**Nếu có lỗi:** Rollback transaction (`db.session.rollback()`)

### backend/routes/admin.py

**Chức năng:** Quản lý admin (users, orders, statistics)

**Endpoints:**
- `GET /api/admin/users` - Lấy danh sách users
- `PUT /api/admin/users/<id>/status` - Cập nhật trạng thái user
- `GET /api/admin/orders` - Lấy tất cả đơn hàng
- `PUT /api/admin/orders/<id>/status` - Cập nhật trạng thái đơn hàng
- `GET /api/admin/statistics` - Lấy thống kê

**Flow ví dụ (get_statistics):**
1. Tính tổng doanh thu (query Order với filter status='completed', payment_status='paid')
2. Đếm tổng số đơn hàng
3. Đếm số đơn theo từng trạng thái (group by status)
4. Query top 10 sách bán chạy (JOIN OrderItem, Order, Book, group by, order by)
5. Trả về object thống kê

### backend/routes/categories.py & backend/routes/banners.py

**Chức năng:** Quản lý categories và banners

**Flow tương tự:** Query Models trực tiếp, validate, CRUD operations

## 💾 2. Models Layer

### backend/models.py

**Chức năng:** Định nghĩa database schema và relationships

**Models:**
- `User` - Thông tin người dùng
- `Book` - Thông tin sách
- `Category` - Thể loại sách
- `Cart` - Giỏ hàng
- `Order` - Đơn hàng
- `OrderItem` - Chi tiết đơn hàng
- `Banner` - Banner quảng cáo

**Đặc điểm:**
- Sử dụng SQLAlchemy ORM
- Mỗi model có method `to_dict()` để serialize
- Định nghĩa relationships (1-N, N-N)
- Business methods (như `User.generate_customer_code()`)

**Ví dụ:**

```python
class User(db.Model):
    """
    User model - Lưu thông tin người dùng
    
    Table: users
    Roles: admin, customer
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(20), default='customer', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    customer_code = db.Column(db.String(20), unique=True, nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('Cart', backref='user', lazy=True)
    orders = db.relationship('Order', backref='user', lazy=True)
    
    def to_dict(self):
        """Convert User model thành dictionary (không có password_hash)"""
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
```

## 🔧 3. Utils Layer

### backend/utils/helpers.py

**Chức năng:** Helper functions dùng chung

**Functions:**
- `hash_password(password)` - Hash password với bcrypt
- `check_password(hashed, plain)` - Verify password
- `validate_email(email)` - Validate email format
- `validate_password(password)` - Validate password length
- `@login_required` - Decorator cho routes yêu cầu đăng nhập
- `@admin_required` - Decorator cho routes chỉ admin

**Ví dụ:**

```python
def hash_password(password: str) -> str:
    """
    Hash password với bcrypt
    
    Args:
        password (str): Plain text password
    
    Returns:
        str: Bcrypt hashed password
    """
    return bcrypt.hashpw(
        password.encode('utf-8'), 
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')

@wraps(f)
def login_required(f):
    """
    Decorator để protect routes yêu cầu authentication
    
    Kiểm tra session['user_id']. Nếu không có, return 401.
    """
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        return f(*args, **kwargs)
    return decorated_function
```

### backend/utils/storage.py

**Chức năng:** Cloudflare R2 storage operations

**Functions:**
- `upload_file(file, folder)` - Upload file lên R2 và trả về URL

## 📊 Ví Dụ Code Hoàn Chỉnh

### Ví dụ: routes/orders.py - create_order

```python
@orders_bp.route('/orders', methods=['POST'])
@login_required
def create_order():
    """
    Tạo đơn hàng mới (checkout)
    
    Flow chi tiết:
    1. Lấy user_id từ session (đã login)
    2. Lấy shipping_address từ request body
    3. Bắt đầu transaction (db.session.begin())
    4. Lấy tất cả items trong giỏ hàng của user
    5. Kiểm tra giỏ hàng không rỗng
    6. Với mỗi item trong giỏ:
       - Lấy thông tin sách từ database
       - Kiểm tra stock còn đủ không
       - Tính tiền (price * quantity)
       - Cộng vào tổng tiền
    7. Tạo Order mới với:
       - user_id
       - total_amount
       - shipping_address
       - status = 'pending'
       - payment_status = 'pending'
    8. Với mỗi item trong giỏ:
       - Tạo OrderItem (lưu giá tại thời điểm mua)
       - Giảm stock của sách
    9. Xóa tất cả items trong giỏ hàng
    10. Commit transaction (lưu tất cả thay đổi)
    11. Trả về thông tin đơn hàng
    
    Nếu có lỗi ở bất kỳ bước nào:
    - Rollback transaction (hủy tất cả thay đổi)
    - Trả về lỗi
    
    Returns:
        - 201: Tạo đơn hàng thành công
        - 400: Giỏ hàng rỗng hoặc không đủ stock
        - 500: Lỗi server
    """
    try:
        # Bước 1-2: Lấy dữ liệu
        user_id = session['user_id']
        data = request.get_json()
        shipping_address = data.get('shipping_address', '').strip()
        
        if not shipping_address:
            return jsonify({'error': 'Vui lòng nhập địa chỉ giao hàng'}), 400
        
        # Bước 3: Bắt đầu transaction
        db.session.begin()
        
        # Bước 4: Lấy cart items (JOIN với Book để lấy thông tin sách)
        cart_items = Cart.query.filter_by(user_id=user_id).join(Book).all()
        
        # Bước 5: Kiểm tra cart không rỗng
        if not cart_items:
            db.session.rollback()
            return jsonify({'error': 'Giỏ hàng trống'}), 400
        
        # Bước 6: Validate stock và tính tổng tiền
        total_amount = 0
        for cart_item in cart_items:
            book = cart_item.book
            if book.stock < cart_item.quantity:
                db.session.rollback()
                return jsonify({
                    'error': f'Sách "{book.title}" không đủ số lượng. Còn lại: {book.stock}'
                }), 400
            total_amount += book.price * cart_item.quantity
        
        # Bước 7: Tạo Order
        new_order = Order(
            user_id=user_id,
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='pending',
            payment_status='pending'
        )
        db.session.add(new_order)
        db.session.flush()  # Để lấy order.id
        
        # Bước 8: Tạo OrderItems và update stock
        for cart_item in cart_items:
            book = cart_item.book
            
            # Tạo OrderItem (lưu giá tại thời điểm mua)
            order_item = OrderItem(
                order_id=new_order.id,
                book_id=book.id,
                quantity=cart_item.quantity,
                price=book.price  # Lưu giá tại thời điểm mua
            )
            db.session.add(order_item)
            
            # Giảm stock
            book.stock -= cart_item.quantity
        
        # Bước 9: Xóa cart items
        for cart_item in cart_items:
            db.session.delete(cart_item)
        
        # Bước 10: Commit transaction
        db.session.commit()
        
        # Bước 11: Trả về thông tin đơn hàng
        return jsonify({
            'message': 'Đặt hàng thành công',
            'order': new_order.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi tạo đơn hàng: {str(e)}'}), 500
```

## 🎯 Best Practices

### 1. Error Handling

- Luôn sử dụng try-except cho các operations có thể fail
- Rollback transaction khi có lỗi
- Trả về error messages rõ ràng

### 2. Validation

- Validate input ở đầu function
- Validate business rules (stock, existence, etc.)
- Trả về 400 Bad Request cho validation errors

### 3. Transaction Management

- Sử dụng transaction cho operations phức tạp (tạo đơn hàng)
- Luôn rollback khi có lỗi
- Commit chỉ khi tất cả operations thành công

### 4. Code Comments

- File-level comment: Mô tả mục đích và endpoints
- Function-level comment: Mô tả flow chi tiết
- Inline comments: Giải thích các bước quan trọng

### 5. Security

- Hash passwords với bcrypt
- Sử dụng decorators `@login_required`, `@admin_required`
- Validate và sanitize input
- Không trả về sensitive data (password_hash)

## 📊 Summary

### Code Documentation Standards

1. **File-level docstring**: Mô tả file và các endpoints
2. **Function docstring**: Mô tả flow chi tiết từng bước
3. **Inline comments**: Giải thích logic phức tạp

### Key Patterns

- **Direct database access**: Routes trực tiếp query Models
- **Transaction management**: Quản lý transaction trong routes
- **Decorator Pattern**: Authentication và authorization
- **ORM Pattern**: Sử dụng SQLAlchemy để abstract database

### Best Practices Applied

✅ Simple and clear architecture  
✅ Comprehensive error handling  
✅ Transaction management  
✅ Input validation  
✅ Security (password hashing, session management)  
✅ Performance (pagination, indexes)  
✅ Clear comments (dễ báo cáo)

---

**📌 Note**: Tất cả backend code đều follow patterns và comment style được demonstrate trong document này. Code được thiết kế để dễ đọc, dễ hiểu và dễ giải thích cho thầy cô trong quá trình báo cáo tốt nghiệp.
