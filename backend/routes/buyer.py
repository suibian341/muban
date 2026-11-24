from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Inquiry, Message

buyer_bp = Blueprint('buyer', __name__, url_prefix='/api/buyer')


def _require_buyer():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role != 'buyer':
        return None, uid
    return user, uid


# ─────────────────────────────────────────
# 买家询盘列表
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries', methods=['GET'])
@jwt_required()
def my_inquiries():
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    q = Inquiry.query.filter_by(user_id=uid).order_by(Inquiry.created_at.desc())
    status = request.args.get('status')
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
# 获取某询盘的消息
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries/<int:iid>/messages', methods=['GET'])
@jwt_required()
def get_messages(iid):
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    inq = Inquiry.query.get_or_404(iid)
    if inq.user_id != uid:
        return jsonify({'error': 'Forbidden'}), 403

    msgs = Message.query.filter_by(inquiry_id=iid).order_by(Message.created_at.asc()).all()
    return jsonify([m.to_dict() for m in msgs])


# ─────────────────────────────────────────
# 买家发送消息
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries/<int:iid>/messages', methods=['POST'])
@jwt_required()
def send_message(iid):
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    inq = Inquiry.query.get_or_404(iid)
    if inq.user_id != uid:
        return jsonify({'error': 'Forbidden'}), 403
    if inq.status in ('closed', 'quoted'):
        return jsonify({'error': 'Inquiry is closed'}), 403

    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'error': 'Content is required'}), 400

    msg = Message(inquiry_id=iid, sender_id=uid, content=content)
    db.session.add(msg)
    db.session.commit()

    # Trigger Coze auto-reply in background
    from coze_reply import trigger_auto_reply
    trigger_auto_reply(current_app._get_current_object(), iid, content)

    return jsonify(msg.to_dict()), 201


# ─────────────────────────────────────────
# 买家接受报价
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries/<int:iid>/accept-quote', methods=['POST'])
@jwt_required()
def accept_quote(iid):
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403
    inq = Inquiry.query.get_or_404(iid)
    if inq.user_id != uid:
        return jsonify({'error': 'Forbidden'}), 403
    if inq.status in ('closed', 'quoted'):
        return jsonify({'error': 'Inquiry is already closed'}), 400

    quote = Message.query.filter_by(inquiry_id=iid, msg_type='quote', quote_status='pending').order_by(Message.created_at.desc()).first()
    if not quote:
        return jsonify({'error': 'No pending quote found'}), 400

    quote.quote_status = 'accepted'
    inq.status = 'quoted'
    sys_msg = Message(inquiry_id=iid, sender_id=uid, content='buyer_accepted', msg_type='system')
    db.session.add(sys_msg)
    db.session.commit()
    return jsonify({'message': 'Quote accepted', 'inquiry': inq.to_dict()})


# ─────────────────────────────────────────
# 买家拒绝报价
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries/<int:iid>/reject-quote', methods=['POST'])
@jwt_required()
def reject_quote(iid):
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403
    inq = Inquiry.query.get_or_404(iid)
    if inq.user_id != uid:
        return jsonify({'error': 'Forbidden'}), 403

    quote = Message.query.filter_by(inquiry_id=iid, msg_type='quote', quote_status='pending').order_by(Message.created_at.desc()).first()
    if not quote:
        return jsonify({'error': 'No pending quote found'}), 400

    quote.quote_status = 'rejected'
    sys_msg = Message(inquiry_id=iid, sender_id=uid, content='buyer_rejected', msg_type='system')
    db.session.add(sys_msg)
    db.session.commit()
    return jsonify({'message': 'Quote rejected', 'inquiry': inq.to_dict()})


# ─────────────────────────────────────────
# 买家关闭询盘
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries/<int:iid>/close', methods=['POST'])
@jwt_required()
def close_inquiry(iid):
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403
    inq = Inquiry.query.get_or_404(iid)
    if inq.user_id != uid:
        return jsonify({'error': 'Forbidden'}), 403
    if inq.status in ('closed', 'quoted'):
        return jsonify({'error': 'Inquiry is already closed'}), 400

    inq.status = 'closed'
    sys_msg = Message(inquiry_id=iid, sender_id=uid, content='buyer_closed', msg_type='system')
    db.session.add(sys_msg)
    db.session.commit()
    return jsonify({'message': 'Inquiry closed', 'inquiry': inq.to_dict()})


# ─────────────────────────────────────────
# 未读消息总数
# ─────────────────────────────────────────
@buyer_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def unread_count():
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    count = Message.query.join(Inquiry).filter(
        Inquiry.user_id == uid,
        Message.sender_id != uid,
        Message.is_read == False
    ).count()
    return jsonify({'count': count})


# ─────────────────────────────────────────
# 标记某询盘消息已读
# ─────────────────────────────────────────
@buyer_bp.route('/inquiries/<int:iid>/messages/read', methods=['POST'])
@jwt_required()
def mark_read(iid):
    user, uid = _require_buyer()
    if not user:
        return jsonify({'error': 'Forbidden'}), 403

    inq = Inquiry.query.get_or_404(iid)
    if inq.user_id != uid:
        return jsonify({'error': 'Forbidden'}), 403

    Message.query.filter(
        Message.inquiry_id == iid,
        Message.sender_id != uid,
        Message.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    return jsonify({'ok': True})
