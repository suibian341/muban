from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Factory, Inquiry, Product
from sqlalchemy import func

factories_bp = Blueprint('factories', __name__, url_prefix='/api/factories')


@factories_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(user.factory.to_dict())


@factories_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    f = user.factory
    for field in ['company_name', 'contact_person', 'phone', 'email', 'address', 'description']:
        if field in data:
            setattr(f, field, data[field])
    db.session.commit()
    return jsonify(f.to_dict())


@factories_bp.route('/analytics', methods=['GET'])
@jwt_required()
def get_analytics():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403

    factory_id = user.factory.id
    total_views = db.session.query(func.sum(Product.view_count)).filter_by(factory_id=factory_id).scalar() or 0
    total_inquiries = db.session.query(func.count(Inquiry.id)).join(Product).filter(Product.factory_id == factory_id).scalar() or 0

    return jsonify({
        'total_views': total_views,
        'total_inquiries': total_inquiries,
        'avg_response_time': '2h'
    })


@factories_bp.route('/top-products', methods=['GET'])
@jwt_required()
def get_top_products():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403

    factory_id = user.factory.id
    limit = request.args.get('limit', 10, type=int)

    products = db.session.query(
        Product.id,
        Product.title,
        Product.view_count,
        func.count(Inquiry.id).label('inquiry_count')
    ).outerjoin(Inquiry).filter(
        Product.factory_id == factory_id,
        Product.status == 'active'
    ).group_by(Product.id).order_by(Product.view_count.desc()).limit(limit).all()

    return jsonify([{
        'id': p[0],
        'title': p[1],
        'view_count': p[2] or 0,
        'inquiry_count': p[3] or 0
    } for p in products])
