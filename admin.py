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

app = Flask(__name__)

ALLOWED_EXTENSIONS = [
    'png',
    'jpg',
    'jpeg',
]

app.config['UPLOAD_FOLDER'] = 'C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/Uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce_platform.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    __tablename__ = 'Products'
    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
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
    address = db.Column(db.Text)
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


# Order Management System





# Product Management
# ! FIX: THIS FUNCTION SCANS THE FILE TO MAKE SURE THE CONTENT IS NOT MALICIOUS
def scan_file(file_path):
    cd = pyclamd.ClamdNetworkSocket()  
    try:
        result = cd.scan_file(file_path) 
        return result
    except Exception as e:
        print(f"Error scanning file: {e}")
        return None
    
def validate_information(product):
    try:
        # Validate 'name'
        name = product["name"]
        if not isinstance(name, str):
            raise ValueError("Invalid input for name, must be a string")

        # Validate 'description'
        description = product['description']
        if not isinstance(description, str):
            raise ValueError("Invalid input for description, must be a string")

        # Validate 'price'
        price = product['price']
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValueError("Invalid input for price, must be a float")

        # Validate 'specifications'
        specifications = product.get('specifications', '{}')  # Default to empty JSON object if missing
        try:
            if isinstance(specifications, str):
                specifications = json.loads(specifications)  # Parse JSON string
            elif not isinstance(specifications, dict):
                raise ValueError("Invalid input for specifications, must be a valid JSON string or dictionary")
        except (ValueError, TypeError):
            raise ValueError("Invalid input for specifications, must be valid JSON")

        # Convert back to JSON string for storage
        specifications_json = json.dumps(specifications)

        # Validate 'stock_level'
        stock_level = product['stock_level']
        try:
            stock_level = int(stock_level)
        except (ValueError, TypeError):
            raise ValueError("Invalid input for stock_level, must be an integer")

        # Validate 'warehouse_location'
        warehouse_location = product['warehouse_location']
        if not isinstance(warehouse_location, str):
            raise ValueError("Invalid input for warehouse_location, must be a string")

        # Validate 'category_id'
        category_id = int(product['category_id'])
        if not Category.query.filter_by(category_id=category_id).first():
            raise ValueError(f"Category with ID {category_id} does not exist")

        # Validate 'subcategory_id'
        subcategory_id = int(product['subcategory_id'])
        if not Subcategory.query.filter_by(subcategory_id=subcategory_id).first():
            raise ValueError(f"Subcategory with ID {subcategory_id} does not exist")

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

    except ValueError as e:
        raise e

# THIS FUNCTION VALIDATES FILE TYPE
def allowed_file_type(file_path):
    mime = magic.Magic(mime=True) 
    file_mime_type = mime.from_file(file_path)  
    print(f"Detected MIME type: {file_mime_type}")
    return file_mime_type in ['image/png', 'image/jpeg', 'image/jpg']

# THIS FUNCTION VALIDATES FILE EXTENSION
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
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

        # Insert product into DB
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

    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# THIS FUNCTION DELETES A PRODUCT FROM DATABASE
@app.route('/admin/product-management/delete', methods=['POST'])
def delete_product():
    #verify that the admin position is allowed to do this method

    try:
        data = request.get_json()
        product_id = data.get('product_id')
        if not product_id:
            return jsonify({"error": "Product ID is required"}), 400
    
        product = Product.query.filter_by(product_id=product_id).first()
        if product is None:
            return jsonify({"error": f"No product found with ID {product_id}"}), 404
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": f"Product with ID {product_id} deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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

        # Validate and process inputs
        validated_data = validate_information(updated_product)

        # after verification, update product to the database
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
        return jsonify({"error": str(e)}), 500

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