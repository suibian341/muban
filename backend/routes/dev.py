from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Product, Factory, Inquiry, SiteSettings, Category, Message, WishList
from sqlalchemy import func
import json

dev_bp = Blueprint('dev', __name__, url_prefix='/api/dev')

def _require_dev():
    """验证开发者权限"""
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'dev':
        return None
    return user


@dev_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """获取所有统计数据（三个后台的数据汇总）"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    stats = {
        'users': {
            'total': User.query.count(),
            'admins': User.query.filter_by(role='admin').count(),
            'factories': User.query.filter_by(role='factory').count(),
            'buyers': User.query.filter_by(role='buyer').count(),
            'devs': User.query.filter_by(role='dev').count()
        },
        'factories': {
            'total': Factory.query.count(),
            'pending': Factory.query.filter_by(status='pending').count(),
            'approved': Factory.query.filter_by(status='approved').count(),
            'rejected': Factory.query.filter_by(status='rejected').count(),
            'disabled': Factory.query.filter_by(status='disabled').count()
        },
        'products': {
            'total': Product.query.count(),
            'draft': Product.query.filter_by(status='draft').count(),
            'pending': Product.query.filter_by(status='pending').count(),
            'active': Product.query.filter_by(status='active').count(),
            'rejected': Product.query.filter_by(status='rejected').count()
        },
        'inquiries': {
            'total': Inquiry.query.count(),
            'new': Inquiry.query.filter_by(status='new').count(),
            'replied': Inquiry.query.filter_by(status='replied').count(),
            'closed': Inquiry.query.filter_by(status='closed').count()
        },
        'categories': Category.query.count(),
        'messages': Message.query.count(),
        'wishlist_items': WishList.query.count()
    }
    return jsonify(stats)


@dev_bp.route('/mode', methods=['GET', 'PUT'])
@jwt_required()
def site_mode():
    """获取或设置站点模式（B2C/B2B）"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        setting = SiteSettings.query.filter_by(key='site_mode').first()
        return jsonify({'mode': setting.value if setting else 'b2b'})

    # PUT - 更新模式
    data = request.json
    mode = data.get('mode')
    if mode not in ['b2c', 'b2b']:
        return jsonify({'error': 'Invalid mode. Must be b2c or b2b'}), 400

    setting = SiteSettings.query.filter_by(key='site_mode').first()
    if setting:
        setting.value = mode
    else:
        setting = SiteSettings(key='site_mode', value=mode)
        db.session.add(setting)

    db.session.commit()
    return jsonify({'message': 'Mode updated successfully', 'mode': mode})


@dev_bp.route('/branding', methods=['GET', 'PUT'])
@jwt_required()
def branding():
    """获取或设置品牌配置（Logo、名称、描述）"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        branding_data = {}
        keys = [
            'brand_logo',
            'brand_name_zh', 'brand_name_en', 'brand_name_es', 'brand_name_ar', 'brand_name_ru',
            'brand_desc_zh', 'brand_desc_en', 'brand_desc_es', 'brand_desc_ar', 'brand_desc_ru'
        ]
        for key in keys:
            setting = SiteSettings.query.filter_by(key=key).first()
            branding_data[key] = setting.value if setting else ''
        return jsonify(branding_data)

    # PUT - 更新品牌配置
    data = request.json
    keys = [
        'brand_logo',
        'brand_name_zh', 'brand_name_en', 'brand_name_es', 'brand_name_ar', 'brand_name_ru',
        'brand_desc_zh', 'brand_desc_en', 'brand_desc_es', 'brand_desc_ar', 'brand_desc_ru'
    ]
    for key in keys:
        if key in data:
            setting = SiteSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = data[key]
            else:
                setting = SiteSettings(key=key, value=data[key])
                db.session.add(setting)

    db.session.commit()
    return jsonify({'message': 'Branding updated successfully'})


@dev_bp.route('/footer', methods=['GET', 'PUT'])
@jwt_required()
def footer_config():
    """获取或设置页脚配置（FAQ、物流说明、服务条款、关于我们）"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    if request.method == 'GET':
        footer = {}
        keys = [
            'faq_zh', 'faq_en', 'faq_es', 'faq_ar', 'faq_ru',
            'shipping_zh', 'shipping_en', 'shipping_es', 'shipping_ar', 'shipping_ru',
            'terms_zh', 'terms_en', 'terms_es', 'terms_ar', 'terms_ru',
            'about_zh', 'about_en', 'about_es', 'about_ar', 'about_ru'
        ]
        for key in keys:
            setting = SiteSettings.query.filter_by(key=key).first()
            footer[key] = setting.value if setting else ''
        return jsonify(footer)

    # PUT - 更新页脚
    data = request.json
    keys = [
        'faq_zh', 'faq_en', 'faq_es', 'faq_ar', 'faq_ru',
        'shipping_zh', 'shipping_en', 'shipping_es', 'shipping_ar', 'shipping_ru',
        'terms_zh', 'terms_en', 'terms_es', 'terms_ar', 'terms_ru',
        'about_zh', 'about_en', 'about_es', 'about_ar', 'about_ru'
    ]
    for key in keys:
        if key in data:
            setting = SiteSettings.query.filter_by(key=key).first()
            if setting:
                setting.value = data[key]
            else:
                setting = SiteSettings(key=key, value=data[key])
                db.session.add(setting)

    db.session.commit()
    return jsonify({'message': 'Footer updated successfully'})


@dev_bp.route('/all-users', methods=['GET'])
@jwt_required()
def get_all_users():
    """获取所有用户列表"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    role = request.args.get('role')

    query = User.query
    if role:
        query = query.filter_by(role=role)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    users = [{
        'id': u.id,
        'username': u.username,
        'role': u.role,
        'email': u.email,
        'company_name': u.company_name,
        'country': u.country,
        'phone': u.phone,
        'is_active': u.is_active,
        'created_at': u.created_at.isoformat() if u.created_at else None
    } for u in pagination.items]

    return jsonify({
        'items': users,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@dev_bp.route('/all-factories', methods=['GET'])
@jwt_required()
def get_all_factories():
    """获取所有工厂列表"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')

    query = Factory.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Factory.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    factories = [{
        'id': f.id,
        'user_id': f.user_id,
        'company_name': f.company_name,
        'contact_person': f.contact_person,
        'phone': f.phone,
        'email': f.email,
        'address': f.address,
        'status': f.status,
        'created_at': f.created_at.isoformat() if f.created_at else None
    } for f in pagination.items]

    return jsonify({
        'items': factories,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@dev_bp.route('/all-products', methods=['GET'])
@jwt_required()
def get_all_products():
    """获取所有商品列表"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')

    query = Product.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    products = [{
        'id': p.id,
        'title': p.title,
        'title_en': p.title_en,
        'status': p.status,
        'base_price': float(p.base_price) if p.base_price else None,
        'factory_id': p.factory_id,
        'factory_name': p.factory.company_name if p.factory else None,
        'is_featured': p.is_featured,
        'is_new': p.is_new,
        'is_clearance': p.is_clearance,
        'is_banner': p.is_banner,
        'view_count': p.view_count,
        'created_at': p.created_at.isoformat() if p.created_at else None
    } for p in pagination.items]

    return jsonify({
        'items': products,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })


@dev_bp.route('/all-inquiries', methods=['GET'])
@jwt_required()
def get_all_inquiries():
    """获取所有询盘列表"""
    user = _require_dev()
    if not user:
        return jsonify({'error': 'Unauthorized'}), 403

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')

    query = Inquiry.query
    if status:
        query = query.filter_by(status=status)

    pagination = query.order_by(Inquiry.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    inquiries = [{
        'id': inq.id,
        'product_id': inq.product_id,
        'product_title': inq.product.title if inq.product else None,
        'user_id': inq.user_id,
        'contact_name': inq.contact_name,
        'email': inq.email,
        'message': inq.message,
        'status': inq.status,
        'source': inq.source,
        'created_at': inq.created_at.isoformat() if inq.created_at else None
    } for inq in pagination.items]

    return jsonify({
        'items': inquiries,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    })
