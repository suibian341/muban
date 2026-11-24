from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Product, User, Factory, Category
from sqlalchemy import cast, Integer
import json

products_bp = Blueprint('products', __name__, url_prefix='/api/products')


@products_bp.route('', methods=['GET'])
def list_products():
    q = Product.query.filter_by(status='active')
    cat = request.args.get('category_id', type=int)
    if cat:
        cat_obj = Category.query.get(cat)
        if cat_obj:
            cat_ids = [cat_obj.id]
            for child in cat_obj.children:
                cat_ids.append(child.id)
            q = q.filter(Product.category_id.in_(cat_ids))
    moq_max = request.args.get('moq_max', type=int)
    if moq_max:
        q = q.filter(Product.moq <= moq_max)
    keyword = request.args.get('q', '').strip()
    if keyword:
        like = f'%{keyword}%'
        q = q.filter(db.or_(Product.title.ilike(like), Product.title_en.ilike(like)))
    lead_time_max = request.args.get('lead_time_max', type=int)
    if lead_time_max:
        # lead_time 存储格式如 "15天"，CAST 提取前导数字做数值比较
        q = q.filter(cast(Product.lead_time, Integer) <= lead_time_max)
        q = q.filter(Product.lead_time.isnot(None), Product.lead_time != '')
    certification = request.args.get('certification')
    if certification:
        q = q.filter(Product.certification.ilike(f'%{certification}%'))
    is_clearance = request.args.get('is_clearance', '').lower()
    if is_clearance in ('true', '1', 'yes'):
        q = q.filter(Product.is_clearance == True)
    is_featured = request.args.get('is_featured', '').lower()
    if is_featured in ('true', '1', 'yes'):
        q = q.filter(Product.is_featured == True)
    is_new = request.args.get('is_new', '').lower()
    if is_new in ('true', '1', 'yes'):
        q = q.filter(Product.is_new == True)
    sort = request.args.get('sort', 'newest')
    if sort == 'newest':
        q = q.order_by(Product.created_at.desc())
    elif sort == 'featured':
        q = q.order_by(Product.is_featured.desc(), Product.created_at.desc())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        'items': [p.to_public_dict() for p in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
    })


@products_bp.route('/<int:pid>', methods=['GET'])
def product_detail(pid):
    p = Product.query.get_or_404(pid)
    if p.status != 'active':
        return jsonify({'error': 'Product not available'}), 404
    # Increment view count
    p.view_count = (p.view_count or 0) + 1
    db.session.commit()
    d = p.to_public_dict()
    d['view_count'] = p.view_count
    return jsonify(d)


@products_bp.route('/factory/my', methods=['GET'])
@jwt_required()
def my_products():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    q = user.factory.products.order_by(Product.created_at.desc())
    status = request.args.get('status')
    if status:
        q = q.filter_by(status=status)
    return jsonify([p.to_factory_dict() for p in q.all()])


@products_bp.route('/factory/<int:pid>', methods=['GET'])
@jwt_required()
def get_factory_product(pid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)

    # Allow admin and dev to view any product
    if user.role == 'admin' or user.role == 'dev':
        p = Product.query.get_or_404(pid)
        return jsonify(p.to_factory_dict())

    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    p = Product.query.get_or_404(pid)
    if p.factory_id != user.factory.id:
        return jsonify({'error': 'Forbidden'}), 403
    return jsonify(p.to_factory_dict())


@products_bp.route('/factory', methods=['POST'])
@jwt_required()
def create_product():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)

    # Allow admin and dev to create products directly (B2C mode)
    if user.role == 'admin' or user.role == 'dev':
        from models import SiteSettings
        site_mode_setting = SiteSettings.query.filter_by(key='site_mode').first()
        site_mode = site_mode_setting.value if site_mode_setting else 'b2b'

        data = request.get_json()
        p = Product(
            factory_id=None,  # No factory in B2C mode
            title=data['title'],
            title_en=data.get('title_en', ''),
            description=data.get('description', ''),
            description_en=data.get('description_en', ''),
            images=json.dumps(data.get('images', [])),
            poster_images=json.dumps(data.get('poster_images', [])),
            video_url=data.get('video_url', ''),
            moq=data.get('moq', 1),
            lead_time=data.get('lead_time', ''),
            base_price=data.get('base_price'),
            price_unit=data.get('price_unit', 'USD'),
            packaging_info=data.get('packaging_info', ''),
            packaging_info_en=data.get('packaging_info_en', ''),
            customization=data.get('customization', ''),
            customization_en=data.get('customization_en', ''),
            specs=json.dumps(data.get('specs', {})),
            category_id=data.get('category_id'),
            is_clearance=data.get('is_clearance', False),
            clearance_type=data.get('clearance_type', ''),
            certification=data.get('certification', ''),
            stock_quantity=data.get('stock_quantity'),
            status='active' if site_mode == 'b2c' else 'draft',
        )
        db.session.add(p)
        db.session.commit()
        message = 'Product published' if site_mode == 'b2c' else 'Product saved as draft'
        return jsonify({'message': message, 'id': p.id}), 201

    # Factory user
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    if user.factory.status != 'approved':
        return jsonify({'error': 'Factory not approved yet'}), 403
    data = request.get_json()
    p = Product(
        factory_id=user.factory.id,
        title=data['title'],
        title_en=data.get('title_en', ''),
        description=data.get('description', ''),
        description_en=data.get('description_en', ''),
        images=json.dumps(data.get('images', [])),
        poster_images=json.dumps(data.get('poster_images', [])),
        video_url=data.get('video_url', ''),
        moq=data.get('moq', 1),
        lead_time=data.get('lead_time', ''),
        base_price=data.get('base_price'),
        price_unit=data.get('price_unit', 'USD'),
        packaging_info=data.get('packaging_info', ''),
        packaging_info_en=data.get('packaging_info_en', ''),
        customization=data.get('customization', ''),
        customization_en=data.get('customization_en', ''),
        specs=json.dumps(data.get('specs', {})),
        category_id=data.get('category_id'),
        is_clearance=data.get('is_clearance', False),
        clearance_type=data.get('clearance_type', ''),
        certification=data.get('certification', ''),
        stock_quantity=data.get('stock_quantity'),
        status='draft',
    )
    db.session.add(p)
    db.session.commit()
    return jsonify({'message': 'Product saved as draft', 'id': p.id}), 201


@products_bp.route('/factory/<int:pid>', methods=['PUT'])
@jwt_required()
def update_product(pid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)

    # Allow admin and dev to edit any product
    if user.role == 'admin' or user.role == 'dev':
        p = Product.query.get_or_404(pid)
    elif user.role == 'factory' and user.factory:
        p = Product.query.get_or_404(pid)
        if p.factory_id != user.factory.id:
            return jsonify({'error': 'Forbidden'}), 403
        if not p.editable:
            return jsonify({'error': 'Cannot edit product in current status'}), 400
    else:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    fields = [
        'title', 'title_en', 'description', 'description_en',
        'video_url', 'moq', 'lead_time', 'base_price', 'price_unit',
        'packaging_info', 'packaging_info_en',
        'customization', 'customization_en', 'category_id',
        'is_clearance', 'clearance_type', 'certification', 'stock_quantity',
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

    # Only reset to draft for factory users
    if user.role == 'factory':
        p.status = 'draft'
        p.review_note = None

    db.session.commit()
    return jsonify({'message': 'Updated successfully'})


@products_bp.route('/factory/<int:pid>/submit', methods=['POST'])
@jwt_required()
def submit_for_review(pid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    p = Product.query.get_or_404(pid)
    if p.factory_id != user.factory.id:
        return jsonify({'error': 'Forbidden'}), 403
    if p.status != 'draft':
        return jsonify({'error': 'Only draft products can be submitted'}), 400
    if not p.title or p.base_price is None:
        return jsonify({'error': 'Title and base price are required'}), 400
    p.status = 'pending'
    db.session.commit()
    return jsonify({'message': 'Submitted for review'})


@products_bp.route('/factory/<int:pid>/withdraw', methods=['POST'])
@jwt_required()
def withdraw_review(pid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    p = Product.query.get_or_404(pid)
    if p.factory_id != user.factory.id:
        return jsonify({'error': 'Forbidden'}), 403
    if p.status != 'pending':
        return jsonify({'error': 'Only pending products can be withdrawn'}), 400
    p.status = 'draft'
    db.session.commit()
    return jsonify({'message': 'Withdrawn to draft'})


@products_bp.route('/factory/<int:pid>/offline', methods=['POST'])
@jwt_required()
def factory_take_offline(pid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    p = Product.query.get_or_404(pid)
    if p.factory_id != user.factory.id:
        return jsonify({'error': 'Forbidden'}), 403
    if p.status != 'active':
        return jsonify({'error': 'Only active products can be taken offline'}), 400
    p.status = 'draft'
    db.session.commit()
    return jsonify({'message': 'Product taken offline'})


@products_bp.route('/factory/<int:pid>', methods=['DELETE'])
@jwt_required()
def delete_product(pid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    p = Product.query.get_or_404(pid)
    if p.factory_id != user.factory.id:
        return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(p)
    db.session.commit()
    return jsonify({'message': 'Deleted'})


@products_bp.route('/factory/batch-submit', methods=['POST'])
@jwt_required()
def batch_submit():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    product_ids = data.get('product_ids', [])

    products = Product.query.filter(
        Product.id.in_(product_ids),
        Product.factory_id == user.factory.id,
        Product.status == 'draft'
    ).all()

    for p in products:
        if p.title and p.base_price is not None:
            p.status = 'pending'

    db.session.commit()
    return jsonify({'message': f'Submitted {len(products)} products for review'})


@products_bp.route('/factory/batch-delete', methods=['POST'])
@jwt_required()
def batch_delete():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    product_ids = data.get('product_ids', [])

    products = Product.query.filter(
        Product.id.in_(product_ids),
        Product.factory_id == user.factory.id
    ).all()

    for p in products:
        db.session.delete(p)

    db.session.commit()
    return jsonify({'message': f'Deleted {len(products)} products'})


@products_bp.route('/factory/bulk-create', methods=['POST'])
@jwt_required()
def bulk_create():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'factory' or not user.factory:
        return jsonify({'error': 'Unauthorized'}), 403
    if user.factory.status != 'approved':
        return jsonify({'error': 'Factory not approved yet'}), 403

    data = request.get_json()
    products_data = data.get('products', [])
    created = []

    for prod_data in products_data:
        p = Product(
            factory_id=user.factory.id,
            title=prod_data.get('title', ''),
            title_en=prod_data.get('title_en', ''),
            description=prod_data.get('description', ''),
            moq=prod_data.get('moq', 1),
            lead_time=prod_data.get('lead_time', ''),
            base_price=prod_data.get('base_price'),
            category_id=prod_data.get('category_id'),
            is_clearance=prod_data.get('is_clearance', False),
            stock_quantity=prod_data.get('stock_quantity'),
            status='draft'
        )
        db.session.add(p)
        created.append(p)

    db.session.commit()
    return jsonify({'message': f'Created {len(created)} products', 'count': len(created)}), 201
