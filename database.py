from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

# Initialize SQLAlchemy
db = SQLAlchemy()

class Product(db.Model):
    __tablename__ = 'Products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(400))
    price = db.Column(db.Float, nullable=False)
    image_data = db.Column(db.LargeBinary)
    specifications = db.Column(db.JSON)
    category_id = db.Column(db.Integer, db.ForeignKey('Categories.category_id'))
    subcategory_id = db.Column(db.Integer, db.ForeignKey('Subcategories.subcategory_id'))
    stock_level = db.Column(db.Integer, nullable=False)
    warehouse_location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc),server_default=func.now(), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc),server_default=func.now(), onupdate=datetime.now(timezone.utc))

class Category(db.Model):
    __tablename__ = 'Categories'
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class Subcategory(db.Model):
    __tablename__ = 'Subcategories'
    subcategory_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('Categories.category_id'))
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class InventoryLog(db.Model):
    __tablename__ = 'InventoryLogs'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    change = db.Column(db.Integer, nullable=False) # positive for restock, negative for sale
    reason = db.Column(db.Text) # can make it take one of two options : sale or restock
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc),server_default=func.now(), nullable=False)

class Order(db.Model):
    __tablename__ = 'Orders'
    order_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'))
    status = db.Column(db.String(50), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class OrderItem(db.Model):
    __tablename__ = 'OrderItems'
    order_item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'))
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

class Customer(db.Model):
    __tablename__ = 'Customers'
    customer_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    membership_tier = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(15))
    password_hash = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class CustomerProfile(db.Model):
    __tablename__ = 'CustomerProfile'
    profile_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('Customers.customer_id'))
    preferences = db.Column(db.Text)
    total_spent = db.Column(db.Float, default=0.0)

class Admin(db.Model):
    __tablename__ = 'Admins'
    admin_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Promotion(db.Model):
    __tablename__ = 'Promotions'
    promo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'))
    discount_percentage = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    tier = db.Column(db.String(50))

class ActivityLog(db.Model):
    __tablename__ = 'ActivityLog'
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('Admins.admin_id'))
    action = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc),server_default=func.now(), nullable=False)

class Return(db.Model):
    __tablename__ = 'Returns'
    return_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('Orders.order_id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('Products.product_id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pending")  # Pending, Approved, Rejected, Processed
    reason = db.Column(db.Text, nullable=False)
    action = db.Column(db.String(50), nullable=False)  # Refund, Replacement
    requested_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    processed_at = db.Column(db.DateTime)