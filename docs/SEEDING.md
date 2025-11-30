# Database Seeding Guide

## Tổng Quan

Script `backend/seed_data.py` được sử dụng để seed dữ liệu ban đầu cho database, bao gồm:
- Admin user và test users (customers)
- Categories (Danh mục sản phẩm)
- Books (Sách và sản phẩm)
- Banners (Banner quảng cáo)

## Cách Chạy Seed

### 1. Seed Tự Động (Mặc Định)

Khi backend khởi động, seed script sẽ tự động chạy trong `backend/app.py`:

```python
from seed_data import seed_database
with app.app_context():
    seed_database()
```

**Lưu ý:** Seed script có cơ chế idempotent - nếu đã có users trong database, nó sẽ **skip** và không seed lại.

### 2. Seed Thủ Công (Khi Cần)

#### Option A: Exec vào Backend Container

```bash
# Development
docker-compose exec backend python -c "from app import app; from seed_data import seed_database; app.app_context().push(); seed_database()"

# Production
docker-compose -f docker-compose.prod.yml exec backend python -c "from app import app; from seed_data import seed_database; app.app_context().push(); seed_database()"
```

#### Option B: Reseed Books và Banners (Giữ Nguyên Users)

Nếu bạn muốn reseed books và banners nhưng giữ nguyên users và categories:

```bash
# Tạo script reseed_books.py
cat > backend/reseed_books.py << 'EOF'
from app import create_app
from seed_data import seed_database

app = create_app()
with app.app_context():
    seed_database(force_reseed_books=True)
EOF

# Chạy script
docker-compose -f docker-compose.prod.yml exec backend python reseed_books.py
```

### 3. Seed Categories Riêng (Nếu Thiếu)

Nếu categories bị thiếu nhưng users đã có:

```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app import create_app
from models import db, Category

app = create_app()
with app.app_context():
    categories = [
        {'key': 'Sach Tieng Viet', 'name': 'Sách Tiếng Việt', 'description': 'Sách văn học, sách giáo khoa và tài liệu tiếng Việt', 'display_order': 1, 'is_active': True},
        {'key': 'Truyen Tranh', 'name': 'Truyện Tranh', 'description': 'Truyện tranh, manga, comic từ nhiều quốc gia', 'display_order': 2, 'is_active': True},
        {'key': 'Do Trang Tri', 'name': 'Đồ Trang Trí - Lưu Niệm', 'description': 'Đồ trang trí, quà lưu niệm và phụ kiện đọc sách', 'display_order': 3, 'is_active': True},
        {'key': 'Van Phong Pham', 'name': 'Văn Phòng Phẩm', 'description': 'Văn phòng phẩm, dụng cụ học tập và làm việc', 'display_order': 4, 'is_active': True}
    ]
    for cat_data in categories:
        existing = Category.query.filter_by(key=cat_data['key']).first()
        if not existing:
            category = Category(**cat_data)
            db.session.add(category)
    db.session.commit()
    print('Categories seeded!')
"
```

## Dữ Liệu Được Seed

### Users
- **Admin:** `admin` / `admin123`
- **Customer 1:** `user1` / `pass123` (KH001)
- **Customer 2:** `user2` / `pass123` (KH002)

### Categories (4 categories)
- Sách Tiếng Việt (21 books)
- Truyện Tranh (15 books)
- Đồ Trang Trí - Lưu Niệm (15 books)
- Văn Phòng Phẩm (15 books)

### Books (66 books total)
- Sach Tieng Viet: 21 books
- Truyen Tranh: 15 books
- Do Trang Tri: 15 books
- Van Phong Pham: 15 books

### Banners (5 banners)
- **3 main banners**: Tất cả link đến `/books?category=Sach Tieng Viet`
  - "GIẢM GIÁ 50% - ĐẮC NHÂN TÂM"
  - "NHÀ GIẢ KIM - GIẢM 30%"
  - "SAPIENS - SÁCH MỚI"
- **2 side banners**:
  - "FLASH SALE HÔM NAY" → `/books?category=Truyen Tranh`
  - "SÁCH THIẾU NHI" → `/books?category=Van Phong Pham`

## Troubleshooting

### Vấn Đề: Categories Không Được Seed

**Nguyên nhân:** Seed script check `if User.query.first() is not None` nên skip khi đã có users.

**Giải pháp:**
1. Seed categories thủ công (xem Option 3 ở trên)
2. Hoặc reseed toàn bộ (xóa database và restart)

### Vấn Đề: Books Không Match Với Categories

**Nguyên nhân:** Books đang dùng category names cũ (ví dụ: "Tiểu thuyết") thay vì category keys mới (ví dụ: "Sach Tieng Viet").

**Giải pháp:** Reseed books:
```bash
docker-compose -f docker-compose.prod.yml exec backend python -c "
from app import create_app
from seed_data import seed_database
app = create_app()
with app.app_context():
    seed_database(force_reseed_books=True)
"
```

### Vấn Đề: Database Trống Sau Khi Restart

**Nguyên nhân:** Database volume không được mount hoặc bị xóa.

**Giải pháp:** 
1. Kiểm tra `docker-compose.yml` có mount volume cho database không
2. Đảm bảo seed script chạy khi backend khởi động
3. Nếu cần, seed thủ công (xem Option 2)

## Kiểm Tra Seed Thành Công

```bash
# Kiểm tra users
docker-compose -f docker-compose.prod.yml exec db psql -U bookstore_user -d bookstore -c "SELECT COUNT(*) FROM users;"

# Kiểm tra categories
docker-compose -f docker-compose.prod.yml exec db psql -U bookstore_user -d bookstore -c "SELECT key, name FROM categories;"

# Kiểm tra books theo category
docker-compose -f docker-compose.prod.yml exec db psql -U bookstore_user -d bookstore -c "SELECT category, COUNT(*) FROM books GROUP BY category;"

# Kiểm tra banners
docker-compose -f docker-compose.prod.yml exec db psql -U bookstore_user -d bookstore -c "SELECT COUNT(*) FROM banners;"
```

## Lưu Ý

1. **Idempotent:** Seed script được thiết kế để có thể chạy nhiều lần mà không gây lỗi (trừ khi `force_reseed_books=True`).

2. **Production:** Trong production, nên seed một lần khi deploy lần đầu. Sau đó chỉ reseed khi cần update dữ liệu mẫu.

3. **Best Sellers:** "Sản phẩm bán chạy" được tính động từ lịch sử đơn hàng (`OrderItem`), không phải từ seed data.

4. **Categories:** Categories được lưu trong database, không còn hardcode trong `constants.py`.

