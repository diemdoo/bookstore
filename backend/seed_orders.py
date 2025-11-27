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
    
    # Get some books for orders
    books = Book.query.limit(10).all()
    if len(books) < 7:
        print(f"❌ Error: Not enough books found ({len(books)}). Need at least 7.")
        return False
    
    print(f"✓ Found {len(books)} books")
    
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
    
    # Order 3: Completed order (5 days ago, paid) - 3 books
    order3_total = Decimal(str(books[0].price)) + Decimal(str(books[1].price)) + Decimal(str(books[2].price))
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
    
    db.session.add(OrderItem(order_id=order3.id, book_id=books[0].id, quantity=1, price=books[0].price))
    db.session.add(OrderItem(order_id=order3.id, book_id=books[1].id, quantity=1, price=books[1].price))
    db.session.add(OrderItem(order_id=order3.id, book_id=books[2].id, quantity=1, price=books[2].price))
    
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
    
    # Order 7: Completed order (7 days ago, paid) - 2 books
    order7_total = Decimal(str(books[4].price)) + Decimal(str(books[5].price))
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
    
    db.session.add(OrderItem(order_id=order7.id, book_id=books[4].id, quantity=1, price=books[4].price))
    db.session.add(OrderItem(order_id=order7.id, book_id=books[5].id, quantity=1, price=books[5].price))
    
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
    
    # Commit all orders
    try:
        db.session.commit()
        print("✅ Orders seeded successfully!")
        print("   - User1: 4 orders (1 pending, 1 confirmed, 1 completed, 1 cancelled)")
        print("   - User2: 4 orders (2 pending, 1 confirmed, 1 completed)")
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
