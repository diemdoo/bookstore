from models import db, User, Book, Order, OrderItem
from datetime import datetime, timedelta
from decimal import Decimal
import random
import json
import os
import re

def load_seed_orders():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'seed_orders.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _parse_time_offset(offset_str):
    if not offset_str:
        return timedelta(0)
    
    # Match patterns like "-1d", "2h", "-30m"
    pattern = r'([+-]?\d+)([dhms])'
    matches = re.findall(pattern, offset_str.lower())
    
    delta = timedelta(0)
    for value, unit in matches:
        value = int(value)
        if unit == 'd':
            delta += timedelta(days=value)
        elif unit == 'h':
            delta += timedelta(hours=value)
        elif unit == 'm':
            delta += timedelta(minutes=value)
        elif unit == 's':
            delta += timedelta(seconds=value)
    
    return delta


def _resolve_username_to_user_id(username, users_dict):
    if username in users_dict:
        return users_dict[username].id
    raise ValueError(f"User '{username}' not found")


def _resolve_book_title_to_book_id(book_title, books_dict):
    if book_title in books_dict:
        return books_dict[book_title].id
    raise ValueError(f"Book '{book_title}' not found")


def _prepare_initial_orders_data(customers, books):
    try:
        seed_orders_data = load_seed_orders()
    except FileNotFoundError:
        print("Warning: seed_orders.json not found. Falling back to hardcoded orders.")
        return _prepare_initial_orders_data_fallback(customers, books)
    except json.JSONDecodeError as e:
        print(f"Warning: Invalid JSON in seed_orders.json: {e}. Falling back to hardcoded orders.")
        return _prepare_initial_orders_data_fallback(customers, books)
    
    # Create lookup dictionaries
    users_dict = {user.username: user for user in customers}
    books_dict = {book.title: book for book in books}
    
    orders_data = []
    order_items_data = []
    
    initial_orders = seed_orders_data.get('initial_orders', [])
    
    for order_json in initial_orders:
        try:
            # Resolve username to user_id
            username = order_json.get('username')
            user_id = _resolve_username_to_user_id(username, users_dict)
            
            # Parse datetime offsets
            created_at_offset = _parse_time_offset(order_json.get('created_at_offset', '0'))
            created_at = datetime.utcnow() + created_at_offset
            
            updated_at = None
            if 'updated_at_offset' in order_json:
                updated_at_offset = _parse_time_offset(order_json.get('updated_at_offset', '0'))
                updated_at = datetime.utcnow() + updated_at_offset
            
            # Process items and calculate total amount
            items_data = []
            total_amount = Decimal('0')
            
            for item_json in order_json.get('items', []):
                book_title = item_json.get('book_title')
                quantity = item_json.get('quantity', 1)
                
                # Resolve book title to book_id and get price
                book_id = _resolve_book_title_to_book_id(book_title, books_dict)
                book = books_dict[book_title]
                price = book.price
                
                items_data.append({
                    'book_id': book_id,
                    'quantity': quantity,
                    'price': price
                })
                
                total_amount += Decimal(str(price)) * quantity
            
            # Create order data
            order_data = {
                'user_id': user_id,
                'total_amount': total_amount,
                'status': order_json.get('status', 'pending'),
                'payment_status': order_json.get('payment_status', 'pending'),
                'shipping_address': order_json.get('shipping_address', ''),
                'created_at': created_at
            }
            
            if updated_at:
                order_data['updated_at'] = updated_at
            
            orders_data.append(order_data)
            order_items_data.append(items_data)
            
        except (ValueError, KeyError) as e:
            print(f"Warning: Error processing order from JSON: {e}. Skipping order.")
            continue
    
    return orders_data, order_items_data


def _prepare_initial_orders_data_fallback(customers, books):
    if len(customers) < 2:
        return [], []
    
    user1 = customers[0]
    user2 = customers[1] if len(customers) > 1 else customers[0]
    
    orders_data = []
    order_items_data = []
    
    # Order 1: Pending order (recent) - 2 books
    if len(books) >= 2:
        order1_total = Decimal(str(books[0].price)) + Decimal(str(books[1].price))
        orders_data.append({
            'user_id': user1.id,
            'total_amount': order1_total,
            'status': 'pending',
            'payment_status': 'pending',
            'shipping_address': '123 Đường ABC, Phường XYZ, Quận 1, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=1)
        })
        order_items_data.append([
            {'book_id': books[0].id, 'quantity': 1, 'price': books[0].price},
            {'book_id': books[1].id, 'quantity': 1, 'price': books[1].price}
        ])
    
    # Order 2: Confirmed order (2 days ago) - 1 book
    if len(books) >= 3:
        order2_total = Decimal(str(books[2].price))
        orders_data.append({
            'user_id': user1.id,
            'total_amount': order2_total,
            'status': 'confirmed',
            'payment_status': 'pending',
            'shipping_address': '456 Đường DEF, Phường UVW, Quận 3, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=2)
        })
        order_items_data.append([
            {'book_id': books[2].id, 'quantity': 1, 'price': books[2].price}
        ])
    
    # Order 3: Completed order (5 days ago, paid) - 3 books
    if len(books) >= 3:
        order3_total = Decimal(str(books[0].price)) * 2 + Decimal(str(books[1].price)) * 3 + Decimal(str(books[2].price)) * 5
        orders_data.append({
            'user_id': user1.id,
            'total_amount': order3_total,
            'status': 'completed',
            'payment_status': 'paid',
            'shipping_address': '789 Đường GHI, Phường RST, Quận 5, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=5),
            'updated_at': datetime.utcnow() - timedelta(days=4)
        })
        order_items_data.append([
            {'book_id': books[0].id, 'quantity': 2, 'price': books[0].price},
            {'book_id': books[1].id, 'quantity': 3, 'price': books[1].price},
            {'book_id': books[2].id, 'quantity': 5, 'price': books[2].price}
        ])
    
    # Order 4: Cancelled order (3 days ago) - 1 book
    if len(books) >= 4:
        order4_total = Decimal(str(books[3].price))
        orders_data.append({
            'user_id': user1.id,
            'total_amount': order4_total,
            'status': 'cancelled',
            'payment_status': 'pending',
            'shipping_address': '321 Đường JKL, Phường MNO, Quận 7, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=3),
            'updated_at': datetime.utcnow() - timedelta(days=3)
        })
        order_items_data.append([
            {'book_id': books[3].id, 'quantity': 1, 'price': books[3].price}
        ])
    
    # Order 5: Pending order (recent) - 1 book
    if len(books) >= 5:
        order5_total = Decimal(str(books[4].price))
        orders_data.append({
            'user_id': user2.id,
            'total_amount': order5_total,
            'status': 'pending',
            'payment_status': 'pending',
            'shipping_address': '654 Đường PQR, Phường STU, Quận 2, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(hours=12)
        })
        order_items_data.append([
            {'book_id': books[4].id, 'quantity': 1, 'price': books[4].price}
        ])
    
    # Order 6: Confirmed order (1 day ago, paid) - 1 book
    if len(books) >= 6:
        order6_total = Decimal(str(books[5].price))
        orders_data.append({
            'user_id': user2.id,
            'total_amount': order6_total,
            'status': 'confirmed',
            'payment_status': 'paid',
            'shipping_address': '987 Đường VWX, Phường YZA, Quận 10, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=1),
            'updated_at': datetime.utcnow() - timedelta(hours=20)
        })
        order_items_data.append([
            {'book_id': books[5].id, 'quantity': 1, 'price': books[5].price}
        ])
    
    # Order 7: Completed order (7 days ago, paid) - 2 books
    if len(books) >= 6:
        order7_total = Decimal(str(books[4].price)) * 6 + Decimal(str(books[5].price)) * 10
        orders_data.append({
            'user_id': user2.id,
            'total_amount': order7_total,
            'status': 'completed',
            'payment_status': 'paid',
            'shipping_address': '147 Đường BCD, Phường EFG, Quận Bình Thạnh, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=7),
            'updated_at': datetime.utcnow() - timedelta(days=6)
        })
        order_items_data.append([
            {'book_id': books[4].id, 'quantity': 6, 'price': books[4].price},
            {'book_id': books[5].id, 'quantity': 10, 'price': books[5].price}
        ])
    
    # Order 8: Another pending order for user2 (very recent) - 1 book
    if len(books) >= 7:
        order8_total = Decimal(str(books[6].price))
        orders_data.append({
            'user_id': user2.id,
            'total_amount': order8_total,
            'status': 'pending',
            'payment_status': 'pending',
            'shipping_address': '258 Đường HIJ, Phường KLM, Quận Tân Bình, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(hours=2)
        })
        order_items_data.append([
            {'book_id': books[6].id, 'quantity': 1, 'price': books[6].price}
        ])
    
    # Order 9: Completed order (10 days ago, paid) - user1 - 3 books
    if len(books) >= 9:
        order9_total = Decimal(str(books[6].price)) * 2 + Decimal(str(books[7].price)) * 3 + Decimal(str(books[8].price)) * 5
        orders_data.append({
            'user_id': user1.id,
            'total_amount': order9_total,
            'status': 'completed',
            'payment_status': 'paid',
            'shipping_address': '369 Đường NOP, Phường QRS, Quận 11, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=10),
            'updated_at': datetime.utcnow() - timedelta(days=9)
        })
        order_items_data.append([
            {'book_id': books[6].id, 'quantity': 2, 'price': books[6].price},
            {'book_id': books[7].id, 'quantity': 3, 'price': books[7].price},
            {'book_id': books[8].id, 'quantity': 5, 'price': books[8].price}
        ])
    
    # Order 10: Completed order (12 days ago, paid) - user2 - 3 books
    if len(books) >= 10:
        order10_total = Decimal(str(books[0].price)) * 3 + Decimal(str(books[1].price)) * 2 + Decimal(str(books[9].price)) * 15
        orders_data.append({
            'user_id': user2.id,
            'total_amount': order10_total,
            'status': 'completed',
            'payment_status': 'paid',
            'shipping_address': '741 Đường TUV, Phường WXY, Quận Phú Nhuận, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=12),
            'updated_at': datetime.utcnow() - timedelta(days=11)
        })
        order_items_data.append([
            {'book_id': books[0].id, 'quantity': 3, 'price': books[0].price},
            {'book_id': books[1].id, 'quantity': 2, 'price': books[1].price},
            {'book_id': books[9].id, 'quantity': 15, 'price': books[9].price}
        ])
    
    # Order 11: Completed order (15 days ago, paid) - user1 - 3 books
    if len(books) >= 10:
        order11_total = Decimal(str(books[2].price)) * 5 + Decimal(str(books[3].price)) * 4 + Decimal(str(books[4].price)) * 4
        orders_data.append({
            'user_id': user1.id,
            'total_amount': order11_total,
            'status': 'completed',
            'payment_status': 'paid',
            'shipping_address': '852 Đường ZAB, Phường CDE, Quận Gò Vấp, TP. Hồ Chí Minh',
            'created_at': datetime.utcnow() - timedelta(days=15),
            'updated_at': datetime.utcnow() - timedelta(days=14)
        })
        order_items_data.append([
            {'book_id': books[2].id, 'quantity': 5, 'price': books[2].price},
            {'book_id': books[3].id, 'quantity': 4, 'price': books[3].price},
            {'book_id': books[4].id, 'quantity': 4, 'price': books[4].price}
        ])
    
    return orders_data, order_items_data


def _generate_random_order_data(customers, books, num_orders):
    orders_data = []
    order_items_data = []
    
    payment_statuses = ['pending', 'paid']
    districts = ['Quận 1', 'Quận 2', 'Quận 3', 'Quận 5', 'Quận 7', 'Quận 10', 'Quận 11', 
                 'Quận Bình Thạnh', 'Quận Tân Bình', 'Quận Phú Nhuận', 'Quận Gò Vấp']
    street_names = ["ABC", "DEF", "GHI", "JKL", "MNO", "PQR", "STU", "VWX", "YZA"]
    ward_names = ["XYZ", "UVW", "RST", "MNO", "KLM", "HIJ", "EFG", "CDE"]
    
    for _ in range(num_orders):
        # Randomly select a customer
        customer = random.choice(customers)
        
        # Randomly select 1-3 books
        num_books = random.randint(1, min(3, len(books)))
        selected_books = random.sample(books, num_books)
        
        # Calculate total amount
        total_amount = Decimal('0')
        items_data = []
        for book in selected_books:
            quantity = random.randint(1, 5)
            item_total = Decimal(str(book.price)) * quantity
            total_amount += item_total
            items_data.append({
                'book_id': book.id,
                'quantity': quantity,
                'price': book.price
            })
        
        # Random status (weighted towards completed for realistic data)
        rand_val = random.random()
        if rand_val < 0.5:  # 50% completed
            status = 'completed'
            payment_status = 'paid'
        elif rand_val < 0.7:  # 20% confirmed
            status = 'confirmed'
            payment_status = random.choice(payment_statuses)
        elif rand_val < 0.9:  # 20% pending
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
        shipping_address = (f'{street_num} Đường {random.choice(street_names)}, '
                          f'Phường {random.choice(ward_names)}, {district}, TP. Hồ Chí Minh')
        
        # Prepare order data
        order_data = {
            'user_id': customer.id,
            'total_amount': total_amount,
            'status': status,
            'payment_status': payment_status,
            'shipping_address': shipping_address,
            'created_at': created_at
        }
        
        if status != 'pending':
            # Set updated_at for non-pending orders
            order_data['updated_at'] = created_at + timedelta(hours=random.randint(1, 24))
        
        orders_data.append(order_data)
        order_items_data.append(items_data)
    
    return orders_data, order_items_data


def _bulk_insert_orders_with_items(orders_data, order_items_data, batch_size=20):
    total_created = 0
    
    for i in range(0, len(orders_data), batch_size):
        batch_orders_data = orders_data[i:i + batch_size]
        batch_items_data = order_items_data[i:i + batch_size]
        
        # Get max order ID before inserting (for reliable matching)
        try:
            from sqlalchemy import func
            max_order_id = db.session.query(func.max(Order.id)).scalar() or 0
        except Exception:
            max_order_id = 0
        
        # Prepare Order objects for bulk insert
        orders_to_create = []
        for order_data in batch_orders_data:
            order_obj = Order(**order_data)
            orders_to_create.append(order_obj)
        
        # Bulk insert orders
        try:
            db.session.bulk_save_objects(orders_to_create)
            db.session.commit()
            
            # Get the IDs of orders we just created
            # Query orders with ID > max_order_id, ordered by ID, limit by batch size
            # This gives us the orders we just inserted in the correct order
            created_orders = Order.query.filter(Order.id > max_order_id)\
                .order_by(Order.id.asc())\
                .limit(len(batch_orders_data))\
                .all()
            
            if len(created_orders) != len(batch_orders_data):
                print(f"Warning: Expected {len(batch_orders_data)} orders, got {len(created_orders)}. Trying alternative matching...")
                # Fallback: match by user_id + total_amount + created_at
                created_orders = []
                for order_data in batch_orders_data:
                    order = Order.query.filter_by(
                        user_id=order_data['user_id'],
                        total_amount=order_data['total_amount']
                    ).filter(Order.id > max_order_id)\
                     .order_by(Order.id.asc())\
                     .first()
                    if order:
                        created_orders.append(order)
            
            # Prepare OrderItem objects
            order_items_to_create = []
            for order, items_data in zip(created_orders, batch_items_data):
                for item_data in items_data:
                    order_item = OrderItem(
                        order_id=order.id,
                        book_id=item_data['book_id'],
                        quantity=item_data['quantity'],
                        price=item_data['price']
                    )
                    order_items_to_create.append(order_item)
            
            # Bulk insert order items
            if order_items_to_create:
                try:
                    db.session.bulk_save_objects(order_items_to_create)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(f"Warning: Error committing order items for batch {i // batch_size + 1}: {str(e)}")
                    # Continue anyway - orders are created, items can be retried
            
            total_created += len(batch_orders_data)
            batch_num = i // batch_size + 1
            items_count = len(order_items_to_create) if order_items_to_create else 0
            print(f"Created {len(batch_orders_data)} orders with {items_count} items (batch {batch_num}, total: {total_created})")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error committing orders batch {i // batch_size + 1}: {str(e)}")
            # Continue with next batch
            continue
    
    return total_created


def seed_orders(force_reseed=False):
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
            try:
                OrderItem.query.delete()
                Order.query.delete()
                db.session.commit()
                print("Deleted existing orders")
            except Exception as e:
                db.session.rollback()
                print(f"Error deleting existing orders: {e}")
                return False
        else:
            print("Orders already exist, skipping order seeding")
            return True
    
    # Get books from multiple categories for diverse order data
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
    
    # Prepare initial 11 orders from JSON
    print("Preparing initial orders from JSON...")
    try:
        initial_orders_data, initial_order_items_data = _prepare_initial_orders_data(customers, books)
        print(f"Prepared {len(initial_orders_data)} initial orders")
    except Exception as e:
        print(f"Error preparing initial orders: {e}")
        return False
    
    # Generate random orders (39 more to reach 50 total)
    print("Generating random orders...")
    random_orders_data, random_order_items_data = _generate_random_order_data(customers, books, 39)
    print(f"Generated {len(random_orders_data)} random orders")
    
    # Combine all orders
    all_orders_data = initial_orders_data + random_orders_data
    all_order_items_data = initial_order_items_data + random_order_items_data
    
    # Bulk insert orders and items in batches
    print(f"Inserting {len(all_orders_data)} orders in batches...")
    total_created = _bulk_insert_orders_with_items(all_orders_data, all_order_items_data, batch_size=20)
    
    # Print summary
    try:
        total_orders = Order.query.count()
        pending_count = Order.query.filter_by(status='pending').count()
        confirmed_count = Order.query.filter_by(status='confirmed').count()
        completed_count = Order.query.filter_by(status='completed').count()
        cancelled_count = Order.query.filter_by(status='cancelled').count()
        
        print("\nOrders seeded successfully!")
        print(f"   - Total orders: {total_orders}")
        print(f"   - Pending: {pending_count}")
        print(f"   - Confirmed: {confirmed_count}")
        print(f"   - Completed: {completed_count}")
        print(f"   - Cancelled: {cancelled_count}")
        print(f"   - Distributed across {len(customers)} customers")
        print("   - Books from multiple categories: Sach Tieng Viet, Truyen Tranh, Do Trang Tri, Van Phong Pham")
        return True
    except Exception as e:
        print(f"Error getting order statistics: {e}")
        return True  # Still return True if orders were created


# For standalone execution
if __name__ == '__main__':
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_orders(force_reseed=True)