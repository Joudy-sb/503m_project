from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PRODUCTS = [
    {
        "name": "Body Lotion",
        "description": "A hydrating and moisturizing lotion for the body",
        "price": 15.99,
        "specifications": {
            "skinBenefits": ["Hydrating"],
            "ingredients": ["Aloe Vera", "Shea Butter", "Vitamin E"],
            "texture": "Cream",
            "volume": "200ml"
        },
        "stock_level": 120,
        "warehouse_location": "Aisle 5 Shelf B",
        "category_id": 5,
        "subcategory_id": 19,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/bodylotion.jfif"
    },
    {
        "name": "Cleanser",
        "description": "A gentle cleanser for daily use",
        "price": 9.99,
        "specifications": {
            "skinType": ["Normal", "Oily"],
            "ingredients": ["Salicylic Acid", "Tea Tree Oil"],
            "purpose": ["Deep cleansing"],
            "texture": "Foam",
            "volume": "150ml"
        },
        "stock_level": 150,
        "warehouse_location": "Aisle 2 Shelf A",
        "category_id": 1,
        "subcategory_id": 1,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/cleanser.jfif"
    },
    {
        "name": "Collagen",
        "description": "A beauty supplement for skin elasticity and hydration",
        "price": 24.99,
        "specifications": {
            "type": "Capsules",
            "keyNutrients": ["Collagen", "Vitamin E"],
            "purpose": ["Improve skin elasticity"],
            "servingSize": "30-day supply"
        },
        "stock_level": 80,
        "warehouse_location": "Aisle 9 Shelf C",
        "category_id": 10,
        "subcategory_id": 39,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/collagen.jfif"
    },
    {
        "name": "Scrubs",
        "description": "An exfoliating body scrub for smoother skin",
        "price": 13.50,
        "specifications": {
            "skinBenefits": ["Exfoliating"],
            "ingredients": ["Sea Salt", "Coconut Oil"],
            "texture": "Scrub",
            "volume": "250ml"
        },
        "stock_level": 75,
        "warehouse_location": "Aisle 5 Shelf C",
        "category_id": 5,
        "subcategory_id": 20,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/scrubs.jfif"
    },
    {
        "name": "Shampoo",
        "description": "A nourishing shampoo for daily use",
        "price": 10.99,
        "specifications": {
            "hairType": ["Straight"],
            "purpose": ["Hydration"],
            "ingredients": ["Argan Oil"],
            "volume": "500ml"
        },
        "stock_level": 90,
        "warehouse_location": "Aisle 3 Shelf A",
        "category_id": 3,
        "subcategory_id": 11,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/shampoo.jfif"
    },
    {
        "name": "Cologne",
        "description": "A refreshing and light fragrance",
        "price": 45.50,
        "specifications": {
            "fragranceFamily": "Citrus",
            "concentration": "Eau de Cologne (EDC)",
            "notes": {"top": "Lemon", "middle": "Orange Blossom", "base": "Musk"},
            "volume": "100ml"
        },
        "stock_level": 60,
        "warehouse_location": "Aisle 4 Shelf E",
        "category_id": 4,
        "subcategory_id": 17,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/cologne.jfif"
    },
    {
        "name": "Foundation",
        "description": "A medium coverage foundation for an even skin tone",
        "price": 29.99,
        "specifications": {
            "shade": "Ivory",
            "finish": "Matte",
            "coverage": "Medium",
            "waterproof": True,
            "ingredients": ["Paraben-free"],
            "volumeWeight": "30ml"
        },
        "stock_level": 100,
        "warehouse_location": "Aisle 3 Shelf D",
        "category_id": 2,
        "subcategory_id": 6,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/foundation.jfif"
    },
    {
        "name": "Hairdryer",
        "description": "A powerful hairdryer with adjustable heat settings",
        "price": 39.99,
        "specifications": {
            "material": "Synthetic",
            "heatSettings": 3,
            "size": "Full-size",
            "powerWattage": "2000W"
        },
        "stock_level": 50,
        "warehouse_location": "Aisle 7 Shelf F",
        "category_id": 8,
        "subcategory_id": 34,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/hairdryer.jfif"
    },
    {
        "name": "Lipstick",
        "description": "A bold long lasting lipstick",
        "price": 12.99,
        "specifications": {
            "shade": "Red",
            "finish": "Matte",
            "coverage": "Full",
            "waterproof": False,
            "ingredients": ["Cruelty-free"],
            "volumeWeight": "3g"
        },
        "stock_level": 200,
        "warehouse_location": "Aisle 3 Shelf B",
        "category_id": 2,
        "subcategory_id": 8,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/lipstick.jfif"
    },
    {
        "name": "Mask",
        "description": "A deep hydrating mask for all skin types",
        "price": 16.99,
        "specifications": {
            "skinType": ["Dry", "Combination"],
            "ingredients": ["Hyaluronic Acid", "Chamomile"],
            "purpose": ["Hydration"],
            "texture": "Gel",
            "volume": "75ml"
        },
        "stock_level": 110,
        "warehouse_location": "Aisle 2 Shelf C",
        "category_id": 1,
        "subcategory_id": 5,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/mask.jfif"
    },
    {
        "name": "Nail Polish",
        "description": "A long lasting nail polish with a glossy finish",
        "price": 5.99,
        "specifications": {
            "nailPolish": {"finish": "Glossy", "color": "Pink"},
            "ingredients": ["Non-toxic"]
        },
        "stock_level": 300,
        "warehouse_location": "Aisle 6 Shelf A",
        "category_id": 6,
        "subcategory_id": 23,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/nailpolish.jfif"
    },
    {
        "name": "Perfume",
        "description": "A floral fragrance with a sophisticated touch",
        "price": 70.00,
        "specifications": {
            "fragranceFamily": "Floral",
            "concentration": "Eau de Parfum (EDP)",
            "notes": {"top": "Rose", "middle": "Jasmine", "base": "Sandalwood"},
            "volume": "50ml"
        },
        "stock_level": 40,
        "warehouse_location": "Aisle 4 Shelf B",
        "category_id": 4,
        "subcategory_id": 16,
        "image_data": "C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/product_images/perfume.jfif"
    }
]

@app.route('/api/get-products', methods=['GET'])
def get_products():
    return jsonify(PRODUCTS)

if __name__ == '__main__':
    app.run(debug=True, port=8000)

