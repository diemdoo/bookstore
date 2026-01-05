from flask import Blueprint, request, jsonify
from utils.helpers import admin_required
from utils.storage import storage_service

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/admin/upload', methods=['POST'])
@admin_required
def upload_image():
    try:
        # Bước 1: Kiểm tra có file không
        if 'file' not in request.files:
            return jsonify({'error': 'Không có file được upload'}), 400
        
        file = request.files['file']
        
        # Bước 2: Kiểm tra file có tên không
        if file.filename == '':
            return jsonify({'error': 'Không có file được chọn'}), 400
        
        # Bước 3: Validate kích thước file (max 5MB)
        file.seek(0, 2)  # Seek to end để tính kích thước
        file_size = file.tell()
        file.seek(0)  # Reset về đầu file
        
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            return jsonify({'error': 'File quá lớn. Kích thước tối đa: 5MB'}), 400
        
        # Bước 4: Lấy folder từ query parameter
        folder = request.args.get('folder', 'books')
        
        # Bước 5: Upload lên Cloudflare R2
        url = storage_service.upload_file(file, folder=folder)
        
        # Bước 6: Trả về URL
        return jsonify({
            'message': 'Upload thành công',
            'url': url
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Lỗi khi upload: {str(e)}'}), 500

