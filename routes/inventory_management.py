from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from database import db, Product, Subcategory, Category, InventoryLog
from routes.login import role_required
from sqlalchemy.sql import case
from sqlalchemy import func, Date, text
from utils.log_helper import log_activity


inventory_management = Blueprint('inventory_management', __name__)

# VIEW ALL WAREHOUSES INVENTORY
@inventory_management.route('/inventory/view_all_warehouses', methods=['GET'])
@jwt_required()
@role_required(["Inventory_Manager", "Admin"])
def view_all_warehouses_inventory():
    """
    View all warehouses with their products and stock levels.
    """
    try:
        low_stock_threshold = 10  # Products with stock below this level will trigger an alert

        # Fetch all distinct warehouse locations
        warehouses = db.session.query(Product.warehouse_location).distinct()

        inventory = []  # List to hold inventory details for all warehouses
        low_stock_alerts = []  # List to collect products with low stock

        for warehouse in warehouses:
            # Query products in the current warehouse
            products = (
                db.session.query(
                    Product.product_id,
                    Product.name,
                    Product.stock_level,
                    Subcategory.name.label("subcategory_name"),
                    Category.name.label("category_name")
                )
                .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id)
                .join(Category, Subcategory.category_id == Category.category_id)
                .filter(Product.warehouse_location == warehouse.warehouse_location)
                .all()
            )

            # Prepare inventory details for the current warehouse
            warehouse_inventory = {"warehouse_name": warehouse.warehouse_location, "products": []}
            for product in products:
                # Add product details to the warehouse inventory
                warehouse_inventory["products"].append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "stock_level": product.stock_level,
                    "subcategory": product.subcategory_name,
                    "category": product.category_name
                })

                # Check if product stock is below the threshold and add to alerts if necessary
                if product.stock_level < low_stock_threshold:
                    low_stock_alerts.append({
                        "product_id": product.product_id,
                        "name": product.name,
                        "stock_level": product.stock_level,
                        "subcategory": product.subcategory_name,
                        "category": product.category_name,
                        "warehouse_name": warehouse.warehouse_location
                    })

            # Add the warehouse inventory to the final list
            inventory.append(warehouse_inventory)
        # Log the activity
        log_activity(
            admin_id=get_jwt_identity()["id"],  # Get admin ID from JWT token
            action="Viewed all warehouses inventory",
            description=f"Viewed all warehouses inventory"
        )
        return jsonify({"inventory": inventory, "low_stock_alerts": low_stock_alerts}), 200
    except Exception:
        # Return an error message if something goes wrong
        return jsonify({"error": "Can't View Warehouse Inventories"}), 500


# GENERATE INVENTORY TURNOVER REPORT
@inventory_management.route('/inventory/inventory_turnover_report', methods=['GET'])
@jwt_required()
@role_required(["Inventory_Manager", "Admin"])
def generate_inventory_report():
    """
    Generate inventory turnover reports grouped by warehouse.
    Turnover is calculated based on sales volume and product price.
    """
    try:
        # Fetch all distinct warehouse locations
        warehouses = db.session.query(Product.warehouse_location).distinct()

        report_data = []  # List to hold turnover details for all warehouses

        for warehouse in warehouses:
            # Query products and calculate turnover for the current warehouse
            products = (
                db.session.query(
                    Product.product_id,
                    Product.name,
                    Product.stock_level,
                    Subcategory.name.label("subcategory_name"),
                    Category.name.label("category_name"),
                    func.coalesce(
                        func.sum(
                            case(
                                (InventoryLog.change < 0, func.abs(InventoryLog.change) * Product.price),
                                else_=0
                            )
                        ),
                        0
                    ).label("total_turnover")  # Default turnover to 0 if no sales
                )
                .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id)
                .join(Category, Subcategory.category_id == Category.category_id)
                .outerjoin(InventoryLog, InventoryLog.product_id == Product.product_id)  # Include products with no logs
                .filter(Product.warehouse_location == warehouse.warehouse_location)
                .group_by(Product.product_id)
                .all()
            )

            # Prepare report details for the current warehouse
            warehouse_report = {"warehouse_name": warehouse.warehouse_location, "products": []}
            for product in products:
                warehouse_report["products"].append({
                    "product_id": product.product_id,
                    "name": product.name,
                    "stock_level": product.stock_level,
                    "turnover": product.total_turnover or 0,  # Default to 0 if no sales
                    "subcategory": product.subcategory_name,
                    "category": product.category_name
                })

            # Add the warehouse report to the final list
            report_data.append(warehouse_report)
        # Log the activity
        log_activity(
            admin_id=get_jwt_identity()["id"],  # Get admin ID from JWT token
            action="Generated Inventory Turnover Report",
            description=f"Generated Inventory Turnover Report"
        )
        return jsonify({"report": report_data}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({"error": f"Can't Generate Inventory Turnover Report"}), 500


# MOST POPULAR PRODUCTS
@inventory_management.route('/inventory/most_popular_products', methods=['GET'])
@jwt_required()
@role_required(["Inventory_Manager", "Admin"])
def get_most_popular_products():
    """
    Retrieve the top 10 most popular products based on sales volume.
    """
    try:
        # Query top 10 products with the highest sales volume
        products = (
            db.session.query(
                Product.product_id,
                Product.name,
                Subcategory.name.label("subcategory_name"),
                Category.name.label("category_name"),
                func.sum(func.abs(InventoryLog.change)).label("total_sales")
            )
            .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id)
            .join(Category, Subcategory.category_id == Category.category_id)
            .join(InventoryLog, InventoryLog.product_id == Product.product_id)
            .filter(InventoryLog.change < 0)
            .group_by(Product.product_id)
            .order_by(func.sum(func.abs(InventoryLog.change)).desc())
            .limit(10)
            .all()
        )

        results = []
        for rank, product in enumerate(products, start=1):
            # Add ranked product details to the final list
            results.append({
                "rank": rank,
                "product_id": product.product_id,
                "name": product.name,
                "total_sales": product.total_sales,
                "subcategory": product.subcategory_name,
                "category": product.category_name
            })
        # Log the activity
        log_activity(
            admin_id=get_jwt_identity()["id"],  # Get admin ID from JWT token
            action="Generated Popular Products Report",
            description=f"Generated Popular Products Report"
        )
        return jsonify({"popular_products": results}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({"error": f"Can't Generate Popular Products Report"}), 500


# PREDICT FUTURE DEMAND
@inventory_management.route('/inventory/predict_demand_monthly', methods=['GET'])
@jwt_required()
@role_required(["Inventory_Manager", "Admin"])
def predict_future_monthly_demand():
    """
    Predict future demand for the next 30 days based on the last 30 days of sales data.
    Only negative changes (sales) are considered for the prediction.
    """
    try:
        prediction_days = 30  # Future period for prediction

        # Query sales data for the last 30 days for all products
        products = (
            db.session.query(
                Product.product_id,
                Product.name,
                Subcategory.name.label("subcategory_name"),
                Category.name.label("category_name"),
                func.sum(
                    case(
                        (InventoryLog.change < 0, func.abs(InventoryLog.change)),
                        else_=0
                    )
                ).label("total_sales"),  # Sum of negative changes
                func.count(
                    func.distinct(
                        case(
                            (InventoryLog.change < 0, func.date(InventoryLog.timestamp)),
                            else_=None
                        )
                    )
                ).label("sales_days")  # Count unique days with negative changes
            )
            .join(Subcategory, Product.subcategory_id == Subcategory.subcategory_id)
            .join(Category, Subcategory.category_id == Category.category_id)
            .outerjoin(InventoryLog, InventoryLog.product_id == Product.product_id)
            .filter(func.date(InventoryLog.timestamp) >= text("CURRENT_DATE - INTERVAL 30 DAY"))  # Filter for the last 30 days
            .group_by(Product.product_id)
            .all()
        )

        predictions = []
        for product in products:
            # Calculate average daily sales and predict future demand
            avg_daily_sales = product.total_sales / product.sales_days if product.sales_days else 0
            predicted_demand = avg_daily_sales * prediction_days

            predictions.append({
                "product_id": product.product_id,
                "name": product.name,
                "average_daily_sales": round(avg_daily_sales, 2),
                "predicted_demand_next_month": round(predicted_demand, 2),
                "subcategory": product.subcategory_name,
                "category": product.category_name
            })
        # Log the activity
        log_activity(
            admin_id=get_jwt_identity()["id"],  # Get admin ID from JWT token
            action="Generated Predicted Future Demand Report",
            description=f"Generated Predicted Future Demand Report"
        )
        return jsonify({"predictions": predictions}), 200
    except Exception as e:
        # Return an error message if something goes wrong
        return jsonify({"error": f"Can't Generate Predicted Future Demand Report"}), 500