import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

class Config:
    # File upload configuration
    #UPLOAD_FOLDER = os.path.join(os.getcwd(), 'path')  # Define a safe default path
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678910lc@localhost:3306/ecommerce_platform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration
    JWT_SECRET_KEY = "super-secret" #Use Environment Variables to make this key secure + change to smth more complex 
    
