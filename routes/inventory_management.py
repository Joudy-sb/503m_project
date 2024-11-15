from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from database import Product
from routes.login import role_required

inventory_management = Blueprint('inventory_management', __name__)

@inventory_management.route('/inventory/view_all_warehouses', methods=['GET']) #real time montioring of stock level across warehouses
@jwt_required()
@role_required(["Inventory_Manager"])
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