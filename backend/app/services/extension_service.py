"""LifeOS - Productivity Extensions Business Logic Layer."""
from datetime import datetime, timezone, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from sqlalchemy import or_, desc, asc
from app.extensions import db
from app.models.note import Note, NoteTag, note_tag_association
from app.models.extensions import (
    NoteFolder, NoteAttachment,
    Contact, ContactInteraction,
    Subscription,
    LearningGoal, StudySession,
    Trip, TripItineraryItem, TripPackingItem,
    Workout,
    PersonalAsset, AssetMaintenanceRecord,
    Bill, BillPayment
)


class ExtensionService:
    """Unified service for all productivity extension modules."""

    # =========================================================================
    # 12. NOTES & FOLDERS
    # =========================================================================

    def list_folders(self, user_id: str) -> List[Dict[str, Any]]:
        folders = NoteFolder.query.filter_by(user_id=user_id).order_by(NoteFolder.name.asc()).all()
        return [f.to_dict() for f in folders]

    def create_folder(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        folder = NoteFolder(
            user_id=user_id,
            name=data["name"].strip(),
            color_hex=data.get("color_hex", "#6C63FF"),
            icon=data.get("icon", "folder-outline")
        )
        db.session.add(folder)
        db.session.commit()
        return folder.to_dict()

    def delete_folder(self, user_id: str, folder_id: str) -> bool:
        folder = NoteFolder.query.filter_by(id=folder_id, user_id=user_id).first()
        if not folder:
            return False
        db.session.delete(folder)
        db.session.commit()
        return True

    def list_notes(
        self,
        user_id: str,
        search: Optional[str] = None,
        folder_id: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        is_archived: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        query = Note.query.filter_by(user_id=user_id)
        if is_archived is not None:
            query = query.filter_by(is_archived=is_archived)
        if is_pinned is not None:
            query = query.filter_by(is_pinned=is_pinned)
        if folder_id is not None:
            query = query.filter_by(folder_id=folder_id)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(or_(Note.title.ilike(pattern), Note.content.ilike(pattern)))
        notes = query.order_by(Note.is_pinned.desc(), Note.updated_at.desc()).all()
        return [n.to_dict() for n in notes]

    def get_note(self, user_id: str, note_id: str) -> Optional[Dict[str, Any]]:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        return note.to_dict() if note else None

    def create_note(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        note = Note(
            user_id=user_id,
            title=data["title"].strip(),
            content=data.get("content", ""),
            is_pinned=data.get("is_pinned", False),
            is_archived=data.get("is_archived", False),
            folder_id=data.get("folder_id")
        )
        # Handle tags
        tag_names = data.get("tag_names", [])
        for name in tag_names:
            clean_name = name.strip()
            if not clean_name:
                continue
            tag = NoteTag.query.filter_by(user_id=user_id, name=clean_name).first()
            if not tag:
                tag = NoteTag(user_id=user_id, name=clean_name)
                db.session.add(tag)
            note.tags.append(tag)

        db.session.add(note)
        db.session.commit()
        return note.to_dict()

    def update_note(self, user_id: str, note_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return None
        for key in ["title", "content", "is_pinned", "is_archived", "folder_id"]:
            if key in data and data[key] is not None:
                setattr(note, key, data[key])
        
        if "tag_names" in data and data["tag_names"] is not None:
            note.tags.clear()
            for name in data["tag_names"]:
                clean_name = name.strip()
                if not clean_name:
                    continue
                tag = NoteTag.query.filter_by(user_id=user_id, name=clean_name).first()
                if not tag:
                    tag = NoteTag(user_id=user_id, name=clean_name)
                    db.session.add(tag)
                note.tags.append(tag)

        db.session.commit()
        return note.to_dict()

    def delete_note(self, user_id: str, note_id: str) -> bool:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return False
        db.session.delete(note)
        db.session.commit()
        return True

    def add_note_attachment(self, user_id: str, note_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        note = Note.query.filter_by(id=note_id, user_id=user_id).first()
        if not note:
            return None
        attachment = NoteAttachment(
            note_id=note.id,
            file_name=data["file_name"].strip(),
            file_type=data["file_type"].strip(),
            file_size_bytes=data.get("file_size_bytes", 0),
            file_url=data["file_url"].strip()
        )
        db.session.add(attachment)
        db.session.commit()
        return attachment.to_dict()

    # =========================================================================
    # 13. CONTACTS & RELATIONSHIPS
    # =========================================================================

    def list_contacts(self, user_id: str, search: Optional[str] = None, relationship_type: Optional[str] = None) -> List[Dict[str, Any]]:
        query = Contact.query.filter_by(user_id=user_id)
        if relationship_type:
            query = query.filter_by(relationship_type=relationship_type)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(or_(Contact.name.ilike(pattern), Contact.company.ilike(pattern), Contact.email.ilike(pattern)))
        contacts = query.order_by(Contact.is_favorite.desc(), Contact.name.asc()).all()
        return [c.to_dict() for c in contacts]

    def get_contact(self, user_id: str, contact_id: str) -> Optional[Dict[str, Any]]:
        c = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not c:
            return None
        data = c.to_dict()
        data["interactions"] = [i.to_dict() for i in c.interactions]
        return data

    def create_contact(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        contact = Contact(
            user_id=user_id,
            name=data["name"].strip(),
            relationship_type=data.get("relationship_type", "friend"),
            email=data.get("email"),
            phone=data.get("phone"),
            address=data.get("address"),
            company=data.get("company"),
            job_title=data.get("job_title"),
            birthday=data.get("birthday"),
            anniversary=data.get("anniversary"),
            notes=data.get("notes"),
            is_favorite=data.get("is_favorite", False)
        )
        db.session.add(contact)
        db.session.commit()
        return contact.to_dict()

    def update_contact(self, user_id: str, contact_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        c = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not c:
            return None
        for key in ["name", "relationship_type", "email", "phone", "address", "company", "job_title", "birthday", "anniversary", "notes", "is_favorite"]:
            if key in data and data[key] is not None:
                setattr(c, key, data[key])
        db.session.commit()
        return c.to_dict()

    def delete_contact(self, user_id: str, contact_id: str) -> bool:
        c = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not c:
            return False
        db.session.delete(c)
        db.session.commit()
        return True

    def add_contact_interaction(self, user_id: str, contact_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        c = Contact.query.filter_by(id=contact_id, user_id=user_id).first()
        if not c:
            return None
        interaction = ContactInteraction(
            contact_id=c.id,
            interaction_type=data.get("interaction_type", "call"),
            summary=data["summary"].strip(),
            details=data.get("details"),
            interaction_date=data.get("interaction_date") or datetime.now(timezone.utc),
            follow_up_date=data.get("follow_up_date")
        )
        db.session.add(interaction)
        db.session.commit()
        return interaction.to_dict()

    # =========================================================================
    # 14. SUBSCRIPTION MANAGER
    # =========================================================================

    def list_subscriptions(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = Subscription.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        subs = query.order_by(Subscription.renewal_date.asc()).all()
        return [s.to_dict() for s in subs]

    def get_subscription_summary(self, user_id: str) -> Dict[str, Any]:
        subs = Subscription.query.filter_by(user_id=user_id, status="active").all()
        monthly_total = Decimal("0.0")
        yearly_total = Decimal("0.0")
        for s in subs:
            if s.billing_cycle == "monthly":
                monthly_total += s.amount
                yearly_total += s.amount * 12
            elif s.billing_cycle == "yearly":
                yearly_total += s.amount
                monthly_total += s.amount / 12
            elif s.billing_cycle == "quarterly":
                monthly_total += s.amount / 3
                yearly_total += s.amount * 4
            elif s.billing_cycle == "weekly":
                monthly_total += s.amount * Decimal("4.33")
                yearly_total += s.amount * 52

        return {
            "active_count": len(subs),
            "estimated_monthly_expense": round(float(monthly_total), 2),
            "estimated_yearly_expense": round(float(yearly_total), 2),
        }

    def create_subscription(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        sub = Subscription(
            user_id=user_id,
            name=data["name"].strip(),
            category=data.get("category", "entertainment"),
            amount=Decimal(str(data["amount"])),
            currency=data.get("currency", "USD"),
            billing_cycle=data.get("billing_cycle", "monthly"),
            status=data.get("status", "active"),
            renewal_date=data["renewal_date"],
            payment_method=data.get("payment_method"),
            notes=data.get("notes"),
            auto_renew=data.get("auto_renew", True)
        )
        db.session.add(sub)
        db.session.commit()
        return sub.to_dict()

    def update_subscription(self, user_id: str, sub_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        sub = Subscription.query.filter_by(id=sub_id, user_id=user_id).first()
        if not sub:
            return None
        for key in ["name", "category", "currency", "billing_cycle", "status", "renewal_date", "payment_method", "notes", "auto_renew"]:
            if key in data and data[key] is not None:
                setattr(sub, key, data[key])
        if "amount" in data and data["amount"] is not None:
            sub.amount = Decimal(str(data["amount"]))
        db.session.commit()
        return sub.to_dict()

    def delete_subscription(self, user_id: str, sub_id: str) -> bool:
        sub = Subscription.query.filter_by(id=sub_id, user_id=user_id).first()
        if not sub:
            return False
        db.session.delete(sub)
        db.session.commit()
        return True

    # =========================================================================
    # 15. LEARNING & SKILL TRACKER
    # =========================================================================

    def list_learning_goals(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = LearningGoal.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        goals = query.order_by(LearningGoal.created_at.desc()).all()
        return [g.to_dict() for g in goals]

    def get_learning_goal(self, user_id: str, goal_id: str) -> Optional[Dict[str, Any]]:
        g = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not g:
            return None
        data = g.to_dict()
        data["sessions"] = [s.to_dict() for s in g.sessions]
        return data

    def create_learning_goal(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        goal = LearningGoal(
            user_id=user_id,
            title=data["title"].strip(),
            category=data.get("category", "technology"),
            description=data.get("description"),
            target_hours=data.get("target_hours", 50),
            start_date=data.get("start_date") or date.today(),
            target_completion_date=data.get("target_completion_date")
        )
        db.session.add(goal)
        db.session.commit()
        return goal.to_dict()

    def update_learning_goal(self, user_id: str, goal_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        g = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not g:
            return None
        for key in ["title", "category", "description", "target_hours", "status", "start_date", "target_completion_date"]:
            if key in data and data[key] is not None:
                setattr(g, key, data[key])
        db.session.commit()
        return g.to_dict()

    def delete_learning_goal(self, user_id: str, goal_id: str) -> bool:
        g = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not g:
            return False
        db.session.delete(g)
        db.session.commit()
        return True

    def add_study_session(self, user_id: str, goal_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        g = LearningGoal.query.filter_by(id=goal_id, user_id=user_id).first()
        if not g:
            return None
        duration = data["duration_minutes"]
        session = StudySession(
            goal_id=g.id,
            duration_minutes=duration,
            topics_covered=data["topics_covered"].strip(),
            notes=data.get("notes"),
            session_date=data.get("session_date") or date.today()
        )
        # Update current hours
        g.current_hours += Decimal(str(round(duration / 60.0, 2)))
        if g.current_hours >= g.target_hours:
            g.status = "completed"

        db.session.add(session)
        db.session.commit()
        return session.to_dict()

    # =========================================================================
    # 16. TRAVEL PLANNER
    # =========================================================================

    def list_trips(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = Trip.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        trips = query.order_by(Trip.start_date.asc()).all()
        return [t.to_dict() for t in trips]

    def get_trip(self, user_id: str, trip_id: str) -> Optional[Dict[str, Any]]:
        t = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not t:
            return None
        data = t.to_dict()
        data["itinerary"] = [i.to_dict() for i in t.itinerary_items]
        data["packing_items"] = [p.to_dict() for p in t.packing_items]
        return data

    def create_trip(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        trip = Trip(
            user_id=user_id,
            destination=data["destination"].strip(),
            title=data["title"].strip(),
            start_date=data["start_date"],
            end_date=data["end_date"],
            budget=Decimal(str(data.get("budget", "0.0"))),
            currency=data.get("currency", "USD"),
            status=data.get("status", "planned"),
            notes=data.get("notes")
        )
        db.session.add(trip)
        db.session.commit()
        return trip.to_dict()

    def update_trip(self, user_id: str, trip_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        t = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not t:
            return None
        for key in ["destination", "title", "start_date", "end_date", "currency", "status", "notes"]:
            if key in data and data[key] is not None:
                setattr(t, key, data[key])
        if "budget" in data and data["budget"] is not None:
            t.budget = Decimal(str(data["budget"]))
        db.session.commit()
        return t.to_dict()

    def delete_trip(self, user_id: str, trip_id: str) -> bool:
        t = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not t:
            return False
        db.session.delete(t)
        db.session.commit()
        return True

    def add_itinerary_item(self, user_id: str, trip_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        t = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not t:
            return None
        item = TripItineraryItem(
            trip_id=t.id,
            activity_date=data["activity_date"],
            activity_time=data.get("activity_time"),
            title=data["title"].strip(),
            location=data.get("location"),
            booking_reference=data.get("booking_reference"),
            estimated_cost=Decimal(str(data.get("estimated_cost", "0.0")))
        )
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def add_packing_item(self, user_id: str, trip_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        t = Trip.query.filter_by(id=trip_id, user_id=user_id).first()
        if not t:
            return None
        item = TripPackingItem(
            trip_id=t.id,
            item_name=data["item_name"].strip(),
            category=data.get("category", "essentials"),
            quantity=data.get("quantity", 1),
            is_packed=data.get("is_packed", False)
        )
        db.session.add(item)
        db.session.commit()
        return item.to_dict()

    def toggle_packing_item(self, user_id: str, trip_id: str, item_id: str) -> Optional[Dict[str, Any]]:
        item = TripPackingItem.query.filter_by(id=item_id, trip_id=trip_id).first()
        if not item or item.trip.user_id != user_id:
            return None
        item.is_packed = not item.is_packed
        db.session.commit()
        return item.to_dict()

    # =========================================================================
    # 17. FITNESS & WORKOUT TRACKER
    # =========================================================================

    def list_workouts(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.workout_date.desc()).limit(limit).all()
        return [w.to_dict() for w in workouts]

    def get_fitness_stats(self, user_id: str) -> Dict[str, Any]:
        workouts = Workout.query.filter_by(user_id=user_id).all()
        total_workouts = len(workouts)
        total_minutes = sum(w.duration_minutes for w in workouts)
        total_calories = sum(w.calories_burned or 0 for w in workouts)
        total_distance = sum(float(w.distance_km or 0) for w in workouts)
        return {
            "total_workouts": total_workouts,
            "total_minutes": total_minutes,
            "total_calories": total_calories,
            "total_distance_km": round(total_distance, 2)
        }

    def create_workout(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        workout = Workout(
            user_id=user_id,
            workout_type=data.get("workout_type", "strength"),
            title=data["title"].strip(),
            duration_minutes=data["duration_minutes"],
            calories_burned=data.get("calories_burned"),
            distance_km=Decimal(str(data["distance_km"])) if data.get("distance_km") is not None else None,
            intensity=data.get("intensity", "medium"),
            notes=data.get("notes"),
            workout_date=data.get("workout_date") or date.today()
        )
        db.session.add(workout)
        db.session.commit()
        return workout.to_dict()

    def delete_workout(self, user_id: str, workout_id: str) -> bool:
        w = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
        if not w:
            return False
        db.session.delete(w)
        db.session.commit()
        return True

    # =========================================================================
    # 18. PERSONAL ASSET MANAGER
    # =========================================================================

    def list_assets(self, user_id: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        query = PersonalAsset.query.filter_by(user_id=user_id)
        if category:
            query = query.filter_by(category=category)
        assets = query.order_by(PersonalAsset.name.asc()).all()
        return [a.to_dict() for a in assets]

    def get_asset(self, user_id: str, asset_id: str) -> Optional[Dict[str, Any]]:
        a = PersonalAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not a:
            return None
        data = a.to_dict()
        data["maintenance_records"] = [m.to_dict() for m in a.maintenance_records]
        return data

    def create_asset(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        asset = PersonalAsset(
            user_id=user_id,
            name=data["name"].strip(),
            category=data.get("category", "electronics"),
            purchase_date=data.get("purchase_date"),
            purchase_price=Decimal(str(data["purchase_price"])) if data.get("purchase_price") is not None else None,
            currency=data.get("currency", "USD"),
            serial_number=data.get("serial_number"),
            warranty_expiry=data.get("warranty_expiry"),
            location=data.get("location"),
            status=data.get("status", "active"),
            notes=data.get("notes")
        )
        db.session.add(asset)
        db.session.commit()
        return asset.to_dict()

    def update_asset(self, user_id: str, asset_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        a = PersonalAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not a:
            return None
        for key in ["name", "category", "purchase_date", "currency", "serial_number", "warranty_expiry", "location", "status", "notes"]:
            if key in data and data[key] is not None:
                setattr(a, key, data[key])
        if "purchase_price" in data:
            a.purchase_price = Decimal(str(data["purchase_price"])) if data["purchase_price"] is not None else None
        db.session.commit()
        return a.to_dict()

    def delete_asset(self, user_id: str, asset_id: str) -> bool:
        a = PersonalAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not a:
            return False
        db.session.delete(a)
        db.session.commit()
        return True

    def add_asset_maintenance(self, user_id: str, asset_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        a = PersonalAsset.query.filter_by(id=asset_id, user_id=user_id).first()
        if not a:
            return None
        record = AssetMaintenanceRecord(
            asset_id=a.id,
            service_date=data["service_date"],
            description=data["description"].strip(),
            cost=Decimal(str(data.get("cost", "0.0"))),
            service_provider=data.get("service_provider"),
            notes=data.get("notes")
        )
        db.session.add(record)
        db.session.commit()
        return record.to_dict()

    # =========================================================================
    # 19. BILLS & PAYMENTS MANAGER
    # =========================================================================

    def list_bills(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        query = Bill.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        bills = query.order_by(Bill.due_date.asc()).all()
        return [b.to_dict() for b in bills]

    def get_bill(self, user_id: str, bill_id: str) -> Optional[Dict[str, Any]]:
        b = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
        if not b:
            return None
        data = b.to_dict()
        data["payments"] = [p.to_dict() for p in b.payments]
        return data

    def create_bill(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        bill = Bill(
            user_id=user_id,
            title=data["title"].strip(),
            category=data.get("category", "utility"),
            amount=Decimal(str(data["amount"])),
            currency=data.get("currency", "USD"),
            due_date=data["due_date"],
            is_recurring=data.get("is_recurring", True),
            frequency=data.get("frequency", "monthly"),
            status=data.get("status", "unpaid"),
            auto_pay=data.get("auto_pay", False),
            notes=data.get("notes")
        )
        db.session.add(bill)
        db.session.commit()
        return bill.to_dict()

    def update_bill(self, user_id: str, bill_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        b = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
        if not b:
            return None
        for key in ["title", "category", "currency", "due_date", "is_recurring", "frequency", "status", "auto_pay", "notes"]:
            if key in data and data[key] is not None:
                setattr(b, key, data[key])
        if "amount" in data and data["amount"] is not None:
            b.amount = Decimal(str(data["amount"]))
        db.session.commit()
        return b.to_dict()

    def delete_bill(self, user_id: str, bill_id: str) -> bool:
        b = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
        if not b:
            return False
        db.session.delete(b)
        db.session.commit()
        return True

    def record_bill_payment(self, user_id: str, bill_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        b = Bill.query.filter_by(id=bill_id, user_id=user_id).first()
        if not b:
            return None
        payment = BillPayment(
            bill_id=b.id,
            amount_paid=Decimal(str(data["amount_paid"])),
            payment_date=data.get("payment_date") or date.today(),
            payment_method=data.get("payment_method", "bank_transfer"),
            reference_number=data.get("reference_number"),
            notes=data.get("notes")
        )
        b.status = "paid"
        db.session.add(payment)
        db.session.commit()
        return payment.to_dict()


extension_service = ExtensionService()
