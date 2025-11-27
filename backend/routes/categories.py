"""
Routes cho quản lý categories
"""
from flask import Blueprint, request, jsonify
from business.services.category_service import CategoryService
from utils.helpers import admin_required

categories_bp = Blueprint('categories', __name__)

@categories_bp.route('/categories', methods=['GET'])
def get_categories():
    """
    Lấy danh sách categories (public)
    Query params:
    - include_inactive: true/false (default: false) - Include inactive categories (admin only)
    """
    try:
        # Check if user wants to include inactive categories (admin only feature)
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        active_only = not include_inactive
        
        categories = CategoryService.get_all_categories(active_only=active_only)
        
        return jsonify({
            'categories': [cat.to_dict() for cat in categories]
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách categories: {str(e)}'}), 500

@categories_bp.route('/categories/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Lấy chi tiết category
    """
    try:
        category_dto, error = CategoryService.get_category(category_id)
        
        if error:
            return jsonify({'error': error}), 404
        
        return jsonify({'category': category_dto.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy chi tiết category: {str(e)}'}), 500

@categories_bp.route('/categories/<category_key>/books', methods=['GET'])
def get_category_books(category_key):
    """
    Lấy danh sách sách theo category key (RESTful endpoint)
    Query params:
    - page: Số trang (default: 1)
    - per_page: Số items mỗi trang (default: 12)
    """
    try:
        from business.services.book_service import BookService
        
        # Decode URL-encoded category key
        import urllib.parse
        category_key = urllib.parse.unquote(category_key)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        # Get books by category using existing service
        books, total, pages = BookService.get_books(page, per_page, '', category_key, '')
        
        return jsonify({
            'books': [book.to_dict() for book in books],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages,
            'category_key': category_key
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách sách theo category: {str(e)}'}), 500

@categories_bp.route('/categories/<category_key>/books/<int:book_id>', methods=['GET'])
def get_category_book(category_key, book_id):
    """
    Lấy chi tiết sách theo category key và book id (RESTful endpoint)
    """
    try:
        from business.services.book_service import BookService
        
        # Decode URL-encoded category key
        import urllib.parse
        category_key = urllib.parse.unquote(category_key)
        
        # Get book by ID
        book_dto, error = BookService.get_book(book_id)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 500
            return jsonify({'error': error}), status_code
        
        # Verify book belongs to the specified category
        if book_dto.category != category_key:
            return jsonify({'error': 'Sách không thuộc category này'}), 404
        
        return jsonify({
            'book': book_dto.to_dict(),
            'category_key': category_key
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy chi tiết sách: {str(e)}'}), 500

@categories_bp.route('/admin/categories', methods=['POST'])
@admin_required
def create_category():
    """
    Tạo category mới (Admin only)
    """
    try:
        data = request.get_json()
        
        category_dto, error = CategoryService.create_category(data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Tạo category thành công',
            'category': category_dto.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi tạo category: {str(e)}'}), 500

@categories_bp.route('/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """
    Cập nhật category (Admin only)
    """
    try:
        data = request.get_json()
        
        category_dto, error = CategoryService.update_category(category_id, data)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'message': 'Cập nhật category thành công',
            'category': category_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi cập nhật category: {str(e)}'}), 500

@categories_bp.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """
    Xóa category (Admin only)
    """
    try:
        success, error = CategoryService.delete_category(category_id)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({'message': 'Xóa category thành công'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi xóa category: {str(e)}'}), 500

