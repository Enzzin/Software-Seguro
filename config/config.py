# config/config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

COGNITO_USER_POOL_ID      = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID     = os.getenv("COGNITO_APP_CLIENT_ID")
COGNITO_APP_CLIENT_SECRET = os.getenv("COGNITO_APP_CLIENT_SECRET")
COGNITO_REGION            = os.getenv("COGNITO_REGION", "us-east-1")

FLASK_SECRET_KEY          = os.getenv("FLASK_SECRET_KEY")

class Config:
    SECRET_KEY = FLASK_SECRET_KEY

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or \
        "postgresql://brazuca:password@localhost:5432/brazucaphish"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Cognito
    COGNITO_USER_POOL_ID      = COGNITO_USER_POOL_ID
    COGNITO_APP_CLIENT_ID     = COGNITO_APP_CLIENT_ID
    COGNITO_APP_CLIENT_SECRET = COGNITO_APP_CLIENT_SECRET
    COGNITO_REGION            = COGNITO_REGION

    # E-mail
    MAIL_SERVER   = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT     = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS  = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL  = os.getenv("MAIL_USE_SSL", "false").lower() == "true"  
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@brazucaphish.com")

    # Ollama
    OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

    PUBLIC_URL = os.getenv("PUBLIC_URL", "http://localhost:5000")


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


# Dicionário usado pelo factory em app.py
config = {
    "default": Config,
    "production": ProductionConfig,
}
