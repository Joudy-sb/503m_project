from datetime import datetime, timezone
from sqlalchemy.sql import text
from database import db  # Import the database instance from models
from argon2 import PasswordHasher

ph = PasswordHasher(
    time_cost=2,          # Number of iterations
    memory_cost=19456,    # Memory in KiB (19 MiB)
    parallelism=1         # Number of parallel threads) # Initialize the PasswordHasher
)  # Initialize the PasswordHasher

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
        },
        {
            "name": "Khaled Dassouki",
            "email": "khaled@example.com",
            "role": "Admin",
            "password": "password321"
        }
    ]

    rawQueryString = """
    INSERT INTO Admins (name, email, role, password, created_at, updated_at)
    VALUES (:name, :email, :role, :password, :created_at, :updated_at)
    """
    
    for admin in admins:
        # Hash the password before storing it
        hashed_pass = ph.hash(admin["password"])
        query = text(rawQueryString).bindparams(
            name=admin["name"],
            email=admin["email"],
            role=admin["role"],
            password=hashed_pass,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        db.session.execute(query)
        
    db.session.commit()
    print("Admins added successfully!")
