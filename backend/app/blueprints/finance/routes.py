"""LifeOS - Personal Finance Blueprint Routes.

REST endpoints for financial accounts, transactions, categories, budgets,
savings goals, financial dashboard summaries, and AI insights.
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app.schemas.finance import (
    CreateAccountRequest,
    UpdateAccountRequest,
    CreateCategoryRequest,
    UpdateCategoryRequest,
    CreateTransactionRequest,
    UpdateTransactionRequest,
    CreateBudgetRequest,
    CreateSavingsGoalRequest,
    UpdateSavingsGoalRequest,
    AddSavingsContributionRequest,
)
from app.services.finance_service import FinanceService
from app.core.response import api_response

finance_bp = Blueprint("finance", __name__)
finance_service = FinanceService()


# ---------------------------------------------------------
# Account Endpoints
# ---------------------------------------------------------

@finance_bp.route("/accounts", methods=["POST"])
@jwt_required()
def create_account():
    """Create a new financial account."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateAccountRequest(**json_data)

    account = finance_service.create_account(
        user_id=user_id,
        name=validated.name,
        account_type=validated.account_type,
        balance=validated.balance,
        currency=validated.currency,
        color_hex=validated.color_hex or "#6C63FF",
        icon=validated.icon or "wallet",
        is_default=validated.is_default or False
    )

    return api_response(
        data={"account": account.to_dict()},
        message="Financial account created successfully",
        status_code=201
    )


@finance_bp.route("/accounts", methods=["GET"])
@jwt_required()
def list_accounts():
    """List financial accounts for authenticated user."""
    user_id = get_jwt_identity()
    include_archived = request.args.get("include_archived", "false").lower() == "true"
    accounts = finance_service.list_accounts(user_id=user_id, include_archived=include_archived)

    return api_response(
        data={"accounts": [a.to_dict() for a in accounts]},
        message="Accounts retrieved successfully"
    )


@finance_bp.route("/accounts/<account_id>", methods=["GET"])
@jwt_required()
def get_account(account_id: str):
    """Retrieve details of a specific financial account."""
    user_id = get_jwt_identity()
    account = finance_service.get_account(account_id=account_id, user_id=user_id)

    return api_response(
        data={"account": account.to_dict()},
        message="Account retrieved successfully"
    )


@finance_bp.route("/accounts/<account_id>", methods=["PATCH"])
@jwt_required()
def update_account(account_id: str):
    """Update financial account fields."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateAccountRequest(**json_data)

    updates = validated.model_dump(exclude_unset=True)
    account = finance_service.update_account(account_id=account_id, user_id=user_id, updates=updates)

    return api_response(
        data={"account": account.to_dict()},
        message="Account updated successfully"
    )


@finance_bp.route("/accounts/<account_id>/archive", methods=["POST"])
@jwt_required()
def archive_account(account_id: str):
    """Archive a financial account."""
    user_id = get_jwt_identity()
    account = finance_service.archive_account(account_id=account_id, user_id=user_id)

    return api_response(
        data={"account": account.to_dict()},
        message="Account archived successfully"
    )


# ---------------------------------------------------------
# Category Endpoints
# ---------------------------------------------------------

@finance_bp.route("/categories", methods=["GET"])
@jwt_required()
def list_categories():
    """List categories for authenticated user (including system defaults)."""
    user_id = get_jwt_identity()
    category_type = request.args.get("type")
    categories = finance_service.list_categories(user_id=user_id, category_type=category_type)

    return api_response(
        data={"categories": [c.to_dict() for c in categories]},
        message="Categories retrieved successfully"
    )


@finance_bp.route("/categories", methods=["POST"])
@jwt_required()
def create_category():
    """Create a new custom category."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateCategoryRequest(**json_data)

    category = finance_service.create_category(
        user_id=user_id,
        name=validated.name,
        category_type=validated.category_type,
        icon=validated.icon,
        color_hex=validated.color_hex or "#6C63FF",
        monthly_budget=validated.monthly_budget
    )

    return api_response(
        data={"category": category.to_dict()},
        message="Category created successfully",
        status_code=201
    )


@finance_bp.route("/categories/<category_id>", methods=["PATCH"])
@jwt_required()
def update_category(category_id: str):
    """Update custom category."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateCategoryRequest(**json_data)

    updates = validated.model_dump(exclude_unset=True)
    category = finance_service.update_category(category_id=category_id, user_id=user_id, updates=updates)

    return api_response(
        data={"category": category.to_dict()},
        message="Category updated successfully"
    )


@finance_bp.route("/categories/<category_id>", methods=["DELETE"])
@jwt_required()
def delete_category(category_id: str):
    """Delete a custom category."""
    user_id = get_jwt_identity()
    finance_service.delete_category(category_id=category_id, user_id=user_id)

    return api_response(
        data=None,
        message="Category deleted successfully"
    )


# ---------------------------------------------------------
# Transaction Endpoints
# ---------------------------------------------------------

@finance_bp.route("/transactions", methods=["POST"])
@jwt_required()
def create_transaction():
    """Create a new income, expense, or transfer transaction."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateTransactionRequest(**json_data)

    tx = finance_service.create_transaction(
        user_id=user_id,
        account_id=validated.account_id,
        amount=validated.amount,
        transaction_type=validated.transaction_type,
        description=validated.description,
        category_id=validated.category_id,
        transaction_date=validated.transaction_date,
        is_recurring=validated.is_recurring or False
    )

    return api_response(
        data={"transaction": tx.to_dict()},
        message="Transaction recorded successfully",
        status_code=201
    )


@finance_bp.route("/transactions", methods=["GET"])
@jwt_required()
def list_transactions():
    """List transactions with multi-criteria filtering and pagination."""
    user_id = get_jwt_identity()
    account_id = request.args.get("account_id")
    category_id = request.args.get("category_id")
    transaction_type = request.args.get("type")
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")
    limit = request.args.get("limit", 50, type=int)
    offset = request.args.get("offset", 0, type=int)

    date_from = datetime.fromisoformat(date_from_str) if date_from_str else None
    date_to = datetime.fromisoformat(date_to_str) if date_to_str else None

    result = finance_service.list_transactions(
        user_id=user_id,
        account_id=account_id,
        category_id=category_id,
        transaction_type=transaction_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset
    )

    return api_response(
        data=result,
        message="Transactions retrieved successfully"
    )


@finance_bp.route("/transactions/<transaction_id>", methods=["GET"])
@jwt_required()
def get_transaction(transaction_id: str):
    """Retrieve details of a transaction."""
    user_id = get_jwt_identity()
    tx = finance_service.get_transaction(transaction_id=transaction_id, user_id=user_id)

    return api_response(
        data={"transaction": tx.to_dict()},
        message="Transaction details retrieved successfully"
    )


@finance_bp.route("/transactions/<transaction_id>", methods=["PATCH"])
@jwt_required()
def update_transaction(transaction_id: str):
    """Update transaction fields."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateTransactionRequest(**json_data)

    updates = validated.model_dump(exclude_unset=True)
    tx = finance_service.update_transaction(transaction_id=transaction_id, user_id=user_id, updates=updates)

    return api_response(
        data={"transaction": tx.to_dict()},
        message="Transaction updated successfully"
    )


@finance_bp.route("/transactions/<transaction_id>", methods=["DELETE"])
@jwt_required()
def delete_transaction(transaction_id: str):
    """Soft-delete a transaction and reverse account balance."""
    user_id = get_jwt_identity()
    finance_service.delete_transaction(transaction_id=transaction_id, user_id=user_id)

    return api_response(
        data=None,
        message="Transaction deleted successfully"
    )


# ---------------------------------------------------------
# Budget Endpoints
# ---------------------------------------------------------

@finance_bp.route("/budgets", methods=["POST"])
@jwt_required()
def set_budget():
    """Create or update monthly budget for a category or overall."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateBudgetRequest(**json_data)

    budget = finance_service.set_budget(
        user_id=user_id,
        month=validated.month,
        amount=validated.amount,
        category_id=validated.category_id,
        currency=validated.currency or "USD"
    )

    return api_response(
        data={"budget": budget.to_dict()},
        message="Budget configured successfully",
        status_code=201
    )


@finance_bp.route("/budgets", methods=["GET"])
@jwt_required()
def list_budgets():
    """List budgets for given month YYYY-MM with live spent/remaining tracking."""
    user_id = get_jwt_identity()
    month = request.args.get("month", datetime.now().strftime("%Y-%m"))

    budgets = finance_service.list_budgets_with_utilization(user_id=user_id, month=month)

    return api_response(
        data={"month": month, "budgets": budgets},
        message="Budgets retrieved successfully"
    )


# ---------------------------------------------------------
# Savings Goals Endpoints
# ---------------------------------------------------------

@finance_bp.route("/savings-goals", methods=["POST"])
@jwt_required()
def create_savings_goal():
    """Create a new savings goal."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = CreateSavingsGoalRequest(**json_data)

    goal = finance_service.create_savings_goal(
        user_id=user_id,
        title=validated.title,
        target_amount=validated.target_amount,
        initial_deposit=validated.initial_deposit or 0,
        target_date=validated.target_date,
        currency=validated.currency or "USD",
        color_hex=validated.color_hex or "#6C63FF",
        icon=validated.icon or "flag",
        notes=validated.notes
    )

    return api_response(
        data={"savings_goal": goal.to_dict()},
        message="Savings goal created successfully",
        status_code=201
    )


@finance_bp.route("/savings-goals", methods=["GET"])
@jwt_required()
def list_savings_goals():
    """List savings goals for authenticated user."""
    user_id = get_jwt_identity()
    status = request.args.get("status")
    goals = finance_service.list_savings_goals(user_id=user_id, status=status)

    return api_response(
        data={"savings_goals": goals},
        message="Savings goals retrieved successfully"
    )


@finance_bp.route("/savings-goals/<goal_id>", methods=["GET"])
@jwt_required()
def get_savings_goal(goal_id: str):
    """Retrieve savings goal details."""
    user_id = get_jwt_identity()
    goal = finance_service.get_savings_goal(goal_id=goal_id, user_id=user_id)

    return api_response(
        data={"savings_goal": goal.to_dict()},
        message="Savings goal retrieved successfully"
    )


@finance_bp.route("/savings-goals/<goal_id>", methods=["PATCH"])
@jwt_required()
def update_savings_goal(goal_id: str):
    """Update savings goal fields."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = UpdateSavingsGoalRequest(**json_data)

    updates = validated.model_dump(exclude_unset=True)
    goal = finance_service.update_savings_goal(goal_id=goal_id, user_id=user_id, updates=updates)

    return api_response(
        data={"savings_goal": goal.to_dict()},
        message="Savings goal updated successfully"
    )


@finance_bp.route("/savings-goals/<goal_id>/contribute", methods=["POST"])
@jwt_required()
def add_savings_contribution(goal_id: str):
    """Add a funds contribution toward a savings goal."""
    user_id = get_jwt_identity()
    json_data = request.get_json(silent=True) or {}
    validated = AddSavingsContributionRequest(**json_data)

    contribution = finance_service.add_savings_contribution(
        goal_id=goal_id,
        user_id=user_id,
        amount=validated.amount,
        account_id=validated.account_id,
        note=validated.note,
        deduct_from_account=validated.deduct_from_account or False
    )

    return api_response(
        data={"contribution": contribution.to_dict()},
        message="Contribution added successfully",
        status_code=201
    )


@finance_bp.route("/savings-goals/<goal_id>/contributions", methods=["GET"])
@jwt_required()
def list_savings_contributions(goal_id: str):
    """List contribution ledger for a savings goal."""
    user_id = get_jwt_identity()
    contributions = finance_service.list_savings_contributions(goal_id=goal_id, user_id=user_id)

    return api_response(
        data={"contributions": contributions},
        message="Savings contributions retrieved successfully"
    )


# ---------------------------------------------------------
# Dashboard & Local AI Insights Endpoints (Phase 4, 6 & 7)
# ---------------------------------------------------------

@finance_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def get_finance_dashboard():
    """Retrieve full financial dashboard overview metrics."""
    user_id = get_jwt_identity()
    month = request.args.get("month")

    dashboard_data = finance_service.get_dashboard_summary(user_id=user_id, month=month)

    return api_response(
        data=dashboard_data,
        message="Finance dashboard data retrieved successfully"
    )


@finance_bp.route("/insights", methods=["GET"])
@jwt_required()
def get_finance_insights():
    """Retrieve verified read-only AI financial observations from local Ollama model."""
    user_id = get_jwt_identity()
    month = request.args.get("month")

    insights_data = finance_service.get_ai_insights(user_id=user_id, month=month)

    return api_response(
        data=insights_data,
        message="Financial insights retrieved successfully"
    )

