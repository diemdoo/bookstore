"""
File: routes/books.py

Mục đích:
Xử lý các route liên quan đến quản lý sách (CRUD, tìm kiếm, lọc)

Các endpoint trong file này:
- GET /api/books: Lấy danh sách sách (có pagination, search, filter)
- POST /api/books: Tạo sách mới (admin only)
- PUT /api/books/<id>: Cập nhật thông tin sách (admin only)
- DELETE /api/books/<id>: Xóa sách (admin only)
- GET /api/books/bestsellers: Lấy danh sách sách bán chạy nhất

Dependencies:
- models.Book: Model cho bảng books
- models.OrderItem: Model cho bảng order_items (để tính bestsellers)
- utils.helpers: admin_required decorator
- sqlalchemy: Để query và aggregate
"""
from flask import Blueprint, request, jsonify
from models import Book, OrderItem, db
from utils.helpers import admin_required
from sqlalchemy import func, desc

books_bp = Blueprint('books', __name__)

@books_bp.route('/books', methods=['GET'])
def get_books():
    """
    Lấy danh sách sách với pagination, search và filter
    
    Flow:
    1. Lấy các query parameters (page, per_page, search, category, author)
    2. Tạo query cơ bản từ Book model
    3. Áp dụng filter search (tìm trong title)
    4. Áp dụng filter category (lọc theo category)
    5. Áp dụng filter author (lọc theo author)
    6. Thực hiện pagination
    7. Trả về danh sách sách với thông tin pagination
    
    Query Parameters:
    - page (int): Số trang (default: 1)
    - per_page (int): Số items mỗi trang (default: 12)
    - search (string): Từ khóa tìm kiếm trong title
    - category (string): Lọc theo category
    - author (string): Lọc theo author
    
    Returns:
        - 200: Danh sách sách với pagination info
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        author = request.args.get('author', '').strip()
        
        # Bước 2: Tạo query cơ bản
        query = Book.query
        
        # Bước 3: Áp dụng filter search (tìm trong title)
        if search:
            query = query.filter(Book.title.ilike(f'%{search}%'))
        
        # Bước 4: Áp dụng filter category
        if category:
            query = query.filter(Book.category == category)
        
        # Bước 5: Áp dụng filter author
        if author:
            query = query.filter(Book.author.ilike(f'%{author}%'))
        
        # Bước 6: Thực hiện pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Bước 7: Trả về danh sách sách
        return jsonify({
            'books': [book.to_dict() for book in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy danh sách sách: {str(e)}'}), 500

# Note: GET /books/<int:book_id> đã được chuyển sang /categories/<category_key>/books/<book_id>

@books_bp.route('/books', methods=['POST'])
@admin_required
def create_book():
    """
    Tạo sách mới (chỉ admin)
    
    Flow:
    1. Lấy dữ liệu từ request body
    2. Validate các trường bắt buộc (title, author, category, price, stock)
    3. Validate định dạng dữ liệu (price >= 0, stock >= 0, độ dài các trường)
    4. Tạo Book mới trong database
    5. Trả về thông tin sách đã tạo
    
    Returns:
        - 201: Tạo sách thành công
        - 400: Dữ liệu không hợp lệ hoặc thiếu trường bắt buộc
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy dữ liệu từ request
        data = request.get_json()
        
        # Bước 2: Validate các trường bắt buộc
        required_fields = ['title', 'author', 'category', 'price', 'stock']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Thiếu trường {field}'}), 400
        
        # Validate title
        title = data.get('title', '').strip()
        if not title or len(title) < 1:
            return jsonify({'error': 'Tiêu đề sách không được để trống'}), 400
        if len(title) > 200:
            return jsonify({'error': 'Tiêu đề sách không được vượt quá 200 ký tự'}), 400
        
        # Validate author
        author = data.get('author', '').strip()
        if not author or len(author) < 1:
            return jsonify({'error': 'Tác giả không được để trống'}), 400
        
        # Validate category
        category = data.get('category', '').strip()
        if not category:
            return jsonify({'error': 'Thể loại không được để trống'}), 400
        
        # Bước 3: Validate định dạng dữ liệu
        try:
            price = float(data.get('price', 0))
            if price < 0:
                return jsonify({'error': 'Giá sách phải lớn hơn hoặc bằng 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Giá sách không hợp lệ'}), 400
        
        try:
            stock = int(data.get('stock', 0))
            if stock < 0:
                return jsonify({'error': 'Số lượng tồn kho phải lớn hơn hoặc bằng 0'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Số lượng tồn kho không hợp lệ'}), 400
        
        # Bước 4: Tạo Book mới
        new_book = Book(
            title=title,
            author=author,
            category=category,
            description=data.get('description', '').strip() if data.get('description') else None,
            price=price,
            stock=stock,
            image_url=data.get('image_url', '').strip() if data.get('image_url') else None,
            publisher=data.get('publisher', '').strip() if data.get('publisher') else None,
            publish_date=data.get('publish_date', '').strip() if data.get('publish_date') else None,
            distributor=data.get('distributor', '').strip() if data.get('distributor') else None,
            dimensions=data.get('dimensions', '').strip() if data.get('dimensions') else None,
            pages=int(data['pages']) if data.get('pages') else None,
            weight=int(data['weight']) if data.get('weight') else None
        )
        db.session.add(new_book)
        db.session.commit()
        
        # Bước 5: Trả về thông tin sách đã tạo
        return jsonify({
            'message': 'Tạo sách thành công',
            'book': new_book.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi tạo sách: {str(e)}'}), 500

@books_bp.route('/books/<int:book_id>', methods=['PUT'])
@admin_required
def update_book(book_id):
    """
    Cập nhật thông tin sách (chỉ admin)
    
    Flow:
    1. Lấy book_id từ URL
    2. Kiểm tra sách có tồn tại không
    3. Lấy dữ liệu từ request body
    4. Validate dữ liệu (nếu có)
    5. Cập nhật các trường được gửi lên
    6. Lưu vào database
    7. Trả về thông tin sách đã cập nhật
    
    Returns:
        - 200: Cập nhật thành công
        - 400: Dữ liệu không hợp lệ
        - 404: Sách không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1 & 2: Kiểm tra sách có tồn tại không
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Sách không tồn tại'}), 404
        
        # Bước 3: Lấy dữ liệu từ request
        data = request.get_json()
        
        # Bước 4 & 5: Validate và cập nhật các trường
        if 'title' in data:
            title = data['title'].strip()
            if title and len(title) > 200:
                return jsonify({'error': 'Tiêu đề sách không được vượt quá 200 ký tự'}), 400
            if title:
                book.title = title
        
        if 'author' in data:
            author = data['author'].strip()
            if author:
                book.author = author
        
        if 'category' in data:
            category = data['category'].strip()
            if category:
                book.category = category
        
        if 'description' in data:
            book.description = data['description'].strip() if data['description'] else None
        
        if 'price' in data:
            try:
                price = float(data['price'])
                if price < 0:
                    return jsonify({'error': 'Giá sách phải lớn hơn hoặc bằng 0'}), 400
                book.price = price
            except (ValueError, TypeError):
                return jsonify({'error': 'Giá sách không hợp lệ'}), 400
        
        if 'stock' in data:
            try:
                stock = int(data['stock'])
                if stock < 0:
                    return jsonify({'error': 'Số lượng tồn kho phải lớn hơn hoặc bằng 0'}), 400
                book.stock = stock
            except (ValueError, TypeError):
                return jsonify({'error': 'Số lượng tồn kho không hợp lệ'}), 400
        
        if 'image_url' in data:
            book.image_url = data['image_url'].strip() if data['image_url'] else None
        
        if 'publisher' in data:
            book.publisher = data['publisher'].strip() if data['publisher'] else None
        
        if 'publish_date' in data:
            book.publish_date = data['publish_date'].strip() if data['publish_date'] else None
        
        if 'distributor' in data:
            book.distributor = data['distributor'].strip() if data['distributor'] else None
        
        if 'dimensions' in data:
            book.dimensions = data['dimensions'].strip() if data['dimensions'] else None
        
        if 'pages' in data:
            book.pages = int(data['pages']) if data.get('pages') else None
        
        if 'weight' in data:
            book.weight = int(data['weight']) if data.get('weight') else None
        
        # Bước 6: Lưu vào database
        db.session.commit()
        
        # Bước 7: Trả về thông tin sách đã cập nhật
        return jsonify({
            'message': 'Cập nhật sách thành công',
            'book': book.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi cập nhật sách: {str(e)}'}), 500

@books_bp.route('/books/<int:book_id>', methods=['DELETE'])
@admin_required
def delete_book(book_id):
    """
    Xóa sách (chỉ admin)
    
    Flow:
    1. Lấy book_id từ URL
    2. Kiểm tra sách có tồn tại không
    3. Xóa sách khỏi database
    4. Trả về thông báo thành công
    
    Returns:
        - 200: Xóa thành công
        - 404: Sách không tồn tại
        - 500: Lỗi server
    """
    try:
        # Bước 1 & 2: Kiểm tra sách có tồn tại không
        book = Book.query.get(book_id)
        if not book:
            return jsonify({'error': 'Sách không tồn tại'}), 404
        
        # Bước 3: Xóa sách
        db.session.delete(book)
        db.session.commit()
        
        # Bước 4: Trả về thông báo thành công
        return jsonify({'message': 'Xóa sách thành công'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Lỗi xóa sách: {str(e)}'}), 500

@books_bp.route('/books/bestsellers', methods=['GET'])
def get_bestsellers():
    """
    Lấy danh sách sách bán chạy nhất dựa trên số lượng đã bán
    
    Flow:
    1. Lấy limit từ query parameter (default: 10)
    2. Query database để tính tổng số lượng đã bán của mỗi sách
    3. Sắp xếp theo số lượng bán giảm dần
    4. Lấy top N sách
    5. Nếu chưa có đơn hàng nào, trả về top sách theo ID (fallback)
    6. Trả về danh sách sách bán chạy
    
    Query Parameters:
    - limit (int): Số lượng sách cần lấy (default: 10)
    
    Returns:
        - 200: Danh sách sách bán chạy
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy limit từ query parameter
        limit = request.args.get('limit', 10, type=int)
        
        # Bước 2-4: Query top books by total quantity sold
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
        
        # Bước 5: Nếu chưa có đơn hàng, trả về top sách theo ID (fallback)
        if not bestsellers:
            books = Book.query.order_by(Book.id.asc()).limit(limit).all()
            return jsonify({
                'books': [book.to_dict() for book in books],
                'count': len(books)
            }), 200
        
        # Bước 6: Trả về danh sách sách bán chạy
        books = [book for book, _ in bestsellers]
        return jsonify({
            'books': [book.to_dict() for book in books],
            'count': len(books)
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy sách bán chạy: {str(e)}'}), 500