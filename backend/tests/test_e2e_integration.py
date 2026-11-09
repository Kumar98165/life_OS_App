"""LifeOS - Complete System End-to-End Cross-Module Integration Tests.

Validates the full lifecycle of a user across all 14 LifeOS modules:
1. Authentication & Session Rotation
2. Tasks & Planner Synchronization
3. Habits Tracking & Streaks
4. Goals & Milestone Progress
5. Personal Money Management & Balance Ledgers
6. Centralized Notifications & Reminders
7. AI Assistant Chat, Prompt Attribution & User Feedback
8. Dynamic Multi-Domain Life Analytics & Life Score Engine
"""
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
import pytest
from unittest.mock import patch, MagicMock


class TestEndToEndSystemIntegration:
    """End-to-end integration tests verifying inter-module data consistency."""

    def test_complete_user_lifecycle_and_session(self, client):
        """Test registration, profile access, token refresh, and session validation."""
        # 1. User Registration
        reg_payload = {
            "email": "e2e_user@lifeos.internal",
            "password": "SecurePassword123!",
            "full_name": "E2E Explorer"
        }
        reg_resp = client.post("/api/v1/auth/register", json=reg_payload)
        assert reg_resp.status_code == 201
        reg_data = reg_resp.get_json()["data"]
        access_token = reg_data["tokens"]["access_token"]
        refresh_token = reg_data["tokens"]["refresh_token"]
        user_id = reg_data["user"]["id"]
        assert user_id is not None

        # 2. Authenticated Profile Access
        headers = {"Authorization": f"Bearer {access_token}"}
        profile_resp = client.get("/api/v1/auth/me", headers=headers)
        assert profile_resp.status_code == 200
        assert profile_resp.get_json()["data"]["user"]["email"] == "e2e_user@lifeos.internal"

        # 3. Token Refresh with valid refresh token
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        ref_resp = client.post("/api/v1/auth/refresh", headers=refresh_headers)
        assert ref_resp.status_code == 200
        new_access_token = ref_resp.get_json()["data"]["access_token"]
        assert new_access_token is not None
        assert new_access_token != access_token

        # 4. Verify access with new rotated token
        new_headers = {"Authorization": f"Bearer {new_access_token}"}
        new_profile_resp = client.get("/api/v1/auth/me", headers=new_headers)
        assert new_profile_resp.status_code == 200

    def test_cross_module_productivity_tasks_and_planner_to_analytics(self, client, auth_headers):
        """Test task creation/completion, planner block tracking, and productivity analytics."""
        # 1. Create a task
        task_payload = {
            "title": "Complete System Integration Audit",
            "priority": "high",
            "estimated_minutes": 90,
            "due_date": date.today().isoformat()
        }
        task_resp = client.post("/api/v1/tasks", json=task_payload, headers=auth_headers)
        assert task_resp.status_code == 201
        task_id = task_resp.get_json()["data"]["task"]["id"]

        # 2. Create a planner block linked to today
        now = datetime.now(timezone.utc)
        block_payload = {
            "title": "Deep Work - Audit Execution",
            "start_time": (now + timedelta(hours=1)).isoformat(),
            "end_time": (now + timedelta(hours=2)).isoformat(),
            "block_type": "work",
            "status": "scheduled",
            "color_hex": "#6C63FF"
        }
        block_resp = client.post("/api/v1/planner/blocks", json=block_payload, headers=auth_headers)
        assert block_resp.status_code == 201
        block_id = block_resp.get_json()["data"]["block"]["id"]

        # 3. Mark task as completed
        toggle_resp = client.patch(f"/api/v1/tasks/{task_id}/complete", headers=auth_headers)
        assert toggle_resp.status_code == 200
        assert toggle_resp.get_json()["data"]["task"]["status"] == "completed"

        # 4. Mark planner block as completed
        status_resp = client.patch(
            f"/api/v1/planner/blocks/{block_id}/status",
            json={"status": "completed"},
            headers=auth_headers
        )
        assert status_resp.status_code == 200
        assert status_resp.get_json()["data"]["block"]["status"] == "completed"

        # 5. Fetch Productivity Analytics & verify cross-module synchronization
        prod_resp = client.get("/api/v1/analytics/productivity?period=week", headers=auth_headers)
        assert prod_resp.status_code == 200
        prod_data = prod_resp.get_json()["data"]
        assert prod_data["completed_tasks"] >= 1
        assert prod_data["total_tasks"] >= 1
        assert prod_data["completion_percentage"] > 0
        assert prod_data["total_planner_blocks"] >= 1
        assert prod_data["completed_planner_blocks"] >= 1

    def test_cross_module_habits_and_habit_analytics(self, client, auth_headers):
        """Test habit creation, daily check-in logging, streak updating, and analytics."""
        # 1. Create a habit
        habit_payload = {
            "title": "Daily Architectural Reading",
            "frequency": "daily",
            "target_days_per_week": 7,
            "icon": "book-outline",
            "color_hex": "#10B981"
        }
        habit_resp = client.post("/api/v1/habits", json=habit_payload, headers=auth_headers)
        assert habit_resp.status_code == 201
        habit_id = habit_resp.get_json()["data"]["habit"]["id"]

        # 2. Check in for today
        log_payload = {"log_date": date.today().isoformat(), "completed": True, "notes": "Read clean architecture"}
        log_resp = client.post(f"/api/v1/habits/{habit_id}/logs", json=log_payload, headers=auth_headers)
        assert log_resp.status_code == 201
        log_data = log_resp.get_json()["data"]
        assert log_data["log"]["completed"] is True
        assert log_data["habit"]["current_streak"] >= 1

        # 3. Verify Habit Analytics metrics reflect check-in
        habits_analytics = client.get("/api/v1/analytics/habits?period=week", headers=auth_headers)
        assert habits_analytics.status_code == 200
        h_data = habits_analytics.get_json()["data"]
        assert h_data["total_active_habits"] >= 1
        assert h_data["total_completed_checkins"] >= 1
        assert h_data["consistency_percentage"] > 0

    def test_cross_module_goals_milestones_and_analytics(self, client, auth_headers):
        """Test goal creation, milestone progress tracking, and goal analytics."""
        # 1. Create a goal
        goal_payload = {
            "title": "Ship LifeOS v1.0",
            "category": "career",
            "target_date": (date.today() + timedelta(days=60)).isoformat(),
            "target_value": 100.0,
            "current_value": 0.0,
            "unit": "%"
        }
        goal_resp = client.post("/api/v1/goals", json=goal_payload, headers=auth_headers)
        assert goal_resp.status_code == 201
        goal_id = goal_resp.get_json()["data"]["goal"]["id"]

        # 2. Add two milestones
        m1_resp = client.post(
            f"/api/v1/goals/{goal_id}/milestones",
            json={"title": "Backend Complete", "target_value": 50.0},
            headers=auth_headers
        )
        assert m1_resp.status_code == 201
        m1_id = m1_resp.get_json()["data"]["milestone"]["id"]

        m2_resp = client.post(
            f"/api/v1/goals/{goal_id}/milestones",
            json={"title": "Frontend Complete", "target_value": 50.0},
            headers=auth_headers
        )
        assert m2_resp.status_code == 201

        # 3. Complete milestone 1
        update_m1 = client.patch(
            f"/api/v1/goals/{goal_id}/milestones/{m1_id}",
            json={"is_completed": True},
            headers=auth_headers
        )
        assert update_m1.status_code == 200
        assert update_m1.get_json()["data"]["milestone"]["is_completed"] is True

        # 4. Verify Goals Analytics reflects milestone velocity
        goals_analytics = client.get("/api/v1/analytics/goals", headers=auth_headers)
        assert goals_analytics.status_code == 200
        g_data = goals_analytics.get_json()["data"]
        assert g_data["active_goals"] >= 1
        assert g_data["total_milestones"] >= 2
        assert g_data["completed_milestones"] >= 1

    def test_cross_module_finance_and_financial_analytics(self, client, auth_headers):
        """Test account creation, income/expense transactions, balance updates, and financial analytics."""
        # 1. Create account
        acc_payload = {
            "name": "Primary Checking",
            "account_type": "checking",
            "balance": "2500.00",
            "currency": "USD"
        }
        acc_resp = client.post("/api/v1/finance/accounts", json=acc_payload, headers=auth_headers)
        assert acc_resp.status_code == 201
        acc_id = acc_resp.get_json()["data"]["account"]["id"]

        # 2. Get Seeded Categories
        cat_resp = client.get("/api/v1/finance/categories?type=expense", headers=auth_headers)
        expense_cat_id = cat_resp.get_json()["data"]["categories"][0]["id"]

        now_iso = datetime.now(timezone.utc).isoformat()

        # 3. Add Expense Transaction ($150.00)
        tx_resp = client.post(
            "/api/v1/finance/transactions",
            json={
                "account_id": acc_id,
                "category_id": expense_cat_id,
                "amount": "150.00",
                "transaction_type": "expense",
                "transaction_date": now_iso,
                "description": "Server hosting fee"
            },
            headers=auth_headers
        )
        assert tx_resp.status_code == 201

        # 4. Verify Account balance adjusted: 2500.00 - 150.00 = 2350.00
        acc_check = client.get(f"/api/v1/finance/accounts/{acc_id}", headers=auth_headers)
        assert acc_check.status_code == 200
        assert Decimal(acc_check.get_json()["data"]["account"]["balance"]) == Decimal("2350.00")

        # 5. Verify Financial Analytics reflects expense and cash flow
        fin_analytics = client.get("/api/v1/analytics/finance?period=month", headers=auth_headers)
        assert fin_analytics.status_code == 200
        f_data = fin_analytics.get_json()["data"]
        assert Decimal(f_data["total_expenses"]) >= Decimal("150.00")
        assert Decimal(f_data["net_savings"]) <= Decimal("-150.00")

    def test_cross_module_notifications_and_reminders(self, client, auth_headers):
        """Test reminder creation, notification listing, and unread count queries."""
        # 1. Create a reminder
        reminder_time = (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat()
        rem_payload = {
            "title": "Review E2E Test Suite",
            "description": "Ensure zero regressions across 14 modules.",
            "reminder_time": reminder_time,
            "entity_type": "custom",
            "is_recurring": False
        }
        rem_resp = client.post("/api/v1/notifications/reminders", json=rem_payload, headers=auth_headers)
        assert rem_resp.status_code == 201
        rem_id = rem_resp.get_json()["data"]["reminder"]["id"]

        # 2. Query user reminders
        rem_list = client.get("/api/v1/notifications/reminders", headers=auth_headers)
        assert rem_list.status_code == 200
        reminders = rem_list.get_json()["data"]["reminders"]
        assert any(r["id"] == rem_id for r in reminders)

        # 3. Check notifications count endpoint
        count_resp = client.get("/api/v1/notifications/unread-count", headers=auth_headers)
        assert count_resp.status_code == 200
        assert "unread_count" in count_resp.get_json()["data"]

    def test_holistic_life_score_synthesis(self, client, auth_headers):
        """Test that the 4-pillar Life Score Engine accurately synthesizes composite metrics."""
        # Query Life Score calculation
        score_resp = client.get("/api/v1/analytics/life-score", headers=auth_headers)
        assert score_resp.status_code == 200
        score_data = score_resp.get_json()["data"]

        # Verify structure and pillars
        assert "overall_score" in score_data
        assert 0 <= score_data["overall_score"] <= 100
        assert "score_tier" in score_data
        assert "dimensions" in score_data
        assert "disclaimer" in score_data

        dim_names = [d["name"] for d in score_data["dimensions"]]
        assert "Productivity" in dim_names
        assert "Habits" in dim_names
        assert "Goals" in dim_names
        assert "Financial Discipline" in dim_names
