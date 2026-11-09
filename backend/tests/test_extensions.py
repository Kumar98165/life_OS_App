"""Unit and Integration Tests for LifeOS Productivity Extensions.

Tests:
- 12. Notes & Documents (folders, attachments, tags, search)
- 13. Contacts & Relationship Manager (interactions, birthdays)
- 14. Subscriptions Manager (cycle, calculations, renewal tracking)
- 15. Learning & Skill Tracker (goals, study sessions, progress updates)
- 16. Travel Planner (trips, itinerary, packing checklist toggle)
- 17. Fitness & Workouts (logging, summaries)
- 18. Personal Assets (assets, warranties, maintenance)
- 19. Bills & Payments (due dates, payments, status update)
"""
import pytest
from datetime import date, timedelta


def test_notes_and_folders_lifecycle(client, auth_headers):
    # 1. Create folder
    res = client.post("/api/v1/notes/folders", json={
        "name": "Work Projects",
        "color_hex": "#4A90E2",
        "icon": "briefcase"
    }, headers=auth_headers)
    assert res.status_code == 201
    folder_id = res.json["data"]["id"]

    # 2. Create note in folder
    res = client.post("/api/v1/notes", json={
        "title": "Architecture Blueprint",
        "content": "LifeOS v2 specification details and diagrams.",
        "folder_id": folder_id,
        "is_pinned": True,
        "tag_names": ["engineering", "architecture"]
    }, headers=auth_headers)
    assert res.status_code == 201
    note_id = res.json["data"]["id"]
    assert res.json["data"]["is_pinned"] is True
    assert len(res.json["data"]["tags"]) == 2

    # 3. Add attachment
    res = client.post(f"/api/v1/notes/{note_id}/attachments", json={
        "file_name": "spec.pdf",
        "file_type": "application/pdf",
        "file_size_bytes": 1048576,
        "file_url": "https://storage.local/spec.pdf"
    }, headers=auth_headers)
    assert res.status_code == 201

    # 4. Search notes
    res = client.get("/api/v1/notes?search=Blueprint", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json["data"]) == 1
    assert res.json["data"][0]["title"] == "Architecture Blueprint"


def test_contacts_and_interactions(client, auth_headers):
    # 1. Create contact
    bday = str(date.today() - timedelta(days=365 * 25))
    res = client.post("/api/v1/contacts", json={
        "name": "Sarah Connor",
        "relationship_type": "colleague",
        "email": "sarah@cyberdyne.org",
        "phone": "+1-555-0199",
        "company": "Cyberdyne Systems",
        "job_title": "Lead Engineer",
        "birthday": bday,
        "is_favorite": True
    }, headers=auth_headers)
    assert res.status_code == 201
    contact_id = res.json["data"]["id"]

    # 2. Add interaction
    res = client.post(f"/api/v1/contacts/{contact_id}/interactions", json={
        "interaction_type": "meeting",
        "summary": "Quarterly system review",
        "details": "Discussed roadmap and timeline milestones.",
        "follow_up_date": str(date.today() + timedelta(days=7))
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Get contact detail
    res = client.get(f"/api/v1/contacts/{contact_id}", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json["data"]["interactions"]) == 1
    assert res.json["data"]["is_favorite"] is True


def test_subscriptions_and_summary(client, auth_headers):
    renewal = str(date.today() + timedelta(days=15))
    # 1. Create monthly subscription
    res = client.post("/api/v1/subscriptions", json={
        "name": "Cloud Storage",
        "category": "productivity",
        "amount": 9.99,
        "billing_cycle": "monthly",
        "renewal_date": renewal
    }, headers=auth_headers)
    assert res.status_code == 201
    sub_id = res.json["data"]["id"]

    # 2. Create yearly subscription
    res = client.post("/api/v1/subscriptions", json={
        "name": "Domain Registration",
        "category": "productivity",
        "amount": 120.00,
        "billing_cycle": "yearly",
        "renewal_date": str(date.today() + timedelta(days=180))
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Check summary
    res = client.get("/api/v1/subscriptions/summary", headers=auth_headers)
    assert res.status_code == 200
    data = res.json["data"]
    assert data["active_count"] >= 2
    assert data["estimated_monthly_expense"] >= 19.99  # 9.99 + (120/12)


def test_learning_goals_and_sessions(client, auth_headers):
    # 1. Create learning goal
    res = client.post("/api/v1/learning/goals", json={
        "title": "Rust Systems Programming",
        "category": "technology",
        "target_hours": 10,
        "description": "Master memory safety and async runtime in Rust."
    }, headers=auth_headers)
    assert res.status_code == 201
    goal_id = res.json["data"]["id"]

    # 2. Add study session (120 minutes = 2.0 hours)
    res = client.post(f"/api/v1/learning/goals/{goal_id}/sessions", json={
        "duration_minutes": 120,
        "topics_covered": "Borrow checker and lifetimes"
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Verify progress
    res = client.get(f"/api/v1/learning/goals/{goal_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["current_hours"] == 2.0
    assert res.json["data"]["progress_percent"] == 20.0


def test_travel_planner_lifecycle(client, auth_headers):
    # 1. Create trip
    start = str(date.today() + timedelta(days=30))
    end = str(date.today() + timedelta(days=37))
    res = client.post("/api/v1/travel/trips", json={
        "destination": "Kyoto, Japan",
        "title": "Spring Blossom Tour",
        "start_date": start,
        "end_date": end,
        "budget": 2500.00
    }, headers=auth_headers)
    assert res.status_code == 201
    trip_id = res.json["data"]["id"]

    # 2. Add itinerary item
    res = client.post(f"/api/v1/travel/trips/{trip_id}/itinerary", json={
        "activity_date": start,
        "activity_time": "10:00",
        "title": "Visit Fushimi Inari Shrine",
        "estimated_cost": 0.0
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Add packing item
    res = client.post(f"/api/v1/travel/trips/{trip_id}/packing", json={
        "item_name": "Passport & JR Pass",
        "category": "documents",
        "quantity": 1
    }, headers=auth_headers)
    assert res.status_code == 201
    item_id = res.json["data"]["id"]

    # 4. Toggle packing item
    res = client.post(f"/api/v1/travel/trips/{trip_id}/packing/{item_id}/toggle", headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["is_packed"] is True


def test_fitness_workouts(client, auth_headers):
    # 1. Log workout
    res = client.post("/api/v1/fitness/workouts", json={
        "workout_type": "running",
        "title": "Morning 5K Tempo Run",
        "duration_minutes": 25,
        "calories_burned": 280,
        "distance_km": 5.0,
        "intensity": "high"
    }, headers=auth_headers)
    assert res.status_code == 201

    # 2. Check stats
    res = client.get("/api/v1/fitness/stats", headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["total_workouts"] >= 1
    assert res.json["data"]["total_minutes"] >= 25


def test_personal_assets_and_maintenance(client, auth_headers):
    # 1. Create asset
    w_expiry = str(date.today() + timedelta(days=365))
    res = client.post("/api/v1/assets", json={
        "name": "MacBook Pro 16",
        "category": "electronics",
        "purchase_price": 2499.00,
        "serial_number": "C02XYZ1234",
        "warranty_expiry": w_expiry,
        "location": "Home Office"
    }, headers=auth_headers)
    assert res.status_code == 201
    asset_id = res.json["data"]["id"]

    # 2. Add maintenance record
    res = client.post(f"/api/v1/assets/{asset_id}/maintenance", json={
        "service_date": str(date.today()),
        "description": "Battery check and interior dust cleaning",
        "cost": 50.00,
        "service_provider": "Apple Authorized Center"
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Retrieve asset with maintenance
    res = client.get(f"/api/v1/assets/{asset_id}", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json["data"]["maintenance_records"]) == 1


def test_bills_and_payments(client, auth_headers):
    due = str(date.today() + timedelta(days=10))
    # 1. Create bill
    res = client.post("/api/v1/bills", json={
        "title": "High-Speed Fiber Internet",
        "category": "internet",
        "amount": 75.00,
        "due_date": due,
        "frequency": "monthly"
    }, headers=auth_headers)
    assert res.status_code == 201
    bill_id = res.json["data"]["id"]
    assert res.json["data"]["status"] == "unpaid"

    # 2. Record payment
    res = client.post(f"/api/v1/bills/{bill_id}/payments", json={
        "amount_paid": 75.00,
        "payment_method": "credit_card",
        "reference_number": "TXN-998877"
    }, headers=auth_headers)
    assert res.status_code == 201

    # 3. Verify bill status updated to paid
    res = client.get(f"/api/v1/bills/{bill_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json["data"]["status"] == "paid"
    assert len(res.json["data"]["payments"]) == 1

