class LifeOSException(Exception):
    """Base domain exception for LifeOS."""
    status_code = 500
    error_code = "INTERNAL_ERROR"
    message = "An unexpected error occurred"

    def __init__(self, message=None, payload=None, status_code=None, error_code=None):
        if message is not None:
            self.message = message
        if status_code is not None:
            self.status_code = status_code
        if error_code is not None:
            self.error_code = error_code
        self.payload = payload
        super().__init__(self.message)

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["success"] = False
        rv["status"] = "error"
        rv["message"] = self.message
        rv["code"] = self.error_code
        return rv


class NotFoundException(LifeOSException):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "Resource not found"


class BadRequestException(LifeOSException):
    status_code = 400
    error_code = "BAD_REQUEST"
    message = "Bad request"



class ValidationException(LifeOSException):
    status_code = 422
    error_code = "VALIDATION_ERROR"
    message = "Validation failed"


class UnauthorizedException(LifeOSException):
    status_code = 401
    error_code = "AUTHENTICATION_ERROR"
    message = "Authentication required"


class ForbiddenException(LifeOSException):
    status_code = 403
    error_code = "AUTHORIZATION_ERROR"
    message = "Access denied"


class ConflictException(LifeOSException):
    status_code = 409
    error_code = "CONFLICT"
    message = "Resource conflict detected"


class IntegrityException(LifeOSException):
    status_code = 409
    error_code = "INTEGRITY_ERROR"
    message = "Database integrity constraint violated"


class RateLimitException(LifeOSException):
    status_code = 429
    error_code = "RATE_LIMIT_EXCEEDED"
    message = "Rate limit exceeded"
