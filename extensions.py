# extensions.py
"""
Initialize Flask extensions to avoid circular imports
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import logging
from logging.handlers import RotatingFileHandler
import os

# Database
db = SQLAlchemy()
migrate = Migrate()


# Email
mail = Mail()

def init_extensions(app):
    """Initialize all Flask extensions"""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)

    # Email
    mail.init_app(app)
    
    # Logging
    init_logging(app)

def init_logging(app):
    """Configure application logging"""
    
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Set up file handler with rotation
        file_handler = RotatingFileHandler(
            'logs/brazucaphish.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('BrazucaPhish startup')