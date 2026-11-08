import logging
from flask import Flask, request
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException
from flask_limiter.errors import RateLimitExceeded
from app.extensions import jwt
from app.core.exceptions import LifeOSException
from app.core.response import error_response

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    """Register centralized error handlers and JWT callbacks for the Flask app."""

    @app.errorhandler(LifeOSException)
    def handle_lifeos_exception(err: LifeOSException):
        logger.warning(f"Domain exception: {err.message} (code: {err.error_code}, status: {err.status_code})")
        errors = err.payload if isinstance(err.payload, list) else ([err.payload] if err.payload else [])
        return error_response(
            message=err.message,
            status_code=err.status_code,
            errors=errors,
            code=err.error_code
        )

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation(err: ValidationError):
        formatted_errors = [
            {"field": ".".join(str(loc) for loc in e.get("loc", [])), "message": e.get("msg")}
            for e in err.errors()
        ]
        logger.info(f"Pydantic validation error on {request.path}: {formatted_errors}")
        return error_response(
            message="Input validation failed",
            status_code=422,
            errors=formatted_errors,
            code="VALIDATION_ERROR"
        )

    @app.errorhandler(IntegrityError)
    def handle_database_integrity(err: IntegrityError):
        logger.warning(f"Database integrity conflict: {str(err.orig) if hasattr(err, 'orig') else str(err)}")
        return error_response(
            message="Database constraint violation or duplicate record detected.",
            status_code=409,
            code="INTEGRITY_ERROR"
        )

    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(err: SQLAlchemyError):
        logger.error(f"SQLAlchemy error on {request.path}: {str(err)}", exc_info=True)
        return error_response(
            message="A database operation error occurred.",
            status_code=500,
            code="DATABASE_ERROR"
        )

    @app.errorhandler(RateLimitExceeded)
    def handle_rate_limit(err: RateLimitExceeded):
        logger.warning(f"Rate limit exceeded on {request.path} by {request.remote_addr}")
        return error_response(
            message="Rate limit exceeded. Please retry after a brief delay.",
            status_code=429,
            code="RATE_LIMIT_EXCEEDED"
        )

    @app.errorhandler(HTTPException)
    def handle_http_exception(err: HTTPException):
        logger.info(f"HTTP exception {err.code} on {request.path}: {err.description}")
        error_code = "NOT_FOUND" if err.code == 404 else ("METHOD_NOT_ALLOWED" if err.code == 405 else "HTTP_ERROR")
        return error_response(
            message=err.description or "HTTP error occurred",
            status_code=err.code or 500,
            code=error_code
        )

    @app.errorhandler(Exception)
    def handle_unexpected_exception(err: Exception):
        logger.error(f"Unhandled server exception on {request.path}: {str(err)}", exc_info=True)
        return error_response(
            message="An unexpected internal server error occurred. Please try again later.",
            status_code=500,
            code="INTERNAL_ERROR"
        )

    # JWT Callbacks for standardized JSON error envelopes
    @jwt.expired_token_loader
    def handle_expired_token(jwt_header, jwt_payload):
        return error_response(
            message="Token has expired. Please refresh your session.",
            status_code=401,
            code="TOKEN_EXPIRED"
        )

    @jwt.invalid_token_loader
    def handle_invalid_token(reason):
        return error_response(
            message=f"Invalid authentication token: {reason}",
            status_code=401,
            code="INVALID_TOKEN"
        )

    @jwt.unauthorized_loader
    def handle_missing_token(reason):
        return error_response(
            message=f"Missing Authorization header: {reason}",
            status_code=401,
            code="AUTHENTICATION_REQUIRED"
        )

    @jwt.revoked_token_loader
    def handle_revoked_token(jwt_header, jwt_payload):
        return error_response(
            message="Token has been revoked. Please log in again.",
            status_code=401,
            code="TOKEN_REVOKED"
        )
