"""LifeOS - People & Personal Tracking Business Logic Layer."""
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy import or_, desc, asc

TupleResult = Tuple[Optional[Dict[str, Any]], Optional[str]]
from app.extensions import db
from app.models.extensions import Contact
from app.models.people_tracking import (
    AssignedTask, TaskFollowUp,
    MoneyTransaction, MoneyRepayment,
    PersonalItem, ItemLendingRecord,
    PersonActivity
)


class PeopleTrackingService:
    """Service handling task assignment, money lending/borrowing, item lending, and unified people ledger."""

    def _log_activity(
        self,
        user_id: str,
        person_name: str,
        activity_type: str,
        summary: str,
        details: Optional[str] = None,
        contact_id: Optional[str] = None,
        amount: Optional[Decimal] = None,
        reference_id: Optional[str] = None
    ) -> None:
        activity = PersonActivity(
            user_id=user_id,
            contact_id=contact_id,
            person_name=person_name.strip(),
            activity_type=activity_type,
            summary=summary,
            details=details,
            amount=amount,
            reference_id=reference_id,
            activity_date=datetime.now(timezone.utc)
        )
        db.session.add(activity)

    # =========================================================================
    # MODULE 20: ASSIGNED TASKS
    # =========================================================================

    def list_assigned_tasks(
        self,
        user_id: str,
        person_name: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = AssignedTask.query.filter_by(user_id=user_id)
        if person_name:
            query = query.filter(AssignedTask.person_name.ilike(f"%{person_name.strip()}%"))
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        tasks = query.order_by(AssignedTask.assignment_date.desc()).all()
        return [t.to_dict() for t in tasks]

    def get_assigned_task(self, user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
        task = AssignedTask.query.filter_by(id=task_id, user_id=user_id).first()
        return task.to_dict() if task else None

    def create_assigned_task(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        person_name = data["person_name"].strip()
        contact_id = data.get("contact_id")
        if not contact_id:
            # Check if contact exists by name
            existing_contact = Contact.query.filter_by(user_id=user_id, name=person_name).first()
            if existing_contact:
                contact_id = existing_contact.id

        task = AssignedTask(
            user_id=user_id,
            contact_id=contact_id,
            person_name=person_name,
            person_contact=data.get("person_contact"),
            title=data["title"].strip(),
            description=data.get("description"),
            assignment_date=data.get("assignment_date") or date.today(),
            expected_completion_date=data.get("expected_completion_date"),
            priority=data.get("priority", "medium"),
            status=data.get("status", "assigned"),
            attachment_url=data.get("attachment_url")
        )
        db.session.add(task)
        db.session.flush()

        self._log_activity(
            user_id=user_id,
            person_name=person_name,
            activity_type="task_assigned",
            summary=f"Assigned task: {task.title}",
            details=task.description,
            contact_id=contact_id,
            reference_id=task.id
        )

        db.session.commit()
        return task.to_dict()

    def update_assigned_task(self, user_id: str, task_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = AssignedTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return None

        previous_status = task.status
        for key in ["person_name", "person_contact", "contact_id", "title", "description",
                    "assignment_date", "expected_completion_date", "actual_completion_date",
                    "priority", "status", "attachment_url"]:
            if key in data and data[key] is not None:
                setattr(task, key, data[key])

        if data.get("status") == "completed" and previous_status != "completed":
            if not task.actual_completion_date:
                task.actual_completion_date = date.today()
            self._log_activity(
                user_id=user_id,
                person_name=task.person_name,
                activity_type="task_completed",
                summary=f"Completed task: {task.title}",
                contact_id=task.contact_id,
                reference_id=task.id
            )

        db.session.commit()
        return task.to_dict()

    def delete_assigned_task(self, user_id: str, task_id: str) -> bool:
        task = AssignedTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return False
        db.session.delete(task)
        db.session.commit()
        return True

    def add_task_follow_up(self, user_id: str, task_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task = AssignedTask.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return None

        follow_up = TaskFollowUp(
            task_id=task.id,
            note=data["note"].strip(),
            follow_up_date=data.get("follow_up_date") or date.today(),
            reminder_date=data.get("reminder_date")
        )
        db.session.add(follow_up)

        self._log_activity(
            user_id=user_id,
            person_name=task.person_name,
            activity_type="follow_up_added",
            summary=f"Follow-up on '{task.title}': {follow_up.note[:80]}",
            contact_id=task.contact_id,
            reference_id=task.id
        )

        db.session.commit()
        return follow_up.to_dict()

    # =========================================================================
    # MODULE 21: MONEY LENDING & BORROWING
    # =========================================================================

    def get_money_dashboard(self, user_id: str) -> Dict[str, Any]:
        txs = MoneyTransaction.query.filter_by(user_id=user_id).all()
        total_lent = Decimal("0.0")
        total_borrowed = Decimal("0.0")
        total_received_back = Decimal("0.0")
        total_repaid = Decimal("0.0")
        overdue_amount = Decimal("0.0")
        today = date.today()

        for t in txs:
            if t.transaction_type == "lent":
                total_lent += t.amount
                total_received_back += t.amount_repaid
            elif t.transaction_type == "borrowed":
                total_borrowed += t.amount
                total_repaid += t.amount_repaid

            if t.status in ["pending", "partially_paid"] and t.expected_return_date and t.expected_return_date < today:
                overdue_amount += t.remaining_amount

        outstanding_receivables = max(Decimal("0.0"), total_lent - total_received_back)
        outstanding_payables = max(Decimal("0.0"), total_borrowed - total_repaid)

        return {
            "total_money_lent": float(total_lent),
            "total_money_borrowed": float(total_borrowed),
            "total_money_received_back": float(total_received_back),
            "total_money_repaid": float(total_repaid),
            "outstanding_receivables": float(outstanding_receivables),
            "outstanding_payables": float(outstanding_payables),
            "overdue_amount": float(overdue_amount),
        }

    def list_money_transactions(
        self,
        user_id: str,
        transaction_type: Optional[str] = None,
        status: Optional[str] = None,
        person_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        query = MoneyTransaction.query.filter_by(user_id=user_id)
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        if status:
            query = query.filter_by(status=status)
        if person_name:
            query = query.filter(MoneyTransaction.person_name.ilike(f"%{person_name.strip()}%"))

        txs = query.order_by(MoneyTransaction.transaction_date.desc()).all()
        # Evaluate overdue status dynamically
        today = date.today()
        for t in txs:
            if t.status in ["pending", "partially_paid"] and t.expected_return_date and t.expected_return_date < today:
                t.status = "overdue"
        return [t.to_dict() for t in txs]

    def get_money_transaction(self, user_id: str, tx_id: str) -> Optional[Dict[str, Any]]:
        tx = MoneyTransaction.query.filter_by(id=tx_id, user_id=user_id).first()
        return tx.to_dict() if tx else None

    def create_money_transaction(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        person_name = data["person_name"].strip()
        contact_id = data.get("contact_id")
        if not contact_id:
            existing_contact = Contact.query.filter_by(user_id=user_id, name=person_name).first()
            if existing_contact:
                contact_id = existing_contact.id

        tx = MoneyTransaction(
            user_id=user_id,
            contact_id=contact_id,
            person_name=person_name,
            person_contact=data.get("person_contact"),
            transaction_type=data["transaction_type"],
            amount=Decimal(str(data["amount"])),
            amount_repaid=Decimal("0.0"),
            currency=data.get("currency", "INR"),
            transaction_date=data.get("transaction_date") or date.today(),
            expected_return_date=data.get("expected_return_date"),
            payment_method=data.get("payment_method", "UPI"),
            description=data.get("description"),
            proof_url=data.get("proof_url"),
            status="pending"
        )
        db.session.add(tx)
        db.session.flush()

        act_type = "money_lent" if tx.transaction_type == "lent" else "money_borrowed"
        summary = f"Lent ₹{tx.amount:,.2f} to {person_name}" if tx.transaction_type == "lent" else f"Borrowed ₹{tx.amount:,.2f} from {person_name}"
        self._log_activity(
            user_id=user_id,
            person_name=person_name,
            activity_type=act_type,
            summary=summary,
            details=tx.description,
            contact_id=contact_id,
            amount=tx.amount,
            reference_id=tx.id
        )

        db.session.commit()
        return tx.to_dict()

    def record_repayment(self, user_id: str, tx_id: str, data: Dict[str, Any]) -> TupleResult:
        tx = MoneyTransaction.query.filter_by(id=tx_id, user_id=user_id).first()
        if not tx:
            return None, "Transaction not found"

        repay_amount = Decimal(str(data["amount"]))
        if repay_amount <= Decimal("0.0"):
            return None, "Repayment amount must be positive"

        remaining = tx.remaining_amount
        if repay_amount > remaining:
            return None, f"Repayment amount (₹{repay_amount}) cannot exceed remaining balance (₹{remaining})"

        repayment = MoneyRepayment(
            transaction_id=tx.id,
            amount=repay_amount,
            payment_date=data.get("payment_date") or date.today(),
            payment_method=data.get("payment_method", "UPI"),
            notes=data.get("notes"),
            proof_url=data.get("proof_url")
        )
        db.session.add(repayment)

        tx.amount_repaid += repay_amount
        if tx.remaining_amount <= Decimal("0.0"):
            tx.status = "fully_paid"
        else:
            tx.status = "partially_paid"

        act_type = "repayment_received" if tx.transaction_type == "lent" else "repayment_made"
        summary = f"Received repayment of ₹{repay_amount:,.2f} from {tx.person_name}" if tx.transaction_type == "lent" else f"Repaid ₹{repay_amount:,.2f} to {tx.person_name}"
        self._log_activity(
            user_id=user_id,
            person_name=tx.person_name,
            activity_type=act_type,
            summary=summary,
            details=repayment.notes,
            contact_id=tx.contact_id,
            amount=repay_amount,
            reference_id=tx.id
        )

        db.session.commit()
        return tx.to_dict(), None

    def delete_money_transaction(self, user_id: str, tx_id: str) -> bool:
        tx = MoneyTransaction.query.filter_by(id=tx_id, user_id=user_id).first()
        if not tx:
            return False
        db.session.delete(tx)
        db.session.commit()
        return True

    # =========================================================================
    # MODULE 22: PERSONAL ITEM LENDING
    # =========================================================================

    def list_personal_items(self, user_id: str, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query = PersonalItem.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        items = query.order_by(PersonalItem.name.asc()).all()
        today = date.today()
        for it in items:
            active_rec = next((r for r in it.lending_records if r.actual_return_date is None), None)
            if active_rec and active_rec.expected_return_date and active_rec.expected_return_date < today and it.status == "lent":
                it.status = "overdue"
        return [i.to_dict() for i in items]

    def get_personal_item(self, user_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        it = PersonalItem.query.filter_by(id=item_id, user_id=user_id).first()
        return it.to_dict() if it else None

    def create_personal_item(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        item = PersonalItem(
            user_id=user_id,
            name=data["name"].strip(),
            category=data.get("category", "other"),
            description=data.get("description"),
            initial_condition=data.get("initial_condition", "good"),
            photo_url=data.get("photo_url"),
            status="available"
        )
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def lend_item(self, user_id: str, item_id: str, data: Dict[str, Any]) -> TupleResult:
        item = PersonalItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return None, "Item not found"
        if item.status == "lent":
            return None, "Item is already lent out and not yet returned"

        person_name = data["person_name"].strip()
        contact_id = data.get("contact_id")
        if not contact_id:
            c = Contact.query.filter_by(user_id=user_id, name=person_name).first()
            if c:
                contact_id = c.id

        record = ItemLendingRecord(
            item_id=item.id,
            contact_id=contact_id,
            person_name=person_name,
            person_contact=data.get("person_contact"),
            given_date=data.get("given_date") or date.today(),
            expected_return_date=data.get("expected_return_date"),
            notes=data.get("notes")
        )
        item.status = "lent"
        db.session.add(record)

        self._log_activity(
            user_id=user_id,
            person_name=person_name,
            activity_type="item_lent",
            summary=f"Lent '{item.name}' to {person_name}",
            details=record.notes,
            contact_id=contact_id,
            reference_id=item.id
        )

        db.session.commit()
        return item.to_dict(), None

    def return_item(self, user_id: str, item_id: str, data: Dict[str, Any]) -> TupleResult:
        item = PersonalItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return None, "Item not found"

        active_rec = next((r for r in item.lending_records if r.actual_return_date is None), None)
        if not active_rec:
            return None, "No active lending record found for this item"

        active_rec.actual_return_date = data.get("actual_return_date") or date.today()
        active_rec.condition_on_return = data.get("condition_on_return")
        if data.get("notes"):
            active_rec.notes = f"{active_rec.notes or ''} [Return Notes: {data['notes']}]".strip()

        item.status = "available"

        self._log_activity(
            user_id=user_id,
            person_name=active_rec.person_name,
            activity_type="item_returned",
            summary=f"Returned '{item.name}' from {active_rec.person_name}",
            details=f"Condition: {active_rec.condition_on_return or 'Good'}",
            contact_id=active_rec.contact_id,
            reference_id=item.id
        )

        db.session.commit()
        return item.to_dict(), None

    def delete_personal_item(self, user_id: str, item_id: str) -> bool:
        item = PersonalItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

    # =========================================================================
    # MODULE 23: PEOPLE LEDGER — UNIFIED PERSON PROFILE & TIMELINE
    # =========================================================================

    def get_person_profile_and_summary(self, user_id: str, person_identifier: str) -> Optional[Dict[str, Any]]:
        """Fetch unified ledger profile by contact ID or person name."""
        contact = Contact.query.filter(
            Contact.user_id == user_id,
            or_(Contact.id == person_identifier, Contact.name.ilike(person_identifier))
        ).first()

        name = contact.name if contact else person_identifier

        # 1. Assigned tasks
        tasks = AssignedTask.query.filter(
            AssignedTask.user_id == user_id,
            or_(AssignedTask.contact_id == (contact.id if contact else ""), AssignedTask.person_name.ilike(name))
        ).order_by(AssignedTask.assignment_date.desc()).all()
        pending_tasks = [t for t in tasks if t.status not in ["completed", "cancelled"]]
        completed_tasks = [t for t in tasks if t.status == "completed"]

        # 2. Money transactions
        txs = MoneyTransaction.query.filter(
            MoneyTransaction.user_id == user_id,
            or_(MoneyTransaction.contact_id == (contact.id if contact else ""), MoneyTransaction.person_name.ilike(name))
        ).all()
        money_lent = sum((t.amount for t in txs if t.transaction_type == "lent"), Decimal("0.0"))
        money_lent_repaid = sum((t.amount_repaid for t in txs if t.transaction_type == "lent"), Decimal("0.0"))
        money_borrowed = sum((t.amount for t in txs if t.transaction_type == "borrowed"), Decimal("0.0"))
        money_borrowed_repaid = sum((t.amount_repaid for t in txs if t.transaction_type == "borrowed"), Decimal("0.0"))
        net_outstanding = (money_lent - money_lent_repaid) - (money_borrowed - money_borrowed_repaid)

        # 3. Items lent
        item_records = ItemLendingRecord.query.filter(
            or_(ItemLendingRecord.contact_id == (contact.id if contact else ""), ItemLendingRecord.person_name.ilike(name))
        ).all()
        # Ensure user ownership through item
        owned_item_records = [r for r in item_records if r.item.user_id == user_id]
        items_given = len(owned_item_records)
        items_not_returned = [r for r in owned_item_records if r.actual_return_date is None]

        # 4. Activity timeline
        activities = PersonActivity.query.filter(
            PersonActivity.user_id == user_id,
            or_(PersonActivity.contact_id == (contact.id if contact else ""), PersonActivity.person_name.ilike(name))
        ).order_by(PersonActivity.activity_date.desc()).all()

        return {
            "contact": contact.to_dict() if contact else {
                "name": name,
                "relationship_type": "contact",
                "phone": tasks[0].person_contact if tasks else (txs[0].person_contact if txs else None),
                "email": None,
                "notes": None,
            },
            "summary": {
                "total_tasks_assigned": len(tasks),
                "pending_tasks_count": len(pending_tasks),
                "completed_tasks_count": len(completed_tasks),
                "money_lent": float(money_lent),
                "money_lent_repaid": float(money_lent_repaid),
                "money_borrowed": float(money_borrowed),
                "money_borrowed_repaid": float(money_borrowed_repaid),
                "net_outstanding": float(net_outstanding),
                "items_given_count": items_given,
                "items_pending_return_count": len(items_not_returned),
            },
            "pending_tasks": [t.to_dict() for t in pending_tasks],
            "unreturned_items": [r.to_dict() for r in items_not_returned],
            "activity_timeline": [a.to_dict() for a in activities]
        }


# Type helper for operations returning (result, error_message)
TupleResult = tuple[Optional[Dict[str, Any]], Optional[str]]
people_tracking_service = PeopleTrackingService()
