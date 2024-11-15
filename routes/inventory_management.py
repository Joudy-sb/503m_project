from flask import Blueprint, jsonify, request
from database import Product, Subcategory, Category,db
from sqlalchemy import text
from flask_jwt_extended import jwt_required, get_jwt_identity
inventory_management = Blueprint('inventory_management', __name__)

@inventory_management.route('/inventory/view_all_warehouses', methods=['GET']) #real time montioring of stock level across warehouses
@jwt_required()
def view_all_warehouses_inventory():

    """
    View all warehouses with their products and stock levels.
    """
    try:
        low_stock_threshold = 10  # Set low-stock threshold

        # Fetch distinct warehouse names from the Products table
        warehouses = db.session.query(Product.warehouse_location).distinct()

        inventory = []
        low_stock_alerts = []

        for warehouse in warehouses:
            warehouse_location = warehouse.warehouse_location
            warehouse_inventory = {"warehouse_name": warehouse_location, "products": []}
            products = Product.query.filter_by(warehouse_location=warehouse_location).all()

            for product in products:
                # Fetch subcategory and category details
                subcategory = Subcategory.query.get(product.subcategory_id)
                category =  Category.query.get(product.category_id)

                # Add product details to the warehouse inventory
                warehouse_inventory["products"].append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "stock_level": product.stock_level,
                    "subcategory": subcategory.name,
                    "category": category.name
                })

                # Add to low-stock alerts if below threshold
                if product.stock_level < low_stock_threshold:
                    low_stock_alerts.append({
                        "product_id": product.product_id,
                        "name": product.name,
                        "stock_level": product.stock_level,
                        "subcategory": subcategory.name,
                        "category": category.name,
                        "warehouse_name": warehouse_location
                    })

            inventory.append(warehouse_inventory)

        return jsonify({
            "inventory": inventory,
            "low_stock_alerts": low_stock_alerts
        }), 200
    except Exception as e:
        return jsonify({"error": "Can't View Warehouse Inventories"}), 500 #str(e) if we wanna see the error


## TO DO: AUTOMATIC UPDATE OF AVAILABIILITY OF PRODUCTS, AND LOW STOCK LEVEL ALERTS


## INVENTORY REPORT BY WAREHOUSE
@inventory_management.route('/inventory/iventory_turnover_report', methods=['GET'])
def generate_inventory_report():
    """
    Generate inventory reports grouped by warehouse, including turnover.
    """
    try:
        # Fetch distinct warehouse names from the Products table
        warehouses = db.session.query(Product.warehouse_location).distinct()

        report_data = []

        for warehouse in warehouses:
            warehouse_name = warehouse.warehouse_location
            warehouse_report = {"warehouse_name": warehouse_name, "products": []}
            products = Product.query.filter_by(warehouse_location=warehouse_name).all()

            for product in products:
                # Calculate turnover from InventoryLogs
                logs = db.session.execute(
                text("""
                    SELECT SUM(ABS(`change`) * price) AS total_turnover
                    FROM inventoryLogs
                    JOIN Products ON inventoryLogs.product_id = Products.product_id
                    WHERE inventoryLogs.product_id = :product_id AND `change` < 0
                """),
                {"product_id": product.product_id}
                ).fetchone()
                turnover = logs.total_turnover if logs.total_turnover else 0

                # Fetch subcategory and category details
                subcategory = Subcategory.query.get(product.subcategory_id)
                category = Category.query.get(product.category_id)

                # Add product details to the warehouse report
                warehouse_report["products"].append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "stock_level": product.stock_level,
                    "turnover": turnover,
                    "subcategory": subcategory.name,
                    "category": category.name
                })

            report_data.append(warehouse_report)

        return jsonify({"report": report_data}), 200
    except Exception as e:
        return jsonify({"error": "Can't Generate Inventory Turnover Report"}), 500 #str(e) if we wanna see the error


## most popular products
@inventory_management.route('/inventory/most_popular_products', methods=['GET'])
def get_most_popular_products():
    """
    Retrieve the most popular products based on sales volume or frequency of transactions.
    """
    try:
        # Query to get most popular products by sales volume
        popular_by_sales = db.session.execute(
            text("""
                SELECT product_id, SUM(ABS(`change`)) AS total_sales
                FROM inventoryLogs
                WHERE `change` < 0
                GROUP BY product_id
                ORDER BY total_sales DESC
                LIMIT 10
            """)
        ).fetchall()

        popular_products = []

        for rank, entry in enumerate(popular_by_sales, start=1):  # Add ranks with enumerate()
            # Fetch product details
            product = Product.query.get(entry.product_id)
            subcategory = Subcategory.query.get(product.subcategory_id)
            category = Category.query.get(product.category_id)

            # Add product details to the response
            popular_products.append({
                "rank": rank,  # Add the rank
                "product_id": product.product_id,
                "name": product.name,
                "total_sales": entry.total_sales,
                "subcategory": subcategory.name,
                "category": category.name
            })

        return jsonify({"popular_products": popular_products}), 200
    except Exception as e:
        return jsonify({"error": "Can't Generate Popular Products Report"}), 500 #str(e) if we wanna see the error


