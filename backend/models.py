from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.Enum('admin', 'factory', 'buyer', 'dev'), nullable=False, default='factory')
    email = db.Column(db.String(120))
    company_name = db.Column(db.String(200))
    country = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    source = db.Column(db.String(50))  # TikTok/Facebook/Google/Other
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    factory = db.relationship('Factory', backref='user', uselist=False)


class Factory(db.Model):
    __tablename__ = 'factories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    address = db.Column(db.String(300))
    description = db.Column(db.Text)
    certification_files = db.Column(db.Text)  # JSON array of file URLs
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    products = db.relationship('Product', backref='factory', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'contact_person': self.contact_person,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'description': self.description,
            'certification_files': json.loads(self.certification_files) if self.certification_files else [],
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    factory_id = db.Column(db.Integer, db.ForeignKey('factories.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    title = db.Column(db.String(300), nullable=False)
    title_en = db.Column(db.String(300))
    description = db.Column(db.Text)
    description_en = db.Column(db.Text)
    images = db.Column(db.Text, default='[]')
    poster_images = db.Column(db.Text, default='[]')
    video_url = db.Column(db.String(500))
    moq = db.Column(db.Integer, default=1)
    lead_time = db.Column(db.String(100))
    base_price = db.Column(db.Numeric(10, 2))
    price_unit = db.Column(db.String(20), default='USD')
    packaging_info = db.Column(db.Text)
    packaging_info_en = db.Column(db.Text)
    customization = db.Column(db.Text)
    customization_en = db.Column(db.Text)
    specs = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    is_featured = db.Column(db.Boolean, default=False)
    is_new = db.Column(db.Boolean, default=False)
    is_clearance = db.Column(db.Boolean, default=False)
    is_banner = db.Column(db.Boolean, default=False)
    clearance_type = db.Column(db.String(50))
    certification = db.Column(db.String(200))
    stock_quantity = db.Column(db.Integer)
    view_count = db.Column(db.Integer, default=0)
    review_note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category = db.relationship('Category', backref='products', foreign_keys=[category_id])

    @property
    def editable(self):
        return self.status in ('draft', 'rejected')

    def get_images(self):
        try:
            return json.loads(self.images) if self.images else []
        except Exception:
            return []

    def get_poster_images(self):
        try:
            return json.loads(self.poster_images) if self.poster_images else []
        except Exception:
            return []

    def get_specs(self):
        try:
            return json.loads(self.specs) if self.specs else {}
        except Exception:
            return {}

    def to_public_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'title_en': self.title_en,
            'description': self.description,
            'description_en': self.description_en,
            'images': self.get_images(),
            'poster_images': self.get_poster_images(),
            'video_url': self.video_url,
            'moq': self.moq,
            'lead_time': self.lead_time,
            'base_price': float(self.base_price) if self.base_price else None,
            'price_unit': self.price_unit,
            'packaging_info': self.packaging_info,
            'packaging_info_en': self.packaging_info_en,
            'customization': self.customization,
            'customization_en': self.customization_en,
            'specs': self.get_specs(),
            'is_featured': self.is_featured,
            'is_new': self.is_new,
            'is_clearance': self.is_clearance,
            'is_banner': self.is_banner,
            'clearance_type': self.clearance_type,
            'certification': self.certification,
            'stock_quantity': self.stock_quantity,
            'category_id': self.category_id,
            'category_name': self.category.name if self.category else None,
            'category_name_en': self.category.name_en if self.category else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def to_factory_dict(self):
        d = self.to_public_dict()
        d['base_price'] = float(self.base_price) if self.base_price else None
        d['price_unit'] = self.price_unit
        d['status'] = self.status
        d['editable'] = self.editable
        d['review_note'] = self.review_note
        d['factory_id'] = self.factory_id
        return d

    def to_admin_dict(self):
        d = self.to_factory_dict()
        d['factory_name'] = self.factory.company_name if self.factory else None
        return d


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100))
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    icon = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

    def to_dict(self, include_inactive=True):
        children = self.children or []
        if not include_inactive:
            children = [c for c in children if c.is_active]
        return {
            'id': self.id,
            'name': self.name,
            'name_en': self.name_en,
            'parent_id': self.parent_id,
            'icon': self.icon,
            'sort_order': self.sort_order,
            'is_active': self.is_active,
            'children': [c.to_dict(include_inactive=include_inactive) for c in sorted(children, key=lambda x: x.sort_order)],
        }


class Inquiry(db.Model):
    __tablename__ = 'inquiries'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    company_name = db.Column(db.String(200))
    contact_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')
    source = db.Column(db.String(50))
    customer_level = db.Column(db.String(20))
    admin_reply = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('inquiries', cascade='all, delete-orphan'))
    user = db.relationship('User', backref='inquiries')

    def to_dict(self):
        # Find latest accepted quote price for this inquiry
        latest_quote = None
        for msg in self.messages.filter_by(msg_type='quote').order_by(Message.created_at.desc()):
            if msg.quote_status == 'accepted':
                latest_quote = float(msg.quote_price) if msg.quote_price else None
                break
            if msg.quote_status == 'pending' and latest_quote is None:
                latest_quote = float(msg.quote_price) if msg.quote_price else None

        d = {
            'id': self.id,
            'product_id': self.product_id,
            'product_title': self.product.title if self.product else None,
            'product_title_en': self.product.title_en if self.product else None,
            'company_name': self.company_name,
            'contact_name': self.contact_name,
            'email': self.email,
            'phone': self.phone,
            'quantity': self.quantity,
            'message': self.message,
            'status': self.status,
            'source': self.source,
            'admin_reply': self.admin_reply,
            'user_id': self.user_id,
            'username': self.user.username if self.user else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'wishlist_products': None,
            'is_wishlist': False,
            'quote_price': latest_quote,
            'base_price': float(self.product.base_price) if self.product and self.product.base_price else None,
        }
        # Parse wishlist structured message
        if self.message:
            try:
                parsed = json.loads(self.message)
                if isinstance(parsed, dict) and 'products' in parsed:
                    d['message'] = parsed.get('text', '')
                    d['wishlist_products'] = parsed['products']
                    d['is_wishlist'] = True
            except (json.JSONDecodeError, TypeError):
                pass
        return d


class WishList(db.Model):
    __tablename__ = 'wishlists'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    product = db.relationship('Product', backref=db.backref('wishlist_items', cascade='all, delete-orphan'))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'product': self.product.to_public_dict() if self.product else None,
            'quantity': self.quantity,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    inquiry_id = db.Column(db.Integer, db.ForeignKey('inquiries.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    msg_type = db.Column(db.String(10), default='text')  # text / quote / system
    quote_price = db.Column(db.Numeric(10, 2), nullable=True)
    quote_status = db.Column(db.String(10), nullable=True)  # pending / accepted / rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    inquiry = db.relationship('Inquiry', backref=db.backref('messages', lazy='dynamic', order_by='Message.created_at', cascade='all, delete-orphan'))
    sender = db.relationship('User')

    def to_dict(self):
        d = {
            'id': self.id,
            'inquiry_id': self.inquiry_id,
            'sender_id': self.sender_id,
            'sender_name': self.sender.username if self.sender else None,
            'sender_role': self.sender.role if self.sender else None,
            'content': self.content,
            'is_read': self.is_read,
            'msg_type': self.msg_type or 'text',
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if self.msg_type == 'quote':
            d['quote_price'] = float(self.quote_price) if self.quote_price else None
            d['quote_status'] = self.quote_status
        return d


class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    key = db.Column(db.String(200), primary_key=True)
    value = db.Column(db.Text, default='')
