"""
File: routes/categories.py

Mục đích:
Xử lý các route liên quan đến quản lý categories và sách theo category

Các endpoint trong file này:
- GET /api/categories: Lấy danh sách categories (public)
- GET /api/categories/<id>: Lấy chi tiết category theo ID
- GET /api/categories/<slug>/books: Lấy danh sách sách theo category slug (có sorting)
- GET /api/categories/<slug>/books/<book_slug>: Lấy chi tiết sách theo category slug và book slug
- POST /api/admin/categories: Tạo category mới (admin)
- PUT /api/admin/categories/<id>: Cập nhật category (admin)
- DELETE /api/admin/categories/<id>: Xóa category (admin)

Dependencies:
- models.Category: Model cho bảng categories
- models.Book: Model cho bảng books
- utils.helpers: admin_required decorator, generate_slug, generate_unique_slug, generate_category_key, generate_unique_category_key, generate_category_code
"""
from flask import Blueprint, request, jsonify
from models import Category, Book, db
from utils.helpers import admin_required, generate_slug, generate_unique_slug, generate_category_key, generate_unique_category_key, generate_category_code

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Lấy danh sách categories (public)
    
    Flow:
    1. Lấy query parameter include_inactive (default: false)
    2. Query categories từ database
    3. Nếu active_only=True: chỉ lấy categories có is_active=True
    4. Sắp xếp theo display_order và id
    5. Trả về danh sách categories
    
    Query Parameters:
    - include_inactive (string): 'true' để bao gồm categories không active (default: 'false')
    
    Returns:
        - 200: Danh sách categories
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy query parameter
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        active_only = not include_inactive
        
        # Bước 2-4: Query và sắp xếp categories
        query = Category.query
        if active_only:
            query = query.filter_by(is_active=True)
        categories = query.order_by(Category.display_order.asc(), Category.id.asc()).all()
        
        # Bước 5: Trả về danh sách
        return jsonify({
            'categories': [cat.to_dict() for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách categories: {str(e)}'}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Lấy chi tiết category
    
    Flow:
    1. Query category theo category_id
    2. Kiểm tra category có tồn tại không
    3. Trả về thông tin category
    
    Returns:
        - 200: Chi tiết category
        - 404: Category không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1: Query category
        category = Category.query.get(category_id)
        
        # Bước 2: Kiểm tra category có tồn tại không
        if not category:
            return jsonify({'error': 'Category không tồn tại'}), 404
        
        # Bước 3: Trả về thông tin category
        return jsonify({'category': category.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy chi tiết category: {str(e)}'}), 500

@categories_bp.route('/categories/<slug>/books', methods=['GET'])
def get_category_books(slug):
    """
    Lấy danh sách sách theo category slug (RESTful endpoint)
    
    Flow:
    1. Tìm category theo slug
    2. Kiểm tra category có tồn tại không
    3. Lấy query parameters (page, per_page, sort_by)
    4. Query books theo category key với sorting
    5. Áp dụng pagination
    6. Trả về danh sách sách với pagination info
    
    Query Parameters:
    - page (int): Số trang (default: 1)
    - per_page (int): Số items mỗi trang (default: 12)
    - sort_by (str): Sắp xếp (newest|price_asc|price_desc|bestseller, default: newest)
    
    Returns:
        - 200: Danh sách sách với pagination
        - 404: Category không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1-2: Tìm category theo slug
        category = Category.query.filter_by(slug=slug).first()
        if not category:
            return jsonify({'error': 'Category không tồn tại'}), 404
        
        # Bước 3: Lấy query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        sort_by = request.args.get('sort_by', 'newest', type=str)
        
        # Bước 4: Query books theo category key
        query = Book.query.filter_by(category=category.key)
        
        # Áp dụng sorting dựa vào sort_by parameter
        if sort_by == 'price_asc':
            query = query.order_by(Book.price.asc())
        elif sort_by == 'price_desc':
            query = query.order_by(Book.price.desc())
        elif sort_by == 'bestseller':
            # Sort by sold count using subquery
            from models import OrderItem, Order
            from sqlalchemy import func, desc
            
            sold_subquery = (
                db.session.query(
                    OrderItem.book_id,
                    func.sum(OrderItem.quantity).label('total_sold')
                )
                .join(Order)
                .filter(Order.status == 'completed')
                .group_by(OrderItem.book_id)
                .subquery()
            )
            
            query = query.outerjoin(sold_subquery, Book.id == sold_subquery.c.book_id)
            query = query.order_by(desc(func.coalesce(sold_subquery.c.total_sold, 0)))
        else:  # newest (default)
            query = query.order_by(Book.created_at.desc())
        
        # Bước 5: Áp dụng pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Bước 6: Trả về danh sách sách
        return jsonify({
            'books': [book.to_dict() for book in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'category_slug': category.slug,
            'category_key': category.key,
            'category_name': category.name
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách sách theo category: {str(e)}'}), 500

@categories_bp.route('/categories/<slug>/books/<book_slug>', methods=['GET'])
def get_category_book(slug, book_slug):
    """
    Lấy chi tiết sách theo category slug và book slug (RESTful endpoint)
    
    Flow:
    1. Tìm category theo slug
    2. Kiểm tra category có tồn tại không
    3. Query book theo book_slug và category key
    4. Kiểm tra book có tồn tại không
    5. Kiểm tra book có thuộc category đúng không
    6. Trả về thông tin sách
    
    Returns:
        - 200: Chi tiết sách
        - 404: Category không tồn tại, sách không tồn tại hoặc không thuộc category này
        - 500: Lỗi server
    """
    try:
        # Bước 1-2: Tìm category theo slug
        category = Category.query.filter_by(slug=slug).first()
        if not category:
            return jsonify({'error': 'Category không tồn tại'}), 404
        
        # Bước 3-4: Query book theo book_slug và category key
        book = Book.query.filter_by(slug=book_slug, category=category.key).first()
        if not book:
            return jsonify({'error': 'Sách không tồn tại hoặc không thuộc category này'}), 404
        
        # Bước 5-6: Trả về thông tin sách
        return jsonify({
            'book': book.to_dict(),
            'category_slug': category.slug,
            'category_key': category.key,
            'category_name': category.name
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy chi tiết sách: {str(e)}'}), 500

@categories_bp.route('/admin/categories', methods=['POST'])
@admin_required
def create_category():
    """
    Tạo category mới (chỉ admin)
    
    Flow:
    1. Lấy dữ liệu từ request body
    2. Validate các trường bắt buộc (name)
    3. Tự động generate key và slug từ name
    4. Đảm bảo slug unique (auto-append số nếu trùng)
    5. Tạo category mới trong database
    6. Trả về thông tin category đã tạo
    
    Returns:
        - 201: Tạo category thành công
        - 400: Dữ liệu không hợp lệ
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy dữ liệu từ request
        data = request.get_json()
        
        # Bước 2: Validate các trường bắt buộc
        if not data.get('name'):
            return jsonify({'error': 'Tên danh mục là bắt buộc'}), 400
        
        name = data['name'].strip()
        
        # Bước 3: Tự động generate key và slug từ name
        # =====================================================================
        # Generate key tự động (VD: "Sách Thiếu Nhi" -> "SACH_THIEU_NHI")
        base_key = generate_category_key(name)
        
        # Kiểm tra: Nếu key rỗng (tên chỉ chứa ký tự đặc biệt), trả về lỗi
        if not base_key:
            return jsonify({
                'error': 'Không thể tạo key từ tên danh mục. Vui lòng sử dụng tên có ký tự chữ cái hoặc số.'
            }), 400
        
        # Đảm bảo key là duy nhất trong database (thêm suffix nếu trùng)
        key = generate_unique_category_key(base_key, Category)
        
        # Generate slug tự động (VD: "Sách Thiếu Nhi" -> "sach-thieu-nhi")
        base_slug = generate_slug(name)
        
        # Kiểm tra: Nếu slug rỗng (tên chỉ chứa ký tự đặc biệt), trả về lỗi
        if not base_slug:
            return jsonify({
                'error': 'Không thể tạo slug từ tên danh mục. Vui lòng sử dụng tên có ký tự chữ cái hoặc số.'
            }), 400
        
        # Đảm bảo slug là duy nhất trong database (thêm suffix nếu trùng)
        slug = generate_unique_slug(base_slug, Category)
        
        # Generate category_code
        category_code = generate_category_code(Category)
        
        # Bước 4: Tạo category mới
        new_category = Category(
            category_code=category_code,
            key=key,
            name=name,
            slug=slug,
            description=data.get('description', '').strip() if data.get('description') else None,
            display_order=data.get('display_order', 0),
            is_active=data.get('is_active', True)
        )
        db.session.add(new_category)
        db.session.commit()
        
        # Bước 5: Trả về thông tin category
        return jsonify({
            'message': 'Tạo category thành công',
            'category': new_category.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi tạo category: {str(e)}'}), 500

@categories_bp.route('/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """
    Cập nhật category (chỉ admin)
    
    Flow:
    1. Lấy category_id từ URL
    2. Kiểm tra category có tồn tại không
    3. Lấy dữ liệu từ request body
    4. Validate name nếu có
    5. Tự động regenerate key và slug nếu name thay đổi
    6. Cập nhật các trường được gửi lên
    7. Lưu vào database
    8. Trả về thông tin category đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Dữ liệu không hợp lệ
        - 404: Category không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1 & 2: Kiểm tra category có tồn tại không
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category không tồn tại'}), 404
        
        # Bước 3: Lấy dữ liệu từ request
        data = request.get_json()
        
        # Bước 4-5: Validate và regenerate key/slug nếu name thay đổi
        if 'name' in data:
            new_name = data['name'].strip()
            if not new_name:
                return jsonify({'error': 'Tên danh mục không được để trống'}), 400
            
            # Chỉ regenerate nếu name thực sự thay đổi
            if new_name != category.name:
                category.name = new_name
                
                # Tự động regenerate key nếu name thay đổi
                base_key = generate_category_key(new_name)
                category.key = generate_unique_category_key(base_key, Category, exclude_id=category.id)
                
                # Tự động regenerate slug nếu name thay đổi
                base_slug = generate_slug(new_name)
                category.slug = generate_unique_slug(base_slug, Category, exclude_id=category.id)
        
        if 'description' in data:
            category.description = data['description'].strip() if data['description'] else None
        if 'display_order' in data:
            category.display_order = data['display_order']
        if 'is_active' in data:
            category.is_active = data['is_active']
        
        # Bước 6: Lưu vào database
        db.session.commit()
        
        # Bước 7: Trả về thông tin category
        return jsonify({
            'message': 'Cập nhật category thành công',
            'category': category.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật category: {str(e)}'}), 500

@categories_bp.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """
    Xóa category (chỉ admin)
    
    Flow:
    1. Lấy category_id từ URL
    2. Kiểm tra category có tồn tại không
    3. Xóa category khỏi database
    4. Trả về thông báo thành công
    
    Returns:
        - 200: Xóa thành công
        - 404: Category không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1 & 2: Kiểm tra category có tồn tại không
        category = Category.query.get(category_id)
        if not category:
            return jsonify({'error': 'Category không tồn tại'}), 404
        
        # Bước 3: Xóa category
        db.session.delete(category)
        db.session.commit()
        
        # Bước 4: Trả về thông báo thành công
        return jsonify({'message': 'Xóa category thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi xóa category: {str(e)}'}), 500

