from flask import Flask, jsonify
from database import Admin, db
from routes.inventory_management import inventory_management
from routes.order_management import order_management
from routes.product_management import product_management
from routes.login import login
from config import Config
from database import Category, Subcategory
from utils.initial_admins import create_admins
from utils.initial_categories_data import create_categories, create_subcategories
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)  # Initialize Flask-JWT-Extended with the app

# Directly register blueprints with the app
app.register_blueprint(inventory_management, url_prefix='/admin')
app.register_blueprint(order_management, url_prefix='/admin')
app.register_blueprint(product_management, url_prefix='/admin')
app.register_blueprint(login, url_prefix='/admin')


# handler for missing authorization headers
@jwt.unauthorized_loader
def custom_unauthorized_response(err):
    return jsonify({"msg": "Unauthorized"}), 401



if __name__ == '__main__':
    with app.app_context():
        # db.drop_all()
        db.create_all()  
        print("Database and tables created!")
        if not Category.query.first():
            create_categories()
            print("Categories created!")
        if not Subcategory.query.first():
            create_subcategories()
            print("Subategories created!")
        if not Admin.query.first():
            create_admins()
    app.run(debug=True)