"""
Routes cho chatbot FAQ
"""
from flask import Blueprint, request, jsonify

chatbot_bp = Blueprint('chatbot', __name__)

# FAQ database đơn giản
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

@chatbot_bp.route('/chatbot', methods=['POST'])
def chatbot():
    """
    Xử lý câu hỏi từ chatbot
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip().lower()
        
        if not question:
            return jsonify({'error': 'Vui lòng nhập câu hỏi'}), 400
        
        # Tìm câu trả lời phù hợp
        answer = FAQ_DATABASE.get('mặc định')
        
        for keyword, response in FAQ_DATABASE.items():
            if keyword in question:
                answer = response
                break
        
        return jsonify({
            'answer': answer
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi xử lý chatbot: {str(e)}'}), 500

