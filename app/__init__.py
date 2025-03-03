from flask import Flask
from app.routes import main  # Importing the routes Blueprint

def create_app():
    """Application Factory Pattern: Creates and configures a Flask app instance"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("config.Config")

    # Register Blueprints (Routes)
    app.register_blueprint(main)

    return app  # Returns a Flask app instance
