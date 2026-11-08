import pytest
from app import create_app
from app.config import ProductionConfig, DevelopmentConfig, TestingConfig


def test_development_config():
    """Verify development configuration attributes."""
    app = create_app("development")
    assert app.config["DEBUG"] is True
    assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
    assert app.config["MAX_CONTENT_LENGTH"] == 10 * 1024 * 1024


def test_testing_config():
    """Verify testing configuration isolates DB and disables rate limits."""
    app = create_app("testing")
    assert app.config["TESTING"] is True
    assert app.config["RATELIMIT_ENABLED"] is False


def test_production_config_validation():
    """Verify production configuration enforces secure secrets at startup."""
    # Temporarily set dummy insecure key
    orig_key = ProductionConfig.SECRET_KEY
    orig_db = ProductionConfig.SQLALCHEMY_DATABASE_URI
    try:
        ProductionConfig.SECRET_KEY = "dev-secret-key-change-in-production-32chars"
        ProductionConfig.SQLALCHEMY_DATABASE_URI = None
        with pytest.raises(ValueError) as exc:
            ProductionConfig.validate_production()
        assert "DATABASE_URL" in str(exc.value)
    finally:
        ProductionConfig.SECRET_KEY = orig_key
        ProductionConfig.SQLALCHEMY_DATABASE_URI = orig_db

