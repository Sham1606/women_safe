"""Main application entry point"""

from backend import create_app
import os

# Create Flask app
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # Get port from environment or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Get debug mode
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    print(f"\n{'='*60}")
    print(f"Women Safety System Backend")
    print(f"{'='*60}")
    print(f"Environment: {config_name}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    print(f"Debug Mode: {debug}")
    print(f"Running on: http://localhost:{port}")
    print(f"{'='*60}\n")
    
    # Run app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )