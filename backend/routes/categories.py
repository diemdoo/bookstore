"""
File: routes/categories.py

Mục đích:
Xử lý các route liên quan đến quản lý categories và sách theo category

Các endpoint trong file này:
- GET /api/categories: Lấy danh sách categories (public)
- GET /api/categories/<id>: Lấy chi tiết category
- GET /api/categories/<key>/books: Lấy danh sách sách theo category
- GET /api/categories/<key>/books/<id>: Lấy chi tiết sách theo category
- POST /api/admin/categories: Tạo category mới (admin)
- PUT /api/admin/categories/<id>: Cập nhật category (admin)
- DELETE /api/admin/categories/<id>: Xóa category (admin)

Dependencies:
- models.Category: Model cho bảng categories
- models.Book: Model cho bảng books
- utils.helpers: admin_required decorator
"""
from flask import Blueprint, request, jsonify
from models import Category, Book, db
from utils.helpers import admin_required
import urllib.parse

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

@categories_bp.route('/categories/<category_key>/books', methods=['GET'])
def get_category_books(category_key):
    """
    Lấy danh sách sách theo category key (RESTful endpoint)
    
    Flow:
    1. Decode URL-encoded category key
    2. Lấy query parameters (page, per_page)
    3. Query books theo category với pagination
    4. Trả về danh sách sách với pagination info
    
    Query Parameters:
    - page (int): Số trang (default: 1)
    - per_page (int): Số items mỗi trang (default: 12)
    
    Returns:
        - 200: Danh sách sách với pagination
        - 500: Lỗi server
    """
    try:
        # Bước 1: Decode URL-encoded category key
        category_key = urllib.parse.unquote(category_key)
        
        # Bước 2: Lấy query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        # Bước 3: Query books theo category với pagination
        query = Book.query.filter_by(category=category_key)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Bước 4: Trả về danh sách sách
        return jsonify({
            'books': [book.to_dict() for book in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages,
            'category_key': category_key
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách sách theo category: {str(e)}'}), 500

@categories_bp.route('/categories/<category_key>/books/<int:book_id>', methods=['GET'])
def get_category_book(category_key, book_id):
    """
    Lấy chi tiết sách theo category key và book id (RESTful endpoint)
    
    Flow:
    1. Decode URL-encoded category key
    2. Query book theo book_id
    3. Kiểm tra book có tồn tại không
    4. Kiểm tra book có thuộc category đúng không
    5. Trả về thông tin sách
    
    Returns:
        - 200: Chi tiết sách
        - 404: Sách không tồn tại hoặc không thuộc category này
        - 500: Lỗi server
    """
    try:
        # Bước 1: Decode URL-encoded category key
        category_key = urllib.parse.unquote(category_key)
        
        # Bước 2: Query book
        book = Book.query.get(book_id)
        
        # Bước 3: Kiểm tra book có tồn tại không
        if not book:
            return jsonify({'error': 'Sách không tồn tại'}), 404
        
        # Bước 4: Kiểm tra book có thuộc category đúng không
        if book.category != category_key:
            return jsonify({'error': 'Sách không thuộc category này'}), 404
        
        # Bước 5: Trả về thông tin sách
        return jsonify({
            'book': book.to_dict(),
            'category_key': category_key
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
    2. Validate các trường bắt buộc (key, name)
    3. Kiểm tra key đã tồn tại chưa
    4. Tạo category mới trong database
    5. Trả về thông tin category đã tạo
    
    Returns:
        - 201: Tạo category thành công
        - 400: Dữ liệu không hợp lệ hoặc key đã tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy dữ liệu từ request
        data = request.get_json()
        
        # Bước 2: Validate các trường bắt buộc
        if not data.get('key'):
            return jsonify({'error': 'Key là bắt buộc'}), 400
        if not data.get('name'):
            return jsonify({'error': 'Name là bắt buộc'}), 400
        
        # Bước 3: Kiểm tra key đã tồn tại chưa
        if Category.query.filter_by(key=data['key']).first():
            return jsonify({'error': f"Key '{data['key']}' đã tồn tại"}), 400
        
        # Bước 4: Tạo category mới
        new_category = Category(
            key=data['key'].strip(),
            name=data['name'].strip(),
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
    4. Validate key (nếu có) chưa được sử dụng bởi category khác
    5. Cập nhật các trường được gửi lên
    6. Lưu vào database
    7. Trả về thông tin category đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Dữ liệu không hợp lệ hoặc key đã tồn tại
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
        
        # Bước 4: Validate key nếu có thay đổi
        if 'key' in data and data['key'] != category.key:
            if Category.query.filter_by(key=data['key']).first():
                return jsonify({'error': f"Key '{data['key']}' đã tồn tại"}), 400
        
        # Bước 5: Cập nhật các trường
        if 'key' in data:
            category.key = data['key'].strip()
        if 'name' in data:
            category.name = data['name'].strip()
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

