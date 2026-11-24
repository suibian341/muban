from flask import Blueprint, jsonify, request
from models import Category, Product, SiteSettings

public_bp = Blueprint('public', __name__, url_prefix='/api')


@public_bp.route('/categories', methods=['GET'])
def get_categories():
    # Exclude clearance category — it has its own dedicated page
    clearance = Category.query.filter_by(name_en='Clearance Stock').first()
    exclude_id = clearance.id if clearance else -1
    cats = Category.query.filter(
        Category.is_active == True,
        Category.parent_id == None,
        Category.id != exclude_id
    ).order_by(Category.sort_order).all()
    return jsonify([c.to_dict(include_inactive=False) for c in cats])


@public_bp.route('/clearance-categories', methods=['GET'])
def get_clearance_categories():
    parent = Category.query.filter_by(name_en='Clearance Stock').first()
    if not parent:
        return jsonify({'enabled': False, 'categories': []})
    children = Category.query.filter_by(parent_id=parent.id, is_active=True).order_by(Category.sort_order).all()
    return jsonify({
        'enabled': parent.is_active,
        'categories': [{'id': c.id, 'name': c.name, 'name_en': c.name_en, 'icon': c.icon} for c in children]
    })


@public_bp.route('/featured-products', methods=['GET'])
def featured_products():
    products = Product.query.filter_by(status='active', is_featured=True).order_by(Product.created_at.desc()).limit(12).all()
    return jsonify([p.to_public_dict() for p in products])


@public_bp.route('/new-products', methods=['GET'])
def new_products():
    products = Product.query.filter_by(status='active', is_new=True).order_by(Product.created_at.desc()).limit(12).all()
    return jsonify([p.to_public_dict() for p in products])


@public_bp.route('/clearance-products', methods=['GET'])
def clearance_products():
    # Only show products whose clearance_type matches an active clearance subcategory
    # Products with empty clearance_type are always shown (general clearance)
    clearance_parent = Category.query.filter_by(name_en='Clearance Stock').first()
    allowed_types = []
    if clearance_parent:
        active_children = Category.query.filter_by(parent_id=clearance_parent.id, is_active=True).all()
        allowed_types = [c.name_en.lower().replace(' ', '_') for c in active_children if c.name_en]
    q = Product.query.filter_by(status='active', is_clearance=True)
    if allowed_types:
        from sqlalchemy import or_
        q = q.filter(or_(
            Product.clearance_type.in_(allowed_types),
            Product.clearance_type == '',
            Product.clearance_type == None
        ))
    clearance_type = request.args.get('clearance_type')
    if clearance_type:
        q = q.filter(Product.clearance_type == clearance_type)
    keyword = request.args.get('q', '').strip()
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(Product.title.ilike(like) | Product.title_en.ilike(like))
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    paginated = q.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [p.to_public_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
    })


@public_bp.route('/site-settings', methods=['GET'])
def get_site_settings():
    rows = SiteSettings.query.all()
    return jsonify({r.key: r.value for r in rows})


@public_bp.route('/banner-products', methods=['GET'])
def get_banner_products():
    products = Product.query.filter_by(is_banner=True, status='active').all()
    return jsonify([p.to_public_dict() for p in products if p.images])

