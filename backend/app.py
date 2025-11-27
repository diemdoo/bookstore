"""
Flask app chính cho Bookstore API
"""
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from config import Config
from models import db
from routes.auth import auth_bp
from routes.books import books_bp
from routes.cart import cart_bp
from routes.orders import orders_bp
from routes.admin import admin_bp
from routes.chatbot import chatbot_bp
from routes.upload import upload_bp
from routes.banners import banners_bp
from routes.categories import categories_bp

def create_app():
    """Tạo và cấu hình Flask app"""
    # Trong Docker, frontend được mount vào /app/static
    # Ở local, có thể dùng ../frontend
    import os
    static_path = 'static' if os.path.exists('static') else '../frontend'
    app = Flask(__name__, static_folder=static_path, static_url_path='')
    app.config.from_object(Config)
    
    # CORS để frontend có thể gọi API
    CORS(app, 
         origins=["http://localhost:5173", "http://localhost", "http://localhost:80"],
         supports_credentials=True,
         allow_headers=["Content-Type"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    
    # Khởi tạo database
    db.init_app(app)
    
    # Đăng ký blueprints (phải đăng ký trước catch-all routes)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(books_bp, url_prefix='/api')
    app.register_blueprint(cart_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    app.register_blueprint(chatbot_bp, url_prefix='/api')
    app.register_blueprint(upload_bp, url_prefix='/api')
    app.register_blueprint(banners_bp, url_prefix='/api')
    app.register_blueprint(categories_bp, url_prefix='/api')
    
    # Route để serve frontend (phải đặt sau API routes)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Bỏ qua API routes
        if path.startswith('api/'):
            return jsonify({'error': 'Not Found'}), 404
        
        # Serve index.html cho root
        if path == '' or path == '/':
            return send_from_directory(app.static_folder, 'index.html')
        
        # Serve các file static khác (HTML, CSS, JS, images)
        import os
        file_path = os.path.join(app.static_folder, path)
        
        # Kiểm tra file có tồn tại không
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return send_from_directory(app.static_folder, path)
        
        # Nếu không tìm thấy file
        # Với HTML files, serve index.html (cho SPA routing)
        if path.endswith(('.html', '.htm')):
            return send_from_directory(app.static_folder, 'index.html')
        
        # Với các file khác (images, etc), trả về 404 ngay lập tức để tránh loop
        return jsonify({'error': 'File not found'}), 404
    
    # Tạo database tables
    with app.app_context():
        db.create_all()
    
    return app

# Create app instance for Gunicorn
app = create_app()

# Seed database data
from seed_data import seed_database
with app.app_context():
    seed_database()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

