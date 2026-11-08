import logging
from flask import Blueprint
from sqlalchemy import text
from app.extensions import db
from app.core.response import api_response, error_response

logger = logging.getLogger(__name__)
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """Liveness probe: verifies service process is running."""
    return api_response(
        data={
            "status": "healthy",
            "service": "LifeOS Backend API",
            "version": "1.0.0"
        },
        message="Service is operational"
    )


@health_bp.route("/ready", methods=["GET"])
def readiness_check():
    """Readiness probe: verifies live PostgreSQL database connectivity."""
    try:
        db.session.execute(text("SELECT 1"))
        return api_response(
            data={
                "status": "ready",
                "database": "connected",
                "service": "LifeOS Backend API"
            },
            message="Service and database are ready"
        )
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}", exc_info=True)
        return error_response(
            message="Database connectivity check failed",
            status_code=503,
            errors=[{"detail": "Unable to execute query on database"}],
            code="SERVICE_UNAVAILABLE"
        )
