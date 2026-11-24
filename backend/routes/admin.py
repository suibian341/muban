from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Factory, Product, Category, Inquiry, SiteSettings
from sqlalchemy import func
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def _require_admin():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or (user.role != 'admin' and user.role != 'dev'):
        return None
    return user


@admin_bp.route('/factories', methods=['GET'])
@jwt_required()
def list_factories():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    status = request.args.get('status')
    q = Factory.query.order_by(Factory.created_at.desc())
    if status:
        q = q.filter_by(status=status)
    result = []
    for f in q.all():
        d = f.to_dict()
        d['product_count'] = Product.query.filter_by(factory_id=f.id).count()
        d['active_product_count'] = Product.query.filter_by(factory_id=f.id, status='active').count()
        result.append(d)
    return jsonify(result)


@admin_bp.route('/factories/<int:fid>/approve', methods=['POST'])
@jwt_required()
def approve_factory(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    f.status = 'approved'
    db.session.commit()
    return jsonify({'message': 'Factory approved'})


@admin_bp.route('/factories/<int:fid>/reject', methods=['POST'])
@jwt_required()
def reject_factory(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()
    if not reason:
        return jsonify({'error': 'Rejection reason is required'}), 400
    f.status = 'rejected'
    f.description = reason
    db.session.commit()
    return jsonify({'message': 'Factory rejected'})


@admin_bp.route('/factories/<int:fid>/disable', methods=['POST'])
@jwt_required()
def disable_factory(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    f.status = 'disabled'
    data = request.get_json() or {}
    f.description = data.get('reason', 'Account disabled by admin')
    # Bulk offline all active products
    Product.query.filter_by(factory_id=fid, status='active').update({'status': 'draft', 'review_note': 'Factory disabled'})
    db.session.commit()
    return jsonify({'message': 'Factory disabled'})


@admin_bp.route('/factories/<int:fid>/enable', methods=['POST'])
@jwt_required()
def enable_factory(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    user = User.query.get(f.user_id)
    if user:
        user.is_active = True
    f.status = 'approved'
    f.description = ''
    # Re-activate products that were offlined due to disable
    Product.query.filter_by(factory_id=fid, status='draft').filter(Product.review_note == 'Factory disabled').update({'status': 'active', 'review_note': None})
    db.session.commit()
    return jsonify({'message': 'Factory enabled'})


@admin_bp.route('/factories/<int:fid>', methods=['DELETE'])
@jwt_required()
def delete_factory(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    user = User.query.get(f.user_id)
    # Delete all factory products first
    Product.query.filter_by(factory_id=fid).delete()
    db.session.delete(f)
    if user:
        db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'Factory deleted'})


@admin_bp.route('/products', methods=['GET'])
@jwt_required()
def list_products():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    status = request.args.get('status')
    q = Product.query.order_by(Product.created_at.desc())
    if status == 'pending':
        q = q.filter_by(status='pending')
    elif status == 'active':
        q = q.filter_by(status='active')
    elif status == 'rejected':
        q = q.filter_by(status='rejected')
    elif status == 'draft':
        q = q.filter_by(status='draft')
    # else: return all products (no filter)
    return jsonify([p.to_admin_dict() for p in q.all()])


@admin_bp.route('/products/<int:pid>', methods=['GET'])
@jwt_required()
def admin_product_detail(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    return jsonify(p.to_admin_dict())


@admin_bp.route('/products/<int:pid>/approve', methods=['POST'])
@jwt_required()
def approve_product(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    if p.status != 'pending':
        return jsonify({'error': 'Only pending products can be approved'}), 400
    p.status = 'active'
    p.review_note = None
    db.session.commit()
    return jsonify({'message': 'Product approved'})


@admin_bp.route('/products/<int:pid>/reject', methods=['POST'])
@jwt_required()
def reject_product(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    if p.status != 'pending':
        return jsonify({'error': 'Only pending products can be rejected'}), 400
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()
    if not reason:
        return jsonify({'error': 'Rejection reason is required'}), 400
    p.status = 'rejected'
    p.review_note = reason
    db.session.commit()
    return jsonify({'message': 'Product rejected'})


@admin_bp.route('/products/<int:pid>/hide', methods=['POST'])
@jwt_required()
def hide_product(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    if p.status != 'active':
        return jsonify({'error': 'Only active products can be taken offline'}), 400
    data = request.get_json() or {}
    reason = data.get('reason', '').strip()
    if not reason:
        return jsonify({'error': 'Reason is required'}), 400
    p.status = 'draft'
    p.review_note = reason
    db.session.commit()
    return jsonify({'message': 'Product taken offline'})


@admin_bp.route('/products/<int:pid>/feature', methods=['POST'])
@jwt_required()
def toggle_feature(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    p.is_featured = not p.is_featured
    db.session.commit()
    return jsonify({'message': 'ok', 'is_featured': p.is_featured})


@admin_bp.route('/products/<int:pid>/new', methods=['POST'])
@jwt_required()
def toggle_new(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    p.is_new = not p.is_new
    db.session.commit()
    return jsonify({'message': 'ok', 'is_new': p.is_new})


@admin_bp.route('/products/<int:pid>/clearance', methods=['POST'])
@jwt_required()
def toggle_clearance(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    p.is_clearance = not p.is_clearance
    db.session.commit()
    return jsonify({'message': 'ok', 'is_clearance': p.is_clearance})


@admin_bp.route('/products/<int:pid>/banner', methods=['POST'])
@jwt_required()
def toggle_banner(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    p.is_banner = not p.is_banner
    db.session.commit()
    return jsonify({'message': 'ok', 'is_banner': p.is_banner})


@admin_bp.route('/products/<int:pid>', methods=['DELETE'])
@jwt_required()
def admin_delete_product(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@admin_bp.route('/products/<int:pid>', methods=['PUT'])
@jwt_required()
def admin_update_product(pid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    p = Product.query.get_or_404(pid)
    data = request.get_json()
    fields = [
        'title', 'title_en', 'description', 'description_en',
        'video_url', 'moq', 'lead_time', 'base_price', 'price_unit',
        'packaging_info', 'packaging_info_en',
        'customization', 'customization_en', 'category_id',
        'is_clearance', 'clearance_type', 'certification', 'stock_quantity',
        'is_featured', 'is_new', 'status',
    ]
    for field in fields:
        if field in data:
            setattr(p, field, data[field])
    if 'images' in data:
        p.images = json.dumps(data['images'])
    if 'poster_images' in data:
        p.poster_images = json.dumps(data['poster_images'])
    if 'specs' in data:
        p.specs = json.dumps(data['specs'])
    db.session.commit()
    return jsonify({'message': 'Product updated'})


@admin_bp.route('/categories', methods=['GET'])
@jwt_required()
def list_categories():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    cats = Category.query.filter_by(parent_id=None).order_by(Category.sort_order).all()
    return jsonify([c.to_dict() for c in cats])


@admin_bp.route('/categories', methods=['POST'])
@jwt_required()
def create_category():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    cat = Category(
        name=data['name'],
        name_en=data.get('name_en', ''),
        parent_id=data.get('parent_id'),
        icon=data.get('icon', ''),
        sort_order=data.get('sort_order', 0),
    )
    db.session.add(cat)
    db.session.commit()
    return jsonify(cat.to_dict()), 201


@admin_bp.route('/categories/<int:cid>', methods=['PUT'])
@jwt_required()
def update_category(cid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    cat = Category.query.get_or_404(cid)
    data = request.get_json()
    old_active = cat.is_active
    for f in ['name', 'name_en', 'parent_id', 'icon', 'sort_order', 'is_active']:
        if f in data:
            setattr(cat, f, data[f])
    db.session.commit()
    # Sync clearance products when a clearance subcategory is toggled
    if 'is_active' in data and data['is_active'] != old_active:
        _sync_clearance_products(cat, data['is_active'])
    return jsonify(cat.to_dict())


@admin_bp.route('/categories/<int:cid>', methods=['DELETE'])
@jwt_required()
def delete_category(cid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    cat = Category.query.get_or_404(cid)
    # Remove clearance flag from products if deleting a clearance subcategory
    _sync_clearance_products(cat, False, clear_type=True)
    db.session.delete(cat)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


def _sync_clearance_products(cat, enable, clear_type=False):
    """When a clearance category is toggled/deleted, update matching products."""
    clearance_parent = Category.query.filter_by(name_en='Clearance Stock').first()
    if not clearance_parent:
        return

    # If toggling the parent "Clearance Stock" category itself
    if cat.id == clearance_parent.id:
        if enable:
            # Re-enable: find products that still have clearance_type set
            products = Product.query.filter(
                Product.clearance_type != None,
                Product.clearance_type != '',
                Product.is_clearance == False
            ).all()
            for p in products:
                p.is_clearance = True
        else:
            # Disable: turn off is_clearance but keep clearance_type for restore
            products = Product.query.filter_by(is_clearance=True).all()
            for p in products:
                p.is_clearance = False
                if clear_type:
                    p.clearance_type = ''
        db.session.commit()
        return

    # Only act on direct children of Clearance Stock
    if cat.parent_id != clearance_parent.id:
        return
    type_key = (cat.name_en or '').lower().replace(' ', '_')
    if not type_key:
        return
    products = Product.query.filter_by(clearance_type=type_key).all()
    for p in products:
        p.is_clearance = enable
        if clear_type:
            p.clearance_type = ''
    db.session.commit()


@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def stats():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify({
        'total_factories': Factory.query.count(),
        'pending_factories': Factory.query.filter_by(status='pending').count(),
        'total_products': Product.query.count(),
        'active_products': Product.query.filter_by(status='active').count(),
        'pending_products': Product.query.filter_by(status='pending').count(),
        'draft_products': Product.query.filter_by(status='draft').count(),
        'rejected_products': Product.query.filter_by(status='rejected').count(),
    })


@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def dashboard():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403

    total_inquiries = Inquiry.query.count()
    new_inquiries = Inquiry.query.filter_by(status='new').count()

    active_products = Product.query.filter_by(status='active').count()
    clearance_products = Product.query.filter_by(status='active', is_clearance=True).count()

    factory_stats = db.session.query(
        Factory.id,
        Factory.company_name,
        func.count(Product.id).label('product_count'),
        func.count(Inquiry.id).label('inquiry_count')
    ).outerjoin(Product).outerjoin(Inquiry).group_by(Factory.id).all()

    return jsonify({
        'total_inquiries': total_inquiries,
        'new_inquiries': new_inquiries,
        'active_products': active_products,
        'clearance_products': clearance_products,
        'factory_stats': [
            {
                'factory_id': f[0],
                'company_name': f[1],
                'product_count': f[2] or 0,
                'inquiry_count': f[3] or 0,
            }
            for f in factory_stats
        ]
    })


@admin_bp.route('/factories/<int:fid>', methods=['GET'])
@jwt_required()
def get_factory_detail(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    data = f.to_dict()
    products = Product.query.filter_by(factory_id=fid)
    data['product_count'] = products.count()
    data['active_product_count'] = products.filter_by(status='active').count()
    # Inquiry count through products
    product_ids = [p.id for p in products.all()]
    if product_ids:
        data['inquiry_count'] = Inquiry.query.filter(Inquiry.product_id.in_(product_ids)).count()
        data['total_views'] = sum(p.view_count or 0 for p in products.all())
    else:
        data['inquiry_count'] = 0
        data['total_views'] = 0
    return jsonify(data)


@admin_bp.route('/factories/<int:fid>', methods=['PUT'])
@jwt_required()
def update_factory(fid):
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    f = Factory.query.get_or_404(fid)
    data = request.get_json()
    for field in ['company_name', 'contact_person', 'email', 'phone', 'address', 'business_scope']:
        if field in data:
            setattr(f, field, data[field])
    db.session.commit()
    return jsonify(f.to_dict())


@admin_bp.route('/products/batch-update', methods=['POST'])
@jwt_required()
def batch_update_products():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json()
    product_ids = data.get('product_ids', [])
    action = data.get('action')

    if action == 'feature':
        Product.query.filter(Product.id.in_(product_ids)).update({'is_featured': True})
    elif action == 'unfeature':
        Product.query.filter(Product.id.in_(product_ids)).update({'is_featured': False})
    elif action == 'clearance':
        Product.query.filter(Product.id.in_(product_ids)).update({'is_clearance': True})
    elif action == 'unclearance':
        Product.query.filter(Product.id.in_(product_ids)).update({'is_clearance': False})
    elif action == 'delete':
        Product.query.filter(Product.id.in_(product_ids)).delete()

    db.session.commit()
    return jsonify({'message': f'Updated {len(product_ids)} products'})


@admin_bp.route('/analytics', methods=['GET'])
@jwt_required()
def analytics():
    if not _require_admin():
        return jsonify({'error': 'Forbidden'}), 403

    days = request.args.get('days', 30, type=int)
    from datetime import datetime, timedelta
    start_date = datetime.utcnow() - timedelta(days=days)

    inquiries_by_date = db.session.query(
        func.date(Inquiry.created_at).label('date'),
        func.count(Inquiry.id).label('count')
    ).filter(Inquiry.created_at >= start_date).group_by(func.date(Inquiry.created_at)).all()

    inquiries_by_status = db.session.query(
        Inquiry.status,
        func.count(Inquiry.id).label('count')
    ).group_by(Inquiry.status).all()

    products_by_category = db.session.query(
        Category.name,
        func.count(Product.id).label('count')
    ).outerjoin(Product).group_by(Category.id).all()

    return jsonify({
        'inquiries_by_date': [{'date': str(d[0]), 'count': d[1]} for d in inquiries_by_date],
        'inquiries_by_status': [{'status': d[0], 'count': d[1]} for d in inquiries_by_status],
        'products_by_category': [{'category': d[0], 'count': d[1]} for d in products_by_category],
    })


@admin_bp.route('/site-settings', methods=['PUT'])
@jwt_required()
def update_site_settings():
    admin = _require_admin()
    if not admin:
        return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json() or {}
    for key, value in data.items():
        row = SiteSettings.query.get(key)
        if row:
            row.value = value
        else:
            db.session.add(SiteSettings(key=key, value=value))
    db.session.commit()
    return jsonify({'ok': True})
