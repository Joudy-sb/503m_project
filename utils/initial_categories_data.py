from sqlalchemy.sql import text
from database import db  # Import the database instance from models

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