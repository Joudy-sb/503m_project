import os

class Config:
    # File upload configuration
    #UPLOAD_FOLDER = os.path.join(os.getcwd(), 'path')  # Define a safe default path
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit

    # Database configuration
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345@localhost:3306/ecommerce_platform'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
