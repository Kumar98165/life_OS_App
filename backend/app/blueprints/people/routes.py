"""LifeOS - People & Personal Tracking API Endpoints.

Blueprints for:
- /api/v1/people/tasks (Assigned Tasks)
- /api/v1/people/money (Lending & Borrowing)
- /api/v1/people/items (Item Lending)
- /api/v1/people/ledger (Unified Person Profile & Timeline)
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.people_tracking_service import people_tracking_service
from app.schemas.people_tracking import (
    AssignedTaskCreateSchema, AssignedTaskUpdateSchema, TaskFollowUpCreateSchema,
    MoneyTransactionCreateSchema, MoneyRepaymentCreateSchema,
    PersonalItemCreateSchema, ItemLendActionSchema, ItemReturnActionSchema
)

people_bp = Blueprint("people", __name__)


# ============================================================================
# MODULE 20: TASK ASSIGNMENT & FOLLOW-UP MANAGER
# ============================================================================

@people_bp.route("/tasks", methods=["GET"])
@jwt_required()
def list_assigned_tasks():
    user_id = get_jwt_identity()
    person = request.args.get("person")
    status = request.args.get("status")
    priority = request.args.get("priority")
    tasks = people_tracking_service.list_assigned_tasks(user_id, person, status, priority)
    return jsonify({"status": "success", "data": tasks}), 200


@people_bp.route("/tasks/<task_id>", methods=["GET"])
@jwt_required()
def get_assigned_task(task_id: str):
    user_id = get_jwt_identity()
    task = people_tracking_service.get_assigned_task(user_id, task_id)
    if not task:
        return jsonify({"status": "error", "message": "Assigned task not found"}), 404
    return jsonify({"status": "success", "data": task}), 200


@people_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_assigned_task():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = AssignedTaskCreateSchema(**body)
    task = people_tracking_service.create_assigned_task(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": task}), 201


@people_bp.route("/tasks/<task_id>", methods=["PATCH"])
@jwt_required()
def update_assigned_task(task_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = AssignedTaskUpdateSchema(**body)
    task = people_tracking_service.update_assigned_task(user_id, task_id, validated.model_dump(exclude_unset=True))
    if not task:
        return jsonify({"status": "error", "message": "Assigned task not found"}), 404
    return jsonify({"status": "success", "data": task}), 200


@people_bp.route("/tasks/<task_id>", methods=["DELETE"])
@jwt_required()
def delete_assigned_task(task_id: str):
    user_id = get_jwt_identity()
    if not people_tracking_service.delete_assigned_task(user_id, task_id):
        return jsonify({"status": "error", "message": "Assigned task not found"}), 404
    return jsonify({"status": "success", "message": "Task deleted successfully"}), 200


@people_bp.route("/tasks/<task_id>/follow-ups", methods=["POST"])
@jwt_required()
def add_task_follow_up(task_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = TaskFollowUpCreateSchema(**body)
    fu = people_tracking_service.add_task_follow_up(user_id, task_id, validated.model_dump())
    if not fu:
        return jsonify({"status": "error", "message": "Assigned task not found"}), 404
    return jsonify({"status": "success", "data": fu}), 201


# ============================================================================
# MODULE 21: PERSONAL LENDING & BORROWING MANAGER
# ============================================================================

@people_bp.route("/money/dashboard", methods=["GET"])
@jwt_required()
def get_money_dashboard():
    user_id = get_jwt_identity()
    dash = people_tracking_service.get_money_dashboard(user_id)
    return jsonify({"status": "success", "data": dash}), 200


@people_bp.route("/money", methods=["GET"])
@jwt_required()
def list_money_transactions():
    user_id = get_jwt_identity()
    tx_type = request.args.get("type")
    status = request.args.get("status")
    person = request.args.get("person")
    txs = people_tracking_service.list_money_transactions(user_id, tx_type, status, person)
    return jsonify({"status": "success", "data": txs}), 200


@people_bp.route("/money/<tx_id>", methods=["GET"])
@jwt_required()
def get_money_transaction(tx_id: str):
    user_id = get_jwt_identity()
    tx = people_tracking_service.get_money_transaction(user_id, tx_id)
    if not tx:
        return jsonify({"status": "error", "message": "Transaction not found"}), 404
    return jsonify({"status": "success", "data": tx}), 200


@people_bp.route("/money", methods=["POST"])
@jwt_required()
def create_money_transaction():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = MoneyTransactionCreateSchema(**body)
    tx = people_tracking_service.create_money_transaction(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": tx}), 201


@people_bp.route("/money/<tx_id>/repayments", methods=["POST"])
@jwt_required()
def record_money_repayment(tx_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = MoneyRepaymentCreateSchema(**body)
    tx, err = people_tracking_service.record_repayment(user_id, tx_id, validated.model_dump())
    if err:
        return jsonify({"status": "error", "message": err}), 400
    return jsonify({"status": "success", "data": tx}), 201


@people_bp.route("/money/<tx_id>", methods=["DELETE"])
@jwt_required()
def delete_money_transaction(tx_id: str):
    user_id = get_jwt_identity()
    if not people_tracking_service.delete_money_transaction(user_id, tx_id):
        return jsonify({"status": "error", "message": "Transaction not found"}), 404
    return jsonify({"status": "success", "message": "Transaction deleted successfully"}), 200


# ============================================================================
# MODULE 22: PERSONAL ITEM LENDING MANAGER
# ============================================================================

@people_bp.route("/items", methods=["GET"])
@jwt_required()
def list_personal_items():
    user_id = get_jwt_identity()
    status = request.args.get("status")
    category = request.args.get("category")
    items = people_tracking_service.list_personal_items(user_id, status, category)
    return jsonify({"status": "success", "data": items}), 200


@people_bp.route("/items/<item_id>", methods=["GET"])
@jwt_required()
def get_personal_item(item_id: str):
    user_id = get_jwt_identity()
    item = people_tracking_service.get_personal_item(user_id, item_id)
    if not item:
        return jsonify({"status": "error", "message": "Item not found"}), 404
    return jsonify({"status": "success", "data": item}), 200


@people_bp.route("/items", methods=["POST"])
@jwt_required()
def create_personal_item():
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = PersonalItemCreateSchema(**body)
    item = people_tracking_service.create_personal_item(user_id, validated.model_dump())
    return jsonify({"status": "success", "data": item}), 201


@people_bp.route("/items/<item_id>/lend", methods=["POST"])
@jwt_required()
def lend_personal_item(item_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = ItemLendActionSchema(**body)
    item, err = people_tracking_service.lend_item(user_id, item_id, validated.model_dump())
    if err:
        return jsonify({"status": "error", "message": err}), 400
    return jsonify({"status": "success", "data": item}), 200


@people_bp.route("/items/<item_id>/return", methods=["POST"])
@jwt_required()
def return_personal_item(item_id: str):
    user_id = get_jwt_identity()
    body = request.get_json() or {}
    validated = ItemReturnActionSchema(**body)
    item, err = people_tracking_service.return_item(user_id, item_id, validated.model_dump())
    if err:
        return jsonify({"status": "error", "message": err}), 400
    return jsonify({"status": "success", "data": item}), 200


@people_bp.route("/items/<item_id>", methods=["DELETE"])
@jwt_required()
def delete_personal_item(item_id: str):
    user_id = get_jwt_identity()
    if not people_tracking_service.delete_personal_item(user_id, item_id):
        return jsonify({"status": "error", "message": "Item not found"}), 404
    return jsonify({"status": "success", "message": "Item deleted successfully"}), 200


# ============================================================================
# MODULE 23: PEOPLE LEDGER — UNIFIED PERSON PROFILE
# ============================================================================

@people_bp.route("/ledger/<person_identifier>", methods=["GET"])
@jwt_required()
def get_person_ledger(person_identifier: str):
    user_id = get_jwt_identity()
    profile = people_tracking_service.get_person_profile_and_summary(user_id, person_identifier)
    if not profile:
        return jsonify({"status": "error", "message": "Person ledger profile not found"}), 404
    return jsonify({"status": "success", "data": profile}), 200
