from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from models import db, WishList, Product, Inquiry, Message, User
from datetime import datetime
import json

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/api/wishlist')


def _get_owner():
    """返回 (user_id, session_id)，登录用户优先用 user_id"""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            return int(identity), None
    except Exception:
        pass
    return None, request.headers.get('X-Session-ID', request.remote_addr)


def _query_items(user_id, session_id):
    if user_id:
        return WishList.query.filter_by(user_id=user_id)
    return WishList.query.filter_by(session_id=session_id)


def _owns_item(item, user_id, session_id):
    if user_id:
        return item.user_id == user_id
    return item.session_id == session_id


@wishlist_bp.route('', methods=['GET'])
def get_wishlist():
    user_id, session_id = _get_owner()
    items = _query_items(user_id, session_id).all()
    return jsonify([item.to_dict() for item in items])


@wishlist_bp.route('', methods=['POST'])
def add_to_wishlist():
    user_id, session_id = _get_owner()
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({'error': 'product_id required'}), 400

    p = Product.query.get_or_404(product_id)
    if p.status != 'active':
        return jsonify({'error': 'Product not available'}), 400

    if user_id:
        existing = WishList.query.filter_by(user_id=user_id, product_id=product_id).first()
    else:
        existing = WishList.query.filter_by(session_id=session_id, product_id=product_id).first()

    if existing:
        existing.quantity += quantity
    else:
        item = WishList(user_id=user_id, session_id=session_id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return jsonify({'message': 'Added to wishlist'}), 201


@wishlist_bp.route('/<int:item_id>', methods=['DELETE'])
def remove_from_wishlist(item_id):
    user_id, session_id = _get_owner()
    item = WishList.query.get_or_404(item_id)
    if not _owns_item(item, user_id, session_id):
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Removed from wishlist'})


@wishlist_bp.route('/<int:item_id>', methods=['PUT'])
def update_wishlist_item(item_id):
    user_id, session_id = _get_owner()
    item = WishList.query.get_or_404(item_id)
    if not _owns_item(item, user_id, session_id):
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    if 'quantity' in data:
        item.quantity = data['quantity']
    db.session.commit()
    return jsonify(item.to_dict())


@wishlist_bp.route('/clear', methods=['POST'])
def clear_wishlist():
    user_id, session_id = _get_owner()
    _query_items(user_id, session_id).delete()
    db.session.commit()
    return jsonify({'message': 'Wishlist cleared'})


@wishlist_bp.route('/submit', methods=['POST'])
def submit_wishlist():
    user_id, session_id = _get_owner()
    data = request.get_json()
    items = _query_items(user_id, session_id).all()

    if not items:
        return jsonify({'error': 'Wishlist is empty'}), 400

    contact_name = data.get('contact_name', '').strip()
    email = data.get('email', '').strip()
    if not contact_name or not email:
        return jsonify({'error': 'contact_name and email are required'}), 400

    product_ids = [item.product_id for item in items]
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    product_map = {p.id: p for p in products}

    wishlist_products = []
    for item in items:
        p = product_map.get(item.product_id)
        if p:
            imgs = p.get_images()
            wishlist_products.append({
                'product_id': p.id,
                'title': p.title,
                'title_en': p.title_en or '',
                'quantity': item.quantity,
                'image': imgs[0] if imgs else None,
            })

    user_message = data.get('message', '').strip()
    message_data = json.dumps({
        'text': user_message or 'Wishlist inquiry',
        'products': wishlist_products,
    }, ensure_ascii=False)

    first_product_id = items[0].product_id if items else None

    # 来源：优先表单提交 > 用户注册来源 > 空
    user_source = ''
    if user_id:
        user_obj = User.query.get(user_id)
        if user_obj:
            user_source = user_obj.source or ''
    inquiry_source = data.get('source') or user_source or ''

    inquiry = Inquiry(
        product_id=first_product_id,
        user_id=user_id,
        contact_name=contact_name,
        email=email,
        phone=data.get('phone', ''),
        company_name=data.get('company_name', ''),
        message=message_data,
        source=inquiry_source,
        status='new',
        created_at=datetime.utcnow()
    )
    db.session.add(inquiry)
    db.session.flush()

    # Create initial message so admin sees unread notification
    if user_id:
        user_msg_text = data.get('message', '').strip() or 'Wishlist inquiry'
        initial_msg = Message(
            inquiry_id=inquiry.id,
            sender_id=user_id,
            content=user_msg_text,
            msg_type='text',
        )
        db.session.add(initial_msg)

    _query_items(user_id, session_id).delete()
    db.session.commit()

    # Trigger auto-reply
    lang = request.headers.get('X-Lang', 'zh')
    from coze_reply import trigger_inquiry_auto_reply
    trigger_inquiry_auto_reply(current_app._get_current_object(), inquiry.id, lang)

    return jsonify({'message': 'Inquiry submitted', 'inquiry_id': inquiry.id}), 201
