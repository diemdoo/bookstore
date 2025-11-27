"""
Business logic cho Category management
"""
from data.category_dao import CategoryDAO
from business.dto.category_dto import CategoryDTO

class CategoryService:
    """Service layer cho Category"""
    
    @staticmethod
    def get_all_categories(active_only=True):
        """
        Lấy tất cả categories
        
        Args:
            active_only: Chỉ lấy categories active (default: True)
            
        Returns:
            List[CategoryDTO]: Danh sách category DTOs
        """
        categories = CategoryDAO.get_all(active_only=active_only)
        return [CategoryDTO.from_model(cat) for cat in categories]
    
    @staticmethod
    def get_category(category_id):
        """
        Lấy category theo ID
        
        Args:
            category_id: ID của category
            
        Returns:
            Tuple[CategoryDTO | None, str | None]: (CategoryDTO, error_message)
        """
        category = CategoryDAO.get_by_id(category_id)
        if not category:
            return None, 'Category không tồn tại'
        
        return CategoryDTO.from_model(category), None
    
    @staticmethod
    def get_category_by_key(category_key):
        """
        Lấy category theo key
        
        Args:
            category_key: Key của category (e.g., 'Do Trang Tri')
            
        Returns:
            Tuple[CategoryDTO | None, str | None]: (CategoryDTO, error_message)
        """
        category = CategoryDAO.get_by_key(category_key)
        if not category:
            return None, 'Category không tồn tại'
        
        return CategoryDTO.from_model(category), None
    
    @staticmethod
    def create_category(data):
        """
        Tạo category mới
        
        Args:
            data: Dictionary chứa thông tin category
            
        Returns:
            Tuple[CategoryDTO | None, str | None]: (CategoryDTO, error_message)
        """
        # Validate required fields
        if not data.get('key'):
            return None, 'Key là bắt buộc'
        if not data.get('name'):
            return None, 'Name là bắt buộc'
        
        # Check if key already exists
        if CategoryDAO.key_exists(data['key']):
            return None, f"Key '{data['key']}' đã tồn tại"
        
        try:
            category = CategoryDAO.create(data)
            return CategoryDTO.from_model(category), None
        except Exception as e:
            return None, f'Lỗi tạo category: {str(e)}'
    
    @staticmethod
    def update_category(category_id, data):
        """
        Cập nhật category
        
        Args:
            category_id: ID của category
            data: Dictionary chứa thông tin cần update
            
        Returns:
            Tuple[CategoryDTO | None, str | None]: (CategoryDTO, error_message)
        """
        category = CategoryDAO.get_by_id(category_id)
        if not category:
            return None, 'Category không tồn tại'
        
        # If updating key, check for duplicates
        if 'key' in data and data['key'] != category.key:
            if CategoryDAO.key_exists(data['key'], exclude_id=category_id):
                return None, f"Key '{data['key']}' đã tồn tại"
        
        try:
            updated_category = CategoryDAO.update(category_id, data)
            return CategoryDTO.from_model(updated_category), None
        except Exception as e:
            return None, f'Lỗi cập nhật category: {str(e)}'
    
    @staticmethod
    def delete_category(category_id):
        """
        Xóa category
        
        Args:
            category_id: ID của category
            
        Returns:
            Tuple[bool, str | None]: (success, error_message)
        """
        category = CategoryDAO.get_by_id(category_id)
        if not category:
            return False, 'Category không tồn tại'
        
        # TODO: Check if category is being used by any books
        # from data.book_dao import BookDAO
        # if BookDAO.exists_with_category(category.key):
        #     return False, 'Không thể xóa category đang được sử dụng bởi sách'
        
        try:
            CategoryDAO.delete(category_id)
            return True, None
        except Exception as e:
            return False, f'Lỗi xóa category: {str(e)}'

