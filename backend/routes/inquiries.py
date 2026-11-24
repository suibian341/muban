from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from models import db, Inquiry, User, Message

inquiries_bp = Blueprint('inquiries', __name__, url_prefix='/api/inquiries')


# ─────────────────────────────────────────
# 公开提交询盘
# ─────────────────────────────────────────
@inquiries_bp.route('', methods=['POST'])
def submit_inquiry():
    data = request.get_json()
    if not data.get('contact_name') or not data.get('email') or not data.get('message'):
        return jsonify({'error': 'Name, email, and message are required'}), 400

    # 如果用户已登录，自动关联 user_id 并获取用户来源
    user_id = None
    user_source = None
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = int(identity)
            user = User.query.get(user_id)
            if user:
                user_source = user.source
    except Exception:
        pass

    # 优先使用表单提交的来源，如果没有则使用用户注册来源
    inquiry_source = data.get('source') or user_source or ''

    inq = Inquiry(
        product_id=data.get('product_id'),
        user_id=user_id,
        company_name=data.get('company_name', ''),
        contact_name=data['contact_name'],
        email=data['email'],
        phone=data.get('phone', ''),
        quantity=data.get('quantity'),
        message=data['message'],
        source=inquiry_source,
        status='new',
    )
    db.session.add(inq)
    db.session.flush()  # get inq.id

    # Create initial message in Message table so admin sees it as unread
    if user_id:
        initial_msg = Message(
            inquiry_id=inq.id,
            sender_id=user_id,
            content=data['message'],
            msg_type='text',
        )
        db.session.add(initial_msg)

    db.session.commit()

    # Trigger auto-reply with full inquiry context
    lang = request.headers.get('X-Lang', 'zh')
    from coze_reply import trigger_inquiry_auto_reply
    trigger_inquiry_auto_reply(current_app._get_current_object(), inq.id, lang)

    return jsonify({'message': 'Inquiry submitted successfully', 'id': inq.id}), 201


# ─────────────────────────────────────────
# 平台后台：查看所有询盘
# ─────────────────────────────────────────
@inquiries_bp.route('/admin', methods=['GET'])
@jwt_required()
def admin_list():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    status = request.args.get('status')
    q = Inquiry.query.order_by(Inquiry.created_at.desc())
    if status:
        q = q.filter_by(status=status)

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    paginated = q.paginate(page=page, per_page=per_page, error_out=False)

    items = []
    for inq in paginated.items:
        d = inq.to_dict()
        d['unread_count'] = Message.query.filter(
            Message.inquiry_id == inq.id,
            Message.sender_id != uid,
            Message.is_read == False
        ).count()
        items.append(d)

    return jsonify({
        'items': items,
        'total': paginated.total,
        'pages': paginated.pages,
    })


# ─────────────────────────────────────────
# 平台后台：回复 / 更新询盘状态
# ─────────────────────────────────────────
@inquiries_bp.route('/admin/<int:iid>', methods=['PUT'])
@jwt_required()
def admin_update(iid):
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    inq = Inquiry.query.get_or_404(iid)
    data = request.get_json()
    if 'admin_reply' in data:
        inq.admin_reply = data['admin_reply']
    db.session.commit()
    return jsonify(inq.to_dict())


def _require_admin():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'admin':
        return None, uid
    return user, uid


# ─────────────────────────────────────────
# 管理员：获取某询盘的消息
# ─────────────────────────────────────────
@inquiries_bp.route('/admin/<int:iid>/messages', methods=['GET'])
@jwt_required()
def admin_get_messages(iid):
    user, uid = _require_admin()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    Inquiry.query.get_or_404(iid)
    msgs = Message.query.filter_by(inquiry_id=iid).order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in msgs])


# ─────────────────────────────────────────
# 管理员：发送消息
# ─────────────────────────────────────────
@inquiries_bp.route('/admin/<int:iid>/messages', methods=['POST'])
@jwt_required()
def admin_send_message(iid):
    user, uid = _require_admin()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    inq = Inquiry.query.get_or_404(iid)
    if inq.status in ('closed', 'quoted'):
        return jsonify({'error': 'Inquiry is closed'}), 403

    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    msg = Message(inquiry_id=iid, sender_id=uid, content=content)
    db.session.add(msg)
    # Auto transition: new → contacted
    if inq.status == 'new':
        inq.status = 'contacted'
    db.session.commit()
    return jsonify(msg.to_dict()), 201


# ─────────────────────────────────────────
# 管理员：发送报价
# ─────────────────────────────────────────
@inquiries_bp.route('/admin/<int:iid>/send-quote', methods=['POST'])
@jwt_required()
def admin_send_quote(iid):
    user, uid = _require_admin()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    inq = Inquiry.query.get_or_404(iid)
    if inq.status in ('closed', 'quoted'):
        return jsonify({'error': 'Inquiry is closed'}), 403

    data = request.get_json()
    price = data.get('price')
    if not price or float(price) <= 0:
        return jsonify({'error': 'Valid price is required'}), 400

    note = data.get('note', '').strip()

    # Auto-reject any previous pending quotes
    Message.query.filter_by(inquiry_id=iid, msg_type='quote', quote_status='pending').update({'quote_status': 'rejected'})

    msg = Message(
        inquiry_id=iid, sender_id=uid,
        content=note or f'${float(price):.2f}',
        msg_type='quote', quote_price=float(price), quote_status='pending'
    )
    db.session.add(msg)
    # Auto transition: new → contacted
    if inq.status == 'new':
        inq.status = 'contacted'
    db.session.commit()
    return jsonify(msg.to_dict()), 201


# ─────────────────────────────────────────
# 管理员：未读消息总数
# ─────────────────────────────────────────
@inquiries_bp.route('/admin/unread-count', methods=['GET'])
@jwt_required()
def admin_unread_count():
    user, uid = _require_admin()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    count = Message.query.join(User, Message.sender_id == User.id).filter(
        User.role == 'buyer',
        Message.is_read == False
    ).count()
    return jsonify({'count': count})


# ─────────────────────────────────────────
# 管理员：标记某询盘消息已读
# ─────────────────────────────────────────
@inquiries_bp.route('/admin/<int:iid>/messages/read', methods=['POST'])
@jwt_required()
def admin_mark_read(iid):
    user, uid = _require_admin()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    Message.query.filter(
        Message.inquiry_id == iid,
        Message.sender_id != uid,
        Message.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'ok': True})
