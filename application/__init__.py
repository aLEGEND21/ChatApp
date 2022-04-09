from flask import Flask


def create_app():
    """Create the core application."""
    app = Flask(__name__)

    with app.app_context():
        # Imports
        from .views import view
        from .api import api

        # Register routes
        app.register_blueprint(view, url_prefix="/")
        app.register_blueprint(api, url_prefix="/api")

        return app