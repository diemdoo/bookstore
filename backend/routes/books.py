"""
Routes cho quản lý sách (CRUD, tìm kiếm)
"""
from flask import Blueprint, request, jsonify
from business.services.book_service import BookService
from utils.helpers import admin_required

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách sách (có pagination, filter, search)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        author = request.args.get('author', '').strip()
        
        # Call business service
        books, total, pages = BookService.get_books(page, per_page, search, category, author)
        
        return jsonify({
            'books': [book.to_dict() for book in books],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách sách: {str(e)}'}), 500

# Removed GET /books/<int:book_id> - Now use /categories/<category_key>/books/<book_id> instead

@books_bp.route('/books', methods=['POST'])
@admin_required
def create_book():
    """
    Tạo sách mới (admin only)
    """
    try:
        data = request.get_json()
        
        # Call business service
        book_dto, error = BookService.create_book(data)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Tạo sách thành công',
            'book': book_dto.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi tạo sách: {str(e)}'}), 500

@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    """
    Cập nhật thông tin sách (admin only)
    """
    try:
        data = request.get_json()
        
        # Call business service
        book_dto, error = BookService.update_book(book_id, data)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 400
            return jsonify({'error': error}), status_code
        
        return jsonify({
            'message': 'Cập nhật sách thành công',
            'book': book_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi cập nhật sách: {str(e)}'}), 500

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """
    Xóa sách (admin only)
    """
    try:
        # Call business service
        success, error = BookService.delete_book(book_id)
        
        if error:
            status_code = 404 if 'không tồn tại' in error else 500
            return jsonify({'error': error}), status_code
        
        return jsonify({'message': 'Xóa sách thành công'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi xóa sách: {str(e)}'}), 500

@books_bp.route('/books/bestsellers', methods=['GET'])
def get_bestsellers():
    """
    Lấy danh sách sách bán chạy nhất dựa trên số lượng đã bán (dynamic query from order_items)
    """
    try:
        from models import db, Book, OrderItem
        from business.dto.book_dto import BookDTO
        from sqlalchemy import func, desc
        
        limit = request.args.get('limit', 10, type=int)
        
        # Query top books by total quantity sold
        bestsellers = db.session.query(
            Book,
            func.sum(OrderItem.quantity).label('total_sold')
        ).join(
            OrderItem, Book.id == OrderItem.book_id
        ).group_by(
            Book.id
        ).order_by(
            desc('total_sold')
        ).limit(limit).all()
        
        # If no orders yet, return top books by ID (fallback)
        if not bestsellers:
            books = Book.query.order_by(Book.id.asc()).limit(limit).all()
            return jsonify({
                'books': [BookDTO.from_model(book).to_dict() for book in books],
                'count': len(books)
            }), 200
        
        books = [book for book, _ in bestsellers]
        return jsonify({
            'books': [BookDTO.from_model(book).to_dict() for book in books],
            'count': len(books)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy sách bán chạy: {str(e)}'}), 500