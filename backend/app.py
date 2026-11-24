import os
import sys

# 确保从当前目录导入，而不是系统包
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from models import db

from routes.auth import auth_bp
from routes.products import products_bp
from routes.factories import factories_bp
from routes.admin import admin_bp
from routes.inquiries import inquiries_bp
from routes.public import public_bp
from routes.upload import upload_bp
from routes.wishlist import wishlist_bp
from routes.buyer import buyer_bp
from routes.dev import dev_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(factories_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(inquiries_bp)
    app.register_blueprint(public_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(buyer_bp)
    app.register_blueprint(dev_bp)

    @app.route('/uploads/<path:filename>')
    def serve_upload(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5003)
