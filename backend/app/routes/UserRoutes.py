from flask import Blueprint, jsonify
from app.service.UserService import get_all_user

user_bp = Blueprint('user_bp', __name__)

@user_bp.route('/', methods=['GET'])
def get_users():
    return jsonify({"Xin chao":"Ngoc Diem","message": "List of users"})

@user_bp.route("/all",  methods=['GET'])
def get_all():
    users = get_all_user()
    return jsonify([{"id": u.id, "name": u.full_name , "email": u.email} for u in users])
# trả dữ lieu jsonify