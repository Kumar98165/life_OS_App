"""LifeOS API Routing Module."""
from flask import Flask
from app.blueprints.health import health_bp
from app.blueprints.auth import auth_bp
from app.blueprints.users import users_bp
from app.blueprints.tasks import tasks_bp
from app.blueprints.planner import planner_bp
from app.blueprints.goals import goals_bp
from app.blueprints.habits import habits_bp
from app.blueprints.finance import finance_bp
from app.blueprints.notifications import notifications_bp
from app.blueprints.analytics import analytics_bp
from app.blueprints.automations import automations_bp
from app.blueprints.personalization import personalization_bp

def register_api_blueprints(app: Flask) -> None:
    """Register all API route blueprints to the Flask application."""
    app.register_blueprint(health_bp, url_prefix="/api/v1")
    app.register_blueprint(auth_bp, url_prefix="/api/v1/auth")
    app.register_blueprint(users_bp, url_prefix="/api/v1/users")
    app.register_blueprint(tasks_bp, url_prefix="/api/v1/tasks")
    app.register_blueprint(planner_bp, url_prefix="/api/v1/planner")
    app.register_blueprint(goals_bp, url_prefix="/api/v1/goals")
    app.register_blueprint(habits_bp, url_prefix="/api/v1/habits")
    app.register_blueprint(finance_bp, url_prefix="/api/v1/finance")
    app.register_blueprint(notifications_bp, url_prefix="/api/v1/notifications")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(automations_bp, url_prefix="/api/v1/automations")
    app.register_blueprint(personalization_bp, url_prefix="/api/v1/personalization")
 
