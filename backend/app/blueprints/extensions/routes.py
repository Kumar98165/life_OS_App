"""LifeOS - Productivity Extensions API Blueprints.

Exposes RESTful endpoints for:
- /api/v1/notes
- /api/v1/contacts
- /api/v1/subscriptions
- /api/v1/learning
- /api/v1/travel
- /api/v1/fitness
- /api/v1/assets
- /api/v1/bills
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.extension_service import extension_service
from app.schemas.extensions import (
    NoteFolderCreateSchema, NoteCreateSchema, NoteUpdateSchema, NoteAttachmentCreateSchema,
    ContactCreateSchema, ContactUpdateSchema, ContactInteractionCreateSchema,
    SubscriptionCreateSchema, SubscriptionUpdateSchema,
    LearningGoalCreateSchema, LearningGoalUpdateSchema, StudySessionCreateSchema,
    TripCreateSchema, TripUpdateSchema, TripItineraryItemCreateSchema, TripPackingItemCreateSchema,
    WorkoutCreateSchema, WorkoutUpdateSchema,
    PersonalAssetCreateSchema, PersonalAssetUpdateSchema, AssetMaintenanceCreateSchema,
    BillCreateSchema, BillUpdateSchema, BillPaymentCreateSchema
)

extensions_bp = Blueprint("extensions", __name__)


# ============================================================================
# 12. NOTES & DOCUMENTS
# ============================================================================

@extensions_bp.route("/notes/folders", methods=["GET"])
@jwt_required()
def list_note_folders():
    user_id = get_jwt_identity()
    folders = extension_service.list_folders(user_id)
    return jsonify({"status": "success", "data": folders}), 200


@extensions_bp.route("/notes/folders", methods=["POST"])
@jwt_required()
def create_note_folder():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = NoteFolderCreateSchema(**body)
    folder = extension_service.create_folder(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": folder}), 201


@extensions_bp.route("/notes/folders/<folder_id>", methods=["DELETE"])
@jwt_required()
def delete_note_folder(folder_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_folder(user_id, folder_id):
        return jsonify({"status": "error", "message": "Folder not found"}), 404
    return jsonify({"status": "success", "message": "Folder deleted"}), 200


@extensions_bp.route("/notes", methods=["GET"])
@jwt_required()
def list_notes():
    user_id = get_jwt_identity()
    search = request.args.get("search")
    folder_id = request.args.get("folder_id")
    is_pinned = request.args.get("is_pinned", type=lambda v: v.lower() == "true" if v else None)
    is_archived = request.args.get("is_archived", type=lambda v: v.lower() == "true" if v else None)
    notes = extension_service.list_notes(user_id, search, folder_id, is_pinned, is_archived)
    return jsonify({"status": "success", "data": notes}), 200


@extensions_bp.route("/notes/<note_id>", methods=["GET"])
@jwt_required()
def get_note(note_id: str):
    user_id = get_jwt_identity()
    note = extension_service.get_note(user_id, note_id)
    if not note:
        return jsonify({"status": "error", "message": "Note not found"}), 404
    return jsonify({"status": "success", "data": note}), 200


@extensions_bp.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = NoteCreateSchema(**body)
    note = extension_service.create_note(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": note}), 201


@extensions_bp.route("/notes/<note_id>", methods=["PATCH"])
@jwt_required()
def update_note(note_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = NoteUpdateSchema(**body)
    note = extension_service.update_note(user_id, note_id, validated.model_dump(exclude_unset=True))
    if not note:
        return jsonify({"status": "error", "message": "Note not found"}), 404
    return jsonify({"status": "success", "data": note}), 200


@extensions_bp.route("/notes/<note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_note(user_id, note_id):
        return jsonify({"status": "error", "message": "Note not found"}), 404
    return jsonify({"status": "success", "message": "Note deleted"}), 200


@extensions_bp.route("/notes/<note_id>/attachments", methods=["POST"])
@jwt_required()
def add_note_attachment(note_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = NoteAttachmentCreateSchema(**body)
    att = extension_service.add_note_attachment(user_id, note_id, validated.model_dump())
    if not att:
        return jsonify({"status": "error", "message": "Note not found"}), 404
    return jsonify({"status": "success", "data": att}), 201


# ============================================================================
# 13. CONTACTS & RELATIONSHIP MANAGER
# ============================================================================

@extensions_bp.route("/contacts", methods=["GET"])
@jwt_required()
def list_contacts():
    user_id = get_jwt_identity()
    search = request.args.get("search")
    rel_type = request.args.get("relationship_type")
    contacts = extension_service.list_contacts(user_id, search, rel_type)
    return jsonify({"status": "success", "data": contacts}), 200


@extensions_bp.route("/contacts/<contact_id>", methods=["GET"])
@jwt_required()
def get_contact(contact_id: str):
    user_id = get_jwt_identity()
    c = extension_service.get_contact(user_id, contact_id)
    if not c:
        return jsonify({"status": "error", "message": "Contact not found"}), 404
    return jsonify({"status": "success", "data": c}), 200


@extensions_bp.route("/contacts", methods=["POST"])
@jwt_required()
def create_contact():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = ContactCreateSchema(**body)
    c = extension_service.create_contact(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": c}), 201


@extensions_bp.route("/contacts/<contact_id>", methods=["PATCH"])
@jwt_required()
def update_contact(contact_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = ContactUpdateSchema(**body)
    c = extension_service.update_contact(user_id, contact_id, validated.model_dump(exclude_unset=True))
    if not c:
        return jsonify({"status": "error", "message": "Contact not found"}), 404
    return jsonify({"status": "success", "data": c}), 200


@extensions_bp.route("/contacts/<contact_id>", methods=["DELETE"])
@jwt_required()
def delete_contact(contact_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_contact(user_id, contact_id):
        return jsonify({"status": "error", "message": "Contact not found"}), 404
    return jsonify({"status": "success", "message": "Contact deleted"}), 200


@extensions_bp.route("/contacts/<contact_id>/interactions", methods=["POST"])
@jwt_required()
def add_contact_interaction(contact_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = ContactInteractionCreateSchema(**body)
    i = extension_service.add_contact_interaction(user_id, contact_id, validated.model_dump())
    if not i:
        return jsonify({"status": "error", "message": "Contact not found"}), 404
    return jsonify({"status": "success", "data": i}), 201


# ============================================================================
# 14. SUBSCRIPTION MANAGER
# ============================================================================

@extensions_bp.route("/subscriptions", methods=["GET"])
@jwt_required()
def list_subscriptions():
    user_id = get_jwt_identity()
    status = request.args.get("status")
    subs = extension_service.list_subscriptions(user_id, status)
    return jsonify({"status": "success", "data": subs}), 200


@extensions_bp.route("/subscriptions/summary", methods=["GET"])
@jwt_required()
def get_subscription_summary():
    user_id = get_jwt_identity()
    summary = extension_service.get_subscription_summary(user_id)
    return jsonify({"status": "success", "data": summary}), 200


@extensions_bp.route("/subscriptions", methods=["POST"])
@jwt_required()
def create_subscription():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = SubscriptionCreateSchema(**body)
    sub = extension_service.create_subscription(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": sub}), 201


@extensions_bp.route("/subscriptions/<sub_id>", methods=["PATCH"])
@jwt_required()
def update_subscription(sub_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = SubscriptionUpdateSchema(**body)
    sub = extension_service.update_subscription(user_id, sub_id, validated.model_dump(exclude_unset=True))
    if not sub:
        return jsonify({"status": "error", "message": "Subscription not found"}), 404
    return jsonify({"status": "success", "data": sub}), 200


@extensions_bp.route("/subscriptions/<sub_id>", methods=["DELETE"])
@jwt_required()
def delete_subscription(sub_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_subscription(user_id, sub_id):
        return jsonify({"status": "error", "message": "Subscription not found"}), 404
    return jsonify({"status": "success", "message": "Subscription deleted"}), 200


# ============================================================================
# 15. LEARNING & SKILL TRACKER
# ============================================================================

@extensions_bp.route("/learning/goals", methods=["GET"])
@jwt_required()
def list_learning_goals():
    user_id = get_jwt_identity()
    status = request.args.get("status")
    goals = extension_service.list_learning_goals(user_id, status)
    return jsonify({"status": "success", "data": goals}), 200


@extensions_bp.route("/learning/goals/<goal_id>", methods=["GET"])
@jwt_required()
def get_learning_goal(goal_id: str):
    user_id = get_jwt_identity()
    goal = extension_service.get_learning_goal(user_id, goal_id)
    if not goal:
        return jsonify({"status": "error", "message": "Learning goal not found"}), 404
    return jsonify({"status": "success", "data": goal}), 200


@extensions_bp.route("/learning/goals", methods=["POST"])
@jwt_required()
def create_learning_goal():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = LearningGoalCreateSchema(**body)
    goal = extension_service.create_learning_goal(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": goal}), 201


@extensions_bp.route("/learning/goals/<goal_id>", methods=["PATCH"])
@jwt_required()
def update_learning_goal(goal_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = LearningGoalUpdateSchema(**body)
    goal = extension_service.update_learning_goal(user_id, goal_id, validated.model_dump(exclude_unset=True))
    if not goal:
        return jsonify({"status": "error", "message": "Learning goal not found"}), 404
    return jsonify({"status": "success", "data": goal}), 200


@extensions_bp.route("/learning/goals/<goal_id>", methods=["DELETE"])
@jwt_required()
def delete_learning_goal(goal_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_learning_goal(user_id, goal_id):
        return jsonify({"status": "error", "message": "Learning goal not found"}), 404
    return jsonify({"status": "success", "message": "Learning goal deleted"}), 200


@extensions_bp.route("/learning/goals/<goal_id>/sessions", methods=["POST"])
@jwt_required()
def add_study_session(goal_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = StudySessionCreateSchema(**body)
    s = extension_service.add_study_session(user_id, goal_id, validated.model_dump())
    if not s:
        return jsonify({"status": "error", "message": "Learning goal not found"}), 404
    return jsonify({"status": "success", "data": s}), 201


# ============================================================================
# 16. TRAVEL PLANNER
# ============================================================================

@extensions_bp.route("/travel/trips", methods=["GET"])
@jwt_required()
def list_trips():
    user_id = get_jwt_identity()
    status = request.args.get("status")
    trips = extension_service.list_trips(user_id, status)
    return jsonify({"status": "success", "data": trips}), 200


@extensions_bp.route("/travel/trips/<trip_id>", methods=["GET"])
@jwt_required()
def get_trip(trip_id: str):
    user_id = get_jwt_identity()
    trip = extension_service.get_trip(user_id, trip_id)
    if not trip:
        return jsonify({"status": "error", "message": "Trip not found"}), 404
    return jsonify({"status": "success", "data": trip}), 200


@extensions_bp.route("/travel/trips", methods=["POST"])
@jwt_required()
def create_trip():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = TripCreateSchema(**body)
    trip = extension_service.create_trip(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": trip}), 201


@extensions_bp.route("/travel/trips/<trip_id>", methods=["PATCH"])
@jwt_required()
def update_trip(trip_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = TripUpdateSchema(**body)
    trip = extension_service.update_trip(user_id, trip_id, validated.model_dump(exclude_unset=True))
    if not trip:
        return jsonify({"status": "error", "message": "Trip not found"}), 404
    return jsonify({"status": "success", "data": trip}), 200


@extensions_bp.route("/travel/trips/<trip_id>", methods=["DELETE"])
@jwt_required()
def delete_trip(trip_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_trip(user_id, trip_id):
        return jsonify({"status": "error", "message": "Trip not found"}), 404
    return jsonify({"status": "success", "message": "Trip deleted"}), 200


@extensions_bp.route("/travel/trips/<trip_id>/itinerary", methods=["POST"])
@jwt_required()
def add_itinerary_item(trip_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = TripItineraryItemCreateSchema(**body)
    item = extension_service.add_itinerary_item(user_id, trip_id, validated.model_dump())
    if not item:
        return jsonify({"status": "error", "message": "Trip not found"}), 404
    return jsonify({"status": "success", "data": item}), 201


@extensions_bp.route("/travel/trips/<trip_id>/packing", methods=["POST"])
@jwt_required()
def add_packing_item(trip_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = TripPackingItemCreateSchema(**body)
    item = extension_service.add_packing_item(user_id, trip_id, validated.model_dump())
    if not item:
        return jsonify({"status": "error", "message": "Trip not found"}), 404
    return jsonify({"status": "success", "data": item}), 201


@extensions_bp.route("/travel/trips/<trip_id>/packing/<item_id>/toggle", methods=["POST"])
@jwt_required()
def toggle_packing_item(trip_id: str, item_id: str):
    user_id = get_jwt_identity()
    item = extension_service.toggle_packing_item(user_id, trip_id, item_id)
    if not item:
        return jsonify({"status": "error", "message": "Item not found"}), 404
    return jsonify({"status": "success", "data": item}), 200


# ============================================================================
# 17. FITNESS & ACTIVITY TRACKER
# ============================================================================

@extensions_bp.route("/fitness/workouts", methods=["GET"])
@jwt_required()
def list_workouts():
    user_id = get_jwt_identity()
    workouts = extension_service.list_workouts(user_id)
    return jsonify({"status": "success", "data": workouts}), 200


@extensions_bp.route("/fitness/stats", methods=["GET"])
@jwt_required()
def get_fitness_stats():
    user_id = get_jwt_identity()
    stats = extension_service.get_fitness_stats(user_id)
    return jsonify({"status": "success", "data": stats}), 200


@extensions_bp.route("/fitness/workouts", methods=["POST"])
@jwt_required()
def create_workout():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = WorkoutCreateSchema(**body)
    workout = extension_service.create_workout(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": workout}), 201


@extensions_bp.route("/fitness/workouts/<workout_id>", methods=["DELETE"])
@jwt_required()
def delete_workout(workout_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_workout(user_id, workout_id):
        return jsonify({"status": "error", "message": "Workout not found"}), 404
    return jsonify({"status": "success", "message": "Workout deleted"}), 200


# ============================================================================
# 18. PERSONAL ASSET MANAGER
# ============================================================================

@extensions_bp.route("/assets", methods=["GET"])
@jwt_required()
def list_assets():
    user_id = get_jwt_identity()
    cat = request.args.get("category")
    assets = extension_service.list_assets(user_id, cat)
    return jsonify({"status": "success", "data": assets}), 200


@extensions_bp.route("/assets/<asset_id>", methods=["GET"])
@jwt_required()
def get_asset(asset_id: str):
    user_id = get_jwt_identity()
    asset = extension_service.get_asset(user_id, asset_id)
    if not asset:
        return jsonify({"status": "error", "message": "Asset not found"}), 404
    return jsonify({"status": "success", "data": asset}), 200


@extensions_bp.route("/assets", methods=["POST"])
@jwt_required()
def create_asset():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = PersonalAssetCreateSchema(**body)
    asset = extension_service.create_asset(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": asset}), 201


@extensions_bp.route("/assets/<asset_id>", methods=["PATCH"])
@jwt_required()
def update_asset(asset_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = PersonalAssetUpdateSchema(**body)
    asset = extension_service.update_asset(user_id, asset_id, validated.model_dump(exclude_unset=True))
    if not asset:
        return jsonify({"status": "error", "message": "Asset not found"}), 404
    return jsonify({"status": "success", "data": asset}), 200


@extensions_bp.route("/assets/<asset_id>", methods=["DELETE"])
@jwt_required()
def delete_asset(asset_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_asset(user_id, asset_id):
        return jsonify({"status": "error", "message": "Asset not found"}), 404
    return jsonify({"status": "success", "message": "Asset deleted"}), 200


@extensions_bp.route("/assets/<asset_id>/maintenance", methods=["POST"])
@jwt_required()
def add_asset_maintenance(asset_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = AssetMaintenanceCreateSchema(**body)
    record = extension_service.add_asset_maintenance(user_id, asset_id, validated.model_dump())
    if not record:
        return jsonify({"status": "error", "message": "Asset not found"}), 404
    return jsonify({"status": "success", "data": record}), 201


# ============================================================================
# 19. BILLS & PAYMENTS MANAGER
# ============================================================================

@extensions_bp.route("/bills", methods=["GET"])
@jwt_required()
def list_bills():
    user_id = get_jwt_identity()
    status = request.args.get("status")
    bills = extension_service.list_bills(user_id, status)
    return jsonify({"status": "success", "data": bills}), 200


@extensions_bp.route("/bills/<bill_id>", methods=["GET"])
@jwt_required()
def get_bill(bill_id: str):
    user_id = get_jwt_identity()
    bill = extension_service.get_bill(user_id, bill_id)
    if not bill:
        return jsonify({"status": "error", "message": "Bill not found"}), 404
    return jsonify({"status": "success", "data": bill}), 200


@extensions_bp.route("/bills", methods=["POST"])
@jwt_required()
def create_bill():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = BillCreateSchema(**body)
    bill = extension_service.create_bill(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": bill}), 201


@extensions_bp.route("/bills/<bill_id>", methods=["PATCH"])
@jwt_required()
def update_bill(bill_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = BillUpdateSchema(**body)
    bill = extension_service.update_bill(user_id, bill_id, validated.model_dump(exclude_unset=True))
    if not bill:
        return jsonify({"status": "error", "message": "Bill not found"}), 404
    return jsonify({"status": "success", "data": bill}), 200


@extensions_bp.route("/bills/<bill_id>", methods=["DELETE"])
@jwt_required()
def delete_bill(bill_id: str):
    user_id = get_jwt_identity()
    if not extension_service.delete_bill(user_id, bill_id):
        return jsonify({"status": "error", "message": "Bill not found"}), 404
    return jsonify({"status": "success", "message": "Bill deleted"}), 200


@extensions_bp.route("/bills/<bill_id>/payments", methods=["POST"])
@jwt_required()
def record_bill_payment(bill_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = BillPaymentCreateSchema(**body)
    payment = extension_service.record_bill_payment(user_id, bill_id, validated.model_dump())
    if not payment:
        return jsonify({"status": "error", "message": "Bill not found"}), 404
    return jsonify({"status": "success", "data": payment}), 201
