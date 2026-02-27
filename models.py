from extensions import db
from datetime import datetime

# USERS
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20))  # admin / vendor / user
    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
# MEMBERSHIP
class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.String(50))
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)

# VENDOR
class Vendor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(200))

# PRODUCT
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
    name = db.Column(db.String(100))
    price = db.Column(db.Float)
    image = db.Column(db.String(200))

# CART
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)

# ORDER
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    total_amount = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    status = db.Column(db.String(50), default="Received")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ORDER ITEMS
class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)