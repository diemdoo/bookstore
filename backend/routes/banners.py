from flask import Blueprint, request, jsonify
from models import Banner, db
from utils.helpers import admin_required, generate_banner_code

banners_bp = Blueprint('banners', __name__)

@banners_bp.route('/banners', methods=['GET'])
def get_banners():
    # Bước 1: Lấy query parameter
    position = request.args.get('position', 'all')
    
    # Bước 2: Query banners active
    query = Banner.query.filter_by(is_active=True)
    
    # Bước 3: Lọc theo position nếu cần
    if position != 'all':
        query = query.filter_by(position=position)
    
    # Bước 4: Sắp xếp và lấy kết quả
    banners = query.order_by(Banner.display_order.asc()).all()
    
    # Bước 5: Trả về danh sách
    return jsonify({
        'banners': [banner.to_dict() for banner in banners]
    })

@banners_bp.route('/admin/banners', methods=['GET'])
@admin_required
def get_all_banners():
    # Bước 1: Lấy query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Bước 2-3: Query và sắp xếp
    pagination = Banner.query.order_by(
        Banner.display_order.asc(),
        Banner.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    # Bước 4: Trả về danh sách
    return jsonify({
        'banners': [banner.to_dict() for banner in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })

@banners_bp.route('/admin/banners/<int:banner_id>', methods=['GET'])
@admin_required
def get_banner(banner_id):
    # Bước 1: Query banner
    banner = Banner.query.get_or_404(banner_id)
    
    # Bước 2-3: Trả về thông tin banner
    return jsonify({'banner': banner.to_dict()})

@banners_bp.route('/admin/banners', methods=['POST'])
@admin_required
def create_banner():
    # Bước 1: Lấy dữ liệu từ request
    data = request.get_json()
    
    # Bước 2: Validate các trường bắt buộc
    required_fields = ['title']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Thiếu trường {field}'}), 400
    
    try:
        # Generate banner_code
        banner_code = generate_banner_code(Banner)
        
        # Bước 3: Tạo Banner mới
        banner = Banner(
            banner_code=banner_code,
            title=data['title'],
            description=data.get('description'),
            image_url=data.get('image_url', ''),
            link=data.get('link'),
            bg_color=data.get('bg_color', '#6366f1'),
            text_color=data.get('text_color', '#ffffff'),
            position=data.get('position', 'main'),
            display_order=data.get('display_order', 0),
            is_active=data.get('is_active', True)
        )
        
        # Bước 4: Lưu vào database
        db.session.add(banner)
        db.session.commit()
        
        # Bước 5: Trả về thông tin banner
        return jsonify({
            'message': 'Tạo banner thành công',
            'banner': banner.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@banners_bp.route('/admin/banners/<int:banner_id>', methods=['PUT'])
@admin_required
def update_banner(banner_id):
    # Bước 1-2: Query và kiểm tra banner
    banner = Banner.query.get_or_404(banner_id)
    data = request.get_json()
    
    try:
        # Bước 3-4: Cập nhật các trường
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
        
        # Bước 5: Lưu vào database
        db.session.commit()
        
        # Bước 6: Trả về thông tin banner
        return jsonify({
            'message': 'Cập nhật banner thành công',
            'banner': banner.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@banners_bp.route('/admin/banners/<int:banner_id>', methods=['DELETE'])
@admin_required
def delete_banner(banner_id):
    # Bước 1-2: Query và kiểm tra banner
    banner = Banner.query.get_or_404(banner_id)
    
    try:
        # Bước 3: Xóa banner
        db.session.delete(banner)
        db.session.commit()
        
        # Bước 4: Trả về thông báo thành công
        return jsonify({'message': 'Xóa banner thành công'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@banners_bp.route('/admin/banners/<int:banner_id>/toggle', methods=['PUT'])
@admin_required
def toggle_banner_status(banner_id):
    # Bước 1-2: Query và kiểm tra banner
    banner = Banner.query.get_or_404(banner_id)
    
    try:
        # Bước 3: Đảo ngược trạng thái
        banner.is_active = not banner.is_active
        
        # Bước 4: Lưu vào database
        db.session.commit()
        
        # Bước 5: Trả về thông tin banner
        return jsonify({
            'message': f'Banner đã {"kích hoạt" if banner.is_active else "vô hiệu hóa"}',
            'banner': banner.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

