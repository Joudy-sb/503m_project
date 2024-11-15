from flask import request, jsonify, Blueprint
from database import db, Product, Category, Subcategory
from datetime import datetime
import magic 
import pyclamd
import csv
import json
import os
from sqlalchemy.sql import text
from jsonschema import validate, ValidationError
from utils.product_json_specifications import skincare_specifications_schema, makeup_schema, haircare_schema, fragrances_schema, bodycare_schema, nailcare_schema, mens_grooming_schema, tools_accessories_schema, natural_organic_schema, beauty_supplements_schema


product_management = Blueprint('product_management', __name__)

ALLOWED_EXTENSIONS = [
    'png',
    'jpg',
    'jpeg',
    'csv',
]

# THIS FUNCTION SCANS THE FILE TO MAKE SURE THE CONTENT IS NOT MALICIOUS    
def scan_file(file_path):
    try:
        cd = pyclamd.ClamdNetworkSocket(host='127.0.0.1', port=3310)
        if cd.ping():
            print("ClamAV Daemon is running.")
            result = cd.scan_file(file_path)
            if result:
                for file, status in result.items():
                    if status[0] == "FOUND":
                        return jsonify({"error": f"Virus {status[1]} found in {file}"}), 400
            print("No infection found.")
            return jsonify({"message": "File is clean."}), 200
        else:
            print("ClamAV Daemon not responding.")
            return jsonify({"error": "ClamAV Daemon not responding."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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
                raise ValueError(f"Invalid JSON format for specifications")
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
        #print("Specifications are valid!")
        # Validate image file (if provided)
        image_data = product['image_data']
        file_path = None
        if image_data:
            if not allowed_file(image_data.filename):
                raise ValueError("Invalid file extension for image")
            file_path = os.path.normpath(os.path.join(product_management.config['UPLOAD_FOLDER'], image_data.filename))
            image_data.save(file_path)
            print(file_path)
            if not allowed_file_type(file_path):
                raise ValueError("Invalid file type for image")
            scan_file(file_path)
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
        raise ValueError("An error occurred")
    
# THIS FUNCTION ADDS A PRODUCT TO THE DATABASE
@product_management.route('/product-management/add', methods=['POST'])
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
        return jsonify({"error": "Unable to add product, try again"}), 500

# THIS FUNCTION DELETES A PRODUCT FROM DATABASE
@product_management.route('/product-management/delete/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    try:
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
@product_management.route('/product-management/update/<int:product_id>', methods=['PUT'])
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

# THIS FUNCTION ADDS BULK AMOUNT OF PRODUCTS
@product_management.route('/product-management/add-csv', methods=['POST'])
def bulk_add():
    try:
        csv_file = request.files.get('csv_file')
        if not csv_file:
            return jsonify({"error": "No file provided"}), 400
        if not allowed_file(csv_file.filename):
            raise ValueError("Invalid file extension for CSV")
        file_path = os.path.normpath(os.path.join(product_management.config['UPLOAD_FOLDER'], csv_file.filename))
        csv_file.save(file_path)
        if not allowed_file_type(file_path):
            raise ValueError("Invalid file type for CSV")
        scan_file(file_path)
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
                    errors.append({"row": row_index, "error": str(e)})
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
    
# THIS FUNCTION ADDS PROMOTION TO PRODUCTS
@product_management.route('/product-management/price-promotion/<int:product_id>', methods = ['POST'])
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