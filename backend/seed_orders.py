"""
Script to seed orders for testing
"""
from models import db, User, Book, Order, OrderItem
from datetime import datetime, timedelta
from decimal import Decimal
import random

def seed_orders(force_reseed=False):
    """Seed orders for testing
    
    Args:
        force_reseed: If True, delete existing orders before seeding
    """
    print("Starting order seeding...")
    
    # Get all customers (wrap in try-except in case column doesn't exist yet)
    try:
        customers = User.query.filter_by(role='customer', is_active=True).all()
    except Exception as e:
        # If column doesn't exist yet, users don't exist either
        if 'customer_code' in str(e) or 'does not exist' in str(e):
            print("Error: Database schema not fully migrated. Please ensure customer_code column exists.")
            return False
        else:
            raise
    
    if len(customers) < 2:
        print(f"Error: Not enough customers found ({len(customers)}). Need at least 2. Please run seed_data.py first.")
        return False
    
    print(f"✓ Found {len(customers)} customers")
    
    # Check if orders already exist
    existing_orders = Order.query.first()
    if existing_orders:
        if force_reseed:
            print("Deleting existing orders...")
            OrderItem.query.delete()
            Order.query.delete()
            db.session.commit()
            print("Deleted existing orders")
        else:
            print("Orders already exist, skipping order seeding")
            return True
    
    # Get books from multiple categories for diverse order data
    # Lấy books từ nhiều categories để có dữ liệu đa dạng
    books = []
    categories = ['SACH_TIENG_VIET', 'TRUYEN_TRANH', 'DO_TRANG_TRI', 'VAN_PHONG_PHAM']
    
    for category in categories:
        category_books = Book.query.filter_by(category=category).limit(5).all()
        books.extend(category_books)
        if category_books:
            print(f"Found {len(category_books)} books from {category}")
    
    if len(books) < 10:
        print(f"Error: Not enough books found ({len(books)}). Need at least 10.")
        return False
    
    print(f"Total: {len(books)} books from multiple categories")
    
    # Use first 2 customers for initial orders (backward compatibility)
    user1 = customers[0]
    user2 = customers[1] if len(customers) > 1 else customers[0]
    
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
    
    # Generate additional 39 orders (total 50 orders) distributed across all customers
    statuses = ['pending', 'confirmed', 'completed', 'cancelled']
    payment_statuses = ['pending', 'paid']
    districts = ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 5', 'Quận 7', 'Quận 10', 'Quận 11', 'Quận Bình Thạnh', 'Quận Tân Bình', 'Quận Phú Nhuận', 'Quận Gò Vấp']
    
    orders_created = 11  # Already created 11 orders above
    
    for i in range(orders_created, 50):
        # Randomly select a customer
        customer = random.choice(customers)
        
        # Randomly select 1-3 books
        num_books = random.randint(1, min(3, len(books)))
        selected_books = random.sample(books, num_books)
        
        # Calculate total amount
        total_amount = Decimal('0')
        order_items_data = []
        for book in selected_books:
            quantity = random.randint(1, 5)
            item_total = Decimal(str(book.price)) * quantity
            total_amount += item_total
            order_items_data.append({
                'book_id': book.id,
                'quantity': quantity,
                'price': book.price
            })
        
        # Random status (weighted towards completed for realistic data)
        if random.random() < 0.5:  # 50% completed
            status = 'completed'
            payment_status = 'paid'
        elif random.random() < 0.7:  # 20% confirmed
            status = 'confirmed'
            payment_status = random.choice(payment_statuses)
        elif random.random() < 0.9:  # 20% pending
            status = 'pending'
            payment_status = 'pending'
        else:  # 10% cancelled
            status = 'cancelled'
            payment_status = 'pending'
        
        # Random date within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        created_at = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
        
        # Random address
        district = random.choice(districts)
        street_num = random.randint(1, 999)
        shipping_address = f'{street_num} Đường {random.choice(["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWX", "YZA"])}, Phường {random.choice(["XYZ", "UVW", "RST", "MNO", "KLM", "HIJ", "EFG", "CDE"])}, {district}, TP. Hồ Chí Minh'
        
        # Create order
        order = Order(
            user_id=customer.id,
            total_amount=total_amount,
            status=status,
            payment_status=payment_status,
            shipping_address=shipping_address,
            created_at=created_at
        )
        
        if status != 'pending':
            # Set updated_at for non-pending orders
            order.updated_at = created_at + timedelta(hours=random.randint(1, 24))
        
        db.session.add(order)
        db.session.flush()
        
        # Create order items
        for item_data in order_items_data:
            db.session.add(OrderItem(
                order_id=order.id,
                book_id=item_data['book_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            ))
    
    # Commit all orders
    try:
        db.session.commit()
        total_orders = Order.query.count()
        pending_count = Order.query.filter_by(status='pending').count()
        confirmed_count = Order.query.filter_by(status='confirmed').count()
        completed_count = Order.query.filter_by(status='completed').count()
        cancelled_count = Order.query.filter_by(status='cancelled').count()
        
        print("Orders seeded successfully!")
        print(f"   - Total orders: {total_orders}")
        print(f"   - Pending: {pending_count}")
        print(f"   - Confirmed: {confirmed_count}")
        print(f"   - Completed: {completed_count}")
        print(f"   - Cancelled: {cancelled_count}")
        print(f"   - Distributed across {len(customers)} customers")
        print("   - Books from multiple categories: Sach Tieng Viet, Truyen Tranh, Do Trang Tri, Van Phong Pham")
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding orders: {e}")
        raise

# For standalone execution
if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_orders(force_reseed=True)
