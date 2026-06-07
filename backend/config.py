import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/saas_financeiro')
    SQLALCHEMY_TRACK_MODIFICATIONS = False