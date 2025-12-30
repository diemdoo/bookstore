"""
Database seed script with sample data for Bookstore
Includes admin user, test customers, sample books, categories, banners, and orders
"""
from models import db, User, Book, Banner, Category, Order, OrderItem
from utils.helpers import hash_password, generate_slug, generate_unique_book_slug, generate_book_code, generate_category_code, generate_banner_code
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import text, inspect
from seed_orders import seed_orders
def seed_database():
    """Seed the database with initial data (chỉ chạy một lần khi database trống)"""
    print(" Starting database seed...")
    
    
    # Check if users already exist (wrap in try-except in case column doesn't exist yet)
    try:
        existing_admin = User.query.filter_by(username='admin').first()
        existing_user1 = User.query.filter_by(username='user1').first()
        existing_user2 = User.query.filter_by(username='user2').first()

        # Early return: Only skip if admin, user1, and user2 all exist
        # This ensures admin is always created even if other users exist
        if existing_admin and existing_user1 and existing_user2:
            # Check if books also exist to confirm full seeding
            if Book.query.first() is not None:
                print("Database already seeded. Skipping seed process.")
                return
    except Exception as e:
        # If schema not ready, continue with seeding
        if 'does not exist' in str(e) or 'customer_code' in str(e):
            print("Database schema not fully ready, continuing with seed...")
            existing_admin = None
            existing_user1 = None
            existing_user2 = None
        else:
            raise
    
    # Create Admin User (if not exists)
    if not existing_admin:
        admin = User(
            username='admin',
            password_hash=hash_password('admin123'),
            email='admin@bookstore.com',
            full_name='Administrator',
            role='admin',
            is_active=True
        )
        db.session.add(admin)
        print("Created admin user (admin/admin123)")
    else:
        print("Admin user already exists")

    # Create Test Customers with customer codes (if not exist)
    # Check if customer_code column exists by trying to query it
    has_customer_code_column = True
    try:
        # Try a simple query that would fail if column doesn't exist
        db.session.execute(text("SELECT customer_code FROM users LIMIT 1"))
    except Exception:
        has_customer_code_column = False
    
    if not existing_user1:
        user1_data = {
            'username': 'user1',
            'password_hash': hash_password('pass123'),
            'email': 'user1@example.com',
            'full_name': 'Nguyễn Văn A',
            'role': 'customer',
            'is_active': True
        }
        if has_customer_code_column:
            user1_data['customer_code'] = 'KH001'  # First customer
        user1 = User(**user1_data)
        db.session.add(user1)
        if has_customer_code_column:
            print("Created user1 (user1/pass123, Customer KH001)")
        else:
            print("Created user1 (user1/pass123)")
    else:
        print("User1 already exists")
    
    if not existing_user2:
        user2_data = {
            'username': 'user2',
            'password_hash': hash_password('pass123'),
            'email': 'user2@example.com',
            'full_name': 'Trần Thị B',
            'role': 'customer',
            'is_active': True
        }
        if has_customer_code_column:
            user2_data['customer_code'] = 'KH002'  # Second customer
        user2 = User(**user2_data)
        db.session.add(user2)
        if has_customer_code_column:
            print("Created user2 (user2/pass123, Customer KH002)")
        else:
            print("Created user2 (user2/pass123)")
    else:
        print("User2 already exists")

    # Commit initial users (admin, user1, user2) immediately
    # to prevent autoflush issues when creating categories
    try:
        db.session.commit()
        print("Committed initial users (admin, user1, user2)")
    except Exception as e:
        db.session.rollback()
        print(f"Warning committing initial users: {e}")
    
    # Create additional 18 customers (total 20 customers)
    # Vietnamese names for realistic test data
    vietnamese_names = [
        ('user3', 'user3@example.com', 'Lê Văn C', 'KH003'),
        ('user4', 'user4@example.com', 'Phạm Thị D', 'KH004'),
        ('user5', 'user5@example.com', 'Hoàng Văn E', 'KH005'),
        ('user6', 'user6@example.com', 'Vũ Thị F', 'KH006'),
        ('user7', 'user7@example.com', 'Đặng Văn G', 'KH007'),
        ('user8', 'user8@example.com', 'Bùi Thị H', 'KH008'),
        ('user9', 'user9@example.com', 'Đỗ Văn I', 'KH009')
    ]
    
    # Commit users in batches to avoid large transactions
    batch_size = 5
    for i, (username, email, full_name, customer_code) in enumerate(vietnamese_names):
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            user_data = {
                'username': username,
                'password_hash': hash_password('pass123'),
                'email': email,
                'full_name': full_name,
                'role': 'customer',
                'is_active': True
            }
            if has_customer_code_column:
                user_data['customer_code'] = customer_code
            new_user = User(**user_data)
            db.session.add(new_user)
            if has_customer_code_column:
                print(f"Created {username} ({username}/pass123, Customer {customer_code})")
            else:
                print(f"Created {username} ({username}/pass123)")
        else:
            print(f"{username} already exists")
        
        # Commit every batch_size users or at the end
        if (i + 1) % batch_size == 0 or i == len(vietnamese_names) - 1:
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Warning committing users batch: {e}")
    
    # Create Categories
    from utils.helpers import generate_slug
    
    sample_categories = [
        {
            'key': 'SACH_TIENG_VIET',
            'name': 'Sách Tiếng Việt',
            'slug': 'sach-tieng-viet',
            'description': 'Sách văn học, sách giáo khoa và tài liệu tiếng Việt',
            'display_order': 1,
            'is_active': True
        },
        {
            'key': 'TRUYEN_TRANH',
            'name': 'Truyện Tranh',
            'slug': 'truyen-tranh',
            'description': 'Truyện tranh, manga, comic từ nhiều quốc gia',
            'display_order': 2,
            'is_active': True
        },
        {
            'key': 'DO_TRANG_TRI',
            'name': 'Đồ Trang Trí - Lưu Niệm',
            'slug': 'do-trang-tri-luu-niem',
            'description': 'Đồ trang trí, quà lưu niệm và phụ kiện đọc sách',
            'display_order': 3,
            'is_active': True
        },
        {
            'key': 'VAN_PHONG_PHAM',
            'name': 'Văn Phòng Phẩm',
            'slug': 'van-phong-pham',
            'description': 'Văn phòng phẩm, dụng cụ học tập và làm việc',
            'display_order': 4,
            'is_active': True
        }
    ]
    
    # Check if slug column exists
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('categories')]
        has_slug_column = 'slug' in columns
    except Exception:
        # Table might not exist yet, db.create_all() will create it
        has_slug_column = False
    
    created_count = 0
    skipped_count = 0
    
    # Query max category_code once before the loop to avoid duplicate codes
    # Track next number in memory to ensure uniqueness within the batch
    if has_slug_column:
        from sqlalchemy import func
        max_code = db.session.query(func.max(Category.category_code)).scalar()
        if max_code:
            next_category_number = int(max_code[2:]) + 1
        else:
            next_category_number = 1
    else:
        next_category_number = 1
    
    # Only create categories if they don't exist (check by slug if available, else by key)
    for category_data in sample_categories:
        try:
            # Check existence by slug if column exists, else by key
            if has_slug_column:
                result = db.session.execute(
                    text("SELECT id FROM categories WHERE slug = :slug"),
                    {'slug': category_data['slug']}
                )
            else:
                result = db.session.execute(
                    text("SELECT id FROM categories WHERE key = :key"),
                    {'key': category_data['key']}
                )
            existing_row = result.fetchone()
            
            if existing_row:
                # Category already exists, skip
                skipped_count += 1
                if has_slug_column:
                    print(f"  Category '{category_data['slug']}' already exists, skipping")
                else:
                    print(f"  Category '{category_data['key']}' already exists, skipping")
            else:
                # Create new category
                try:
                    if has_slug_column:
                        # Table has slug column, use ORM and generate category_code
                        # Generate category_code from memory counter to ensure uniqueness within batch
                        category_code = f'DM{next_category_number:06d}'
                        next_category_number += 1
                        
                        # Use no_autoflush to prevent premature flush during category creation
                        with db.session.no_autoflush:
                            category_data_with_code = {**category_data, 'category_code': category_code}
                            category = Category(**category_data_with_code)
                            db.session.add(category)
                        created_count += 1
                    else:
                        # Table doesn't have slug column yet, use raw SQL without slug
                        db.session.execute(
                            text("""
                                INSERT INTO categories (key, name, description, display_order, is_active, created_at, updated_at)
                                VALUES (:key, :name, :description, :display_order, :is_active, :created_at, :updated_at)
                            """),
                            {
                                'key': category_data['key'],
                                'name': category_data['name'],
                                'description': category_data['description'],
                                'display_order': category_data['display_order'],
                                'is_active': category_data['is_active'],
                                'created_at': datetime.utcnow(),
                                'updated_at': datetime.utcnow()
                            }
                        )
                        created_count += 1
                except Exception as insert_error:
                    # Handle duplicate key/slug constraint violation gracefully
                    error_str = str(insert_error)
                    if 'unique' in error_str.lower() or 'duplicate' in error_str.lower():
                        skipped_count += 1
                        if has_slug_column:
                            print(f"  Category '{category_data['slug']}' already exists (duplicate constraint), skipping")
                        else:
                            print(f"  Category '{category_data['key']}' already exists (duplicate constraint), skipping")
                        db.session.rollback()
                    else:
                        # Other error, log and skip
                        print(f"Error creating category '{category_data.get('name', 'unknown')}': {str(insert_error)}")
                        db.session.rollback()
        except Exception as e:
            # If categories table doesn't exist or other error, skip this category
            print(f"Skipping category '{category_data.get('name', 'unknown')}': {str(e)}")
            db.session.rollback()
            continue
    
    try:
        db.session.commit()
        if created_count > 0:
            print(f"Created {created_count} new categories")
        if skipped_count > 0:
            print(f"Skipped {skipped_count} existing categories")
        if created_count == 0 and skipped_count == 0:
            print(f"Categories check completed")
    except Exception as e:
        db.session.rollback()
        print(f"Category seed failed: {str(e)}")
    
    # Create Sample Books (20 books total)
    # Distribution: 5 books per category (Sach Tieng Viet, Truyen Tranh, Do Trang Tri, Van Phong Pham)
    # Note: Best Sellers are now dynamically computed from order history via /api/books/bestsellers
    sample_books = [
        # ===== CATEGORY: Sach Tieng Viet (5 books) =====
        {
            'title': 'Đắc Nhân Tâm',
            'author': 'Dale Carnegie',
            'publisher': 'NXB Tổng Hợp TP.HCM',
            'publish_date': '2020-01-15',
            'price': 86000,
            'stock': 50,
            'description': 'Đắc Nhân Tâm của Dale Carnegie là quyển sách nổi tiếng nhất, bán chạy nhất và có tầm ảnh hưởng nhất của mọi thời đại.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 320,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Nhà Giả Kim',
            'author': 'Paulo Coelho',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2019-05-20',
            'price': 79000,
            'stock': 45,
            'description': 'Tất cả những trải nghiệm trong chuyến phiêu du theo đuổi vận mệnh của mình đã giúp Santiago thấu hiểu được ý nghĩa sâu xa nhất của hạnh phúc.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 227,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Sapiens: Lược Sử Loài Người',
            'author': 'Yuval Noah Harari',
            'publisher': 'NXB Thế Giới',
            'publish_date': '2018-09-10',
            'price': 198000,
            'stock': 30,
            'description': 'Sapiens là một cuốn sách đột phá về lịch sử nhân loại, từ khi xuất hiện cho đến ngày nay.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 543,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Tuổi Trẻ Đáng Giá Bao Nhiêu',
            'author': 'Rosie Nguyễn',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2021-03-05',
            'price': 90000,
            'stock': 60,
            'description': 'Bạn hối tiếc vì không nỗ lực hết mình khi còn trẻ, bởi vì bạn không thể có được những gì mình muốn.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 268,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Nghĩ Giàu & Làm Giàu',
            'author': 'Napoleon Hill',
            'publisher': 'NXB Lao Động',
            'publish_date': '2019-11-20',
            'price': 125000,
            'stock': 35,
            'description': 'Cuốn sách này đã giúp hàng triệu người trên thế giới đạt được thành công trong cuộc sống.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 382,
            'category': 'SACH_TIENG_VIET'
        },
        # ===== CATEGORY: Truyen Tranh =====
        {
            'title': 'One Piece - Tập 1',
            'author': 'Oda Eiichiro',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-01-10',
            'price': 25000,
            'stock': 100,
            'description': 'Câu chuyện về hải tặc Luffy và ước mơ trở thành vua hải tặc.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 192,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Naruto - Tập 1',
            'author': 'Kishimoto Masashi',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-11-05',
            'price': 25000,
            'stock': 95,
            'description': 'Ninja Naruto và ước mơ trở thành Hokage làng Lá.',
            'image_url': 'https://cdn.diemdoo.me/books/a1ba0dfd-23f8-4522-ba70-df78aa5c27a2.jpg',
            'pages': 184,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Dragon Ball - Tập 1',
            'author': 'Toriyama Akira',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2018-06-20',
            'price': 22000,
            'stock': 88,
            'description': 'Cuộc phiêu lưu tìm kiếm bảy viên ngọc rồng của Son Goku.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 200,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Doraemon - Tập 1',
            'author': 'Fujiko F. Fujio',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-03-15',
            'price': 20000,
            'stock': 120,
            'description': 'Chú mèo máy đến từ tương lai và những bảo bối kỳ diệu.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 176,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Attack on Titan - Tập 1',
            'author': 'Hajime Isayama',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2021-02-10',
            'price': 28000,
            'stock': 80,
            'description': 'Câu chuyện về cuộc chiến sinh tồn của loài người trước những Titan khổng lồ.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 200,
            'category': 'TRUYEN_TRANH'
        },
        # ===== CATEGORY: Do Trang Tri (5 books) =====
        {
            'title': 'Sổ Tay Ghi Chép A5',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 45000,
            'stock': 150,
            'description': 'Sổ tay ghi chép chất lượng cao, giấy dày, bìa cứng, kích thước A5.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 200,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Bút Máy Cao Cấp',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 85000,
            'stock': 80,
            'description': 'Bút máy cao cấp với ngòi mực mượt mà, thiết kế sang trọng.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Bộ Thước Kẻ Vẽ Kỹ Thuật',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 65000,
            'stock': 100,
            'description': 'Bộ thước kẻ vẽ kỹ thuật chuyên nghiệp, đầy đủ các kích thước.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Kẹp Sách Từ Tính',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 35000,
            'stock': 200,
            'description': 'Kẹp sách từ tính tiện lợi, giữ trang sách một cách chắc chắn.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Bìa Bọc Sách Nhựa',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 25000,
            'stock': 180,
            'description': 'Bìa bọc sách nhựa trong suốt, bảo vệ sách khỏi bụi bẩn và nước.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        # ===== CATEGORY: Van Phong Pham (5 books) =====
        {
            'title': 'Bút Bi 0.5mm',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 12000,
            'stock': 500,
            'description': 'Bút bi ngòi 0.5mm, mực đen, viết mượt mà, bền bỉ.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Tẩy Chuột Chất Lượng',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 15000,
            'stock': 300,
            'description': 'Tẩy chuột chất lượng cao, không làm bẩn giấy, mùi thơm.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Compa Vẽ Hình Tròn',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 55000,
            'stock': 120,
            'description': 'Compa vẽ hình tròn chuyên nghiệp, độ chính xác cao.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Bút Chì 2B',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 8000,
            'stock': 400,
            'description': 'Bút chì 2B chất lượng, mềm mại, dễ tẩy xóa.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Giấy Vở Kẻ Ngang',
            'author': 'N/A',
            'publisher': 'Nhà sản xuất',
            'publish_date': '2023-01-01',
            'price': 18000,
            'stock': 250,
            'description': 'Giấy vở kẻ ngang, 200 tờ, chất lượng tốt, không bị lem mực.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
        'pages': 200,
            'category': 'VAN_PHONG_PHAM'
        },
    ]
    
    # Check if books already exist
    existing_books = Book.query.first()
    if existing_books:
        print(f"✓ Books already exist ({Book.query.count()} books), skipping book creation")
    else:
        # Check if books table has slug column
        has_book_slug_column = False
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('books')]
            has_book_slug_column = 'slug' in columns
        except Exception:
            pass
        
        created_books_count = 0
        skipped_books_count = 0
        
        for book_data in sample_books:
            try:
                title = book_data.get('title', '')
                if not title:
                    continue
                
                # Check if book already exists
                existing_book = None
                slug = None
                
                if has_book_slug_column:
                    # Generate slug from title
                    base_slug = generate_slug(title)
                    if not base_slug:
                        print(f"Cannot generate slug for book '{title}', skipping")
                        continue
                    
                    # Check if book already exists by base_slug (match base_slug, base_slug-1, base_slug-2, etc.)
                    # This prevents duplicate books when seed runs multiple times
                    existing_book_result = db.session.execute(
                        text("SELECT id FROM books WHERE slug = :base_slug OR slug LIKE :pattern LIMIT 1"),
                        {'base_slug': base_slug, 'pattern': f'{base_slug}-%'}
                    ).fetchone()
                    
                    if existing_book_result:
                        skipped_books_count += 1
                        print(f"  Book with base_slug '{base_slug}' already exists, skipping")
                        continue
                    
                    # Generate unique slug using raw SQL query to ensure we see existing books in database
                    # This avoids SQLAlchemy session issues
                    slug = base_slug
                    counter = 1
                    while True:
                        # Use raw SQL to check if slug exists in database (not just in session)
                        slug_check = db.session.execute(
                            text("SELECT id FROM books WHERE slug = :slug LIMIT 1"),
                            {'slug': slug}
                        ).fetchone()
                        
                        if not slug_check:
                            break  # Slug is unique, use it
                        
                        # Slug exists, try next number
                        slug = f"{base_slug}-{counter}"
                        counter += 1
                else:
                    # Fallback: check by title using raw SQL if slug column doesn't exist
                    # (to avoid SQLAlchemy trying to query slug column)
                    result = db.session.execute(
                        text("SELECT id FROM books WHERE title = :title LIMIT 1"),
                        {'title': title}
                    ).fetchone()
                    if result:
                        # Don't use Book.query.get() here as it will try to query slug column
                        existing_book = True  # Just mark as existing
                
                if existing_book:
                    skipped_books_count += 1
                    print(f"  Book '{title}' already exists, skipping")
                    continue
                
                # Add slug to book_data if column exists
                if has_book_slug_column:
                    book_data['slug'] = slug
                    print(f"Generated slug: '{slug}' for book '{title}'")
                else:
                    print(f"Slug column not found, book '{title}' will be created without slug")
                
                # Create book
                if has_book_slug_column:
                    # Generate book_code
                    book_code = generate_book_code(Book)
                    book_data['book_code'] = book_code
                    print(f"Generated book_code: '{book_code}' for book '{title}'")
                    
                    book = Book(**book_data)
                    db.session.add(book)
                    created_books_count += 1
                else:
                    # Use raw SQL if slug column doesn't exist
                    db.session.execute(
                        text("""
                            INSERT INTO books (title, author, category, description, price, stock, image_url, publisher, publish_date, pages, created_at, updated_at)
                            VALUES (:title, :author, :category, :description, :price, :stock, :image_url, :publisher, :publish_date, :pages, :created_at, :updated_at)
                        """),
                        {
                            'title': book_data.get('title'),
                            'author': book_data.get('author'),
                            'category': book_data.get('category'),
                            'description': book_data.get('description'),
                            'price': book_data.get('price', 0),
                            'stock': book_data.get('stock', 0),
                            'image_url': book_data.get('image_url'),
                            'publisher': book_data.get('publisher'),
                            'publish_date': book_data.get('publish_date'),
                            'pages': book_data.get('pages', 0),
                            'created_at': datetime.utcnow(),
                            'updated_at': datetime.utcnow()
                        }
                    )
                    created_books_count += 1
            except Exception as e:
                error_str = str(e)
                if 'unique' in error_str.lower() or 'duplicate' in error_str.lower():
                    skipped_books_count += 1
                    print(f"  Book '{book_data.get('title', 'unknown')}' already exists (duplicate constraint), skipping")
                    db.session.rollback()
                else:
                    print(f"Error creating book '{book_data.get('title', 'unknown')}': {str(e)}")
                    db.session.rollback()
        
        # Commit books before checking banners to avoid autoflush issues
        if created_books_count > 0:
            try:
                db.session.commit()
                print(f"Committed {created_books_count} books to database")
            except Exception as e:
                print(f"Error committing books: {str(e)}")
                db.session.rollback()
    
    # Create Sample Banners (only if not exists)
    # Note: Banners are now text-only with background and text colors (no images)
    # Use no_autoflush to prevent autoflush of pending book objects
    with db.session.no_autoflush:
        existing_banners = Banner.query.first()
    if not existing_banners:
        sample_banners = [
            {
                'title': 'GIẢM GIÁ 50% - ĐẮC NHÂN TÂM',
                'description': 'Ưu đãi đặc biệt cho sách bán chạy nhất',
                'link': '/category/sach-tieng-viet',
                'bg_color': '#ef4444',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 1,
                'is_active': True
            },
            {
                'title': 'NHÀ GIẢ KIM - GIẢM 30%',
                'description': 'Tác phẩm văn học kinh điển',
                'link': '/category/sach-tieng-viet',
                'bg_color': '#f59e0b',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 2,
                'is_active': True
            },
            {
                'title': 'SAPIENS - SÁCH MỚI',
                'description': 'Lược sử loài người - Best seller',
                'link': '/category/sach-tieng-viet',
                'bg_color': '#8b5cf6',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 3,
                'is_active': True
            },
            {
                'title': 'FLASH SALE HÔM NAY',
                'description': 'Giảm đến 40% các đầu sách hot',
                'link': '/category/truyen-tranh',
                'bg_color': '#10b981',
                'text_color': '#ffffff',
                'position': 'side_top',
                'display_order': 1,
                'is_active': True
            },
            {
                'title': 'SÁCH THIẾU NHI',
                'description': 'Bộ sưu tập cho bé yêu',
                'link': '/category/van-phong-pham',
                'bg_color': '#ec4899',
                'text_color': '#ffffff',
                'position': 'side_bottom',
                'display_order': 1,
                'is_active': True
            }
        ]
        
        for banner_data in sample_banners:
            # Generate banner_code
            banner_code = generate_banner_code(Banner)
            banner_data['banner_code'] = banner_code
            
            banner = Banner(**banner_data)
            db.session.add(banner)
        
        print(f"Created {len(sample_banners)} sample banners")
    else:
        print(f"Banners already exist ({Banner.query.count()} banners), skipping banner creation")
    
    # Commit books and banners
    # Note: Users are already committed (initial users committed immediately, additional users committed in batches)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Warning committing books/banners: {e}")
    
    # Seed Orders
    # Use seed_orders function from seed_orders.py
    # Note: seed_orders() commits internally, so no need to commit again
    seed_orders()
    
    # Print success message (seed_orders() already committed)
    print("Database seeded successfully!")
    print("\n Login Credentials:")
    print("   Admin:  admin / admin123 (Super Admin)")
    print("   User1:  user1 / pass123 (Customer KH001)")
    print("   User2:  user2 / pass123 (Customer KH002)")
    print("\n Banners: 3 main banners + 2 side banners")
    print(f"\n Books: {len(sample_books)} books across 4 categories")
    print("   - Sach Tieng Viet: 5 books")
    print("   - Truyen Tranh: 5 books")
    print("   - Do Trang Tri: 5 books")
    print("   - Van Phong Pham: 5 books")
    print("\n Orders: 50 orders with various statuses")
    print("\n Note: Best Sellers are dynamically computed from order history")

if __name__ == '__main__':
    # For standalone testing
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()












    
    if not skip_to_books:
        # Check if users already exist (wrap in try-except in case column doesn't exist yet)
        try:
            existing_admin = User.query.filter_by(username='admin').first()
            existing_user1 = User.query.filter_by(username='user1').first()
            existing_user2 = User.query.filter_by(username='user2').first()
        except Exception as e:
            # Early return: Only skip if admin, user1, and user2 all exist
            # This ensures admin is always created even if other users exist
            if existing_admin and existing_user1 and existing_user2:
                existing_admin = None
                existing_user1 = None
                existing_user2 = None
            else:
                raise
        
        # Create Admin User 1 (if not exists)
        if not existing_admin:
            admin = User(
                username='admin',
                password_hash=hash_password('admin123'),
                email='admin@bookstore.com',
                full_name='Administrator',
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            print("Created admin user (admin/admin123)")
        else:
            print("Admin user already exists")
        
        # Create Test Customers with customer codes (if not exist)
        # Check if customer_code column exists by trying to query it
        has_customer_code_column = True
        try:
            # Try a simple query that would fail if column doesn't exist
            db.session.execute(text("SELECT customer_code FROM users LIMIT 1"))
        except Exception:
            has_customer_code_column = False
        
        if not existing_user1:
            user1_data = {
                'username': 'user1',
                'password_hash': hash_password('pass123'),
                'email': 'user1@example.com',
                'full_name': 'Nguyễn Văn A',
                'role': 'customer',
                'is_active': True
            }
            if has_customer_code_column:
                user1_data['customer_code'] = 'KH001'  # First customer
            user1 = User(**user1_data)
            db.session.add(user1)
            if has_customer_code_column:
                print("Created user1 (user1/pass123, Customer KH001)")
            else:
                print("Created user1 (user1/pass123)")
        else:
            print("User1 already exists")
        
        if not existing_user2:
            user2_data = {
                'username': 'user2',
                'password_hash': hash_password('pass123'),
                'email': 'user2@example.com',
                'full_name': 'Trần Thị B',
                'role': 'customer',
                'is_active': True
            }
            if has_customer_code_column:
                user2_data['customer_code'] = 'KH002'  # Second customer
            user2 = User(**user2_data)
            db.session.add(user2)
            if has_customer_code_column:
                print("Created user2 (user2/pass123, Customer KH002)")
            else:
                print("Created user2 (user2/pass123)")
        else:
            print("User2 already exists")
        
        # Commit initial users (admin, moderator, editor, user1, user2) immediately
        # to prevent autoflush issues when creating categories
        try:
            db.session.commit()
            print("Committed initial users (admin, moderator, editor, user1, user2)")
        except Exception as e:
            db.session.rollback()
            print(f"Warning committing initial users: {e}")
        
        # Create additional 18 customers (total 20 customers)
        # Vietnamese names for realistic test data
        vietnamese_names = [
            ('user3', 'user3@example.com', 'Lê Văn C', 'KH003'),
            ('user4', 'user4@example.com', 'Phạm Thị D', 'KH004'),
            ('user5', 'user5@example.com', 'Hoàng Văn E', 'KH005'),
            ('user6', 'user6@example.com', 'Vũ Thị F', 'KH006'),
            ('user7', 'user7@example.com', 'Đặng Văn G', 'KH007'),
            ('user8', 'user8@example.com', 'Bùi Thị H', 'KH008'),
            ('user9', 'user9@example.com', 'Đỗ Văn I', 'KH009')
        ]
        
        # Commit users in batches to avoid large transactions
        batch_size = 5
        for i, (username, email, full_name, customer_code) in enumerate(vietnamese_names):
            existing_user = User.query.filter_by(username=username).first()
            if not existing_user:
                user_data = {
                    'username': username,
                    'password_hash': hash_password('pass123'),
                    'email': email,
                    'full_name': full_name,
                    'role': 'customer',
                    'is_active': True
                }
                if has_customer_code_column:
                    user_data['customer_code'] = customer_code
                new_user = User(**user_data)
                db.session.add(new_user)
                if has_customer_code_column:
                    print(f"Created {username} ({username}/pass123, Customer {customer_code})")
                else:
                    print(f"Created {username} ({username}/pass123)")
            else:
                print(f"{username} already exists")
            
            # Commit every batch_size users or at the end
            if (i + 1) % batch_size == 0 or i == len(vietnamese_names) - 1:
                try:
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Warning committing users batch: {e}")
    
    # Create Categories (always define, but only create if not skip_to_books)
    from utils.helpers import generate_slug
    
    sample_categories = [
        {
            'key': 'SACH_TIENG_VIET',
            'name': 'Sách Tiếng Việt',
            'slug': 'sach-tieng-viet',
            'description': 'Sách văn học, sách giáo khoa và tài liệu tiếng Việt',
            'display_order': 1,
            'is_active': True
        },
        {
            'key': 'TRUYEN_TRANH',
            'name': 'Truyện Tranh',
            'slug': 'truyen-tranh',
            'description': 'Truyện tranh, manga, comic từ nhiều quốc gia',
            'display_order': 2,
            'is_active': True
        },
        {
            'key': 'DO_TRANG_TRI',
            'name': 'Đồ Trang Trí - Lưu Niệm',
            'slug': 'do-trang-tri-luu-niem',
            'description': 'Đồ trang trí, quà lưu niệm và phụ kiện đọc sách',
            'display_order': 3,
            'is_active': True
        },
        {
            'key': 'VAN_PHONG_PHAM',
            'name': 'Văn Phòng Phẩm',
            'slug': 'van-phong-pham',
            'description': 'Văn phòng phẩm, dụng cụ học tập và làm việc',
            'display_order': 4,
            'is_active': True
        }
    ]
    
    if not skip_to_books:
        # Check if slug column exists
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('categories')]
            has_slug_column = 'slug' in columns
        except Exception:
            # Table might not exist yet, db.create_all() will create it
            has_slug_column = False
        
        created_count = 0
        skipped_count = 0
        
        # Query max category_code once before the loop to avoid duplicate codes
        # Track next number in memory to ensure uniqueness within the batch
        if has_slug_column:
            from sqlalchemy import func
            max_code = db.session.query(func.max(Category.category_code)).scalar()
            if max_code:
                next_category_number = int(max_code[2:]) + 1
            else:
                next_category_number = 1
        else:
            next_category_number = 1
        
        # Only create categories if they don't exist (check by slug if available, else by key)
        for category_data in sample_categories:
            try:
                # Check existence by slug if column exists, else by key
                if has_slug_column:
                    result = db.session.execute(
                        text("SELECT id FROM categories WHERE slug = :slug"),
                        {'slug': category_data['slug']}
                    )
                else:
                    result = db.session.execute(
                        text("SELECT id FROM categories WHERE key = :key"),
                        {'key': category_data['key']}
                    )
                existing_row = result.fetchone()
                
                if existing_row:
                    # Category already exists, skip
                    skipped_count += 1
                    if has_slug_column:
                        print(f"  Category '{category_data['slug']}' already exists, skipping")
                    else:
                        print(f"  Category '{category_data['key']}' already exists, skipping")
                else:
                    # Create new category
                    try:
                        if has_slug_column:
                            # Table has slug column, use ORM and generate category_code
                            # Generate category_code from memory counter to ensure uniqueness within batch
                            category_code = f'DM{next_category_number:06d}'
                            next_category_number += 1
                            
                            # Use no_autoflush to prevent premature flush during category creation
                            with db.session.no_autoflush:
                                category_data_with_code = {**category_data, 'category_code': category_code}
                                category = Category(**category_data_with_code)
                                db.session.add(category)
                            created_count += 1
                        else:
                            # Table doesn't have slug column yet, use raw SQL without slug
                            db.session.execute(
                                text("""
                                    INSERT INTO categories (key, name, description, display_order, is_active, created_at, updated_at)
                                    VALUES (:key, :name, :description, :display_order, :is_active, :created_at, :updated_at)
                                """),
                                {
                                    'key': category_data['key'],
                                    'name': category_data['name'],
                                    'description': category_data['description'],
                                    'display_order': category_data['display_order'],
                                    'is_active': category_data['is_active'],
                                    'created_at': datetime.utcnow(),
                                    'updated_at': datetime.utcnow()
                                }
                            )
                            created_count += 1
                    except Exception as insert_error:
                        # Handle duplicate key/slug constraint violation gracefully
                        error_str = str(insert_error)
                        if 'unique' in error_str.lower() or 'duplicate' in error_str.lower():
                            skipped_count += 1
                            if has_slug_column:
                                print(f"  Category '{category_data['slug']}' already exists (duplicate constraint), skipping")
                            else:
                                print(f"  Category '{category_data['key']}' already exists (duplicate constraint), skipping")
                            db.session.rollback()
                        else:
                            # Other error, log and skip
                            print(f" Error creating category '{category_data.get('name', 'unknown')}': {str(insert_error)}")
                            db.session.rollback()
            except Exception as e:
                # If categories table doesn't exist or other error, skip this category
                print(f" Skipping category '{category_data.get('name', 'unknown')}': {str(e)}")
                db.session.rollback()
                continue
        
        try:
            db.session.commit()
            if created_count > 0:
                print(f"Created {created_count} new categories")
            if skipped_count > 0:
                print(f"Skipped {skipped_count} existing categories")
            if created_count == 0 and skipped_count == 0:
                print(f"Categories check completed")
        except Exception as e:
            db.session.rollback()
            print(f"Category seed failed: {str(e)}")
    
    # Create Sample Books (60 books total)
    # Distribution: Sach Tieng Viet (21), Truyen Tranh (15), Do Trang Tri (15), Van Phong Pham (15)
    # Note: Best Sellers are now dynamically computed from order history via /api/books/bestsellers
    sample_books = [
        # ===== CATEGORY: Sach Tieng Viet  =====
        {
            'title': 'Đắc Nhân Tâm',
            'author': 'Dale Carnegie',
            'publisher': 'NXB Tổng Hợp TP.HCM',
            'publish_date': '2020-01-15',
            'price': 86000,
            'stock': 50,
            'description': 'Đắc Nhân Tâm của Dale Carnegie là quyển sách nổi tiếng nhất, bán chạy nhất và có tầm ảnh hưởng nhất của mọi thời đại.',
            'image_url': 'https://cdn.diemdoo.me/books/9685220f-0d4f-47eb-b98a-912b6f5e0b26.jpg',
            'pages': 320,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Nhà Giả Kim',
            'author': 'Paulo Coelho',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2019-05-20',
            'price': 79000,
            'stock': 45,
            'description': 'Tất cả những trải nghiệm trong chuyến phiêu du theo đuổi vận mệnh của mình đã giúp Santiago thấu hiểu được ý nghĩa sâu xa nhất của hạnh phúc.',
            'image_url': 'https://cdn.diemdoo.me/books/660ca73b-633e-4834-bee5-2ab602e83c62.jpg',
            'pages': 227,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Sapiens: Lược Sử Loài Người',
            'author': 'Yuval Noah Harari',
            'publisher': 'NXB Thế Giới',
            'publish_date': '2018-09-10',
            'price': 198000,
            'stock': 30,
            'description': 'Sapiens là một cuốn sách đột phá về lịch sử nhân loại, từ khi xuất hiện cho đến ngày nay.',
            'image_url': 'https://cdn.diemdoo.me/books/images.jpg',
            'pages': 543,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Tuổi Trẻ Đáng Giá Bao Nhiêu',
            'author': 'Rosie Nguyễn',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2021-03-05',
            'price': 90000,
            'stock': 60,
            'description': 'Bạn hối tiếc vì không nỗ lực hết mình khi còn trẻ, bởi vì bạn không thể có được những gì mình muốn.',
            'image_url': 'https://cdn.diemdoo.me/books/a08dba75-37a9-4d66-8469-0b7baabd6f7c.jpg',
            'pages': 268,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Nghĩ Giàu & Làm Giàu',
            'author': 'Napoleon Hill',
            'publisher': 'NXB Lao Động',
            'publish_date': '2019-11-20',
            'price': 125000,
            'stock': 35,
            'description': 'Cuốn sách này đã giúp hàng triệu người trên thế giới đạt được thành công trong cuộc sống.',
            'image_url': 'https://cdn.diemdoo.me/books/0d596b7f-6f9f-46d4-8e81-b543a685f856.jpg',
            'pages': 382,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Cây Cam Ngọt Của Tôi',
            'author': 'José Mauro de Vasconcelos',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2020-07-15',
            'price': 108000,
            'stock': 40,
            'description': 'Câu chuyện cảm động về cậu bé Zezé và cây cam ngọt nhỏ. Một tác phẩm kinh điển về tuổi thơ.',
            'image_url': 'https://cdn.diemdoo.me/books/70b2a8dc-9367-4308-a983-b7b630adf19d.jpg',
            'pages': 244,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2018-05-10',
            'price': 95000,
            'stock': 55,
            'description': 'Những câu chuyện tuổi thơ dung dị nhưng đầy ắp kỷ niệm của hai anh em Thiều và Tường.',
            'image_url': 'https://cdn.diemdoo.me/books/e8b76d3d-1b87-48b6-b1bf-bb51ca1f9ed2.jpg',
            'pages': 368,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Cho Tôi Xin Một Vé Đi Tuổi Thơ',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2018-08-15',
            'price': 82000,
            'stock': 52,
            'description': 'Tập truyện ngắn về tuổi thơ với những ký ức đẹp đẽ, những trò chơi và bạn bè thân thiết.',
            'image_url': 'https://cdn.diemdoo.me/books/c7e565ef-6a89-46b1-a512-6acdfd80bc43.jpg',
            'pages': 312,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Số Đỏ',
            'author': 'Vũ Trọng Phụng',
            'publisher': 'NXB Văn Học',
            'publish_date': '2018-11-10',
            'price': 72000,
            'stock': 60,
            'description': 'Tiểu thuyết châm biếm xã hội Việt Nam thời thuộc địa, qua nhân vật Xuân Tóc Đỏ.',
            'image_url': 'https://cdn.diemdoo.me/books/8f40311a-bba8-4967-b427-1515ec7c5cd6.jpg',
            'pages': 220,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Chí Phèo',
            'author': 'Nam Cao',
            'publisher': 'NXB Văn Học',
            'publish_date': '2019-06-15',
            'price': 58000,
            'stock': 65,
            'description': 'Truyện ngắn kinh điển về số phận Chí Phèo - người nông dân bị xã hội đẩy vào chỗ đáo.',
            'image_url': 'https://cdn.diemdoo.me/books/aec541a7-167c-48ae-b6eb-a11d8d234f64.jpg',
            'pages': 96,
            'category': 'SACH_TIENG_VIET'
        },
        {
            'title': 'Vợ Nhặt',
            'author': 'Kim Lân',
            'publisher': 'NXB Văn Học',
            'publish_date': '2018-07-20',
            'price': 54000,
            'stock': 68,
            'description': 'Truyện ngắn nổi tiếng về tình người trong hoàn cảnh nạn đói 1945.',
            'image_url': 'https://cdn.diemdoo.me/books/1bf519f9-6307-42a4-b6db-bdff6e0ec2f9.jpg',
            'pages': 88,
            'category': 'SACH_TIENG_VIET'
        },
        
        # ===== CATEGORY: Truyen Tranh  =====
        {
            'title': 'One Piece - Tập 1',
            'author': 'Oda Eiichiro',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-01-10',
            'price': 25000,
            'stock': 100,
            'description': 'Câu chuyện về hải tặc Luffy và ước mơ trở thành vua hải tặc.',
            'image_url': 'https://cdn.diemdoo.me/books/4f4766e6-f2a0-40b6-b5d5-3976cd35d0a2.jpg',
            'pages': 192,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Doraemon - Tập 1',
            'author': 'Fujiko F. Fujio',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-03-15',
            'price': 20000,
            'stock': 120,
            'description': 'Chú mèo máy đến từ tương lai và những bảo bối kỳ diệu.',
            'image_url': 'https://cdn.diemdoo.me/books/cf162373-c333-41af-b841-4c2360833b03.png',
            'pages': 176,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Naruto - Tập 1',
            'author': 'Kishimoto Masashi',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-11-05',
            'price': 25000,
            'stock': 95,
            'description': 'Ninja Naruto và ước mơ trở thành Hokage làng Lá.',
            'image_url': 'https://cdn.diemdoo.me/books/a1ba0dfd-23f8-4522-ba70-df78aa5c27a2.jpg',
            'pages': 184,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Dragon Ball - Tập 1',
            'author': 'Toriyama Akira',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2018-06-20',
            'price': 22000,
            'stock': 88,
            'description': 'Cuộc phiêu lưu tìm kiếm bảy viên ngọc rồng của Son Goku.',
            'image_url': 'https://cdn.diemdoo.me/books/2ecf3ea8-6ff8-4ddf-baae-b9bfea961ecc.jpg',
            'pages': 200,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Conan - Tập 1',
            'author': 'Aoyama Gosho',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-08-25',
            'price': 23000,
            'stock': 105,
            'description': 'Thám tử lừng danh Conan và những vụ án bí ẩn.',
            'image_url': 'https://cdn.diemdoo.me/books/9c2e9ed0-c497-4e2b-8248-bcba291b38f0.jpg',
            'pages': 188,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Thám Tử Lừng Danh Conan - Tập Đặc Biệt',
            'author': 'Aoyama Gosho',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-12-01',
            'price': 35000,
            'stock': 68,
            'description': 'Những vụ án đặc biệt và hấp dẫn nhất của thám tử Conan.',
            'image_url': 'https://cdn.diemdoo.me/books/46013ce4-d90b-481b-84cd-944de5359a85.png',
            'pages': 220,
            'category': 'TRUYEN_TRANH'
        },
        {
            'title': 'Fairy Tail - Tập 1',
            'author': 'Mashima Hiro',
            'publisher': 'NXB Trẻ',
            'publish_date': '2020-07-15',
            'price': 26000,
            'stock': 82,
            'description': 'Hội pháp sư Fairy Tail và những cuộc phiêu lưu đầy ma thuật.',
            'image_url': 'https://cdn.diemdoo.me/books/751c59f2-9b59-44be-90af-dd5220208f36.jpg',
            'pages': 184,
            'category': 'TRUYEN_TRANH'
        },

        # ===== CATEGORY: Do Trang Tri =====
        {
            'title': 'Đèn Đọc Sách LED - Kẹp Bàn',
            'author': 'LightUp',
            'publisher': 'Tech Accessories',
            'publish_date': '2020-11-20',
            'price': 165000,
            'stock': 60,
            'description': 'Đèn LED chiếu sáng đọc sách, có thể kẹp vào bàn hoặc sách.',
            'image_url': 'https://cdn.diemdoo.me/books/566f40ee-e55f-42d3-b486-6c8e164a7dc3.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Giá Sách Mini - Gỗ Thông',
            'author': 'Furniture Plus',
            'publisher': 'Home Deco',
            'publish_date': '2021-03-10',
            'price': 320000,
            'stock': 42,
            'description': 'Giá sách mini để bàn, chất liệu gỗ thông tự nhiên.',
            'image_url': 'https://cdn.diemdoo.me/books/45ce48bc-38c6-41b2-a345-05919c7160fc.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Bộ Sticker Trang Trí Sách',
            'author': 'Sticker Art',
            'publisher': 'Creative Studio',
            'publish_date': '2020-09-05',
            'price': 35000,
            'stock': 200,
            'description': 'Bộ 50 sticker dán trang trí sách vở, nhiều mẫu mã đa dạng.',
            'image_url': 'https://cdn.diemdoo.me/books/65513642-6e4d-4e42-ae54-d9abeb723ba8.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Túi Đựng Sách Vải Canvas',
            'author': 'EcoBag',
            'publisher': 'Eco Life',
            'publish_date': '2021-05-15',
            'price': 95000,
            'stock': 88,
            'description': 'Túi vải canvas dày dặn, in hình sách, dung tích lớn.',
            'image_url': 'https://cdn.diemdoo.me/books/3ebd2fcd-e172-4e1a-93f0-005f164a092b.png',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        {
            'title': 'Móc Khóa Hình Sách Mini',
            'author': 'KeyChain Craft',
            'publisher': 'Gifts & More',
            'publish_date': '2020-12-20',
            'price': 28000,
            'stock': 180,
            'description': 'Móc khóa hình quyển sách nhỏ xinh, có thể mở được.',
            'image_url': 'https://cdn.diemdoo.me/books/f08a3430-512d-48d7-9f94-4ddf6651860f.jpg',
            'pages': 0,
            'category': 'DO_TRANG_TRI'
        },
        
        # ===== CATEGORY: Van Phong Pham  =====
        {
            'title': 'Bút Bi Thiên Long TL-079',
            'author': 'Thiên Long',
            'publisher': 'Thiên Long Corporation',
            'publish_date': '2021-01-01',
            'price': 5000,
            'stock': 500,
            'description': 'Bút bi Thiên Long TL-079 màu xanh, mực viết êm, không lem.',
            'image_url': 'https://cdn.diemdoo.me/books/0c48b741-0f07-4c1a-8bd7-a431b3e1da42.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Vở Kẻ Ngang Campus 200 Trang',
            'author': 'Campus',
            'publisher': 'Saigon Paper',
            'publish_date': '2020-09-01',
            'price': 18000,
            'stock': 300,
            'description': 'Vở kẻ ngang Campus 200 trang, giấy trắng dày dặn.',
            'image_url': 'https://cdn.diemdoo.me/books/76fad8e7-2daf-408e-b76d-7c56f806de92.jpg',
            'pages': 200,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Bút Chì 2B - Hộp 12 Cây',
            'author': 'Staedtler',
            'publisher': 'Staedtler Vietnam',
            'publish_date': '2021-02-10',
            'price': 42000,
            'stock': 180,
            'description': 'Bút chì 2B Staedtler cao cấp, hộp 12 cây, độ bền cao.',
            'image_url': 'https://cdn.diemdoo.me/books/bbe8ae18-1561-4999-9b8a-d74c534bae60.png',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Thước Kẻ Nhựa 30cm',
            'author': 'Thiên Long',
            'publisher': 'Thiên Long Corporation',
            'publish_date': '2020-11-15',
            'price': 8000,
            'stock': 400,
            'description': 'Thước kẻ nhựa trong suốt 30cm, có chia vạch mm.',
            'image_url': 'https://cdn.diemdoo.me/books/ba678803-905c-4a6e-a1dc-fe7e6c692627.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
        {
            'title': 'Gôm Tẩy Trắng - Hộp 20 Viên',
            'author': 'Elephant',
            'publisher': 'Paper World',
            'publish_date': '2021-03-20',
            'price': 25000,
            'stock': 250,
            'description': 'Gôm tẩy trắng Elephant, không để lại vết ố, hộp 20 viên.',
            'image_url': 'https://cdn.diemdoo.me/books/fc0a63a6-50b3-4de9-bd6a-db28f06ecd06.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },

        {
            'title': 'Bảng Kẹp Giấy A4',
            'author': 'Deli',
            'publisher': 'Deli Stationery',
            'publish_date': '2021-06-10',
            'price': 45000,
            'stock': 140,
            'description': 'Bảng kẹp giấy A4 Deli, chất liệu nhựa bền, có móc treo.',
            'image_url': 'https://cdn.diemdoo.me/books/05892fa6-11f9-4677-8fbd-ede3e0641141.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        },
       
        {
            'title': 'Bút Dạ Quang - Bộ 5 Màu',
            'author': 'Stabilo',
            'publisher': 'Stabilo Vietnam',
            'publish_date': '2021-09-10',
            'price': 78000,
            'stock': 110,
            'description': 'Bút dạ quang Stabilo Boss Original, bộ 5 màu nổi bật.',
            'image_url': 'https://cdn.diemdoo.me/books/da3fff1f-3eae-41e1-bb65-3a6bfc892c9b.jpg',
            'pages': 0,
            'category': 'VAN_PHONG_PHAM'
        }
    ]
    
    # Check if books table has slug column
    has_book_slug_column = False
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('books')]
        has_book_slug_column = 'slug' in columns
    except Exception:
        pass
    
    created_books_count = 0
    skipped_books_count = 0
    
    for book_data in sample_books:
        try:
            title = book_data.get('title', '')
            if not title:
                continue
            
            # Check if book already exists
            existing_book = None
            slug = None
            
            if has_book_slug_column:
                # Generate slug from title
                base_slug = generate_slug(title)
                if not base_slug:
                    print(f"Cannot generate slug for book '{title}', skipping")
                    continue
                
                slug = generate_unique_book_slug(base_slug, Book)
                existing_book = Book.query.filter_by(slug=slug).first()
            else:
                # Fallback: check by title using raw SQL if slug column doesn't exist
                # (to avoid SQLAlchemy trying to query slug column)
                result = db.session.execute(
                    text("SELECT id FROM books WHERE title = :title LIMIT 1"),
                    {'title': title}
                ).fetchone()
                if result:
                    # Don't use Book.query.get() here as it will try to query slug column
                    existing_book = True  # Just mark as existing
            
            if existing_book:
                skipped_books_count += 1
                if has_book_slug_column:
                    print(f"  Book '{slug}' already exists, skipping")
                else:
                    print(f"  Book '{title}' already exists, skipping")
                continue
            
            # Add slug to book_data if column exists
            if has_book_slug_column:
                book_data['slug'] = slug
                print(f"Generated slug: '{slug}' for book '{title}'")
            else:
                print(f"Slug column not found, book '{title}' will be created without slug")
            
            # Create book
            if has_book_slug_column:
                # Generate book_code
                book_code = generate_book_code(Book)
                book_data['book_code'] = book_code
                print(f"Generated book_code: '{book_code}' for book '{title}'")
                
                book = Book(**book_data)
                db.session.add(book)
                created_books_count += 1
            else:
                # Use raw SQL if slug column doesn't exist
                db.session.execute(
                    text("""
                        INSERT INTO books (title, author, category, description, price, stock, image_url, publisher, publish_date, pages, created_at, updated_at)
                        VALUES (:title, :author, :category, :description, :price, :stock, :image_url, :publisher, :publish_date, :pages, :created_at, :updated_at)
                    """),
                    {
                        'title': book_data.get('title'),
                        'author': book_data.get('author'),
                        'category': book_data.get('category'),
                        'description': book_data.get('description'),
                        'price': book_data.get('price', 0),
                        'stock': book_data.get('stock', 0),
                        'image_url': book_data.get('image_url'),
                        'publisher': book_data.get('publisher'),
                        'publish_date': book_data.get('publish_date'),
                        'pages': book_data.get('pages', 0),
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                )
                created_books_count += 1
        except Exception as e:
            error_str = str(e)
            if 'unique' in error_str.lower() or 'duplicate' in error_str.lower():
                skipped_books_count += 1
                print(f" Book '{book_data.get('title', 'unknown')}' already exists (duplicate constraint), skipping")
                db.session.rollback()
            else:
                print(f"Error creating book '{book_data.get('title', 'unknown')}': {str(e)}")
                db.session.rollback()
    
    try:
        db.session.commit()
        if created_books_count > 0:
            print(f"Created {created_books_count} new books")
        if skipped_books_count > 0:
            print(f"Skipped {skipped_books_count} existing books")
        if created_books_count == 0 and skipped_books_count == 0:
            print(f"Books check completed")
    except Exception as e:
        db.session.rollback()
        print(f"Books seed failed: {str(e)}")
    
    # Create Sample Banners (only if not exists)
    # Note: Banners are now text-only with background and text colors (no images)
    existing_banners = Banner.query.first()
    if not existing_banners:
        sample_banners = [
            {
                'title': 'GIẢM GIÁ 50% - ĐẮC NHÂN TÂM',
                'description': 'Ưu đãi đặc biệt cho sách bán chạy nhất',
                'link': '/category/sach-tieng-viet',
                'bg_color': '#ef4444',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 1,
                'is_active': True
            },
            {
                'title': 'NHÀ GIẢ KIM - GIẢM 30%',
                'description': 'Tác phẩm văn học kinh điển',
                'link': '/category/sach-tieng-viet',
                'bg_color': '#f59e0b',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 2,
                'is_active': True
            },
            {
                'title': 'SAPIENS - SÁCH MỚI',
                'description': 'Lược sử loài người - Best seller',
                'link': '/category/sach-tieng-viet',
                'bg_color': '#8b5cf6',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 3,
                'is_active': True
            },
            {
                'title': 'FLASH SALE HÔM NAY',
                'description': 'Giảm đến 40% các đầu sách hot',
                'link': '/category/truyen-tranh',
                'bg_color': '#10b981',
                'text_color': '#ffffff',
                'position': 'side_top',
                'display_order': 1,
                'is_active': True
            },
            {
                'title': 'SÁCH THIẾU NHI',
                'description': 'Bộ sưu tập cho bé yêu',
                'link': '/category/van-phong-pham',
                'bg_color': '#ec4899',
                'text_color': '#ffffff',
                'position': 'side_bottom',
                'display_order': 1,
                'is_active': True
            }
        ]
        
        for banner_data in sample_banners:
            # Generate banner_code
            banner_code = generate_banner_code(Banner)
            banner_data['banner_code'] = banner_code
            
            banner = Banner(**banner_data)
            db.session.add(banner)
        
        print(f"Created {len(sample_banners)} sample banners")
    else:
        print(f"Banners already exist ({Banner.query.count()} banners), skipping banner creation")
    
    # Commit books and banners
    # Note: Users are already committed (initial users committed immediately, additional users committed in batches)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Warning committing books/banners: {e}")
    
    # Seed Orders (only if not skip_to_books, and users exist)
    if not skip_to_books:
        # Use seed_orders function from seed_orders.py
        # Note: seed_orders() commits internally, so no need to commit again
        seed_orders(force_reseed=force_reseed_orders)
    
    # Print success message (seed_orders() already committed)
    print("Database seeded successfully!")
    print("\n Login Credentials:")
    print("   Admin:     admin / admin123 (Super Admin)")
    print("   Moderator: moderator / moderator123 (Limited Admin)")
    print("   Editor:    editor / editor123 (Content Manager)")
    print("   User1:     user1 / pass123 (Customer KH001)")
    print("   User2:     user2 / pass123 (Customer KH002)")
    print("\n Banners: 3 main banners + 2 side banners")
    print(f"\n Books: {len(sample_books)} books across 4 categories")
    print("   - Sach Tieng Viet: 21 books")
    print("   - Truyen Tranh: 15 books")
    print("   - Do Trang Tri: 15 books")
    print("   - Van Phong Pham: 15 books")
    print("\n Orders: 50 orders with various statuses")
    print("\n Note: Best Sellers are dynamically computed from order history")

if __name__ == '__main__':
    # For standalone testing
    import sys
    from app import create_app
    app = create_app()
    with app.app_context():
        force_reseed_orders = '--force-orders' in sys.argv
        seed_database(force_reseed_orders=force_reseed_orders)
