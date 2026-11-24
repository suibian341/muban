import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'chenghai-b2b-secret-key-change-in-production')

    # ── MySQL ──
    DB_USER = os.getenv('MYSQL_USER', 'root')
    DB_PASS = os.getenv('MYSQL_PASSWORD', 'root')
    DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
    DB_PORT = os.getenv('MYSQL_PORT', '3306')
    DB_NAME = os.getenv('MYSQL_DB', 'chenghai_b2b')
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── JWT ──
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-chenghai-b2b-secret-key-2025-prod')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # ── Upload ──
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
