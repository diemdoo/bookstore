"""
Database seed script with sample data for Bookstore
Includes admin user, test customers, sample books, categories, banners, and orders
"""
from models import db, User, Book, Banner, Category, Order, OrderItem
from utils.helpers import hash_password
from datetime import datetime, timedelta
from decimal import Decimal
from seed_orders import seed_orders

def seed_database(force_reseed_books=False, force_reseed_orders=False):
    """Seed the database with initial data (idempotent)
    
    Args:
        force_reseed_books: If True, reseed books even if users exist
        force_reseed_orders: If True, reseed orders even if they exist
    """
    print("🌱 Starting database seed...")
    
    # If force_reseed_books, only reseed books and banners, skip users and categories
    if force_reseed_books:
        print("🔄 Force reseeding books and banners (keeping users and categories)...")
        Book.query.delete()
        Banner.query.delete()
        db.session.commit()
        print("✓ Deleted existing books and banners")
        # Skip to books seeding
        skip_to_books = True
    else:
        skip_to_books = False
        # Check if data already exists
        if User.query.first() is not None:
            print("✅ Users already exist, skipping user creation...")
            # Don't return, continue to seed orders if needed
    
    if not skip_to_books:
        # Check if users already exist
        existing_admin = User.query.filter_by(username='admin').first()
        existing_user1 = User.query.filter_by(username='user1').first()
        existing_user2 = User.query.filter_by(username='user2').first()
        
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
            print("✓ Created admin user (admin/admin123)")
        else:
            print("✓ Admin user already exists")
        
        # Create Test Customers with customer codes (if not exist)
        if not existing_user1:
            user1 = User(
                username='user1',
                password_hash=hash_password('pass123'),
                email='user1@example.com',
                full_name='Nguyễn Văn A',
                role='customer',
                customer_code='KH001',  # First customer
                is_active=True
            )
            db.session.add(user1)
            print("✓ Created user1 (user1/pass123, Customer KH001)")
        else:
            print("✓ User1 already exists")
        
        if not existing_user2:
            user2 = User(
                username='user2',
                password_hash=hash_password('pass123'),
                email='user2@example.com',
                full_name='Trần Thị B',
                role='customer',
                customer_code='KH002',  # Second customer
                is_active=True
            )
            db.session.add(user2)
            print("✓ Created user2 (user2/pass123, Customer KH002)")
        else:
            print("✓ User2 already exists")
    
    # Create Categories (always define, but only create if not skip_to_books)
    sample_categories = [
        {
            'key': 'Sach Tieng Viet',
            'name': 'Sách Tiếng Việt',
            'description': 'Sách văn học, sách giáo khoa và tài liệu tiếng Việt',
            'display_order': 1,
            'is_active': True
        },
        {
            'key': 'Truyen Tranh',
            'name': 'Truyện Tranh',
            'description': 'Truyện tranh, manga, comic từ nhiều quốc gia',
            'display_order': 2,
            'is_active': True
        },
        {
            'key': 'Do Trang Tri',
            'name': 'Đồ Trang Trí - Lưu Niệm',
            'description': 'Đồ trang trí, quà lưu niệm và phụ kiện đọc sách',
            'display_order': 3,
            'is_active': True
        },
        {
            'key': 'Van Phong Pham',
            'name': 'Văn Phòng Phẩm',
            'description': 'Văn phòng phẩm, dụng cụ học tập và làm việc',
            'display_order': 4,
            'is_active': True
        }
    ]
    
    if not skip_to_books:
        # Only create categories if they don't exist
        for category_data in sample_categories:
            existing = Category.query.filter_by(key=category_data['key']).first()
            if not existing:
                category = Category(**category_data)
                db.session.add(category)
        
        print(f"✓ Created/verified {len(sample_categories)} categories")
    
    # Create Sample Books (60 books total)
    # Distribution: Sach Tieng Viet (21), Truyen Tranh (15), Do Trang Tri (15), Van Phong Pham (15)
    # Note: Best Sellers are now dynamically computed from order history via /api/books/bestsellers
    sample_books = [
        # ===== CATEGORY: Sach Tieng Viet (21 books - includes former best sellers) =====
        {
            'title': 'Đắc Nhân Tâm',
            'author': 'Dale Carnegie',
            'publisher': 'NXB Tổng Hợp TP.HCM',
            'publish_date': '2020-01-15',
            'price': 86000,
            'stock': 50,
            'description': 'Đắc Nhân Tâm của Dale Carnegie là quyển sách nổi tiếng nhất, bán chạy nhất và có tầm ảnh hưởng nhất của mọi thời đại.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 320,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Nhà Giả Kim',
            'author': 'Paulo Coelho',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2019-05-20',
            'price': 79000,
            'stock': 45,
            'description': 'Tất cả những trải nghiệm trong chuyến phiêu du theo đuổi vận mệnh của mình đã giúp Santiago thấu hiểu được ý nghĩa sâu xa nhất của hạnh phúc.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 227,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Sapiens: Lược Sử Loài Người',
            'author': 'Yuval Noah Harari',
            'publisher': 'NXB Thế Giới',
            'publish_date': '2018-09-10',
            'price': 198000,
            'stock': 30,
            'description': 'Sapiens là một cuốn sách đột phá về lịch sử nhân loại, từ khi xuất hiện cho đến ngày nay.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 543,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Tuổi Trẻ Đáng Giá Bao Nhiêu',
            'author': 'Rosie Nguyễn',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2021-03-05',
            'price': 90000,
            'stock': 60,
            'description': 'Bạn hối tiếc vì không nỗ lực hết mình khi còn trẻ, bởi vì bạn không thể có được những gì mình muốn.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 268,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Nghĩ Giàu & Làm Giàu',
            'author': 'Napoleon Hill',
            'publisher': 'NXB Lao Động',
            'publish_date': '2019-11-20',
            'price': 125000,
            'stock': 35,
            'description': 'Cuốn sách này đã giúp hàng triệu người trên thế giới đạt được thành công trong cuộc sống.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 382,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Atomic Habits',
            'author': 'James Clear',
            'publisher': 'NXB Thế Giới',
            'publish_date': '2020-06-10',
            'price': 179000,
            'stock': 40,
            'description': 'Cuốn sách giúp bạn xây dựng thói quen tốt và loại bỏ thói quen xấu. Một hệ thống đơn giản nhưng mạnh mẽ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 319,
            'category': 'Sach Tieng Viet'
        },
        
        # ===== Continued: Sach Tieng Viet (remaining 15 books) =====
        {
            'title': 'Cây Cam Ngọt Của Tôi',
            'author': 'José Mauro de Vasconcelos',
            'publisher': 'NXB Hội Nhà Văn',
            'publish_date': '2020-07-15',
            'price': 108000,
            'stock': 40,
            'description': 'Câu chuyện cảm động về cậu bé Zezé và cây cam ngọt nhỏ. Một tác phẩm kinh điển về tuổi thơ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 244,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Tôi Thấy Hoa Vàng Trên Cỏ Xanh',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2018-05-10',
            'price': 95000,
            'stock': 55,
            'description': 'Những câu chuyện tuổi thơ dung dị nhưng đầy ắp kỷ niệm của hai anh em Thiều và Tường.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 368,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Mắt Biếc',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2017-12-01',
            'price': 85000,
            'stock': 48,
            'description': 'Câu chuyện tình đầu trong trẻo và day dứt của Ngạn dành cho Hà Lan - cô gái có đôi mắt biếc.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 280,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Cho Tôi Xin Một Vé Đi Tuổi Thơ',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2018-08-15',
            'price': 82000,
            'stock': 52,
            'description': 'Tập truyện ngắn về tuổi thơ với những ký ức đẹp đẽ, những trò chơi và bạn bè thân thiết.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 312,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Tôi Là Bêtô',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2019-03-10',
            'price': 88000,
            'stock': 45,
            'description': 'Câu chuyện về cậu bé Bêtô với những ước mơ và hy vọng trong cuộc sống bình dị.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 296,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Cô Gái Đến Từ Hôm Qua',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2016-09-20',
            'price': 92000,
            'stock': 42,
            'description': 'Chuyện tình lãng mạn và huyền bí giữa Thư và Việt trong bối cảnh miền quê Nam Bộ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 340,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Lá Nằm Trong Lá',
            'author': 'Nguyễn Nhật Ánh',
            'publisher': 'NXB Trẻ',
            'publish_date': '2020-04-25',
            'price': 79000,
            'stock': 50,
            'description': 'Tập truyện ngắn về những mảnh đời, những số phận trong cuộc sống thường nhật.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 264,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Truyện Kiều',
            'author': 'Nguyễn Du',
            'publisher': 'NXB Văn Học',
            'publish_date': '2019-01-01',
            'price': 65000,
            'stock': 70,
            'description': 'Tác phẩm thơ nổi tiếng nhất văn học Việt Nam, kể về số phận của nàng Thúy Kiều.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 180,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Số Đỏ',
            'author': 'Vũ Trọng Phụng',
            'publisher': 'NXB Văn Học',
            'publish_date': '2018-11-10',
            'price': 72000,
            'stock': 60,
            'description': 'Tiểu thuyết châm biếm xã hội Việt Nam thời thuộc địa, qua nhân vật Xuân Tóc Đỏ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 220,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Chí Phèo',
            'author': 'Nam Cao',
            'publisher': 'NXB Văn Học',
            'publish_date': '2019-06-15',
            'price': 58000,
            'stock': 65,
            'description': 'Truyện ngắn kinh điển về số phận Chí Phèo - người nông dân bị xã hội đẩy vào chỗ đáo.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 96,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Vợ Nhặt',
            'author': 'Kim Lân',
            'publisher': 'NXB Văn Học',
            'publish_date': '2018-07-20',
            'price': 54000,
            'stock': 68,
            'description': 'Truyện ngắn nổi tiếng về tình người trong hoàn cảnh nạn đói 1945.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 88,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Tắt Đèn',
            'author': 'Ngô Tất Tố',
            'publisher': 'NXB Văn Học',
            'publish_date': '2019-09-05',
            'price': 68000,
            'stock': 55,
            'description': 'Tiểu thuyết hiện thực phê phán về nông thôn Việt Nam đầu thế kỷ 20.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 315,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Những Ngày Thơ Ấu',
            'author': 'Nguyên Hồng',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-02-10',
            'price': 76000,
            'stock': 58,
            'description': 'Tự truyện về tuổi thơ của tác giả, với những kỷ niệm về làng quê Bắc Bộ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 240,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Vang Bóng Một Thời',
            'author': 'Nguyễn Tuân',
            'publisher': 'NXB Văn Học',
            'publish_date': '2018-10-18',
            'price': 64000,
            'stock': 62,
            'description': 'Tập truyện ký về những người nghệ sĩ và nghề thủ công truyền thống.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 192,
            'category': 'Sach Tieng Viet'
        },
        {
            'title': 'Lão Hạc',
            'author': 'Nam Cao',
            'publisher': 'NXB Văn Học',
            'publish_date': '2019-04-12',
            'price': 52000,
            'stock': 72,
            'description': 'Truyện ngắn cảm động về ông Lão Hạc và con chó Vàng trong hoàn cảnh nghèo khó.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 72,
            'category': 'Sach Tieng Viet'
        },
        
        # ===== CATEGORY: Truyen Tranh (15 books) =====
        {
            'title': 'One Piece - Tập 1',
            'author': 'Oda Eiichiro',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-01-10',
            'price': 25000,
            'stock': 100,
            'description': 'Câu chuyện về hải tặc Luffy và ước mơ trở thành vua hải tặc.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 192,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Naruto - Tập 1',
            'author': 'Kishimoto Masashi',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-11-05',
            'price': 25000,
            'stock': 95,
            'description': 'Ninja Naruto và ước mơ trở thành Hokage làng Lá.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 184,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Dragon Ball - Tập 1',
            'author': 'Toriyama Akira',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2018-06-20',
            'price': 22000,
            'stock': 88,
            'description': 'Cuộc phiêu lưu tìm kiếm bảy viên ngọc rồng của Son Goku.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 200,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Doraemon - Tập 1',
            'author': 'Fujiko F. Fujio',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-03-15',
            'price': 20000,
            'stock': 120,
            'description': 'Chú mèo máy đến từ tương lai và những bảo bối kỳ diệu.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 176,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Conan - Tập 1',
            'author': 'Aoyama Gosho',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-08-25',
            'price': 23000,
            'stock': 105,
            'description': 'Thám tử lừng danh Conan và những vụ án bí ẩn.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 188,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Attack On Titan - Tập 1',
            'author': 'Isayama Hajime',
            'publisher': 'NXB Trẻ',
            'publish_date': '2020-05-10',
            'price': 28000,
            'stock': 75,
            'description': 'Cuộc chiến sinh tồn giữa loài người và những người khổng lồ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 196,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Thám Tử Lừng Danh Conan - Tập Đặc Biệt',
            'author': 'Aoyama Gosho',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2019-12-01',
            'price': 35000,
            'stock': 68,
            'description': 'Những vụ án đặc biệt và hấp dẫn nhất của thám tử Conan.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 220,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Fairy Tail - Tập 1',
            'author': 'Mashima Hiro',
            'publisher': 'NXB Trẻ',
            'publish_date': '2020-07-15',
            'price': 26000,
            'stock': 82,
            'description': 'Hội pháp sư Fairy Tail và những cuộc phiêu lưu đầy ma thuật.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 184,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Slam Dunk - Tập 1',
            'author': 'Inoue Takehiko',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2018-09-20',
            'price': 24000,
            'stock': 90,
            'description': 'Câu chuyện về bóng rổ và thanh xuân của Sakuragi Hanamichi.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 192,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'My Hero Academia - Tập 1',
            'author': 'Horikoshi Kohei',
            'publisher': 'NXB Trẻ',
            'publish_date': '2020-09-10',
            'price': 29000,
            'stock': 78,
            'description': 'Thế giới siêu anh hùng và ước mơ trở thành hero của Midoriya Izuku.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 188,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Tokyo Ghoul - Tập 1',
            'author': 'Ishida Sui',
            'publisher': 'NXB Trẻ',
            'publish_date': '2019-10-25',
            'price': 32000,
            'stock': 72,
            'description': 'Thế giới của ghoul và câu chuyện về Kaneki Ken.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 204,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Fullmetal Alchemist - Tập 1',
            'author': 'Arakawa Hiromu',
            'publisher': 'NXB Trẻ',
            'publish_date': '2018-12-15',
            'price': 27000,
            'stock': 85,
            'description': 'Hai anh em nhà Elric và hành trình tìm kiếm Hòn đá현자.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 196,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Death Note - Tập 1',
            'author': 'Ohba Tsugumi',
            'publisher': 'NXB Trẻ',
            'publish_date': '2019-05-30',
            'price': 30000,
            'stock': 80,
            'description': 'Quyển sổ tử thần và cuộc đối đầu giữa Light và L.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 200,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Bleach - Tập 1',
            'author': 'Kubo Tite',
            'publisher': 'NXB Kim Đồng',
            'publish_date': '2020-11-20',
            'price': 25000,
            'stock': 92,
            'description': 'Thần chết Ichigo và nhiệm vụ tiêu diệt Hollow.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 188,
            'category': 'Truyen Tranh'
        },
        {
            'title': 'Kimetsu No Yaiba - Tập 1',
            'author': 'Gotouge Koyoharu',
            'publisher': 'NXB Trẻ',
            'publish_date': '2020-12-05',
            'price': 33000,
            'stock': 98,
            'description': 'Thanh gươm diệt quỷ và hành trình của Tanjirou.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 192,
            'category': 'Truyen Tranh'
        },
        
        # ===== CATEGORY: Do Trang Tri (15 books) =====
        {
            'title': 'Bộ Bookmark Kim Loại - Hoa Văn',
            'author': 'BookArt Studio',
            'publisher': 'NXB Mỹ Thuật',
            'publish_date': '2021-01-10',
            'price': 45000,
            'stock': 150,
            'description': 'Bộ 5 bookmark kim loại cao cấp với họa tiết hoa văn tinh xảo.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Hộp Đựng Sách Gỗ - Vintage',
            'author': 'WoodCraft',
            'publisher': 'Handmade Vietnam',
            'publish_date': '2021-02-15',
            'price': 280000,
            'stock': 35,
            'description': 'Hộp đựng sách bằng gỗ thông phong cách vintage, kiểu dáng cổ điển.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Đèn Đọc Sách LED - Kẹp Bàn',
            'author': 'LightUp',
            'publisher': 'Tech Accessories',
            'publish_date': '2020-11-20',
            'price': 165000,
            'stock': 60,
            'description': 'Đèn LED chiếu sáng đọc sách, có thể kẹp vào bàn hoặc sách.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Giá Sách Mini - Gỗ Thông',
            'author': 'Furniture Plus',
            'publisher': 'Home Deco',
            'publish_date': '2021-03-10',
            'price': 320000,
            'stock': 42,
            'description': 'Giá sách mini để bàn, chất liệu gỗ thông tự nhiên.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Bộ Sticker Trang Trí Sách',
            'author': 'Sticker Art',
            'publisher': 'Creative Studio',
            'publish_date': '2020-09-05',
            'price': 35000,
            'stock': 200,
            'description': 'Bộ 50 sticker dán trang trí sách vở, nhiều mẫu mã đa dạng.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Túi Đựng Sách Vải Canvas',
            'author': 'EcoBag',
            'publisher': 'Eco Life',
            'publish_date': '2021-05-15',
            'price': 95000,
            'stock': 88,
            'description': 'Túi vải canvas dày dặn, in hình sách, dung tích lớn.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Móc Khóa Hình Sách Mini',
            'author': 'KeyChain Craft',
            'publisher': 'Gifts & More',
            'publish_date': '2020-12-20',
            'price': 28000,
            'stock': 180,
            'description': 'Móc khóa hình quyển sách nhỏ xinh, có thể mở được.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Poster Motivational Quotes',
            'author': 'Wall Art',
            'publisher': 'Print House',
            'publish_date': '2021-04-10',
            'price': 55000,
            'stock': 120,
            'description': 'Bộ 3 poster trích dẫn hay về sách và tri thức, khổ A3.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Kệ Sách Treo Tường',
            'author': 'Wall Mount',
            'publisher': 'Home Furniture',
            'publish_date': '2021-06-05',
            'price': 245000,
            'stock': 48,
            'description': 'Kệ sách treo tường gỗ MDF, tiết kiệm không gian.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Bìa Bọc Sách Trong Suốt',
            'author': 'BookCare',
            'publisher': 'Stationery Pro',
            'publish_date': '2020-10-15',
            'price': 32000,
            'stock': 250,
            'description': 'Bìa bọc sách trong suốt, bảo vệ sách khỏi bụi bẩn và hư hại.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Đồng Hồ Cát Vintage',
            'author': 'Time Piece',
            'publisher': 'Decorative Items',
            'publish_date': '2021-07-20',
            'price': 125000,
            'stock': 75,
            'description': 'Đồng hồ cát phong cách vintage, trang trí bàn đọc sách.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Lọ Hoa Gốm Sứ Mini',
            'author': 'Ceramic Art',
            'publisher': 'Home Decor',
            'publish_date': '2020-08-10',
            'price': 68000,
            'stock': 95,
            'description': 'Lọ hoa gốm sứ nhỏ xinh, trang trí bàn làm việc.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Khay Gỗ Đựng Sách & Cốc',
            'author': 'Wood Design',
            'publisher': 'Handmade Store',
            'publish_date': '2021-08-15',
            'price': 185000,
            'stock': 62,
            'description': 'Khay gỗ đa năng, có chỗ đựng sách và cốc nước.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Tranh Treo Tường - Thư Viện',
            'author': 'Art Print',
            'publisher': 'Wall Gallery',
            'publish_date': '2021-09-20',
            'price': 145000,
            'stock': 52,
            'description': 'Tranh in canvas hình thư viện cổ điển, khổ 40x60cm.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        {
            'title': 'Đế Kê Sách Gỗ - Đọc Sách Nằm',
            'author': 'Reading Aid',
            'publisher': 'Comfort Plus',
            'publish_date': '2021-10-05',
            'price': 195000,
            'stock': 45,
            'description': 'Đế kê sách gỗ có thể điều chỉnh góc độ, tiện lợi khi đọc sách.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Do Trang Tri'
        },
        
        # ===== CATEGORY: Van Phong Pham (15 books) =====
        {
            'title': 'Bút Bi Thiên Long TL-079',
            'author': 'Thiên Long',
            'publisher': 'Thiên Long Corporation',
            'publish_date': '2021-01-01',
            'price': 5000,
            'stock': 500,
            'description': 'Bút bi Thiên Long TL-079 màu xanh, mực viết êm, không lem.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Vở Kẻ Ngang Campus 200 Trang',
            'author': 'Campus',
            'publisher': 'Saigon Paper',
            'publish_date': '2020-09-01',
            'price': 18000,
            'stock': 300,
            'description': 'Vở kẻ ngang Campus 200 trang, giấy trắng dày dặn.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 200,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Bút Chì 2B - Hộp 12 Cây',
            'author': 'Staedtler',
            'publisher': 'Staedtler Vietnam',
            'publish_date': '2021-02-10',
            'price': 42000,
            'stock': 180,
            'description': 'Bút chì 2B Staedtler cao cấp, hộp 12 cây, độ bền cao.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Thước Kẻ Nhựa 30cm',
            'author': 'Thiên Long',
            'publisher': 'Thiên Long Corporation',
            'publish_date': '2020-11-15',
            'price': 8000,
            'stock': 400,
            'description': 'Thước kẻ nhựa trong suốt 30cm, có chia vạch mm.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Gôm Tẩy Trắng - Hộp 20 Viên',
            'author': 'Elephant',
            'publisher': 'Paper World',
            'publish_date': '2021-03-20',
            'price': 25000,
            'stock': 250,
            'description': 'Gôm tẩy trắng Elephant, không để lại vết ố, hộp 20 viên.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Kéo Văn Phòng 21cm',
            'author': 'Thiên Long',
            'publisher': 'Thiên Long Corporation',
            'publish_date': '2020-12-10',
            'price': 35000,
            'stock': 160,
            'description': 'Kéo văn phòng Thiên Long 21cm, lưỡi thép không gỉ, cắt êm.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Hồ Dán Lớn 120ml',
            'author': 'UHU',
            'publisher': 'UHU Vietnam',
            'publish_date': '2021-04-15',
            'price': 22000,
            'stock': 200,
            'description': 'Hồ dán UHU lớn 120ml, dán giấy, vải, gỗ hiệu quả.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Bìa Hồ Sơ A4 - 10 Cái',
            'author': 'Plus',
            'publisher': 'Office Supplies',
            'publish_date': '2020-10-05',
            'price': 38000,
            'stock': 220,
            'description': 'Bìa hồ sơ A4 Plus, nhựa cứng, nhiều màu sắc, hộp 10 cái.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Băng Keo Trong Lớn',
            'author': 'Scotch',
            'publisher': '3M Vietnam',
            'publish_date': '2021-05-20',
            'price': 28000,
            'stock': 280,
            'description': 'Băng keo trong Scotch 3M, cuộn lớn, dính chắc, không vàng.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Bảng Kẹp Giấy A4',
            'author': 'Deli',
            'publisher': 'Deli Stationery',
            'publish_date': '2021-06-10',
            'price': 45000,
            'stock': 140,
            'description': 'Bảng kẹp giấy A4 Deli, chất liệu nhựa bền, có móc treo.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Ghim Bấm - Hộp 1000 Chiếc',
            'author': 'Max',
            'publisher': 'Office Max',
            'publish_date': '2020-07-25',
            'price': 15000,
            'stock': 350,
            'description': 'Ghim bấm Max hộp 1000 chiếc, size 10, không gỉ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Bộ Bấm Kim Ghim + 1000 Ghim',
            'author': 'Max',
            'publisher': 'Office Max',
            'publish_date': '2021-07-15',
            'price': 65000,
            'stock': 120,
            'description': 'Bộ bấm kim ghim Max HD-10, kèm hộp 1000 ghim, bấm được 20 tờ.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Sổ Tay Bìa Da A5',
            'author': 'Crabit',
            'publisher': 'Crabit Notebook',
            'publish_date': '2021-08-05',
            'price': 85000,
            'stock': 95,
            'description': 'Sổ tay bìa da A5 Crabit, 200 trang giấy dày, có dây đánh dấu.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 200,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Giấy Note Dán 3M - 100 Tờ',
            'author': '3M',
            'publisher': '3M Vietnam',
            'publish_date': '2020-09-20',
            'price': 32000,
            'stock': 260,
            'description': 'Giấy note dán 3M Post-it, 100 tờ, nhiều màu, dính tốt.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        },
        {
            'title': 'Bút Dạ Quang - Bộ 5 Màu',
            'author': 'Stabilo',
            'publisher': 'Stabilo Vietnam',
            'publish_date': '2021-09-10',
            'price': 78000,
            'stock': 110,
            'description': 'Bút dạ quang Stabilo Boss Original, bộ 5 màu nổi bật.',
            'image_url': 'https://cdn.duyne.me/books/3cdd9987-0942-4b44-81d7-f537d47e2397.jpg',
            'pages': 0,
            'category': 'Van Phong Pham'
        }
    ]
    
    for book_data in sample_books:
        book = Book(**book_data)
        db.session.add(book)
    
    print(f"✓ Created {len(sample_books)} sample books")
    
    # Create Sample Banners (only if not exists)
    # Note: Banner images should be uploaded to R2 folder 'banners/' via admin panel
    # These URLs use 'banners/' folder instead of 'books/' folder
    existing_banners = Banner.query.first()
    if not existing_banners:
        sample_banners = [
            {
                'title': 'GIẢM GIÁ 50% - ĐẮC NHÂN TÂM',
                'description': 'Ưu đãi đặc biệt cho sách bán chạy nhất',
                'image_url': 'https://cdn.duyne.me/banners/banner-main-1.jpg',
                'link': '/books?category=Sach Tieng Viet',
                'bg_color': '#ef4444',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 1,
                'is_active': True
            },
            {
                'title': 'NHÀ GIẢ KIM - GIẢM 30%',
                'description': 'Tác phẩm văn học kinh điển',
                'image_url': 'https://cdn.duyne.me/banners/banner-main-2.jpg',
                'link': '/books?category=Sach Tieng Viet',
                'bg_color': '#f59e0b',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 2,
                'is_active': True
            },
            {
                'title': 'SAPIENS - SÁCH MỚI',
                'description': 'Lược sử loài người - Best seller',
                'image_url': 'https://cdn.duyne.me/banners/banner-main-3.jpg',
                'link': '/books?category=Sach Tieng Viet',
                'bg_color': '#8b5cf6',
                'text_color': '#ffffff',
                'position': 'main',
                'display_order': 3,
                'is_active': True
            },
            {
                'title': 'FLASH SALE HÔM NAY',
                'description': 'Giảm đến 40% các đầu sách hot',
                'image_url': 'https://cdn.duyne.me/banners/banner-side-top.jpg',
                'link': '/books?category=Truyen Tranh',
                'bg_color': '#10b981',
                'text_color': '#ffffff',
                'position': 'side_top',
                'display_order': 1,
                'is_active': True
            },
            {
                'title': 'SÁCH THIẾU NHI',
                'description': 'Bộ sưu tập cho bé yêu',
                'image_url': 'https://cdn.duyne.me/banners/banner-side-bottom.jpg',
                'link': '/books?category=Van Phong Pham',
                'bg_color': '#ec4899',
                'text_color': '#ffffff',
                'position': 'side_bottom',
                'display_order': 1,
                'is_active': True
            }
        ]
        
        for banner_data in sample_banners:
            banner = Banner(**banner_data)
            db.session.add(banner)
        
        print(f"✓ Created {len(sample_banners)} sample banners")
    else:
        print(f"✓ Banners already exist ({Banner.query.count()} banners), skipping banner creation")
    
    # Commit books and banners first
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ Warning committing books/banners: {e}")
    
    # Seed Orders (only if not skip_to_books, and users exist)
    if not skip_to_books:
        # Use seed_orders function from seed_orders.py
        seed_orders(force_reseed=force_reseed_orders)
    
    # Commit all changes
    try:
        db.session.commit()
        print("✅ Database seeded successfully!")
        print("\n📝 Login Credentials:")
        print("   Admin:  admin / admin123")
        print("   User1:  user1 / pass123 (Customer KH001)")
        print("   User2:  user2 / pass123 (Customer KH002)")
        print("\n🎨 Banners: 3 main banners + 2 side banners")
        print(f"\n📚 Books: {len(sample_books)} books across 4 categories")
        print("   - Sach Tieng Viet: 21 books")
        print("   - Truyen Tranh: 15 books")
        print("   - Do Trang Tri: 15 books")
        print("   - Van Phong Pham: 15 books")
        print("\n📦 Orders: 8 sample orders with various statuses")
        print("\n💡 Note: Best Sellers are dynamically computed from order history")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding database: {e}")
        raise

if __name__ == '__main__':
    # For standalone testing
    import sys
    from app import create_app
    app = create_app()
    with app.app_context():
        force_reseed_orders = '--force-orders' in sys.argv
        seed_database(force_reseed_orders=force_reseed_orders)
