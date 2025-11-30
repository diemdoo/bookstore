"""
File: routes/chatbot.py

Mục đích:
Xử lý chatbot thông minh với Google Gemini Pro API, kết hợp với FAQ database.
Chatbot có thể hiểu context về bookstore và trả lời khách hàng một cách tự nhiên.

Các endpoint trong file này:
- POST /api/chatbot: Xử lý câu hỏi từ chatbot và trả về câu trả lời (FAQ + Gemini)

Dependencies:
- google.genai: Google Gen AI SDK (new library, replaces deprecated google-generativeai)
- models.Book, models.Category: Để lấy thông tin từ database
- config.Config: Để lấy GEMINI_API_KEY
"""
from flask import Blueprint, request, jsonify
from google import genai
from google.genai import types
from google.genai import errors
import logging
from sqlalchemy import func, desc, case
from models import Book, Category, OrderItem, Order, db
from config import Config

chatbot_bp = Blueprint('chatbot', __name__)

# Setup logger cho chatbot
logger = logging.getLogger(__name__)

# Module-level client (lazy initialization)
_genai_client = None

def get_genai_client():
    """
    Lazy initialization của Gemini client
    Tái sử dụng client across requests để tối ưu performance
    
    Returns:
        genai.Client: Gemini client instance, hoặc None nếu không có API key
    """
    global _genai_client
    
    if _genai_client is None:
        api_key = Config.GEMINI_API_KEY
        if api_key:
            try:
                _genai_client = genai.Client(api_key=api_key)
                logger.info("[CHATBOT] ✓ Gemini client initialized")
            except Exception as e:
                logger.error(f"[CHATBOT] ❌ Failed to initialize Gemini client: {str(e)}")
                return None
        else:
            logger.warning("[CHATBOT] ⚠️ No API key, cannot initialize Gemini client")
            return None
    
    return _genai_client

# FAQ database đơn giản - lưu các câu hỏi và câu trả lời (ưu tiên xử lý nhanh)
FAQ_DATABASE = {
    'chào': 'Xin chào! Tôi có thể giúp gì cho bạn?',
    'hello': 'Xin chào! Tôi có thể giúp gì cho bạn?',
    'giá': 'Bạn có thể xem giá sách ở trang chi tiết sách. Giá được hiển thị rõ ràng cho từng cuốn sách.',
    'thanh toán': 'Chúng tôi hỗ trợ thanh toán khi nhận hàng (COD). Bạn sẽ thanh toán khi nhận được sách.',
    'giao hàng': 'Chúng tôi giao hàng toàn quốc. Thời gian giao hàng từ 3-7 ngày làm việc.',
    'đổi trả': 'Bạn có thể đổi trả sách trong vòng 7 ngày kể từ ngày nhận hàng nếu sách có lỗi.',
    'đăng ký': 'Bạn có thể đăng ký tài khoản bằng cách click vào nút "Đăng ký" ở góc trên bên phải.',
    'đăng nhập': 'Bạn có thể đăng nhập bằng username và password đã đăng ký.',
    'giỏ hàng': 'Bạn cần đăng nhập để thêm sách vào giỏ hàng. Sau đó có thể xem và chỉnh sửa giỏ hàng.',
    'đơn hàng': 'Bạn có thể xem lịch sử đơn hàng sau khi đăng nhập vào tài khoản.',
    'mặc định': 'Xin lỗi, tôi chưa hiểu câu hỏi của bạn. Bạn có thể hỏi về: giá, thanh toán, giao hàng, đổi trả, đăng ký, đăng nhập, giỏ hàng, đơn hàng.'
}

def get_bookstore_context():
    """
    Lấy thông tin context về bookstore từ database (bao gồm bestsellers và sách theo category)
    
    Flow:
    1. Query danh sách categories (chỉ active)
    2. Đếm tổng số sách
    3. Query top 10 bestseller books (dựa trên số lượng đã bán)
    4. Query sample books từ mỗi category (top 3-5 sách với số lượng đã bán)
    5. Tạo context string với tất cả thông tin
    
    Returns:
        str: Context string mô tả về bookstore với bestsellers và sách theo category
    """
    try:
        # Bước 1: Lấy danh sách categories (chỉ active)
        categories = Category.query.filter_by(is_active=True).order_by(Category.display_order.asc()).all()
        category_names = [cat.name for cat in categories]
        
        # Bước 2: Đếm tổng số sách
        total_books = Book.query.count()
        
        # Bước 3: Query top 10 bestseller books (dựa trên số lượng đã bán từ orders completed)
        bestsellers_text = ""
        try:
            bestsellers = db.session.query(
                Book,
                func.sum(OrderItem.quantity).label('total_sold')
            ).join(OrderItem).join(Order).filter(
                Order.status == 'completed'
            ).group_by(Book.id).order_by(desc('total_sold')).limit(10).all()
            
            if bestsellers:
                bestsellers_list = []
                for idx, (book, total_sold) in enumerate(bestsellers, 1):
                    sold_count = int(total_sold) if total_sold else 0
                    bestsellers_list.append(f"{idx}. {book.title} - {book.author} (Đã bán: {sold_count})")
                
                bestsellers_text = "\n\nTop 10 sách bán chạy nhất:\n" + "\n".join(bestsellers_list)
        except Exception as e:
            logger.warning(f"[CHATBOT] Failed to query bestsellers: {str(e)}")
            # Continue without bestsellers if query fails
        
        # Bước 4: Query sample books từ mỗi category (top 3-5 sách với số lượng đã bán)
        category_books_text = ""
        try:
            category_sections = []
            for category in categories:
                # Query top 5 books trong category này (có sold count)
                # Sử dụng outerjoin để lấy cả sách chưa có order
                # Chỉ tính sold count từ orders completed
                category_books = db.session.query(
                    Book,
                    func.sum(
                        case(
                            (Order.status == 'completed', OrderItem.quantity),
                            else_=0
                        )
                    ).label('total_sold')
                ).outerjoin(OrderItem, Book.id == OrderItem.book_id).outerjoin(
                    Order, OrderItem.order_id == Order.id
                ).filter(
                    Book.category == category.key
                ).group_by(Book.id).order_by(
                    desc('total_sold'), Book.id.asc()
                ).limit(5).all()
                
                if category_books:
                    book_list = []
                    for book, total_sold in category_books:
                        sold_count = int(total_sold) if total_sold else 0
                        if sold_count > 0:
                            book_list.append(f"{book.title} - {book.author} (Đã bán: {sold_count})")
                        else:
                            book_list.append(f"{book.title} - {book.author}")
                    
                    if book_list:
                        category_sections.append(f"- {category.name}: {', '.join(book_list[:3])}")  # Chỉ lấy top 3 để không quá dài
            
            if category_sections:
                category_books_text = "\n\nSách theo danh mục:\n" + "\n".join(category_sections)
        except Exception as e:
            logger.warning(f"[CHATBOT] Failed to query category books: {str(e)}")
            # Continue without category books if query fails
        
        # Bước 5: Tạo context string với tất cả thông tin
        context = f"""
Cửa hàng có {total_books} cuốn sách trong các danh mục sau:
- {', '.join(category_names) if category_names else 'Chưa có danh mục'}{bestsellers_text}{category_books_text}
"""
        return context
    except Exception as e:
        # Nếu có lỗi khi query database, trả về context mặc định
        logger.error(f"[CHATBOT] Error in get_bookstore_context: {str(e)}")
        return "\nCửa hàng sách trực tuyến với nhiều danh mục sách đa dạng."

def detect_and_get_book_info(question):
    """
    Detect tên sách từ câu hỏi và query thông tin chi tiết sách
    
    Flow:
    1. Sử dụng Gemini để extract tên sách từ question (nếu có)
    2. Search trong database (fuzzy match với title)
    3. Nếu tìm thấy:
       - Query thông tin chi tiết sách
       - Query sách tương tự (same author, same category, top 3-5)
       - Return book info dict
    4. Nếu không tìm thấy: return None
    
    Parameters:
        question (str): Câu hỏi của người dùng
    
    Returns:
        dict: Thông tin sách và sách tương tự, hoặc None nếu không tìm thấy
    """
    try:
        # Bước 1: Sử dụng Gemini để extract tên sách từ question
        client = get_genai_client()
        if not client:
            logger.warning("[CHATBOT] Cannot detect book - Gemini client not available")
            return None
        
        # Prompt để extract tên sách
        extract_prompt = f"""Bạn là một hệ thống extract thông tin. Nhiệm vụ của bạn là tìm tên sách trong câu hỏi sau đây.

Câu hỏi: "{question}"

Hãy trả lời CHỈ tên sách (nếu có), không thêm gì khác. Nếu không có tên sách cụ thể, trả lời "KHONG".

Ví dụ:
- "Sách Harry Potter có hay không?" -> "Harry Potter"
- "Giới thiệu về Đắc Nhân Tâm" -> "Đắc Nhân Tâm"
- "Sách nào bán chạy nhất?" -> "KHONG"
"""
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=extract_prompt
            )
            
            if response and response.text:
                book_title = response.text.strip()
                # Loại bỏ dấu ngoặc kép nếu có
                book_title = book_title.strip('"').strip("'").strip()
                
                if book_title.upper() == "KHONG" or not book_title:
                    logger.info("[CHATBOT] No book title detected in question")
                    return None
                
                logger.info(f"[CHATBOT] Detected book title: {book_title}")
            else:
                return None
        except Exception as e:
            logger.warning(f"[CHATBOT] Failed to extract book title: {str(e)}")
            return None
        
        # Bước 2: Search trong database (fuzzy match với title)
        # Tìm sách có title chứa book_title
        books = Book.query.filter(
            Book.title.ilike(f'%{book_title}%')
        ).all()
        
        if not books:
            logger.info(f"[CHATBOT] No book found matching: {book_title}")
            return None
        
        # Lấy sách đầu tiên (có thể cải thiện bằng cách tính điểm khớp)
        book = books[0]
        logger.info(f"[CHATBOT] Found book: {book.title} (ID: {book.id})")
        
        # Bước 3: Query thông tin chi tiết sách
        sold_count = book.get_sold_count()
        category = Category.query.filter_by(key=book.category).first()
        category_name = category.name if category else book.category
        
        # Query sách tương tự (same author hoặc same category, top 5, loại trừ sách hiện tại)
        similar_books = []
        try:
            # Sách cùng tác giả
            same_author_books = Book.query.filter(
                Book.author == book.author,
                Book.id != book.id
            ).limit(3).all()
            
            # Sách cùng category (loại trừ sách đã có trong same_author_books)
            same_author_ids = [b.id for b in same_author_books]
            same_category_query = Book.query.filter(
                Book.category == book.category,
                Book.id != book.id
            )
            if same_author_ids:
                same_category_query = same_category_query.filter(~Book.id.in_(same_author_ids))
            same_category_books = same_category_query.limit(2).all()
            
            # Kết hợp và tính sold count
            for similar_book in same_author_books + same_category_books:
                similar_sold = similar_book.get_sold_count()
                similar_books.append({
                    'book': similar_book,
                    'sold': similar_sold
                })
        except Exception as e:
            logger.warning(f"[CHATBOT] Failed to query similar books: {str(e)}")
        
        # Return book info dict
        return {
            'book': book,
            'sold_count': sold_count,
            'category_name': category_name,
            'similar_books': similar_books
        }
        
    except Exception as e:
        logger.error(f"[CHATBOT] Error in detect_and_get_book_info: {str(e)}")
        return None

def format_book_context(book_info):
    """
    Format thông tin sách thành text dễ đọc cho AI
    
    Parameters:
        book_info (dict): Thông tin sách từ detect_and_get_book_info()
    
    Returns:
        str: Formatted text về thông tin sách
    """
    if not book_info:
        return ""
    
    book = book_info['book']
    sold_count = book_info['sold_count']
    category_name = book_info['category_name']
    similar_books = book_info.get('similar_books', [])
    
    # Format thông tin sách chính
    context = f"""
[Thông tin sách cụ thể:]
Sách: {book.title}
- Tác giả: {book.author}
- Mô tả: {book.description if book.description else 'Chưa có mô tả'}
- Nhà xuất bản: {book.publisher if book.publisher else 'Chưa có thông tin'}
- Số trang: {book.pages if book.pages else 'Chưa có thông tin'}
- Giá: {float(book.price):,.0f} VNĐ
- Đã bán: {sold_count} cuốn
- Danh mục: {category_name}
"""
    
    # Format sách tương tự
    if similar_books:
        similar_text = "\nSách tương tự:\n"
        for idx, item in enumerate(similar_books[:5], 1):
            similar_book = item['book']
            similar_sold = item['sold']
            similar_text += f"- {similar_book.title} - {similar_book.author} (Đã bán: {similar_sold})\n"
        context += similar_text
    
    return context

def build_system_prompt(question=None):
    """
    Tạo system prompt cho Gemini với context về bookstore và thông tin sách cụ thể (nếu có)
    
    Flow:
    1. Lấy bookstore context từ database
    2. Nếu có question, detect và lấy thông tin sách cụ thể
    3. Format thông tin sách (nếu có)
    4. Tạo system prompt với instructions cải thiện về đánh giá sách
    5. Trả về system prompt hoàn chỉnh
    
    Parameters:
        question (str, optional): Câu hỏi của người dùng để detect sách
    
    Returns:
        str: System prompt cho Gemini
    """
    # Bước 1: Lấy context từ database
    bookstore_context = get_bookstore_context()
    
    # Bước 2: Detect và lấy thông tin sách cụ thể (nếu có question)
    book_context = ""
    if question:
        book_info = detect_and_get_book_info(question)
        if book_info:
            book_context = format_book_context(book_info)
            logger.info(f"[CHATBOT] Book context added for: {book_info['book'].title}")
    
    # Bước 3-4: Tạo system prompt với instructions cải thiện
    system_prompt = f"""Bạn là trợ lý AI thân thiện của một cửa hàng sách trực tuyến. Nhiệm vụ của bạn là:

1. Trả lời câu hỏi về sách, danh mục, giá cả, tác giả
2. Hướng dẫn khách hàng về cách mua hàng, thanh toán, giao hàng
3. Gợi ý sách theo sở thích hoặc danh mục
4. Giải đáp thắc mắc về chính sách đổi trả, vận chuyển
5. Đánh giá và tư vấn về chất lượng sách dựa trên thông tin có sẵn

Thông tin về cửa hàng:
{bookstore_context}
{book_context}

Khi khách hàng hỏi về chất lượng sách, bạn có thể đánh giá dựa trên:
1. Mô tả sách (description) - phân tích nội dung, thể loại, đối tượng độc giả phù hợp
2. Số lượng đã bán - sách bán chạy thường được nhiều người yêu thích và đánh giá cao
3. Tác giả - tác giả nổi tiếng thường viết sách chất lượng, có thể tham khảo các tác phẩm khác của cùng tác giả
4. Nhà xuất bản - NXB uy tín thường chọn và xuất bản sách hay, chất lượng
5. Số trang - cho biết độ dài và mức độ chi tiết của nội dung
6. So sánh với sách tương tự - để đưa ra đánh giá tương đối và gợi ý lựa chọn

Hãy trả lời một cách khách quan, dựa trên thông tin có sẵn. Nếu có thông tin về sách cụ thể, hãy sử dụng nó để đưa ra đánh giá chi tiết. Gợi ý khách hàng đọc thử description để quyết định phù hợp với sở thích của họ.

Chính sách và dịch vụ:
- Thanh toán: COD (thanh toán khi nhận hàng)
- Giao hàng: Giao hàng toàn quốc, thời gian 3-7 ngày làm việc
- Đổi trả: Có thể đổi trả trong vòng 7 ngày kể từ ngày nhận hàng nếu sách có lỗi
- Đăng ký/Đăng nhập: Khách hàng cần đăng ký tài khoản để mua hàng và quản lý đơn hàng

Hãy trả lời một cách thân thiện, chuyên nghiệp và hữu ích. Nếu không chắc chắn về thông tin, hãy hướng dẫn khách hàng tìm kiếm trên website hoặc liên hệ hỗ trợ."""
    
    return system_prompt

def query_gemini(question, system_prompt):
    """
    Gọi Gemini API để lấy câu trả lời (sử dụng new google-genai library)
    
    Flow:
    1. Lấy Gemini client (lazy initialization)
    2. Gọi generate_content với model gemini-2.5-flash và system instruction
    3. Trả về text response
    
    Parameters:
        question (str): Câu hỏi của người dùng
        system_prompt (str): System prompt với context về bookstore
    
    Returns:
        str: Câu trả lời từ Gemini, hoặc None nếu có lỗi
    """
    try:
        # Bước 1: Lấy Gemini client
        client = get_genai_client()
        if not client:
            logger.warning("[CHATBOT] ❌ Gemini client not available")
            return None
        
        api_key = Config.GEMINI_API_KEY
        logger.info(f"[CHATBOT] ✓ API Key exists: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else '***'}")
        logger.info(f"[CHATBOT] 📤 Calling Gemini API with question: {question[:50]}...")
        
        # Bước 2: Gọi API với new library structure
        # Sử dụng gemini-2.5-flash (latest model, nhanh, phù hợp cho chatbot)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=question,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt
            )
        )
        
        # Bước 3: Trả về text response
        if response and response.text:
            answer_text = response.text
            logger.info(f"[CHATBOT] ✅ Gemini response received: {answer_text[:100]}...")
            return answer_text
        else:
            logger.warning("[CHATBOT] ⚠️ Gemini response is empty")
            return None
        
    except errors.APIError as e:
        # Log API error chi tiết
        logger.error(f"[CHATBOT] ❌ Gemini API Error: {e.code} - {e.message}")
        import traceback
        logger.error(f"[CHATBOT] Traceback: {traceback.format_exc()}")
        return None
    except Exception as e:
        # Log generic error chi tiết
        logger.error(f"[CHATBOT] ❌ Error querying Gemini: {str(e)}")
        logger.error(f"[CHATBOT] Error type: {type(e).__name__}")
        import traceback
        logger.error(f"[CHATBOT] Traceback: {traceback.format_exc()}")
        return None

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    """
    Xử lý câu hỏi từ chatbot và trả về câu trả lời (luôn gọi Gemini API trước)
    
    Flow:
    1. Lấy question từ request body
    2. Validate question không rỗng
    3. Kiểm tra GEMINI_API_KEY có tồn tại không
    4. Nếu có API key:
       - Lấy bookstore context từ database
       - Build system prompt với context
       - Gọi Gemini API với system prompt + user question
       - Nếu thành công: trả về response từ Gemini
       - Nếu fail: fallback về FAQ
    5. Nếu không có API key: dùng FAQ matching
    6. Trả về câu trả lời
    
    Request Body:
        {
            "question": "Câu hỏi của người dùng"
        }
    
    Returns:
        - 200: Câu trả lời từ Gemini hoặc FAQ
        - 400: Thiếu question
        - 500: Lỗi server
    """
    try:
        # Bước 1: Lấy question từ request
        data = request.get_json()
        question = data.get('question', '').strip()
        
        logger.info("=" * 50)
        logger.info(f"[CHATBOT] 📨 Received question: {question}")
        
        # Bước 2: Validate question
        if not question:
            return jsonify({'error': 'Vui lòng nhập câu hỏi'}), 400
        
        # Bước 3: Kiểm tra API key
        api_key = Config.GEMINI_API_KEY
        logger.info(f"[CHATBOT] 🔍 Checking API key... (exists: {api_key is not None})")
        if api_key:
            logger.info(f"[CHATBOT] 🔑 API Key found: {api_key[:10]}...{api_key[-5:] if len(api_key) > 15 else '***'}")
        else:
            logger.warning("[CHATBOT] ⚠️ API Key is None or empty")
        
        answer = None
        source = None
        
        if api_key:
            # Bước 4: Có API key - luôn gọi Gemini trước
            logger.info("[CHATBOT] 🔑 API Key found, calling Gemini...")
            
            # Build system prompt với context về bookstore và thông tin sách (nếu có)
            system_prompt = build_system_prompt(question=question)
            logger.info(f"[CHATBOT] 📝 System prompt built (length: {len(system_prompt)} chars)")
            
            # Gọi Gemini API
            gemini_answer = query_gemini(question, system_prompt)
            
            if gemini_answer:
                answer = gemini_answer
                source = 'gemini'
                logger.info("[CHATBOT] ✅ Using Gemini response")
            else:
                # Fallback về FAQ nếu Gemini fail
                logger.warning("[CHATBOT] ⚠️ Gemini failed, falling back to FAQ")
                question_lower = question.lower()
                for keyword, response in FAQ_DATABASE.items():
                    if keyword != 'mặc định' and keyword in question_lower:
                        answer = response
                        source = 'faq'
                        break
                
                if not answer:
                    answer = FAQ_DATABASE.get('mặc định')
                    source = 'faq_default'
        else:
            # Bước 5: Không có API key - dùng FAQ
            logger.warning("[CHATBOT] ⚠️ No API Key, using FAQ matching")
            question_lower = question.lower()
            for keyword, response in FAQ_DATABASE.items():
                if keyword != 'mặc định' and keyword in question_lower:
                    answer = response
                    source = 'faq'
                    break
            
            if not answer:
                answer = FAQ_DATABASE.get('mặc định')
                source = 'faq_default'
        
        logger.info(f"[CHATBOT] 📤 Response source: {source}")
        logger.info("=" * 50)
        
        # Bước 6: Trả về câu trả lời
        return jsonify({
            'answer': answer,
            'source': source  # Thêm source để debug
        }), 200
        
    except Exception as e:
        # Log error và fallback
        logger.error(f"[CHATBOT] ❌ Exception in chatbot route: {str(e)}")
        import traceback
        logger.error(f"[CHATBOT] Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'answer': FAQ_DATABASE.get('mặc định', 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.'),
            'source': 'error'
        }), 200

