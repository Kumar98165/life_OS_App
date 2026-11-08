"""LifeOS - Administrative CLI Commands.

Provides safe, out-of-band operational controls for establishing administrator
roles without public elevation vectors.
"""
import click
from flask import Flask
from app.extensions import db
from app.models.user import User


def register_commands(app: Flask) -> None:
    """Register custom Click commands with the Flask CLI."""

    @app.cli.group("auth")
    def auth_group():
        """User identity and authorization management commands."""
        pass

    @auth_group.command("make-admin")
    @click.argument("email")
    def make_admin(email: str):
        """Promote an existing user to administrator role by email."""
        cleaned_email = email.strip().lower()
        user = User.query.filter_by(email=cleaned_email).first()
        if not user:
            click.echo(f"Error: User with email '{cleaned_email}' was not found.", err=True)
            return

        user.role = "admin"
        db.session.commit()
        click.echo(f"Success: User '{cleaned_email}' is now an administrator (role='admin').")

    @auth_group.command("revoke-admin")
    @click.argument("email")
    def revoke_admin(email: str):
        """Demote an administrator to normal user role by email."""
        cleaned_email = email.strip().lower()
        user = User.query.filter_by(email=cleaned_email).first()
        if not user:
            click.echo(f"Error: User with email '{cleaned_email}' was not found.", err=True)
            return

        user.role = "user"
        db.session.commit()
        click.echo(f"Success: Administrator '{cleaned_email}' demoted to user (role='user').")

