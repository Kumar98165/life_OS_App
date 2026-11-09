"""Tests for LifeOS People & Personal Tracking Modules (Modules 20, 21, 22, 23)."""
import pytest
from datetime import date, timedelta


def test_assigned_task_lifecycle(client, auth_headers):
    # 1. Create assigned task
    due = str(date.today() + timedelta(days=5))
    res = client.post("/api/v1/people/tasks", json={
        "person_name": "Aarav Sharma",
        "person_contact": "+91 9876543210",
        "title": "Deliver Q3 Marketing Report",
        "description": "Finalize slides and key engagement metrics.",
        "expected_completion_date": due,
        "priority": "high",
    }, headers=auth_headers)
    assert res.status_code == 201
    task_id = res.json["data"]["id"]
    assert res.json["data"]["status"] == "assigned"

    # 2. Add follow-up
    res = client.post(f"/api/v1/people/tasks/{task_id}/follow-ups", json={
        "note": "Checked in over phone. Draft is 80% ready."
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Update status to completed
    res = client.patch(f"/api/v1/people/tasks/{task_id}", json={
        "status": "completed"
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["status"] == "completed"
    assert res.json["data"]["actual_completion_date"] is not None


def test_money_lending_borrowing_and_repayment(client, auth_headers):
    # 1. Lend money: ₹10,000 to Rohan
    res = client.post("/api/v1/people/money", json={
        "person_name": "Rohan Verma",
        "transaction_type": "lent",
        "amount": 10000.0,
        "expected_return_date": str(date.today() + timedelta(days=30)),
        "description": "Short-term loan for laptop repair"
    }, headers=auth_headers)
    assert res.status_code == 201
    tx_id = res.json["data"]["id"]
    assert res.json["data"]["remaining_amount"] == 10000.0

    # 2. Partial repayment of ₹4,000
    res = client.post(f"/api/v1/people/money/{tx_id}/repayments", json={
        "amount": 4000.0,
        "payment_method": "UPI",
        "notes": "Partial repayment via GPay"
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json["data"]["amount_repaid"] == 4000.0
    assert res.json["data"]["remaining_amount"] == 6000.0
    assert res.json["data"]["status"] == "partially_paid"

    # 3. Prevent overpayment (attempting ₹7,000 when remaining is ₹6,000)
    res = client.post(f"/api/v1/people/money/{tx_id}/repayments", json={
        "amount": 7000.0
    }, headers=auth_headers)
    assert res.status_code == 400
    assert "cannot exceed remaining balance" in res.json["message"]

    # 4. Settle remaining ₹6,000
    res = client.post(f"/api/v1/people/money/{tx_id}/repayments", json={
        "amount": 6000.0
    }, headers=auth_headers)
    assert res.status_code == 201
    assert res.json["data"]["amount_repaid"] == 10000.0
    assert res.json["data"]["remaining_amount"] == 0.0
    assert res.json["data"]["status"] == "fully_paid"

    # 5. Check dashboard
    res = client.get("/api/v1/people/money/dashboard", headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["total_money_lent"] >= 10000.0
    assert res.json["data"]["total_money_received_back"] >= 10000.0


def test_personal_item_lending_and_return(client, auth_headers):
    # 1. Add item
    res = client.post("/api/v1/people/items", json={
        "name": "Sony Noise Cancelling Headphones",
        "category": "electronics",
        "initial_condition": "excellent",
        "description": "WH-1000XM5 Black"
    }, headers=auth_headers)
    assert res.status_code == 201
    item_id = res.json["data"]["id"]
    assert res.json["data"]["status"] == "available"

    # 2. Lend to Priya
    res = client.post(f"/api/v1/people/items/{item_id}/lend", json={
        "person_name": "Priya Nair",
        "person_contact": "+91 9988776655",
        "expected_return_date": str(date.today() + timedelta(days=7)),
        "notes": "Borrowed for flight trip"
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["status"] == "lent"
    assert res.json["data"]["currently_with"] == "Priya Nair"

    # 3. Cannot lend again while lent
    res = client.post(f"/api/v1/people/items/{item_id}/lend", json={
        "person_name": "Other person"
    }, headers=auth_headers)
    assert res.status_code == 400

    # 4. Return item
    res = client.post(f"/api/v1/people/items/{item_id}/return", json={
        "condition_on_return": "excellent",
        "notes": "Returned safely with case and cable"
    }, headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["status"] == "available"
    assert res.json["data"]["currently_with"] is None


def test_people_ledger_profile_aggregation(client, auth_headers):
    person = "Vikram Patel"
    # Assign task to Vikram
    client.post("/api/v1/people/tasks", json={
        "person_name": person,
        "title": "Review Legal Contract",
    }, headers=auth_headers)

    # Lend money to Vikram
    client.post("/api/v1/people/money", json={
        "person_name": person,
        "transaction_type": "lent",
        "amount": 5000.0,
    }, headers=auth_headers)

    # Fetch unified ledger for Vikram
    res = client.get(f"/api/v1/people/ledger/{person}", headers=auth_headers)
    assert res.status_code == 200
    data = res.json["data"]
    assert data["contact"]["name"] == person
    assert data["summary"]["total_tasks_assigned"] >= 1
    assert data["summary"]["pending_tasks_count"] >= 1
    assert data["summary"]["money_lent"] >= 5000.0
    assert len(data["activity_timeline"]) >= 2
