from datetime import datetime
from app import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Tạo index cho slug (như trong SQL bạn đã làm)
    __table_args__ = (
        db.Index('idx_slug', 'slug'),
    )

    def __repr__(self):
        return f"<Category {self.name}>"