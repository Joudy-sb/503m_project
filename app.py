from flask import Flask
from database import db
from routes.inventory_management import inventory_management
from routes.order_management import order_management
from routes.product_management import product_management
from config import Config
from database import Category, Subcategory
from utils.initial_categories_data import create_categories, create_subcategories

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)

# Directly register blueprints with the app
app.register_blueprint(inventory_management, url_prefix='/admin')
app.register_blueprint(order_management, url_prefix='/admin')
app.register_blueprint(product_management, url_prefix='/admin')

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