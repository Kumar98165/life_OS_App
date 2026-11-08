import time
import uuid
import logging
from flask import Flask, request, g

logger = logging.getLogger("lifeos.request")
def setup_request_logging(app: Flask) -> None:
    """Attach request tracing, execution duration, and structured logging hooks."""

    # Set root logger level
    log_level = app.config.get("LOG_LEVEL", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    )

    @app.before_request
    def before_request():
        g.start_time = time.time()
        # Extract or generate unique Request ID
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        g.request_id = request_id

    @app.after_request
    def after_request(response):
        duration_ms = round((time.time() - getattr(g, "start_time", time.time())) * 1000, 2)
        request_id = getattr(g, "request_id", "none")
        response.headers["X-Request-ID"] = request_id

        # Redact query params / sensitive paths if needed
        path = request.path
        method = request.method
        status_code = response.status_code

        # Avoid spamming log on health checks if healthy
        if path in ["/api/v1/health"] and status_code == 200:
            return response

        logger.info(
            f"req_id={request_id} method={method} path={path} status={status_code} duration={duration_ms}ms"
        )
        return response

