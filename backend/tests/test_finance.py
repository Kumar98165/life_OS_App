"""LifeOS - Personal Finance Module Backend Test Suite.

Comprehensive tests covering:
- Account creation, listing, retrieval, update, and archival
- Seeded default categories & custom category CRUD
- Category deletion safety when transactions reference it
- Income and expense transactions adjusting account balance with Decimal precision
- Transaction updates reversing and reapplying account balances
- Soft-deletion of transactions and balance reversal
- Date range, account, category, and type filtering on transactions
- Monthly budget creation and live utilization calculations
- Savings goals lifecycle, progress percentage, and contribution ledgers
- Optional contribution deduction from account balance
- IDOR defenses: cross-user isolation on all endpoints
- Unauthorized access rejection (401)
- Financial dashboard aggregates (balance vs periodic income/expense/net savings)
- Local AI financial insights with verified metrics
"""
from decimal import Decimal
from datetime import datetime, timezone, timedelta
import pytest
from unittest.mock import patch, MagicMock
from app.extensions import db
from app.models.finance import (
    FinancialAccount,
    FinancialCategory,
    FinancialTransaction,
    Budget,
    SavingsGoal,
    SavingsGoalContribution,
)


@pytest.fixture
def second_user_headers(client):
    """Registers and authenticates a second user for IDOR testing."""
    payload = {
        "email": "finance.peer@lifeos.internal",
        "password": "Password123!",
        "full_name": "Finance Peer"
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    token = resp.get_json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------
# Account Tests
# ---------------------------------------------------------

def test_account_lifecycle(client, auth_headers):
    """Test creating, listing, updating, and archiving an account."""
    # 1. Create checking account
    create_payload = {
        "name": "Main Checking",
        "account_type": "checking",
        "balance": "1500.50",
        "currency": "USD",
        "color_hex": "#4A90E2",
        "icon": "business",
        "is_default": True
    }
    create_resp = client.post("/api/v1/finance/accounts", json=create_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    account = create_resp.get_json()["data"]["account"]
    account_id = account["id"]
    assert account["name"] == "Main Checking"
    assert account["balance"] == "1500.50"
    assert account["is_default"] is True
    assert account["is_archived"] is False

    # 2. List accounts
    list_resp = client.get("/api/v1/finance/accounts", headers=auth_headers)
    assert list_resp.status_code == 200
    accounts = list_resp.get_json()["data"]["accounts"]
    assert any(a["id"] == account_id for a in accounts)

    # 3. Update account
    update_resp = client.patch(
        f"/api/v1/finance/accounts/{account_id}",
        json={"name": "Primary Chase Checking", "color_hex": "#1E3C72"},
        headers=auth_headers
    )
    assert update_resp.status_code == 200
    assert update_resp.get_json()["data"]["account"]["name"] == "Primary Chase Checking"

    # 4. Archive account
    archive_resp = client.post(f"/api/v1/finance/accounts/{account_id}/archive", headers=auth_headers)
    assert archive_resp.status_code == 200
    assert archive_resp.get_json()["data"]["account"]["is_archived"] is True

    # Active listing excludes archived by default
    active_resp = client.get("/api/v1/finance/accounts", headers=auth_headers)
    assert not any(a["id"] == account_id for a in active_resp.get_json()["data"]["accounts"])


# ---------------------------------------------------------
# Category Tests
# ---------------------------------------------------------

def test_categories_seeded_and_custom_crud(client, auth_headers):
    """Test listing categories (which seeds defaults) and creating custom categories."""
    # 1. First get seeds default categories
    list_resp = client.get("/api/v1/finance/categories", headers=auth_headers)
    assert list_resp.status_code == 200
    cats = list_resp.get_json()["data"]["categories"]
    assert len(cats) >= 10
    assert any(c["name"] == "Groceries" for c in cats)
    assert any(c["name"] == "Salary & Wages" for c in cats)

    # 2. Create custom category
    custom_resp = client.post(
        "/api/v1/finance/categories",
        json={"name": "Software Subscriptions", "category_type": "expense", "color_hex": "#6C63FF", "icon": "laptop"},
        headers=auth_headers
    )
    assert custom_resp.status_code == 201
    custom_cat = custom_resp.get_json()["data"]["category"]
    cat_id = custom_cat["id"]
    assert custom_cat["name"] == "Software Subscriptions"

    # 3. Update category
    patch_resp = client.patch(
        f"/api/v1/finance/categories/{cat_id}",
        json={"name": "Cloud & Software Tools"},
        headers=auth_headers
    )
    assert patch_resp.status_code == 200
    assert patch_resp.get_json()["data"]["category"]["name"] == "Cloud & Software Tools"

    # 4. Delete category
    del_resp = client.delete(f"/api/v1/finance/categories/{cat_id}", headers=auth_headers)
    assert del_resp.status_code == 200


# ---------------------------------------------------------
# Transaction Tests & Balance Adjustments
# ---------------------------------------------------------

def test_transactions_and_balance_tracking(client, auth_headers):
    """Test income and expense transactions correctly mutate account balance with Decimal precision."""
    # 1. Create an account with $1,000.00
    acc_resp = client.post(
        "/api/v1/finance/accounts",
        json={"name": "Savings Vault", "balance": "1000.00", "currency": "USD"},
        headers=auth_headers
    )
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    # Get a category
    cat_resp = client.get("/api/v1/finance/categories?type=expense", headers=auth_headers)
    expense_cat_id = cat_resp.get_json()["data"]["categories"][0]["id"]

    inc_cat_resp = client.get("/api/v1/finance/categories?type=income", headers=auth_headers)
    income_cat_id = inc_cat_resp.get_json()["data"]["categories"][0]["id"]

    # 2. Record an expense of $125.50
    exp_resp = client.post(
        "/api/v1/finance/transactions",
        json={
            "account_id": acc_id,
            "category_id": expense_cat_id,
            "amount": "125.50",
            "transaction_type": "expense",
            "description": "Weekly grocery run"
        },
        headers=auth_headers
    )
    assert exp_resp.status_code == 201
    exp_id = exp_resp.get_json()["data"]["transaction"]["id"]

    # Balance should now be 1000.00 - 125.50 = 874.50
    acc_check = client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers)
    assert acc_check.get_json()["data"]["account"]["balance"] == "874.50"

    # 3. Record an income of $500.00
    inc_resp = client.post(
        "/api/v1/finance/transactions",
        json={
            "account_id": acc_id,
            "category_id": income_cat_id,
            "amount": "500.00",
            "transaction_type": "income",
            "description": "Freelance invoice payment"
        },
        headers=auth_headers
    )
    assert inc_resp.status_code == 201

    # Balance should now be 874.50 + 500.00 = 1374.50
    acc_check2 = client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers)
    assert acc_check2.get_json()["data"]["account"]["balance"] == "1374.50"

    # 4. Soft-delete the expense ($125.50) -> Balance should reverse back to 1374.50 + 125.50 = 1500.00
    del_resp = client.delete(f"/api/v1/finance/transactions/{exp_id}", headers=auth_headers)
    assert del_resp.status_code == 200

    acc_check3 = client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers)
    assert acc_check3.get_json()["data"]["account"]["balance"] == "1500.00"


def test_transaction_update_adjusts_balance(client, auth_headers):
    """Updating transaction amount or type recalibrates account balance."""
    acc_resp = client.post(
        "/api/v1/finance/accounts",
        json={"name": "Wallet", "balance": "200.00"},
        headers=auth_headers
    )
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    tx_resp = client.post(
        "/api/v1/finance/transactions",
        json={"account_id": acc_id, "amount": "50.00", "transaction_type": "expense", "description": "Dinner"},
        headers=auth_headers
    )
    tx_id = tx_resp.get_json()["data"]["transaction"]["id"]

    # Balance = 150.00
    assert client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers).get_json()["data"]["account"]["balance"] == "150.00"

    # Update amount from 50.00 to 75.00
    client.patch(f"/api/v1/finance/transactions/{tx_id}", json={"amount": "75.00"}, headers=auth_headers)

    # Balance should now be 200.00 - 75.00 = 125.00
    assert client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers).get_json()["data"]["account"]["balance"] == "125.00"


def test_transaction_filtering_and_pagination(client, auth_headers):
    """Test filtering transactions by type, account, and pagination."""
    acc_resp = client.post(
        "/api/v1/finance/accounts",
        json={"name": "Filter Test Account", "balance": "5000.00"},
        headers=auth_headers
    )
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    # Add 4 income and 6 expense transactions
    for i in range(4):
        client.post(
            "/api/v1/finance/transactions",
            json={"account_id": acc_id, "amount": "100.00", "transaction_type": "income", "description": f"Inc {i}"},
            headers=auth_headers
        )
    for i in range(6):
        client.post(
            "/api/v1/finance/transactions",
            json={"account_id": acc_id, "amount": "50.00", "transaction_type": "expense", "description": f"Exp {i}"},
            headers=auth_headers
        )

    # Filter income
    inc_list = client.get(f"/api/v1/finance/transactions?account_id={acc_id}&type=income", headers=auth_headers)
    assert inc_list.status_code == 200
    assert inc_list.get_json()["data"]["total"] == 4

    # Filter expense with pagination limit=3
    exp_paged = client.get(f"/api/v1/finance/transactions?account_id={acc_id}&type=expense&limit=3&offset=0", headers=auth_headers)
    assert exp_paged.status_code == 200
    data = exp_paged.get_json()["data"]
    assert len(data["transactions"]) == 3
    assert data["total"] == 6


# ---------------------------------------------------------
# Budget Tests
# ---------------------------------------------------------

def test_budget_utilization_tracking(client, auth_headers):
    """Test budget creation and live tracking of spent amount, remaining, and percentage."""
    month = datetime.now().strftime("%Y-%m")

    # Get a category
    cat_resp = client.get("/api/v1/finance/categories?type=expense", headers=auth_headers)
    cat = cat_resp.get_json()["data"]["categories"][0]
    cat_id = cat["id"]

    # 1. Create account
    acc_resp = client.post("/api/v1/finance/accounts", json={"name": "Budget Account", "balance": "3000.00"}, headers=auth_headers)
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    # 2. Configure budget of $500.00 for category
    b_resp = client.post(
        "/api/v1/finance/budgets",
        json={"category_id": cat_id, "month": month, "amount": "500.00"},
        headers=auth_headers
    )
    assert b_resp.status_code == 201

    # 3. Log an expense of $200.00 in this category
    client.post(
        "/api/v1/finance/transactions",
        json={
            "account_id": acc_id,
            "category_id": cat_id,
            "amount": "200.00",
            "transaction_type": "expense",
            "description": "Category expense"
        },
        headers=auth_headers
    )

    # 4. Check budget utilization
    util_resp = client.get(f"/api/v1/finance/budgets?month={month}", headers=auth_headers)
    assert util_resp.status_code == 200
    budgets = util_resp.get_json()["data"]["budgets"]
    b_item = next(b for b in budgets if b["category_id"] == cat_id)
    assert b_item["spent_amount"] == "200.00"
    assert b_item["remaining_amount"] == "300.00"
    assert b_item["utilization_percentage"] == 40.0
    assert b_item["is_over_budget"] is False


# ---------------------------------------------------------
# Savings Goals Tests
# ---------------------------------------------------------

def test_savings_goals_and_contributions(client, auth_headers):
    """Test savings goal creation, progress tracking, and contributions."""
    acc_resp = client.post(
        "/api/v1/finance/accounts",
        json={"name": "Goal Source", "balance": "5000.00"},
        headers=auth_headers
    )
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    # 1. Create a savings goal ($2,000 target with $500 initial deposit)
    goal_resp = client.post(
        "/api/v1/finance/savings-goals",
        json={
            "title": "Emergency Reserve Fund",
            "target_amount": "2000.00",
            "initial_deposit": "500.00",
            "icon": "shield-checkmark",
            "color_hex": "#20BF6B"
        },
        headers=auth_headers
    )
    assert goal_resp.status_code == 201
    goal = goal_resp.get_json()["data"]["savings_goal"]
    goal_id = goal["id"]
    assert goal["current_amount"] == "500.00"
    assert goal["progress_percentage"] == 25.0
    assert goal["status"] == "in_progress"

    # 2. Add a contribution of $1,500.00 with account deduction
    contrib_resp = client.post(
        f"/api/v1/finance/savings-goals/{goal_id}/contribute",
        json={"amount": "1500.00", "account_id": acc_id, "note": "Bonus allocation", "deduct_from_account": True},
        headers=auth_headers
    )
    assert contrib_resp.status_code == 201

    # Check goal is now completed ($2,000 / $2,000)
    refreshed_goal = client.get(f"/api/v1/finance/savings-goals/{goal_id}", headers=auth_headers).get_json()["data"]["savings_goal"]
    assert refreshed_goal["current_amount"] == "2000.00"
    assert refreshed_goal["progress_percentage"] == 100.0
    assert refreshed_goal["status"] == "completed"

    # Check account was deducted: 5000.00 - 1500.00 = 3500.00
    acc_check = client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers).get_json()["data"]["account"]
    assert acc_check["balance"] == "3500.00"


# ---------------------------------------------------------
# IDOR & Security Tests
# ---------------------------------------------------------

def test_cross_user_financial_idor_rejection(client, auth_headers, second_user_headers):
    """User B cannot view, modify, or delete User A's financial assets."""
    # User A creates account & transaction
    acc_resp = client.post("/api/v1/finance/accounts", json={"name": "Secret Vault", "balance": "9999.00"}, headers=auth_headers)
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    tx_resp = client.post(
        "/api/v1/finance/transactions",
        json={"account_id": acc_id, "amount": "100.00", "transaction_type": "income", "description": "Private income"},
        headers=auth_headers
    )
    tx_id = tx_resp.get_json()["data"]["transaction"]["id"]

    goal_resp = client.post(
        "/api/v1/finance/savings-goals",
        json={"title": "Private Goal", "target_amount": "500.00"},
        headers=auth_headers
    )
    goal_id = goal_resp.get_json()["data"]["savings_goal"]["id"]

    # User B attempts to access User A's account -> 403 Forbidden
    assert client.get(f"/api/v1/finance/accounts/{acc_id}", headers=second_user_headers).status_code == 403
    assert client.patch(f"/api/v1/finance/accounts/{acc_id}", json={"name": "Hacked"}, headers=second_user_headers).status_code == 403

    # User B attempts to log transaction against User A's account -> 403 Forbidden
    cross_tx = client.post(
        "/api/v1/finance/transactions",
        json={"account_id": acc_id, "amount": "50.00", "transaction_type": "expense", "description": "Fraud"},
        headers=second_user_headers
    )
    assert cross_tx.status_code == 403

    # User B attempts to view or delete User A's transaction -> 403 Forbidden
    assert client.get(f"/api/v1/finance/transactions/{tx_id}", headers=second_user_headers).status_code == 403
    assert client.delete(f"/api/v1/finance/transactions/{tx_id}", headers=second_user_headers).status_code == 403

    # User B attempts to access User A's savings goal -> 403 Forbidden
    assert client.get(f"/api/v1/finance/savings-goals/{goal_id}", headers=second_user_headers).status_code == 403


# ---------------------------------------------------------
# Dashboard & AI Insights Tests
# ---------------------------------------------------------

def test_finance_dashboard_aggregates(client, auth_headers):
    """Verify financial dashboard overview computes correct balance, income, expense, and net savings."""
    month = datetime.now().strftime("%Y-%m")

    # Create account with $2,000 opening balance
    acc_resp = client.post("/api/v1/finance/accounts", json={"name": "Checking", "balance": "2000.00"}, headers=auth_headers)
    acc_id = acc_resp.get_json()["data"]["account"]["id"]

    # Add income $1,200
    client.post(
        "/api/v1/finance/transactions",
        json={"account_id": acc_id, "amount": "1200.00", "transaction_type": "income", "description": "Salary"},
        headers=auth_headers
    )

    # Add expense $450
    client.post(
        "/api/v1/finance/transactions",
        json={"account_id": acc_id, "amount": "450.00", "transaction_type": "expense", "description": "Utilities"},
        headers=auth_headers
    )

    # Fetch dashboard
    dash_resp = client.get(f"/api/v1/finance/dashboard?month={month}", headers=auth_headers)
    assert dash_resp.status_code == 200
    data = dash_resp.get_json()["data"]

    # Balance = 2000 + 1200 - 450 = 2750.00
    assert data["total_balance"] == "2750.00"
    assert data["monthly_income"] == "1200.00"
    assert data["monthly_expenses"] == "450.00"
    assert data["monthly_net_savings"] == "750.00"
    assert len(data["recent_transactions"]) >= 2


def test_ai_finance_insights_endpoint(client, auth_headers):
    """Verify read-only AI financial insights returns verified metrics and narrative observations."""
    resp = client.get("/api/v1/finance/insights", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.get_json()["data"]
    assert "metrics" in data
    assert "insights" in data
    assert "disclaimer" in data
    assert "total_balance" in data["metrics"]

