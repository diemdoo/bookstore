from flask import Blueprint, request, jsonify, session
from models import Banner, db
from functools import wraps

banners_bp = Blueprint('banners', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Yêu cầu đăng nhập'}), 401
        
        from models import User
        user = User.query.get(session['user_id'])
        if not user or user.role != 'admin':
            return jsonify({'error': 'Không có quyền truy cập'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

# Public: Get active banners
@banners_bp.route('/banners', methods=['GET'])
def get_banners():
    """Get all active banners for public display"""
    position = request.args.get('position', 'all')
    
    query = Banner.query.filter_by(is_active=True)
    
    if position != 'all':
        query = query.filter_by(position=position)
    
    banners = query.order_by(Banner.display_order.asc()).all()
    
    return jsonify({
        'banners': [banner.to_dict() for banner in banners]
    })

# Admin: Get all banners (including inactive)
@banners_bp.route('/admin/banners', methods=['GET'])
@admin_required
def get_all_banners():
    """Get all banners for admin management"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    pagination = Banner.query.order_by(
        Banner.display_order.asc(),
        Banner.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'banners': [banner.to_dict() for banner in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

# Admin: Get single banner
@banners_bp.route('/admin/banners/<int:banner_id>', methods=['GET'])
@admin_required
def get_banner(banner_id):
    """Get a specific banner"""
    banner = Banner.query.get_or_404(banner_id)
    return jsonify({'banner': banner.to_dict()})

# Admin: Create banner
@banners_bp.route('/admin/banners', methods=['POST'])
@admin_required
def create_banner():
    """Create a new banner"""
    data = request.get_json()
    
    # Validation
    required_fields = ['title', 'image_url']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Thiếu trường {field}'}), 400
    
    try:
        banner = Banner(
            title=data['title'],
            description=data.get('description'),
            image_url=data['image_url'],
            link=data.get('link'),
            bg_color=data.get('bg_color', '#6366f1'),
            text_color=data.get('text_color', '#ffffff'),
            position=data.get('position', 'main'),
            display_order=data.get('display_order', 0),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(banner)
        db.session.commit()
        
        return jsonify({
            'message': 'Tạo banner thành công',
            'banner': banner.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin: Update banner
@banners_bp.route('/admin/banners/<int:banner_id>', methods=['PUT'])
@admin_required
def update_banner(banner_id):
    """Update an existing banner"""
    banner = Banner.query.get_or_404(banner_id)
    data = request.get_json()
    
    try:
        # Update fields
        if 'title' in data:
            banner.title = data['title']
        if 'description' in data:
            banner.description = data['description']
        if 'image_url' in data:
            banner.image_url = data['image_url']
        if 'link' in data:
            banner.link = data['link']
        if 'bg_color' in data:
            banner.bg_color = data['bg_color']
        if 'text_color' in data:
            banner.text_color = data['text_color']
        if 'position' in data:
            banner.position = data['position']
        if 'display_order' in data:
            banner.display_order = data['display_order']
        if 'is_active' in data:
            banner.is_active = data['is_active']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Cập nhật banner thành công',
            'banner': banner.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin: Delete banner
@banners_bp.route('/admin/banners/<int:banner_id>', methods=['DELETE'])
@admin_required
def delete_banner(banner_id):
    """Delete a banner"""
    banner = Banner.query.get_or_404(banner_id)
    
    try:
        db.session.delete(banner)
        db.session.commit()
        
        return jsonify({'message': 'Xóa banner thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Admin: Toggle banner status
@banners_bp.route('/admin/banners/<int:banner_id>/toggle', methods=['PUT'])
@admin_required
def toggle_banner_status(banner_id):
    """Toggle banner active status"""
    banner = Banner.query.get_or_404(banner_id)
    
    try:
        banner.is_active = not banner.is_active
        db.session.commit()
        
        return jsonify({
            'message': f'Banner đã {"kích hoạt" if banner.is_active else "vô hiệu hóa"}',
            'banner': banner.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

