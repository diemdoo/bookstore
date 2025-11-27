"""
Data Transfer Object cho Category
"""

class CategoryDTO:
    """DTO cho Category entity"""
    
    def __init__(self, id=None, key=None, name=None, description=None, 
                 display_order=0, is_active=True, created_at=None, updated_at=None):
        self.id = id
        self.key = key
        self.name = name
        self.description = description
        self.display_order = display_order
        self.is_active = is_active
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        """Chuyển đổi DTO thành dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'name': self.name,
            'description': self.description,
            'display_order': self.display_order,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @staticmethod
    def from_model(category):
        """Tạo DTO từ Category model"""
        if not category:
            return None
        
        return CategoryDTO(
            id=category.id,
            key=category.key,
            name=category.name,
            description=category.description,
            display_order=category.display_order,
            is_active=category.is_active,
            created_at=category.created_at,
            updated_at=category.updated_at
        )

