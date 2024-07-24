import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', '9cbf4dabadd42ec4c264cbda28af621e')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///users.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
