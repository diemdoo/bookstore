from flask import Flask
from .config import Config
from .extensions import db
from sqlalchemy import text
from .routes.UserRoutes import user_bp
from .model.UserModel import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các extension
    db.init_app(app)
    with app.app_context():
        db.create_all()
        try:
            db.session.execute(text("SELECT 1"))
            print("✅ Database connected successfully!")
        except Exception as e:
            print("❌ Database connection failed:", e)

    # Đăng ký blueprint
    app.register_blueprint(user_bp, url_prefix="/users")

    return app
