from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Factory
import json

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


def _user_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'role': user.role,
        'email': user.email,
        'company_name': user.company_name,
        'country': user.country,
        'phone': user.phone,
        'source': user.source,
    }


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if not user:
        return jsonify({'error': 'User not found', 'error_type': 'user_not_found'}), 401
    if not check_password_hash(user.password_hash, data.get('password', '')):
        return jsonify({'error': 'Incorrect password', 'error_type': 'wrong_password'}), 401
    if not user.is_active:
        if user.role == 'factory' and user.factory:
            status = user.factory.status
            reason = user.factory.description or ''
            if status == 'disabled':
                return jsonify({'error': 'Account disabled', 'reason': reason, 'factory_status': 'disabled'}), 403
            if status == 'rejected':
                return jsonify({'error': 'Account rejected', 'reason': reason, 'factory_status': 'rejected'}), 403
        return jsonify({'error': 'Account disabled'}), 403

    # Factory status checks (account active but factory not approved)
    if user.role == 'factory' and user.factory:
        fstatus = user.factory.status
        if fstatus == 'pending':
            return jsonify({'error': 'Pending review', 'factory_status': 'pending'}), 403
        if fstatus == 'rejected':
            return jsonify({'error': 'Factory rejected', 'reason': user.factory.description or '', 'factory_status': 'rejected'}), 403
        # Disabled factories CAN log in but will see a notice in their dashboard

    token = create_access_token(identity=str(user.id))
    resp = {
        'token': token,
        'user': _user_dict(user)
    }
    if user.role == 'factory' and user.factory:
        resp['factory'] = user.factory.to_dict()
    return jsonify(resp)


@auth_bp.route('/register', methods=['POST'])
def register():
    """工厂注册（入驻）"""
    data = request.get_json()

    # 检查用户名
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists', 'error_type': 'username_exists'}), 400
    # 检查邮箱
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered', 'error_type': 'email_exists'}), 400

    # 创建用户
    user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='factory',
        email=data.get('email', ''),
        country=data.get('country', ''),
        phone=data.get('phone', ''),
        source=data.get('source', ''),
        is_active=True,
    )
    db.session.add(user)
    db.session.flush()  # 获取 user.id

    # 创建工厂
    factory = Factory(
        user_id=user.id,
        company_name=data.get('company_name', ''),
        contact_person=data.get('contact_person', ''),
        phone=data.get('phone', ''),
        email=data.get('email', ''),
        address=data.get('address', ''),
        description=data.get('description', ''),
        certification_files=json.dumps(data.get('certification_files', [])),
        status='pending',
    )
    db.session.add(factory)
    db.session.commit()

    return jsonify({
        'message': 'Registration submitted, awaiting platform approval',
        'user_id': user.id,
    }), 201


@auth_bp.route('/register/buyer', methods=['POST'])
def register_buyer():
    """买家注册"""
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required', 'error_type': 'missing_fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists', 'error_type': 'username_exists'}), 400
    if data.get('email') and User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered', 'error_type': 'email_exists'}), 400

    user = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='buyer',
        email=data.get('email', ''),
        company_name=data.get('company_name', ''),
        country=data.get('country', ''),
        phone=data.get('phone', ''),
        source=data.get('source', ''),
        is_active=True,
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registration successful', 'user_id': user.id}), 201


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    resp = _user_dict(user)
    if user.role == 'factory' and user.factory:
        resp['factory'] = user.factory.to_dict()
    return jsonify(resp)
