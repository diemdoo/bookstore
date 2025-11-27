"""
Data Access Object cho Category
Xử lý các operations CRUD với database
"""
from models import db, Category

class CategoryDAO:
    """DAO cho Category model"""
    
    @staticmethod
    def get_all(active_only=True):
        """
        Lấy tất cả categories
        
        Args:
            active_only: Chỉ lấy categories đang active (default: True)
            
        Returns:
            List[Category]: Danh sách categories
        """
        query = Category.query
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(Category.display_order.asc(), Category.id.asc()).all()
    
    @staticmethod
    def get_by_id(category_id):
        """
        Lấy category theo ID
        
        Args:
            category_id: ID của category
            
        Returns:
            Category hoặc None
        """
        return Category.query.get(category_id)
    
    @staticmethod
    def get_by_key(key):
        """
        Lấy category theo key
        
        Args:
            key: Key của category (e.g., 'Sach_Tieng_Viet')
            
        Returns:
            Category hoặc None
        """
        return Category.query.filter_by(key=key).first()
    
    @staticmethod
    def create(data):
        """
        Tạo category mới
        
        Args:
            data: Dictionary chứa thông tin category
            
        Returns:
            Category: Category vừa tạo
        """
        category = Category(**data)
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def update(category_id, data):
        """
        Cập nhật category
        
        Args:
            category_id: ID của category
            data: Dictionary chứa thông tin cần update
            
        Returns:
            Category hoặc None nếu không tìm thấy
        """
        category = Category.query.get(category_id)
        if not category:
            return None
        
        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)
        
        db.session.commit()
        return category
    
    @staticmethod
    def delete(category_id):
        """
        Xóa category
        
        Args:
            category_id: ID của category
            
        Returns:
            Boolean: True nếu xóa thành công
        """
        category = Category.query.get(category_id)
        if not category:
            return False
        
        db.session.delete(category)
        db.session.commit()
        return True
    
    @staticmethod
    def key_exists(key, exclude_id=None):
        """
        Kiểm tra xem key đã tồn tại chưa
        
        Args:
            key: Key cần kiểm tra
            exclude_id: ID của category cần loại trừ (dùng khi update)
            
        Returns:
            Boolean
        """
        query = Category.query.filter_by(key=key)
        if exclude_id:
            query = query.filter(Category.id != exclude_id)
        return query.first() is not None

