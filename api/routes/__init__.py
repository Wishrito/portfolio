from flask import Blueprint, Flask 
from .api import api_bp

def register_blueprints(app: Flask):
    app.register_blueprint(api_bp, url_prefix="/api")


