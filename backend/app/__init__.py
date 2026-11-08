import os
from flask import Flask
from app.config import config_by_name, ProductionConfig
from app.extensions import db, migrate, jwt, cors, limiter
from app.core.handlers import register_error_handlers
from app.core.logging import setup_request_logging
from app.core.security import init_token_blocklist
from app.api import register_api_blueprints
import app.models  # Ensure models are loaded for Alembic / SQLAlchemy


def create_app(config_name: str = None) -> Flask:
    """Application Factory for LifeOS Backend API."""
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    app = Flask(__name__)
    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)

    # Validate production environment if running in production mode
    if config_name == "production":
        ProductionConfig.validate_production()

    # Configure CORS
    allowed_origins = app.config.get("CORS_ALLOWED_ORIGINS", "*")
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        supports_credentials=True
    )

    # Initialize database and extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # Initialize security blocklist and structured request logging
    init_token_blocklist(jwt)
    setup_request_logging(app)

    # Register centralized error handling
    register_error_handlers(app)

    # Register API blueprints
    register_api_blueprints(app)

    # Register custom CLI commands
    from app.commands import register_commands
    register_commands(app)

    return app
