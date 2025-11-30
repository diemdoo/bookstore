# 04 - Tài Liệu API

> Tài liệu đầy đủ về REST API của hệ thống Bookstore

## 🌐 Base URL

```
Development: http://localhost:5000/api
Production:  https://api.bookstore.com/api
```

## 🔐 Authentication

Hệ thống sử dụng **Session-based Authentication**:
- Session cookie được gửi tự động với mỗi request
- Token không cần thiết (session được quản lý bởi Flask-Session)
- Admin routes yêu cầu role admin

### Headers

```
Content-Type: application/json
Cookie: session=<session_id>
```

## 📋 API Endpoints Overview

| Group | Count | Requires Auth | Description |
|-------|-------|---------------|-------------|
| **Auth** | 5 | Partial | Authentication & Profile |
| **Books** | 5 | Partial | Book catalog management |
| **Cart** | 4 | Yes | Shopping cart operations |
| **Orders** | 3 | Yes | Order management |
| **Admin** | 8+ | Yes (Admin) | Admin operations |
| **Banners** | 5 | Partial | Banner management |

## 🔑 Authentication API

### POST /api/register

**Đăng ký tài khoản mới**

**Request:**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123",
  "full_name": "Nguyễn Văn A"
}
```

**Response: 201 Created**
```json
{
  "message": "Đăng ký thành công",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "customer",
    "customer_code": "KH001",
    "is_active": true
  }
}
```

**Error: 400 Bad Request**
```json
{
  "error": "Username đã tồn tại"
}
```

---

### POST /api/login

**Đăng nhập hệ thống**

**Request:**
```json
{
  "username": "user123",
  "password": "password123"
}
```

**Response: 200 OK**
```json
{
  "message": "Đăng nhập thành công",
  "user": {
    "id": 1,
    "username": "user123",
    "role": "customer"
  }
}
```

---

### POST /api/logout

**Đăng xuất**

**Response: 200 OK**
```json
{
  "message": "Đăng xuất thành công"
}
```

---

### GET /api/me

**Lấy thông tin user hiện tại**

**Auth:** Required

**Response: 200 OK**
```json
{
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com",
    "full_name": "Nguyễn Văn A",
    "role": "customer",
    "customer_code": "KH001"
  }
}
```

---

### PUT /api/profile

**Cập nhật profile (Customer only)**

**Auth:** Required (Customer)

**Request:**
```json
{
  "full_name": "Nguyễn Văn B",
  "email": "newemail@example.com"
}
```

**Response: 200 OK**
```json
{
  "message": "Cập nhật thành công",
  "user": {...}
}
```

## 📚 Books API

### GET /api/books

**Lấy danh sách sách (có pagination)**

**Query Parameters:**
- `page` (int): Số trang (default: 1)
- `per_page` (int): Số items mỗi trang (default: 12, max: 100)
- `search` (string): Tìm kiếm theo title hoặc author
- `category` (string): Lọc theo thể loại
- `author` (string): Lọc theo tác giả

**Response: 200 OK**
```json
{
  "books": [
    {
      "id": 1,
      "title": "Đắc Nhân Tâm",
      "author": "Dale Carnegie",
      "category": "Kỹ năng sống",
      "price": 86000,
      "stock": 50,
      "image_url": "https://...",
      "publisher": "NXB Tổng Hợp",
      "pages": 320
    }
  ],
  "total": 30,
  "page": 1,
  "per_page": 12,
  "pages": 3
}
```

---

### GET /api/categories/:categoryKey/books/:id

**Lấy chi tiết sách theo category key và book id (RESTful endpoint)**

**URL Parameters:**
- `categoryKey` (string): Key của category (e.g., "Do Trang Tri", sẽ được URL encode tự động)
- `id` (int): ID của sách

**Response: 200 OK**
```json
{
  "book": {
    "id": 37,
    "title": "Bộ Bookmark Kim Loại - Hoa Văn",
    "author": "Tác giả",
    "description": "Mô tả sách (TEXT, không giới hạn ký tự, có thể nhập mô tả dài)",
    "price": 86000,
    "stock": 50,
    "category": "Do Trang Tri",
    "image_url": "https://...",
    "publisher": "NXB Tổng Hợp TP.HCM",
    "publish_date": "2020-01-15",
    "pages": 320,
    "dimensions": "14.5 x 20.5 cm",
    "weight": 400
  },
  "category_key": "Do Trang Tri"
}
```

**Error: 404 Not Found**
```json
{
  "error": "Sách không thuộc category này"
}
```

**Note:** 
- Endpoint này thay thế cho `/api/books/:id` (đã được xóa)
- Category key sẽ được URL encode tự động (e.g., "Do Trang Tri" -> "Do%20Trang%20Tri")
- API sẽ verify book thuộc đúng category trước khi trả về

---

### GET /api/books/bestsellers

**Lấy danh sách sách bán chạy nhất (dynamic query from order history)**

**Query Parameters:**
- `limit` (int, optional): Số lượng sách bán chạy cần lấy (default: 10)

**Response: 200 OK**
```json
{
  "books": [
    {
      "id": 1,
      "title": "Đắc Nhân Tâm",
      "author": "Dale Carnegie",
      "category": "Sach Tieng Viet",
      "price": 86000,
      "stock": 50,
      "image_url": "https://...",
      "publisher": "NXB Tổng Hợp",
      "pages": 320
    }
  ],
  "count": 10
}
```

**Logic:**
- Trả về top N sách dựa trên tổng số lượng đã bán (từ `order_items`)
- Nếu chưa có đơn hàng nào, trả về N sách đầu tiên (sắp xếp theo ID)

---

## 📁 Categories API

### GET /api/categories

**Lấy danh sách categories (Public)**

**Query Parameters:**
- `include_inactive` (boolean, optional): Include inactive categories (default: false, admin only)

**Response: 200 OK**
```json
{
  "categories": [
    {
      "id": 1,
      "key": "Sach Tieng Viet",
      "name": "Sách Tiếng Việt",
      "description": "Sách văn học, sách giáo khoa và tài liệu tiếng Việt",
      "display_order": 1,
      "is_active": true,
      "created_at": "2024-11-23T10:00:00",
      "updated_at": "2024-11-23T10:00:00"
    }
  ]
}
```

---

### GET /api/categories/:id

**Lấy chi tiết category**

**Response: 200 OK**
```json
{
  "category": {
    "id": 1,
    "key": "Sach Tieng Viet",
    "name": "Sách Tiếng Việt",
    "description": "Sách văn học, sách giáo khoa và tài liệu tiếng Việt",
    "display_order": 1,
    "is_active": true,
    "created_at": "2024-11-23T10:00:00",
    "updated_at": "2024-11-23T10:00:00"
  }
}
```

---

### GET /api/categories/:categoryKey/books

**Lấy danh sách sách theo category key (RESTful endpoint)**

**URL Parameters:**
- `categoryKey` (string): Key của category (e.g., "Do Trang Tri", sẽ được URL encode tự động)

**Query Parameters:**
- `page` (int, optional): Số trang (default: 1)
- `per_page` (int, optional): Số items mỗi trang (default: 12)

**Response: 200 OK**
```json
{
  "books": [
    {
      "id": 1,
      "title": "Đắc Nhân Tâm",
      "author": "Dale Carnegie",
      "category": "Do Trang Tri",
      "price": 86000,
      "stock": 50,
      "image_url": "https://...",
      "publisher": "NXB Tổng Hợp",
      "pages": 320
    }
  ],
  "total": 30,
  "page": 1,
  "per_page": 12,
  "pages": 3,
  "category_key": "Do Trang Tri"
}
```

**Note:** 
- Endpoint này là RESTful alternative cho `/api/books?category=categoryKey`
- Category key sẽ được URL encode tự động (e.g., "Do Trang Tri" -> "Do%20Trang%20Tri")
- Backward compatible: Endpoint `/api/books?category=...` vẫn hoạt động bình thường

---

### GET /api/categories/:categoryKey/books/:id

**Lấy chi tiết sách theo category key và book id**

Đã được mô tả ở phần Books API ở trên.

---

### POST /api/admin/categories

**Tạo category mới (Admin Only)**

**Request Body:**
```json
{
  "key": "Sach_Ngoai_Van",
  "name": "Sách Ngoại Văn",
  "description": "Sách nước ngoài dịch và nguyên bản",
  "display_order": 5,
  "is_active": true
}
```

**Response: 201 Created**
```json
{
  "message": "Tạo category thành công",
  "category": {
    "id": 5,
    "key": "Sach_Ngoai_Van",
    "name": "Sách Ngoại Văn",
    "description": "Sách nước ngoài dịch và nguyên bản",
    "display_order": 5,
    "is_active": true,
    "created_at": "2024-11-23T10:30:00",
    "updated_at": "2024-11-23T10:30:00"
  }
}
```

---

### PUT /api/admin/categories/:id

**Cập nhật category (Admin Only)**

**Request Body:**
```json
{
  "name": "Sách Nước Ngoài",
  "description": "Updated description",
  "display_order": 6,
  "is_active": false
}
```

**Response: 200 OK**
```json
{
  "message": "Cập nhật category thành công",
  "category": {
    "id": 5,
    "key": "Sach_Ngoai_Van",
    "name": "Sách Nước Ngoài",
    "description": "Updated description",
    "display_order": 6,
    "is_active": false,
    "created_at": "2024-11-23T10:30:00",
    "updated_at": "2024-11-23T10:35:00"
  }
}
```

---

### DELETE /api/admin/categories/:id

**Xóa category (Admin Only)**

**Response: 200 OK**
```json
{
  "message": "Xóa category thành công"
}
```

**Error: 400 Bad Request**
```json
{
  "error": "Không thể xóa category đang được sử dụng bởi sách"
}
```

---

### POST /api/books

**Tạo sách mới (Admin only)**

**Auth:** Required (Admin)

**Request:**
```json
{
  "title": "Tên sách",
  "author": "Tác giả",
  "category": "Thể loại",
  "description": "Mô tả sách (TEXT, không giới hạn ký tự, có thể nhập mô tả dài)",
  "price": 100000,
  "stock": 50,
  "image_url": "url",
  "publisher": "NXB",
  "publish_date": "2024-01-01",
  "pages": 300
}
```

**Field Notes:**
- `description`: TEXT type, **không giới hạn ký tự** - có thể nhập mô tả dài cho sách

---

### PUT /api/books/:id

**Cập nhật sách (Admin only)**

---

### DELETE /api/books/:id

**Xóa sách (Admin only)**

## 🛒 Cart API

### GET /api/cart

**Lấy giỏ hàng của user**

**Auth:** Required

**Response: 200 OK**
```json
{
  "cart_items": [
    {
      "id": 1,
      "user_id": 1,
      "book_id": 1,
      "quantity": 2,
      "book": {
        "id": 1,
        "title": "Đắc Nhân Tâm",
        "price": 86000,
        "image_url": "..."
      }
    }
  ],
  "total": 2
}
```

---

### POST /api/cart

**Thêm sách vào giỏ**

**Auth:** Required

**Request:**
```json
{
  "book_id": 1,
  "quantity": 2
}
```

**Response: 201 Created**
```json
{
  "message": "Đã thêm vào giỏ hàng",
  "cart_item": {...}
}
```

---

### PUT /api/cart/:id

**Cập nhật số lượng**

**Request:**
```json
{
  "quantity": 5
}
```

---

### DELETE /api/cart/:id

**Xóa item khỏi giỏ**

## 📦 Orders API

### POST /api/orders

**Tạo đơn hàng mới**

**Auth:** Required

**Request:**
```json
{
  "shipping_address": "123 Đường ABC, Quận XYZ",
  "phone": "0123456789"
}
```

**Response: 201 Created**
```json
{
  "message": "Đặt hàng thành công",
  "order": {
    "id": 1,
    "user_id": 1,
    "total_amount": 172000,
    "status": "pending",
    "payment_status": "pending",
    "shipping_address": "123 Đường ABC, Quận XYZ",
    "order_items": [
      {
        "id": 1,
        "order_id": 1,
        "book_id": 1,
        "quantity": 2,
        "price": 86000,
        "book": {
          "id": 1,
          "title": "Đắc Nhân Tâm",
          "author": "Dale Carnegie",
          "price": 86000,
          "image_url": "..."
        }
      }
    ],
    "created_at": "2024-01-01T10:00:00",
    "updated_at": "2024-01-01T10:00:00"
  }
}
```

---

### GET /api/orders

**Lấy danh sách đơn hàng của user**

---

### GET /api/orders/:id

**Lấy chi tiết đơn hàng**

## 👑 Admin API

### GET /api/admin/users

**Lấy danh sách users (Admin)**

**Auth:** Required (Admin)

---

### POST /api/admin/users

**Tạo user mới (Admin)**

---

### PUT /api/admin/users/:id

**Cập nhật user (Admin)**

---

### PUT /api/admin/users/:id/status

**Khóa/Mở tài khoản (Admin)**

**Request:**
```json
{
  "is_active": false
}
```

---

### GET /api/admin/orders

**Quản lý tất cả đơn hàng (Admin)**

**Auth:** Required (Admin)

**Response: 200 OK**
```json
{
  "orders": [
    {
      "id": 1,
      "user_id": 2,
      "total_amount": 172000,
      "status": "pending",
      "payment_status": "pending",
      "shipping_address": "123 Đường ABC, Quận XYZ",
      "order_items": [
        {
          "id": 1,
          "order_id": 1,
          "book_id": 1,
          "quantity": 2,
          "price": 86000,
          "book": {
            "id": 1,
            "title": "Đắc Nhân Tâm",
            "author": "Dale Carnegie",
            "price": 86000,
            "image_url": "..."
          }
        }
      ],
      "customer_code": "KH001",
      "customer_username": "user1",
      "customer_full_name": "Nguyễn Văn A",
      "created_at": "2024-01-01T10:00:00",
      "updated_at": "2024-01-01T10:00:00"
    }
  ]
}
```

**Note:** Response includes customer information (`customer_code`, `customer_username`, `customer_full_name`) to help admin identify which customer each order belongs to.

---

### PUT /api/admin/orders/:id/status

**Cập nhật trạng thái đơn hàng (Admin)**

**Auth:** Required (Admin)

**Request:**
```json
{
  "status": "confirmed",
  "payment_status": "paid"
}
```

**Status values:** `pending`, `confirmed`, `completed`, `cancelled`
**Payment Status values:** `pending`, `paid`

**Response: 200 OK**
```json
{
  "message": "Cập nhật trạng thái đơn hàng thành công",
  "order": {
    "id": 1,
    "user_id": 2,
    "status": "confirmed",
    "payment_status": "paid",
    ...
  }
}
```

---

### GET /api/admin/statistics

**Lấy thống kê (Admin)**

**Response:**
```json
{
  "total_revenue": 50000000,
  "total_orders": 150,
  "pending_orders": 10,
  "confirmed_orders": 20,
  "completed_orders": 100,
  "cancelled_orders": 20,
  "orders_by_status": {
    "pending": 10,
    "confirmed": 20,
    "completed": 100,
    "cancelled": 20
  },
  "top_books": [
    {
      "id": 1,
      "title": "Đắc Nhân Tâm",
      "author": "Dale Carnegie",
      "image_url": "https://cdn.duyne.me/books/uuid.jpg",
      "total_sold": 50
    }
  ]
}
```

## �� Banners API

### GET /api/banners

**Lấy danh sách banners**

**Query:** `?position=main|side_top|side_bottom|all`

---

### POST /api/banners

**Tạo banner (Admin)**

**Lưu ý:** Ảnh banner cần được upload trước qua `/api/admin/upload?folder=banners` để lấy URL, sau đó sử dụng URL này trong field `image_url` khi tạo banner.

**Request:**
```json
{
  "title": "Sale cuối năm",
  "description": "Giảm giá 50%",
  "image_url": "https://cdn.duyne.me/banners/uuid.jpg",
  "link": "/books?category=Sach Tieng Viet",
  "bg_color": "#6366f1",
  "text_color": "#ffffff",
  "position": "main",
  "display_order": 1,
  "is_active": true
}
```

---

### PUT /api/banners/:id

**Cập nhật banner (Admin)**

---

### PUT /api/banners/:id/status

**Active/Inactive banner (Admin)**

---

### DELETE /api/banners/:id

**Xóa banner (Admin)**

## ❌ Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required field: username"
}
```

### 401 Unauthorized
```json
{
  "error": "Yêu cầu đăng nhập"
}
```

### 403 Forbidden
```json
{
  "error": "Không có quyền truy cập"
}
```

### 404 Not Found
```json
{
  "error": "Không tìm thấy sách"
}
```

### 500 Internal Server Error
```json
{
  "error": "Lỗi server: <details>"
}
```

## 🧪 Testing với curl

### Register
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"pass123","full_name":"Test User"}'
```

### Login
```bash
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"username":"test","password":"pass123"}'
```

### Get Books (with session)
```bash
curl -X GET http://localhost:5000/api/books \
  -b cookies.txt
```

---

**📌 Notes:**
- Tất cả responses đều là JSON
- Dates theo format ISO 8601
- Prices là số nguyên (VND)
- Session cookie có `httponly=True` và `secure=True` (production)
