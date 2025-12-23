from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from backend.models import db

migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    app.config.from_object(config)
    
    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register Blueprints
    from backend.views import views_bp
    app.register_blueprint(views_bp)

    from backend.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from backend.devices import device_bp
    app.register_blueprint(device_bp, url_prefix='/api/device')

    from backend.alerts import alert_bp
    app.register_blueprint(alert_bp, url_prefix='/api/alerts')

    from backend.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # Static route for Evidence
    @app.route('/static/evidence/<path:filename>')
    def serve_evidence(filename):
        return send_from_directory(config.EVIDENCE_DIR, filename)

    # Create tables if not exists
    with app.app_context():
        db.create_all()
        
    return app
