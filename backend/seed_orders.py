"""
Script to seed orders for testing
"""
from models import db, User, Book, Order, OrderItem
from datetime import datetime, timedelta
from decimal import Decimal

def seed_orders(force_reseed=False):
    """Seed orders for testing
    
    Args:
        force_reseed: If True, delete existing orders before seeding
    """
    print("🌱 Starting order seeding...")
    
    # Get user1 and user2
    user1 = User.query.filter_by(username='user1').first()
    user2 = User.query.filter_by(username='user2').first()
    
    if not user1 or not user2:
        print("❌ Error: user1 or user2 not found. Please run seed_data.py first.")
        return False
    
    # Check if orders already exist
    existing_orders = Order.query.first()
    if existing_orders:
        if force_reseed:
            print("🔄 Deleting existing orders...")
            OrderItem.query.delete()
            Order.query.delete()
            db.session.commit()
            print("✓ Deleted existing orders")
        else:
            print("✓ Orders already exist, skipping order seeding")
            return True
    
    # Get books from multiple categories for diverse order data
    # Lấy books từ nhiều categories để có dữ liệu đa dạng
    books = []
    categories = ['Sach Tieng Viet', 'Truyen Tranh', 'Do Trang Tri', 'Van Phong Pham']
    
    for category in categories:
        category_books = Book.query.filter_by(category=category).limit(5).all()
        books.extend(category_books)
        if category_books:
            print(f"✓ Found {len(category_books)} books from {category}")
    
    if len(books) < 10:
        print(f"❌ Error: Not enough books found ({len(books)}). Need at least 10.")
        return False
    
    print(f"✓ Total: {len(books)} books from multiple categories")
    
    # Create orders with different statuses for user1
    # Order 1: Pending order (recent) - 2 books
    order1_total = Decimal(str(books[0].price)) + Decimal(str(books[1].price))
    order1 = Order(
        user_id=user1.id,
        total_amount=order1_total,
        status='pending',
        payment_status='pending',
        shipping_address='123 Đường ABC, Phường XYZ, Quận 1, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(days=1)
    )
    db.session.add(order1)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order1.id, book_id=books[0].id, quantity=1, price=books[0].price))
    db.session.add(OrderItem(order_id=order1.id, book_id=books[1].id, quantity=1, price=books[1].price))
    
    # Order 2: Confirmed order (2 days ago) - 1 book
    order2_total = Decimal(str(books[2].price))
    order2 = Order(
        user_id=user1.id,
        total_amount=order2_total,
        status='confirmed',
        payment_status='pending',
        shipping_address='456 Đường DEF, Phường UVW, Quận 3, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(days=2)
    )
    db.session.add(order2)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order2.id, book_id=books[2].id, quantity=1, price=books[2].price))
    
    # Order 3: Completed order (5 days ago, paid) - 3 books with increased quantities
    order3_total = Decimal(str(books[0].price)) * 2 + Decimal(str(books[1].price)) * 3 + Decimal(str(books[2].price)) * 5
    order3 = Order(
        user_id=user1.id,
        total_amount=order3_total,
        status='completed',
        payment_status='paid',
        shipping_address='789 Đường GHI, Phường RST, Quận 5, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(days=5),
        updated_at=datetime.utcnow() - timedelta(days=4)
    )
    db.session.add(order3)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order3.id, book_id=books[0].id, quantity=2, price=books[0].price))
    db.session.add(OrderItem(order_id=order3.id, book_id=books[1].id, quantity=3, price=books[1].price))
    db.session.add(OrderItem(order_id=order3.id, book_id=books[2].id, quantity=5, price=books[2].price))
    
    # Order 4: Cancelled order (3 days ago) - 1 book
    order4_total = Decimal(str(books[3].price))
    order4 = Order(
        user_id=user1.id,
        total_amount=order4_total,
        status='cancelled',
        payment_status='pending',
        shipping_address='321 Đường JKL, Phường MNO, Quận 7, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(days=3),
        updated_at=datetime.utcnow() - timedelta(days=3)
    )
    db.session.add(order4)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order4.id, book_id=books[3].id, quantity=1, price=books[3].price))
    
    # Create orders for user2
    # Order 5: Pending order (recent) - 1 book
    order5_total = Decimal(str(books[4].price))
    order5 = Order(
        user_id=user2.id,
        total_amount=order5_total,
        status='pending',
        payment_status='pending',
        shipping_address='654 Đường PQR, Phường STU, Quận 2, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(hours=12)
    )
    db.session.add(order5)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order5.id, book_id=books[4].id, quantity=1, price=books[4].price))
    
    # Order 6: Confirmed order (1 day ago, paid) - 1 book
    order6_total = Decimal(str(books[5].price))
    order6 = Order(
        user_id=user2.id,
        total_amount=order6_total,
        status='confirmed',
        payment_status='paid',
        shipping_address='987 Đường VWX, Phường YZA, Quận 10, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(days=1),
        updated_at=datetime.utcnow() - timedelta(hours=20)
    )
    db.session.add(order6)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order6.id, book_id=books[5].id, quantity=1, price=books[5].price))
    
    # Order 7: Completed order (7 days ago, paid) - 2 books with increased quantities
    order7_total = Decimal(str(books[4].price)) * 6 + Decimal(str(books[5].price)) * 10
    order7 = Order(
        user_id=user2.id,
        total_amount=order7_total,
        status='completed',
        payment_status='paid',
        shipping_address='147 Đường BCD, Phường EFG, Quận Bình Thạnh, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(days=7),
        updated_at=datetime.utcnow() - timedelta(days=6)
    )
    db.session.add(order7)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order7.id, book_id=books[4].id, quantity=6, price=books[4].price))
    db.session.add(OrderItem(order_id=order7.id, book_id=books[5].id, quantity=10, price=books[5].price))
    
    # Order 8: Another pending order for user2 (very recent) - 1 book
    order8_total = Decimal(str(books[6].price))
    order8 = Order(
        user_id=user2.id,
        total_amount=order8_total,
        status='pending',
        payment_status='pending',
        shipping_address='258 Đường HIJ, Phường KLM, Quận Tân Bình, TP. Hồ Chí Minh',
        created_at=datetime.utcnow() - timedelta(hours=2)
    )
    db.session.add(order8)
    db.session.flush()
    
    db.session.add(OrderItem(order_id=order8.id, book_id=books[6].id, quantity=1, price=books[6].price))
    
    # Order 9: Completed order (10 days ago, paid) - user1 - 3 books
    if len(books) >= 9:
        order9_total = Decimal(str(books[6].price)) * 2 + Decimal(str(books[7].price)) * 3 + Decimal(str(books[8].price)) * 5
        order9 = Order(
            user_id=user1.id,
            total_amount=order9_total,
            status='completed',
            payment_status='paid',
            shipping_address='369 Đường NOP, Phường QRS, Quận 11, TP. Hồ Chí Minh',
            created_at=datetime.utcnow() - timedelta(days=10),
            updated_at=datetime.utcnow() - timedelta(days=9)
        )
        db.session.add(order9)
        db.session.flush()
        
        db.session.add(OrderItem(order_id=order9.id, book_id=books[6].id, quantity=2, price=books[6].price))
        db.session.add(OrderItem(order_id=order9.id, book_id=books[7].id, quantity=3, price=books[7].price))
        db.session.add(OrderItem(order_id=order9.id, book_id=books[8].id, quantity=5, price=books[8].price))
    
    # Order 10: Completed order (12 days ago, paid) - user2 - 3 books
    if len(books) >= 10:
        order10_total = Decimal(str(books[0].price)) * 3 + Decimal(str(books[1].price)) * 2 + Decimal(str(books[9].price)) * 15
        order10 = Order(
            user_id=user2.id,
            total_amount=order10_total,
            status='completed',
            payment_status='paid',
            shipping_address='741 Đường TUV, Phường WXY, Quận Phú Nhuận, TP. Hồ Chí Minh',
            created_at=datetime.utcnow() - timedelta(days=12),
            updated_at=datetime.utcnow() - timedelta(days=11)
        )
        db.session.add(order10)
        db.session.flush()
        
        db.session.add(OrderItem(order_id=order10.id, book_id=books[0].id, quantity=3, price=books[0].price))
        db.session.add(OrderItem(order_id=order10.id, book_id=books[1].id, quantity=2, price=books[1].price))
        db.session.add(OrderItem(order_id=order10.id, book_id=books[9].id, quantity=15, price=books[9].price))
    
    # Order 11: Completed order (15 days ago, paid) - user1 - 3 books
    if len(books) >= 10:
        order11_total = Decimal(str(books[2].price)) * 5 + Decimal(str(books[3].price)) * 4 + Decimal(str(books[4].price)) * 4
        order11 = Order(
            user_id=user1.id,
            total_amount=order11_total,
            status='completed',
            payment_status='paid',
            shipping_address='852 Đường ZAB, Phường CDE, Quận Gò Vấp, TP. Hồ Chí Minh',
            created_at=datetime.utcnow() - timedelta(days=15),
            updated_at=datetime.utcnow() - timedelta(days=14)
        )
        db.session.add(order11)
        db.session.flush()
        
        db.session.add(OrderItem(order_id=order11.id, book_id=books[2].id, quantity=5, price=books[2].price))
        db.session.add(OrderItem(order_id=order11.id, book_id=books[3].id, quantity=4, price=books[3].price))
        db.session.add(OrderItem(order_id=order11.id, book_id=books[4].id, quantity=4, price=books[4].price))
    
    # Commit all orders
    try:
        db.session.commit()
        print("✅ Orders seeded successfully!")
        print("   - User1: 6 orders (1 pending, 1 confirmed, 3 completed, 1 cancelled)")
        print("   - User2: 5 orders (2 pending, 1 confirmed, 2 completed)")
        print("   - Books from multiple categories: Sach Tieng Viet, Truyen Tranh, Do Trang Tri, Van Phong Pham")
        print("   - Sold counts: books[0]=5, books[1]=5, books[2]=10, books[3]=4, books[4]=10, books[5]=10, books[6]=2, books[7]=3, books[8]=5, books[9]=15")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error seeding orders: {e}")
        raise

# For standalone execution
if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_orders(force_reseed=True)
