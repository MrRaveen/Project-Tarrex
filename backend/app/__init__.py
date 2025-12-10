from flask import Flask, current_app

from .modules.ingestionLayer.scheduler import addJobs
from .routes.testRoutes import user_bp
from .modules.ingestionLayer.scheduler import scheduler, addJobs


def create_app():
    app = Flask(__name__)
    # Configuration
    app.config.from_pyfile('config.py', silent=True)
    app.register_blueprint(user_bp)
    
    # Start scheduler
    with app.app_context():
        if not scheduler.running:
            scheduler.start()
            addJobs()
    
    return app

# Create the app instance - THIS IS WHAT GUNICORN NEEDS
app = create_app()

if __name__ == '__main__':
    # This runs when you do "python -m app" directly
    app.run(debug=True, host='0.0.0.0', port=5000)
