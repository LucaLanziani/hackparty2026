"""Flask application factory."""
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configuration - using postgresql+psycopg for psycopg3
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'postgresql+psycopg://localhost/ticket_classification'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Import models to ensure they're registered with SQLAlchemy
    with app.app_context():
        from app.models import ticket
    
    # Register blueprints
    from app.routes.tickets import bp as tickets_bp
    app.register_blueprint(tickets_bp, url_prefix='/api')
    
    return app
