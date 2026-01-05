import json
import os
from models import db, User, Book, Banner, Category, Order, OrderItem
from utils.helpers import hash_password, generate_slug, generate_unique_book_slug
from datetime import datetime
from decimal import Decimal
from sqlalchemy import text, inspect
from seed_orders import seed_orders

def load_seed_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'seed_data.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def seed_database():
    print("Starting database seed...")
    
    # Load data from JSON
    try:
        seed_data = load_seed_data()
    except FileNotFoundError:
        print("Error: seed_data.json not found!")
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in seed_data.json: {e}")
        return
    
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
    
    # Check if customer_code column exists
    has_customer_code_column = True
    try:
        db.session.execute(text("SELECT customer_code FROM users LIMIT 1"))
    except Exception:
        has_customer_code_column = False
    
    # Create Users
    users_to_create = []
    users_data = seed_data.get('users', [])
    
    for user_data in users_data:
        username = user_data.get('username')
        if not username:
            continue
            
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"User '{username}' already exists, skipping")
            continue
        
        # Prepare user data
        new_user_data = {
            'username': username,
            'password_hash': hash_password(user_data.get('password', 'pass123')),
            'email': user_data.get('email'),
            'full_name': user_data.get('full_name'),
            'role': user_data.get('role', 'customer'),
            'is_active': user_data.get('is_active', True)
        }
        
        if has_customer_code_column and user_data.get('customer_code'):
            new_user_data['customer_code'] = user_data.get('customer_code')
        
        users_to_create.append(User(**new_user_data))
        if has_customer_code_column and user_data.get('customer_code'):
            print(f"Prepared user {username} (Customer {user_data.get('customer_code')})")
        else:
            print(f"Prepared user {username}")
    
    # Bulk insert users in batches
    if users_to_create:
        batch_size = 10
        for i in range(0, len(users_to_create), batch_size):
            batch = users_to_create[i:i + batch_size]
            try:
                db.session.bulk_save_objects(batch)
                db.session.commit()
                print(f"Created {len(batch)} users (batch {i//batch_size + 1})")
            except Exception as e:
                db.session.rollback()
                print(f"Warning committing users batch: {e}")
    
    # Create Categories
    categories_to_create = []
    categories_data = seed_data.get('categories', [])
    
    # Check if slug column exists
    try:
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('categories')]
        has_slug_column = 'slug' in columns
    except Exception:
        has_slug_column = False
    
    # Query max category_code once before the loop to avoid duplicate codes
    if has_slug_column:
        from sqlalchemy import func
        max_code = db.session.query(func.max(Category.category_code)).scalar()
        if max_code:
            next_category_number = int(max_code[2:]) + 1
        else:
            next_category_number = 1
    else:
        next_category_number = 1
    
    for category_data in categories_data:
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
                print(f"  Category '{category_data.get('slug' if has_slug_column else 'key')}' already exists, skipping")
                continue
            
            # Create new category
            if has_slug_column:
                category_code = f'DM{next_category_number:06d}'
                next_category_number += 1
                
                category_obj = Category(
                    key=category_data['key'],
                    name=category_data['name'],
                    slug=category_data['slug'],
                    description=category_data.get('description'),
                    display_order=category_data.get('display_order', 0),
                    is_active=category_data.get('is_active', True),
                    category_code=category_code
                )
                categories_to_create.append(category_obj)
            else:
                # Use raw SQL if slug column doesn't exist
                db.session.execute(
                    text("""
                        INSERT INTO categories (key, name, description, display_order, is_active, created_at, updated_at)
                        VALUES (:key, :name, :description, :display_order, :is_active, :created_at, :updated_at)
                    """),
                    {
                        'key': category_data['key'],
                        'name': category_data['name'],
                        'description': category_data.get('description'),
                        'display_order': category_data.get('display_order', 0),
                        'is_active': category_data.get('is_active', True),
                        'created_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                )
                db.session.commit()
                print(f"Created category '{category_data['name']}'")
        except Exception as e:
            error_str = str(e)
            if 'unique' in error_str.lower() or 'duplicate' in error_str.lower():
                print(f"  Category '{category_data.get('name', 'unknown')}' already exists (duplicate constraint), skipping")
                db.session.rollback()
            else:
                print(f"Error creating category '{category_data.get('name', 'unknown')}': {str(e)}")
                db.session.rollback()
    
    # Bulk insert categories
    if categories_to_create:
        try:
            db.session.bulk_save_objects(categories_to_create)
            db.session.commit()
            print(f"Created {len(categories_to_create)} categories")
        except Exception as e:
            db.session.rollback()
            print(f"Category seed failed: {str(e)}")
    
    # Create Books
    existing_books = Book.query.first()
    if existing_books:
        print(f"Books already exist ({Book.query.count()} books), skipping book creation")
    else:
        # Check if books table has slug column
        has_book_slug_column = False
        try:
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('books')]
            has_book_slug_column = 'slug' in columns
        except Exception:
            pass
        
        books_to_create = []
        books_data = seed_data.get('books', [])
        
        # Track existing titles to avoid duplicates
        existing_titles = set()
        if has_book_slug_column:
            existing_books_query = db.session.execute(
                text("SELECT title FROM books")
            )
            existing_titles = {row[0] for row in existing_books_query}
        
        # Query max book_code once before the loop to avoid duplicate codes
        # Track next number in memory to ensure uniqueness within the batch
        if has_book_slug_column:
            from sqlalchemy import func
            max_book_code = db.session.query(func.max(Book.book_code)).scalar()
            if max_book_code:
                next_book_number = int(max_book_code[2:]) + 1  # Extract number from MS000001 → 1
            else:
                next_book_number = 1
        else:
            next_book_number = 1
        
        for book_data in books_data:
            try:
                title = book_data.get('title', '')
                if not title:
                    continue
                
                # Check if book already exists
                if has_book_slug_column:
                    if title in existing_titles:
                        print(f"  Book '{title}' already exists, skipping")
                        continue
                    
                    # Generate slug from title
                    base_slug = generate_slug(title)
                    if not base_slug:
                        print(f"Cannot generate slug for book '{title}', skipping")
                        continue
                    
                    # Generate unique slug
                    slug = generate_unique_book_slug(base_slug, Book)
                    existing_titles.add(title)
                else:
                    # Fallback: check by title using raw SQL
                    result = db.session.execute(
                        text("SELECT id FROM books WHERE title = :title LIMIT 1"),
                        {'title': title}
                    ).fetchone()
                    if result:
                        print(f"  Book '{title}' already exists, skipping")
                        continue
                    slug = None
                
                # Generate book_code sequentially
                if has_book_slug_column:
                    book_code = f'MS{next_book_number:06d}'
                    next_book_number += 1
                else:
                    book_code = None  # Will be handled by raw SQL if needed
                
                # Create book object
                if has_book_slug_column:
                    book_obj = Book(
                        title=title,
                        slug=slug,
                        author=book_data.get('author', ''),
                        category=book_data.get('category', ''),
                        description=book_data.get('description'),
                        price=Decimal(str(book_data.get('price', 0))),
                        stock=book_data.get('stock', 0),
                        image_url=book_data.get('image_url'),
                        publisher=book_data.get('publisher'),
                        publish_date=book_data.get('publish_date'),
                        pages=book_data.get('pages', 0),
                        book_code=book_code
                    )
                    books_to_create.append(book_obj)
                else:
                    # Use raw SQL if slug column doesn't exist
                    db.session.execute(
                        text("""
                            INSERT INTO books (title, author, category, description, price, stock, image_url, publisher, publish_date, pages, created_at, updated_at)
                            VALUES (:title, :author, :category, :description, :price, :stock, :image_url, :publisher, :publish_date, :pages, :created_at, :updated_at)
                        """),
                        {
                            'title': title,
                            'author': book_data.get('author', ''),
                            'category': book_data.get('category', ''),
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
            except Exception as e:
                error_str = str(e)
                if 'unique' in error_str.lower() or 'duplicate' in error_str.lower():
                    print(f"  Book '{book_data.get('title', 'unknown')}' already exists (duplicate constraint), skipping")
                    db.session.rollback()
                else:
                    print(f"Error preparing book '{book_data.get('title', 'unknown')}': {str(e)}")
                    db.session.rollback()
        
        # Bulk insert books in batches
        if books_to_create:
            batch_size = 50
            created_count = 0
            for i in range(0, len(books_to_create), batch_size):
                batch = books_to_create[i:i + batch_size]
                try:
                    db.session.bulk_save_objects(batch)
                    db.session.commit()
                    created_count += len(batch)
                    print(f"Created {len(batch)} books (batch {i//batch_size + 1}, total: {created_count})")
                except Exception as e:
                    db.session.rollback()
                    print(f"Error committing books batch: {str(e)}")
    
    # Create Banners
    with db.session.no_autoflush:
        existing_banners = Banner.query.first()
    
    if not existing_banners:
        banners_to_create = []
        banners_data = seed_data.get('banners', [])
        
        # Query max banner_code once before the loop to avoid duplicate codes
        # Track next number in memory to ensure uniqueness within the batch
        from sqlalchemy import func
        max_banner_code = db.session.query(func.max(Banner.banner_code)).scalar()
        if max_banner_code:
            next_banner_number = int(max_banner_code[2:]) + 1  # Extract number from BN000001 → 1
        else:
            next_banner_number = 1
        
        for banner_data in banners_data:
            # Generate banner_code sequentially
            banner_code = f'BN{next_banner_number:06d}'
            next_banner_number += 1
            
            banner_obj = Banner(
                title=banner_data.get('title', ''),
                description=banner_data.get('description'),
                link=banner_data.get('link'),
                bg_color=banner_data.get('bg_color', '#6366f1'),
                text_color=banner_data.get('text_color', '#ffffff'),
                position=banner_data.get('position', 'main'),
                display_order=banner_data.get('display_order', 0),
                is_active=banner_data.get('is_active', True),
                banner_code=banner_code
            )
            banners_to_create.append(banner_obj)
        
        # Bulk insert banners
        if banners_to_create:
            try:
                db.session.bulk_save_objects(banners_to_create)
                db.session.commit()
                print(f"Created {len(banners_to_create)} sample banners")
            except Exception as e:
                db.session.rollback()
                print(f"Warning committing banners: {e}")
    else:
        print(f"Banners already exist ({Banner.query.count()} banners), skipping banner creation")
    
    # Seed Orders
    # Use seed_orders function from seed_orders.py
    # Note: seed_orders() commits internally, so no need to commit again
    seed_orders()
    
    # Print success message (seed_orders() already committed)
    print("\n Database seeded successfully!")
    print("\n Login Credentials:")
    print("   Admin:  admin / admin123 (Super Admin)")
    print("   User1:  user1 / pass123 (Customer KH001)")
    print("   User2:  user2 / pass123 (Customer KH002)")
    
    books_count = Book.query.count()
    print(f"\n Books: {books_count} books across 4 categories")
    print("   - Sach Tieng Viet: Vietnamese literature books")
    print("   - Truyen Tranh: Comics and manga")
    print("   - Do Trang Tri: Decorative items and souvenirs")
    print("   - Van Phong Pham: Office supplies")
    print("\n Banners: 3 main banners + 2 side banners")
    print("\n Orders: 50 orders with various statuses")
    print("\n Note: Best Sellers are dynamically computed from order history")

if __name__ == '__main__':
    # For standalone testing
    from app import create_app
    app = create_app()
    with app.app_context():
        seed_database()