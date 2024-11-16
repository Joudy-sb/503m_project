from datetime import datetime, timezone
from sqlalchemy.sql import text
from database import db  # Import the database instance from models


def create_admins():
    admins = [
        {
            "name": "Joudy Sabbagh",
            "email": "joudy@example.com",
            "role": "Product_Manager",
            "password": "password123"
        },
        {
            "name": "Antoine Saade",
            "email": "antoine@example.com",
            "role": "Inventory_Manager",
            "password": "password456"
        },
        {
            "name": "Lynn Shami",
            "email": "lynn@example.com",
            "role": "Order_Manager",
            "password": "password789"
        }
    ]

    rawQueryString = """
    INSERT INTO Admins (name, email, role, password, created_at, updated_at)
    VALUES (:name, :email, :role, :password, :created_at, :updated_at)
    """
    
    for admin in admins:
        query = text(rawQueryString).bindparams(
            name=admin["name"],
            email=admin["email"],
            role=admin["role"],
            password=admin["password"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.session.execute(query)
        
    db.session.commit()
    print("Admins added successfully!")
