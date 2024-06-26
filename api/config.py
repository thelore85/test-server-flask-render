import os
from datetime import timedelta

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_COOKIE_SECURE = False
    JWT_SECRET_KEY = os.getenv("JWT_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = 43200