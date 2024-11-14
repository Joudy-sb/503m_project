import csv
import json
import os
from sqlalchemy.sql import text
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta, timezone
import magic 
import pyclamd
from sqlalchemy import func
from jsonschema import validate, ValidationError
import csv
from flask import send_file
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from io import BytesIO

app = Flask(__name__)

ALLOWED_EXTENSIONS = [
    'png',
    'jpg',
    'jpeg',
    'csv',
]

# File upload configuration
app.config['UPLOAD_FOLDER'] = 'C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/Uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:987654321@localhost:3306/ecommerce_platform'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

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
    change = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text) # can make it take one of two options : sale or restock
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc))

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
    role = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

class Role(db.Model):
    __tablename__ = 'Roles'
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    permissions = db.Column(db.Text)

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
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

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

# THIS FUNCTION CREATES PRE-SET CATEGORIES
def create_categories():
    categories = [
        {"category_id": 1, "name": "Skincare", "description": "Products for the skin"},
        {"category_id": 2, "name": "Makeup", "description": "Products for makeup"},
        {"category_id": 3, "name": "Haircare", "description": "Products for hair"},
        {"category_id": 4, "name": "Fragrances", "description": "Perfumes and fragrances"},
        {"category_id": 5, "name": "Bodycare", "description": "Body care products"},
        {"category_id": 6, "name": "Nailcare", "description": "Products for nail care"},
        {"category_id": 7, "name": "Men's Grooming", "description": "Grooming products for men"},
        {"category_id": 8, "name": "Tools and Accessories", "description": "Beauty tools and accessories"},
        {"category_id": 9, "name": "Natural and Organic", "description": "Natural and organic beauty products"},
        {"category_id": 10, "name": "Beauty Supplements", "description": "Supplements for beauty and wellness"},
    ]
    rawQueryString = "INSERT INTO Categories (category_id, name, description) VALUES (:category_id, :name, :description)"
    for category in categories:
        query = text(rawQueryString).bindparams(
            category_id=category["category_id"],
            name=category["name"],
            description=category["description"]
        )
        db.session.execute(query)
    db.session.commit()
    print("Categories added successfully!")

# THIS FUNCTION CREATES PRE-SET SUBCATEGORIES
def create_subcategories():
    subcategories = [
        {"subcategory_id": 1, "category_id": 1, "name": "Cleansers", "description": "Products used to clean the skin and remove impurities."},
        {"subcategory_id": 2, "category_id": 1, "name": "Moisturizers", "description": "Products designed to hydrate and protect the skin."},
        {"subcategory_id": 3, "category_id": 1, "name": "Serums", "description": "Concentrated formulas targeting specific skin concerns like wrinkles or dark spots."},
        {"subcategory_id": 4, "category_id": 1, "name": "Sunscreens", "description": "Protects the skin from harmful UV rays."},
        {"subcategory_id": 5, "category_id": 1, "name": "Masks", "description": "Skin treatments for hydration, exfoliation, or detoxification."},

        {"subcategory_id": 6, "category_id": 2, "name": "Foundation", "description": "Makeup used to create an even complexion."},
        {"subcategory_id": 7, "category_id": 2, "name": "Eyeshadow", "description": "Powder or cream applied to the eyelids to add color or dimension."},
        {"subcategory_id": 8, "category_id": 2, "name": "Lipstick", "description": "Makeup for coloring and enhancing the lips."},
        {"subcategory_id": 9, "category_id": 2, "name": "Mascara", "description": "Used to enhance eyelashes by adding length, volume, and color."},
        {"subcategory_id": 10, "category_id": 2, "name": "Blush", "description": "Adds a natural flush of color to the cheeks."},

        {"subcategory_id": 11, "category_id": 3, "name": "Shampoos", "description": "Cleansing products for the hair and scalp."},
        {"subcategory_id": 12, "category_id": 3, "name": "Conditioners", "description": "Hair products used after shampooing to soften and detangle hair."},
        {"subcategory_id": 13, "category_id": 3, "name": "Hair Masks", "description": "Deep conditioning treatments for repairing and moisturizing hair."},
        {"subcategory_id": 14, "category_id": 3, "name": "Styling Products", "description": "Products such as gels, sprays, and creams to style and hold hair in place."},
        {"subcategory_id": 15, "category_id": 3, "name": "Hair Tools", "description": "Tools like brushes, combs, and flat irons for styling hair."},

        {"subcategory_id": 16, "category_id": 4, "name": "Perfumes", "description": "Fragrances designed to add a pleasant scent to the body."},
        {"subcategory_id": 17, "category_id": 4, "name": "Colognes", "description": "Light, fresh fragrances typically used by men."},
        {"subcategory_id": 18, "category_id": 4, "name": "Body Mists", "description": "Lightly fragranced sprays for refreshing the body."},

        {"subcategory_id": 19, "category_id": 5, "name": "Body Lotions", "description": "Moisturizers for hydrating and softening the body."},
        {"subcategory_id": 20, "category_id": 5, "name": "Scrubs", "description": "Exfoliating products to remove dead skin cells."},
        {"subcategory_id": 21, "category_id": 5, "name": "Bath Products", "description": "Items like bath salts and bubble baths for a relaxing bathing experience."},
        {"subcategory_id": 22, "category_id": 5, "name": "Hand Creams", "description": "Rich moisturizers designed specifically for hands."},

        {"subcategory_id": 23, "category_id": 6, "name": "Nail Polish", "description": "Colored or clear lacquer for decorating and protecting nails."},
        {"subcategory_id": 24, "category_id": 6, "name": "Nail Tools", "description": "Tools such as nail clippers, files, and cuticle pushers."},
        {"subcategory_id": 25, "category_id": 6, "name": "Cuticle Care", "description": "Products designed to care for and protect nail cuticles."},
        {"subcategory_id": 26, "category_id": 6, "name": "Nail Treatments", "description": "Products like nail strengtheners and growth treatments."},

        {"subcategory_id": 27, "category_id": 7, "name": "Beard Care", "description": "Products for maintaining and grooming beards, such as oils and balms."},
        {"subcategory_id": 28, "category_id": 7, "name": "Shaving Products", "description": "Razors, shaving creams, and aftershaves for a smooth shave."},
        {"subcategory_id": 29, "category_id": 7, "name": "Skincare for Men", "description": "Skin products specifically designed for men's skincare needs."},
        {"subcategory_id": 30, "category_id": 7, "name": "Colognes for Men", "description": "Fragrances tailored to men."},

        {"subcategory_id": 31, "category_id": 8, "name": "Brushes", "description": "Brushes for makeup application and skincare routines."},
        {"subcategory_id": 32, "category_id": 8, "name": "Sponges", "description": "Makeup sponges for smooth blending and application."},
        {"subcategory_id": 33, "category_id": 8, "name": "Tweezers", "description": "Tools for plucking eyebrows and removing small hairs."},
        {"subcategory_id": 34, "category_id": 8, "name": "Hairdryers", "description": "Electrical devices for drying hair."},
        {"subcategory_id": 35, "category_id": 8, "name": "Curling Irons", "description": "Tools for curling and styling hair."},

        {"subcategory_id": 36, "category_id": 9, "name": "Eco-friendly Skincare", "description": "Sustainable and environmentally friendly skincare products."},
        {"subcategory_id": 37, "category_id": 9, "name": "Natural Makeup", "description": "Makeup products made from natural ingredients."},
        {"subcategory_id": 38, "category_id": 9, "name": "Organic Haircare", "description": "Haircare products with certified organic ingredients."},

        {"subcategory_id": 39, "category_id": 10, "name": "Collagen Supplements", "description": "Supplements designed to improve skin elasticity and hydration."},
        {"subcategory_id": 40, "category_id": 10, "name": "Vitamins for Beauty", "description": "Vitamins aimed at improving hair, skin, and nails."},
        {"subcategory_id": 41, "category_id": 10, "name": "Hair Growth Supplements", "description": "Supplements to promote healthy hair growth."}
    ]
    rawQueryString = "INSERT INTO Subcategories (subcategory_id, category_id, name, description) VALUES (:subcategory_id, :category_id, :name, :description)"
    for subcategory in subcategories:
        query = text(rawQueryString).bindparams(
            subcategory_id=subcategory["subcategory_id"],
            category_id=subcategory["category_id"],
            name=subcategory["name"],
            description=subcategory["description"]
        )
        db.session.execute(query)
    db.session.commit()
    print("Subcategories added successfully!")

# Inventory Management System
@app.route('/admin/inventory/view_all_warehouses', methods=['GET']) #real time montioring of stock level across warehouses
def view_all_warehouses_inventory():
    """
    View all warehouses with their products and stock levels.
    """
    try:
        # Query all products grouped by warehouse location
        warehouses_inventory = {}

        # Get all products and organize by warehouse location
        products = Product.query.all()
        for product in products:
            warehouse = product.warehouse_location
            if warehouse not in warehouses_inventory:
                warehouses_inventory[warehouse] = {"warehouse": warehouse, "products": {}}
            
            warehouses_inventory[warehouse]["products"][product.name] = product.stock_level

        # Convert warehouses_inventory to a list for better JSON structure
        response_data = list(warehouses_inventory.values())

        return jsonify(response_data), 200
        # data looks like this: [{"warehouse": "A", "products": {"Product 1": 10, "Product 2": 20}},
        #                        {"warehouse": "B", "products": {"Product 1": 5, "Product 3": 15}}]
    except Exception as e:
        return jsonify({"error": str(e)}), 500


## TO DO: AUTOMATIC UPDATE OF AVAILABIILITY OF PRODUCTS, AND LOW STOCK LEVEL ALERTS


# --------------------------------Order Management System ----------------------------

@app.route('/admin/orders', methods=['GET']) #manage orders -> gets all orders from the db 
# MUST AUTHENTICATE ADMIN FIRST
def manage_orders():
    status = request.args.get('status')  # Get the status filter from the query params
    
    # Query orders based on the status filter, if provided
    if status:
        orders = Order.query.filter_by(status=status).all()  # Filter orders by status
    else:
        orders = Order.query.all()  # Get all orders if no filter is applied
    
    # Prepare the orders data for JSON response
    orders_data = []
    for order in orders:
        order_data = {
            'order_id': order.order_id,
            'customer_id': order.customer_id,
            'status': order.status,
            'total_price': order.total_price,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': order.updated_at.strftime('%Y-%m-%d %H:%M:%S') if order.updated_at else None,
        }
        
        orders_data.append(order_data)

    # Return the orders data as a JSON response
    return jsonify(orders_data)

@app.route('/admin/orderitems', methods=['GET']) #manage orders -> gets all order items from the db 
# MUST AUTHENTICATE ADMIN FIRST
def get_order_items():
    # Query all OrderItems from the database
    order_items = OrderItem.query.all()
    
    # Format each OrderItem as a dictionary
    order_items_list = [
        {
            "order_item_id": item.order_item_id,
            "order_id": item.order_id,
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_purchase": item.price_at_purchase
        }
        for item in order_items
    ]
    
    # Return the list of order items as JSON
    return jsonify(order_items_list)

@app.route('/admin/order/status/<int:order_id>', methods=['GET']) # Track order status
# MUST AUTHENTICATE ADMIN FIRST
def get_order_status(order_id):
    # Query the Order by the given order_id
    order = Order.query.get(order_id)
    
    # Check if the order exists
    if order is None:
        return jsonify({"error": "Order not found"}), 404
    
    # Return the order status in JSON format
    return jsonify({
        "order_id": order.order_id,
        "status": order.status
    })

@app.route('/admin/order/<int:order_id>/invoice', methods=['GET']) # MAKE THIS SECURE!!!
def generate_invoice(order_id):
    # Query the Order by the given order_id
    order = Order.query.get(order_id)
    if order is None:
        return jsonify({"error": "Order not found"}), 404

    # Fetch associated customer and order items
    customer = Customer.query.get(order.customer_id)
    order_items = OrderItem.query.filter_by(order_id=order_id).all()

    # Create a PDF in memory
    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    # Basic Invoice Layout
    pdf.setTitle(f"Invoice_{order_id}")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(200, height - 100, f"Invoice for Order #{order_id}")
    pdf.setFont("Helvetica", 12)

    # Customer Information
    pdf.drawString(50, height - 150, f"Customer: {customer.name}")
    pdf.drawString(50, height - 170, f"Email: {customer.email}")
    pdf.drawString(50, height - 190, f"Address: {customer.address}")
    pdf.drawString(50, height - 210, f"Phone: {customer.phone}")

    # Order Information
    pdf.drawString(50, height - 250, f"Order Date: {order.created_at.strftime('%Y-%m-%d')}")
    pdf.drawString(50, height - 270, f"Status: {order.status}")
    pdf.drawString(50, height - 290, f"Total Price: ${order.total_price:.2f}")

    # Table of Ordered Items
    data = [["Product ID", "Quantity", "Price at Purchase", "Total Price"]]
    for item in order_items:
        product = Product.query.get(item.product_id)
        data.append([
            item.product_id,
            item.quantity,
            f"${item.price_at_purchase:.2f}",
            f"${item.quantity * item.price_at_purchase:.2f}"
        ])
    
    # Add the order items table to the PDF
    table = Table(data, colWidths=[100, 100, 150, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    table.wrapOn(pdf, width, height)
    table.drawOn(pdf, 50, height - 400)

    pdf.showPage()
    pdf.save()
    pdf_buffer.seek(0)

    # Send the PDF as a file to download
    return send_file(pdf_buffer, as_attachment=True, download_name=f"Invoice_Order_{order_id}.pdf", mimetype='application/pdf')

ALLOWED_ORDER_STATUSES = {"Pending", "Processing", "Shipped", "Delivered"}


@app.route('/admin/update-order-status/<int:order_id>', methods=['PUT'])    # admin can update the status of the order 
                                                                            # validated admin input
#AUTHENTICATION!!
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get("status")

    # Check if the status provided is valid
    if new_status not in ALLOWED_ORDER_STATUSES:
        return jsonify({"error": "Invalid status. Allowed values are 'pending', 'processing', 'shipped', 'delivered'"}), 400

    # Fetch the order from the database
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    # Update the order status
    order.status = new_status
    db.session.commit()

    return jsonify({
        "message": "Order status updated successfully",
        "order_id": order.order_id,
        "new_status": order.status
    }), 200

@app.route('/admin/returns', methods=['GET']) # view return requests
def view_returns():
    status = request.args.get("status")
    if status:
        returns = Return.query.filter_by(status=status).all()
    else:
        returns = Return.query.all()
        
    return jsonify([{
        "return_id": r.return_id,
        "order_id": r.order_id,
        "product_id": r.product_id,
        "status": r.status,
        "reason": r.reason,
        "action": r.action,
        "requested_at": r.requested_at,
        "processed_at": r.processed_at
    } for r in returns])

@app.route('/admin/returns/<int:return_id>/process', methods=['POST']) # process return request
def process_return(return_id):
    # Get the return request from the database
    return_request = Return.query.get_or_404(return_id)

    # Ensure the action is either Refund or Replacement
    action = request.json.get('action', None)
    status = request.json.get('status', None)
    
    #validation
    if not action or action not in ['Refund', 'Replacement']:
        return jsonify({"error": "Invalid action. Action must be 'Refund' or 'Replacement'."}), 400
    
    if not status or status not in ['Approved', 'Rejected']:
        return jsonify({"error": "Invalid status. Status must be 'Approved' or 'Rejected'."}), 400

    # Update the return request based on action and status
    return_request.status = status
    return_request.action = action
    return_request.processed_at = datetime.utcnow()

    # Commit the changes to the database
    db.session.commit()

    return jsonify({
        'message': 'Return request processed successfully.',
        'return_id': return_request.return_id,
        'status': return_request.status,
        'action': return_request.action,
        'processed_at': return_request.processed_at
    }), 200

# --------------------------------Product Management System ----------------------------

# JSON SPECIFICATIONS 
skincare_specifications_schema = {
    "type": "object",
    "properties": {
        "skinType": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["Normal", "Dry", "Oily", "Combination", "Sensitive"]
            },
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {
                "type": "string"
            },
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["Hydration", "Anti-aging", "Brightening", "Sun protection", "Deep cleansing"]
            },
            "minItems": 1
        },
        "texture": {
            "type": "string",
            "enum": ["Gel", "Cream", "Foam", "Oil"]
        },
        "volume": {
            "type": "string",
            "pattern": "^[0-9]+(ml|ML|oz|OZ)$" 
        }
    },
    "required": ["skinType", "ingredients", "purpose", "texture", "volume"]
}

makeup_schema = {
    "type": "object",
    "properties": {
        "shade": {"type": "string", "minLength": 1},
        "finish": {"type": "string", "enum": ["Matte", "Satin", "Glossy", "Dewy"]},
        "coverage": {"type": "string", "enum": ["Light", "Medium", "Full"]},
        "waterproof": {"type": "boolean"},
        "ingredients": {
            "type": "array",
            "items": {"type": "string", "enum": ["Paraben-free", "Cruelty-free", "Vegan"]},
            "minItems": 1
        },
        "volumeWeight": {"type": "string", "pattern": "^[0-9]+(ml|g|oz)$"}
    },
    "required": ["shade", "finish", "coverage", "waterproof", "ingredients", "volumeWeight"]
}

haircare_schema = {
    "type": "object",
    "properties": {
        "hairType": {
            "type": "array",
            "items": {"type": "string", "enum": ["Straight", "Wavy", "Curly", "Coily", "Colored"]},
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {"type": "string", "enum": ["Repair", "Hydration", "Volume", "Anti-dandruff", "Color protection"]},
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|L|oz)$"},
        "tools": {"type": "string"}
    },
    "required": ["hairType", "purpose", "ingredients", "volume"]
}

fragrances_schema = {
    "type": "object",
    "properties": {
        "fragranceFamily": {"type": "string", "enum": ["Floral", "Woody", "Citrus", "Fresh", "Oriental"]},
        "concentration": {"type": "string", "enum": ["Eau de Parfum (EDP)", "Eau de Toilette (EDT)", "Eau de Cologne (EDC)"]},
        "notes": {
            "type": "object",
            "properties": {
                "top": {"type": "string"},
                "middle": {"type": "string"},
                "base": {"type": "string"}
            },
            "required": ["top", "middle", "base"]
        },
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|oz)$"}
    },
    "required": ["fragranceFamily", "concentration", "notes", "volume"]
}

bodycare_schema = {
    "type": "object",
    "properties": {
        "skinBenefits": {
            "type": "array",
            "items": {"type": "string", "enum": ["Hydrating", "Exfoliating", "Soothing"]},
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "texture": {"type": "string", "enum": ["Cream", "Gel", "Scrub"]},
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|oz)$"}
    },
    "required": ["skinBenefits", "ingredients", "texture", "volume"]
}

nailcare_schema = {
    "type": "object",
    "properties": {
        "nailPolish": {
            "type": "object",
            "properties": {
                "finish": {"type": "string", "enum": ["Glossy", "Matte"]},
                "color": {"type": "string"}
            },
            "required": ["finish", "color"]
        },
        "ingredients": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "nailTools": {"type": "string"},
        "treatments": {"type": "array", "items": {"type": "string"}, "minItems": 1}
    },
    "required": ["nailPolish", "ingredients"]
}

mens_grooming_schema = {
    "type": "object",
    "properties": {
        "skinType": {
            "type": "array",
            "items": {"type": "string", "enum": ["Normal", "Oily", "Sensitive"]},
            "minItems": 1
        },
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {"type": "string", "enum": ["Hydration", "Soothing post-shave", "Fragrance"]},
            "minItems": 1
        },
        "volume": {"type": "string", "pattern": "^[0-9]+(ml|oz)$"}
    },
    "required": ["skinType", "ingredients", "purpose", "volume"]
}

tools_accessories_schema = {
    "type": "object",
    "properties": {
        "material": {"type": "string", "enum": ["Synthetic", "Natural Bristles"]},
        "heatSettings": {"type": "integer", "minimum": 1, "maximum": 10}, 
        "size": {"type": "string", "enum": ["Compact", "Full-size"]},
        "powerWattage": {"type": "string", "pattern": "^[0-9]+W$"}  
    },
    "required": ["material", "heatSettings", "size", "powerWattage"]
}

natural_organic_schema = {
    "type": "object",
    "properties": {
        "ingredients": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "description": "Must be 100% organic and plant-based"
        },
        "certifications": {
            "type": "array",
            "items": {"type": "string", "enum": ["USDA Organic", "Cruelty-Free"]},
            "minItems": 1
        },
        "packaging": {"type": "string", "enum": ["Recyclable", "Biodegradable"]}
    },
    "required": ["ingredients", "certifications", "packaging"]
}

beauty_supplements_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["Capsules", "Powders", "Gummies"]},
        "keyNutrients": {
            "type": "array",
            "items": {"type": "string", "enum": ["Biotin", "Collagen", "Vitamin E", "Zinc"]},
            "minItems": 1
        },
        "purpose": {
            "type": "array",
            "items": {"type": "string", "enum": ["Strengthen hair", "Improve skin elasticity", "Nail health"]},
            "minItems": 1
        },
        "servingSize": {"type": "string", "pattern": "^[0-9]+-day supply$"}  
    },
    "required": ["type", "keyNutrients", "purpose", "servingSize"]
}

# ! FIX: THIS FUNCTION SCANS THE FILE TO MAKE SURE THE CONTENT IS NOT MALICIOUS
def scan_file(file_path):
    cd = pyclamd.ClamdNetworkSocket()  
    try:
        result = cd.scan_file(file_path) 
        return result
    except Exception as e:
        print(f"Error scanning file: {e}")
        return None
    
# THIS FUNCTION VALIDATES FILE TYPE
def allowed_file_type(file_path):
    mime = magic.Magic(mime=True) 
    file_mime_type = mime.from_file(file_path)  
    print(f"Detected MIME type: {file_mime_type}")
    return file_mime_type in ['image/png', 'image/jpeg', 'image/jpg', 'file/csv', 'text/plain']

# THIS FUNCTION VALIDATES FILE EXTENSION
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# THIS FUNCTION VALIDATES PRODUCT INFORMATION
def validate_information(product):
    try:
        # Validate 'name'
        name = product["name"]
        if not isinstance(name, str):
            raise ValueError("Name must be a string")
        if not name.replace(" ", "").isalpha():
            raise ValueError("Name must have only alphabet characters")
        if len(name) > 100:
            raise ValueError("Name too long")
        # Validate 'description'
        description = product['description']
        if not isinstance(description, str):
            raise ValueError("Invalid input for description, must be a string")
        if not description.replace(" ", "").isalpha():
            raise ValueError("Description must have only alphabet characters")
        if len(description) > 400:
            raise ValueError("Description too long")
        # Validate 'price'
        price = product['price']
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValueError("Invalid input for price, must be a float")
        if price <= 0:
            raise ValueError("Invalid input for price, must be strictly positive")
        # Validate 'stock_level'
        stock_level = product['stock_level']
        try:
            stock_level = int(stock_level)
        except (ValueError, TypeError):
            raise ValueError("Invalid input for stock_level, must be an integer")
        if stock_level <= 0:
            raise ValueError("Invalid input for stock, must be strictly positive")
        # Validate 'warehouse_location'
        warehouse_location = product['warehouse_location']
        if not isinstance(warehouse_location, str):
            raise ValueError("Invalid input for warehouse_location, must be a string")
        if not warehouse_location.replace(" ", "").isalnum():
            raise ValueError("Invalid input for warehouse_location, must only contain numerical and alphabet characters")
        # Validate 'category_id'
        category_id = int(product['category_id'])
        if not Category.query.filter_by(category_id=category_id).first():
            raise ValueError(f"Category does not exist")
        # Validate 'subcategory_id'
        subcategory_id = int(product['subcategory_id'])
        if not Subcategory.query.filter_by(subcategory_id=subcategory_id).first():
            raise ValueError(f"Subcategory does not exist")
         # Validate 'specifications'
        specifications = product.get('specifications', '{}')  
        # Parse 'specifications' if it's a string
        if isinstance(specifications, str):
            try:
                specifications = json.loads(specifications)
            except json.JSONDecodeError as e:
                raise ValueError("Invalid JSON format for specifications")
        # Ensure 'specifications' is a dictionary
        if not isinstance(specifications, dict):
            raise ValueError("Invalid input for specifications: must be a JSON string or dictionary")
        # Validate 'specifications' against schema
        try:
            if category_id == 1:
                validate(instance=specifications, schema=skincare_specifications_schema)
            if category_id == 2:
                validate(instance=specifications, schema=makeup_schema)
            if category_id == 3:
                validate(instance=specifications, schema=haircare_schema)
            if category_id == 4:
                validate(instance=specifications, schema=fragrances_schema)
            if category_id == 5:
                validate(instance=specifications, schema=bodycare_schema)
            if category_id == 6:
                validate(instance=specifications, schema=nailcare_schema)
            if category_id == 7:
                validate(instance=specifications, schema=mens_grooming_schema)
            if category_id == 8:
                validate(instance=specifications, schema=tools_accessories_schema)
            if category_id == 9:
                validate(instance=specifications, schema=natural_organic_schema)
            if category_id == 10:
                validate(instance=specifications, schema=beauty_supplements_schema)
        except ValidationError as e:
            raise ValueError("Schema validation failed")
        specifications_json = json.dumps(specifications)
        print("Specifications are valid!")
        # Validate image file (if provided)
        image_data = product['image_data']
        file_path = None
        if image_data:
            if not allowed_file(image_data.filename):
                raise ValueError("Invalid file extension for image")
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], image_data.filename)
            image_data.save(file_path)
            if not allowed_file_type(file_path):
                raise ValueError("Invalid file type for image")
        return {
            "name": name,
            "description": description,
            "price": price,
            "specifications": specifications_json,
            "stock_level": stock_level,
            "warehouse_location": warehouse_location,
            "category_id": category_id,
            "subcategory_id": subcategory_id,
            "image_data": file_path
        }
    except ValueError:
        raise ValueError("An error occurred. Please check your input.")
    
# THIS FUNCTION ADDS A PRODUCT TO THE DATABASE
@app.route('/admin/product-management/add', methods=['POST'])
def add_product():
    try:
        data = request.form
        product = {
            "name": data.get('name'),
            "description": data.get('description'),
            "price": data.get('price'),
            "specifications": data.get('specifications'),
            "stock_level": data.get('stock_level'),
            "warehouse_location": data.get('warehouse_location'),
            "category_id": data.get('category_id'),
            "subcategory_id": data.get('subcategory_id'),
            "image_data" : request.files.get('image_data')
        }
        validated_product = validate_information(product)
        validated_product['specifications'] = json.dumps(validated_product['specifications'])
        raw_query = """
        INSERT INTO Products (name, description, price, image_data, specifications, category_id, subcategory_id, stock_level, warehouse_location, created_at)
        VALUES (:name, :description, :price, :image_data, :specifications, :category_id, :subcategory_id, :stock_level, :warehouse_location, :created_at)
        """
        query = text(raw_query).bindparams(
            **validated_product,
            created_at=datetime.utcnow()
        )
        db.session.execute(query)
        db.session.commit()
        return jsonify({"message": "Product added successfully!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Pleace check input and try again"}), 500

# THIS FUNCTION DELETES A PRODUCT FROM DATABASE
@app.route('/admin/product-management/delete', methods=['POST'])
def delete_product():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
        product = Product.query.filter_by(product_id=product_id).first()
        if product is None:
            return jsonify({"error": f"No product found"}), 404
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Can't delete product, try again"}), 500

# THIS FUNCTION UPDATES A PRODUCT FROM DATABASE
@app.route('/admin/product-management/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try: 
        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            return jsonify({"error": "Product not found"}), 404
        data = request.form
        updated_product = {
            "name": data.get('name') or product.name,
            "description": data.get('description') or product.description,
            "price": data.get('price') or product.price,
            "specifications": data.get('specifications') or product.specifications,
            "stock_level": data.get('stock_level') or product.stock_level,
            "warehouse_location": data.get('warehouse_location') or product.warehouse_location,
            "category_id": data.get('category_id') or product.category_id,
            "subcategory_id": data.get('subcategory_id') or product.subcategory_id,
            "image_data": request.files.get('image_data')
        }
        validated_data = validate_information(updated_product)
        raw_query = """
        UPDATE Products
        SET name = :name,description = :description, price = :price, image_data = :image_data,specifications = :specifications, category_id = :category_id, subcategory_id = :subcategory_id, stock_level = :stock_level, warehouse_location = :warehouse_location, updated_at = :updated_at
        WHERE 
            product_id = :product_id
        """
        query = text(raw_query).bindparams(
            **validated_data,
            updated_at=datetime.utcnow(),
            product_id = product_id
        )
        db.session.execute(query)
        db.session.commit()
        return jsonify({"message": "Product updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Can't update product, try again"}), 500

@app.route('/admin/product-management/add-csv', methods=['POST'])
def bulk_add():
    try:
        csv_file = request.files.get('csv_file')
        if not csv_file:
            return jsonify({"error": "No file provided"}), 400
        if not allowed_file(csv_file.filename):
            raise ValueError("Invalid file extension for CSV")
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], csv_file.filename)
        csv_file.save(file_path)
        if not allowed_file_type(file_path):
            raise ValueError("Invalid file type for CSV")
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            errors = []
            successful_entries = []
            for row_index, row in enumerate(csv_reader, start=1):
                try:
                    # Validate and process each product row
                    validated_product = validate_information({
                        "name": row['name'],
                        "description": row['description'],
                        "price": row['price'],
                        "specifications": row['specifications'],
                        "stock_level": row['stock_level'],
                        "warehouse_location": row['warehouse_location'],
                        "category_id": row['category_id'],
                        "subcategory_id": row['subcategory_id'],
                        "image_data": None 
                    })                    
                    successful_entries.append(validated_product)
                except ValueError as e:
                    errors.append({"row": row_index, "error": "Please check inputs"})
            if successful_entries:
                insert_query = """
                INSERT INTO Products (name, description, price, image_data, specifications, 
                                      category_id, subcategory_id, stock_level, warehouse_location, created_at)
                VALUES (:name, :description, :price, :image_data, :specifications, 
                        :category_id, :subcategory_id, :stock_level, :warehouse_location, :created_at)
                """
                for product in successful_entries:
                    product['created_at'] = datetime.utcnow()  
                    db.session.execute(text(insert_query), product)
                db.session.commit()
        response = {
            "message": f"Successfully added {len(successful_entries)} products.",
            "errors": errors  
        }
        return jsonify(response), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "can't process the file"}), 500
    
@app.route('/admin/product-management/price-promotion/<int:product_id>', methods = ['POST'])
def promotion(product_id):
    try:
        data = request.form 
        price_promotion = data.get('price_promotion')
        try:
            price_promotion = int(price_promotion)
        except (ValueError, TypeError):
            raise ValueError("Invalid input for promotion, must be an int")
        if price_promotion > 100 or price_promotion <=0:
            return jsonify({"error": "promotion must be between 0 and 100"})
        product = Product.query.filter_by(product_id=product_id).first()
        price_promoted = product.price*(1-(price_promotion/100))
        raw_query = """
        UPDATE Products
        SET price = :price, updated_at = :updated_at
        WHERE 
            product_id = :product_id
        """
        query = text(raw_query).bindparams(
            price = price_promoted,
            updated_at=datetime.utcnow(),
            product_id = product_id
        )
        db.session.execute(query)
        db.session.commit()
        return jsonify({"message": "Product promotion added successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "can't place promotion, try again"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  
        print("Database and tables created!")
        if not Category.query.first():
            create_categories()
            print("Categories created!")
        if not Subcategory.query.first():
            create_subcategories()
            print("Subategories created!")

    app.run(debug=True)