from typing import Any, Optional
from flask import jsonify, Response


def api_response(
    data: Optional[Any] = None,
    message: str = "Operation successful",
    status_code: int = 200,
    meta: Optional[dict] = None
) -> Response:
    """Standardized successful API response envelope."""
    payload = {
        "success": True,
        "status": "success",
        "message": message,
        "data": data if data is not None else {},
        "meta": meta
    }
    response = jsonify(payload)
    response.status_code = status_code
    return response


def error_response(
    message: str = "An error occurred",
    status_code: int = 400,
    errors: Optional[Any] = None,
    code: str = "ERROR"
) -> Response:
    """Standardized error API response envelope."""
    payload = {
        "success": False,
        "status": "error",
        "message": message,
        "errors": errors if errors is not None else [],
        "code": code
    }
    response = jsonify(payload)
    response.status_code = status_code
    return response
