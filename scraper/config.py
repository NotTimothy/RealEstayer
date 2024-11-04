# config.py
import os
from dotenv import load_dotenv

HOST="192.168.1.71"
USER="root"
PASSWD="Babycakes15!"
DB="airbnb"

# Load environment variables from .env file
load_dotenv()

class Config:
    # Common configurations
    DB_NAME = "airbnb"
    COLLECTION_NAME = "listings"

class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    HOST = os.getenv('DEV_HOST', '127.0.0.1')  # Replace with your local IP
    PORT = int(os.getenv('DEV_PORT', 5000))
    CORS_ORIGINS = [
        'http://localhost:6969',
        'http://127.0.0.1:6969'  # Replace with your local IP
    ]

class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    HOST = os.getenv('PROD_HOST', '0.0.0.0')
    PORT = int(os.getenv('PROD_PORT', 5000))
    CORS_ORIGINS = [
        os.getenv('PROD_DOMAIN', 'https://realestayer.duocore.dev')
    ]

# Configure based on environment
env = os.getenv('FLASK_ENV', 'development')
config = ProductionConfig if env == 'production' else DevelopmentConfig

