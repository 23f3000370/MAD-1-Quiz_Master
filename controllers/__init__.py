from flask import Blueprint

# Import all blueprints
from .auth import auth_bp
from .admin import admin_bp
from .user import user_bp

# Function to register all blueprints
def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
