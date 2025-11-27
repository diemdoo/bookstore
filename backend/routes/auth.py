"""
Routes cho authentication (đăng ký, đăng nhập, đăng xuất)
"""
from flask import Blueprint, request, jsonify, session
from business.services.auth_service import AuthService
from utils.helpers import login_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Đăng ký tài khoản mới
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Call business service
        user_dto, error = AuthService.register(username, email, password, full_name)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Đăng ký thành công',
            'user': user_dto.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Lỗi đăng ký: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Đăng nhập
    """
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Call business service
        user_dto, error = AuthService.login(username, password)
        
        if error:
            status_code = 401 if 'không đúng' in error or 'khóa' in error else 400
            return jsonify({'error': error}), status_code
        
        # Create session
        session['user_id'] = user_dto.id
        session['username'] = user_dto.username
        session['user_role'] = user_dto.role
        
        return jsonify({
            'message': 'Đăng nhập thành công',
            'user': user_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi đăng nhập: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Đăng xuất
    """
    session.clear()
    return jsonify({'message': 'Đăng xuất thành công'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Lấy thông tin user hiện tại
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Chưa đăng nhập'}), 401
    
    try:
        # Call business service
        user_dto, error = AuthService.get_current_user(session['user_id'])
        
        if error:
            if 'không tồn tại' in error:
                session.clear()
                return jsonify({'error': error}), 404
            return jsonify({'error': error}), 500
        
        return jsonify({'user': user_dto.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi lấy thông tin user: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """
    Cập nhật profile user (full_name, email)
    """
    if 'user_id' not in session:
        return jsonify({'error': 'Chưa đăng nhập'}), 401
    
    try:
        data = request.get_json()
        user_id = session.get('user_id')
        
        full_name = data.get('full_name', '').strip()
        email = data.get('email', '').strip()
        
        # Call business service
        user_dto, error = AuthService.update_profile(user_id, full_name, email)
        
        if error:
            return jsonify({'error': error}), 400
        
        return jsonify({
            'message': 'Cập nhật thành công',
            'user': user_dto.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Lỗi cập nhật: {str(e)}'}), 500