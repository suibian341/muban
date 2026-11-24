import os
import uuid
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from models import User

upload_bp = Blueprint('upload', __name__, url_prefix='/api/upload')

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'mp4', 'mov', 'pdf'}


def allowed(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@upload_bp.route('', methods=['POST'])
@jwt_required()
def upload_file():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or user.role not in ('factory', 'admin', 'dev'):
        return jsonify({'error': 'Unauthorized'}), 403
    return _save_file()


@upload_bp.route('/public', methods=['POST'])
def upload_public():
    """Public upload for registration (certification files)"""
    return _save_file()


def _save_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400

    f = request.files['file']
    if f.filename == '' or not allowed(f.filename):
        return jsonify({'error': 'Invalid file'}), 400

    ext = f.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    f.save(os.path.join(upload_dir, filename))

    url = f"/uploads/{filename}"
    return jsonify({'url': url, 'filename': filename})
