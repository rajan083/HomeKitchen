import datetime
import uuid
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# =================================================USER=================================================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    upi_id = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(10), nullable=False)
    items = db.relationship('Item', backref='seller')
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    business_name = db.Column(db.String(150), nullable=True, unique=True)
    terms_accepted = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.String(50), nullable=True)
    longitude = db.Column(db.String(50), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_number = db.Column(db.String(50), nullable=True)
    id_proof = db.Column(db.String(200), nullable=True)
    license = db.Column(db.String(200), nullable=True)
    insurance = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.String(200), nullable=True)
    verified = db.Column(db.Boolean, default=False)
    wallet_balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =================================================RIDER KYC=================================================

class Rider_kyc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password_hash = db.Column(db.String(250), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    email_verified = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(255), nullable=True)
    vehicle_type = db.Column(db.String(50), nullable=True)
    vehicle_number = db.Column(db.String(50), nullable=True)
    id_proof = db.Column(db.String(200), nullable=True)
    license = db.Column(db.String(200), nullable=True)
    insurance = db.Column(db.String(200), nullable=True)
    photo = db.Column(db.String(200), nullable=True)
    verified = db.Column(db.Boolean, default=False)
    wallet_balance = db.Column(db.Float, default=0.0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# =================================================VENDOR KYC=================================================

class Vendor_kyc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(10), nullable=False)
    id_number = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False, unique=True)
    id_proof = db.Column(db.String(255), nullable=False)
    photo_path = db.Column(db.String(255), nullable=False)
    business_name = db.Column(db.String(150), nullable=True, unique=True)
    verified = db.Column(db.Boolean, default=False)


# =================================================ITEM=================================================

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itemid = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    context = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.Column(db.Integer, default=0)
    type = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(100), nullable=True)
    dislikes = db.Column(db.Integer, default=0)
    comments = db.relationship('Comment', backref='item', lazy=True)
    categories = db.Column(db.String(50), nullable=True)
    order_count = db.Column(db.Integer, default=0)


# =================================================ORDER=================================================

class Order(db.Model):
    id = db.Column(db.String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    item_name = db.Column(db.String(100), nullable=False)
    user_email = db.Column(db.String(100), db.ForeignKey('user.email'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    upi_link = db.Column(db.String(500), nullable=True)
    quantity = db.Column(db.Integer, nullable=False)
    payment_status = db.Column(db.String(20), default='Pending')
    consumer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('rider_kyc.id'), nullable=True)
    status = db.Column(db.String(20))
    delivered_at = db.Column(db.DateTime, nullable=True)
    rider_fee = db.Column(db.Float, default=0.0)
    delivery_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    consumer = db.relationship(
        'User',
        primaryjoin="and_(Order.consumer_id == User.id, User.role == 'consumer')",
        backref='consumer_orders'
    )
    vendor = db.relationship(
        'User',
        primaryjoin="and_(Order.vendor_id == User.id, User.role == 'vendor')",
        backref='vendor_orders'
    )
    rider = db.relationship('Rider_kyc', backref='rider_deliveries')


# =================================================TRANSACTION=================================================

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.String(50), db.ForeignKey('order.id'))    
    vendor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    consumer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    rider_id = db.Column(db.Integer, db.ForeignKey('rider_kyc.id'), nullable=True)
    vendor_share = db.Column(db.Float, nullable=False, default=0.0)
    rider_share = db.Column(db.Float, nullable=False, default=0.0)
    platform_share = db.Column(db.Float, nullable=False, default=0.0)
    amount = db.Column(db.Float, nullable=False)
    transaction_id = db.Column(db.String(100), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)


# =================================================COMMENT=================================================

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref=db.backref('comments', lazy=True))


# =================================================SAVED ITEM=================================================

class SavedItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    saved_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user = db.relationship('User', backref='saved_items')
    item = db.relationship('Item', backref='saved_by_users')