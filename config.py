import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

class Config:
    # File upload configuration
    UPLOAD_FOLDER = 'C:/Users/joudy/Desktop/FALL_2024/EECE503M/Project/503m_project/Uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678910lc@localhost:3306/ecommerce_platform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

  # JWT Configuration
    JWT_SECRET_KEY = "super-secret"  # Use environment variables for security
    JWT_TOKEN_LOCATION = ['cookies']  # Enable cookies for JWT
    JWT_COOKIE_SECURE = False  # Set to True in production (requires HTTPS)
    JWT_ACCESS_COOKIE_NAME = 'access_token'  # Name of the access token cookie
    JWT_COOKIE_CSRF_PROTECT = False  # Disable CSRF for simplicity (consider enabling in production)

