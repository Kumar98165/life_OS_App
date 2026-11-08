"""LifeOS - Personal Finance Repository Layer.

Handles data access, persistence, queries, and filters for financial accounts,
transactions, categories, budgets, and savings goals.
"""
from typing import Optional, List, Tuple, Dict, Any
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy import desc, and_, func
from app.extensions import db
from app.models.finance import (
    FinancialAccount,
    FinancialCategory,
    FinancialTransaction,
    Budget,
    SavingsGoal,
    SavingsGoalContribution,
)


class FinanceRepository:
    """Repository handling CRUD and queries for the LifeOS money management module."""

    # ---------------------------------------------------------
    # Account Management
    # ---------------------------------------------------------

    def create_account(
        self,
        user_id: str,
        name: str,
        account_type: str = "checking",
        balance: Decimal = Decimal("0.00"),
        currency: str = "USD",
        color_hex: str = "#6C63FF",
        icon: str = "wallet",
        is_default: bool = False
    ) -> FinancialAccount:
        """Create and persist a new financial account."""
        if is_default:
            # Unset any existing default account for this user
            FinancialAccount.query.filter_by(user_id=user_id, is_default=True).update({"is_default": False})

        account = FinancialAccount(
            user_id=user_id,
            name=name,
            account_type=account_type,
            balance=balance,
            currency=currency,
            color_hex=color_hex,
            icon=icon,
            is_default=is_default,
            is_active=True,
            is_archived=False
        )
        db.session.add(account)
        db.session.commit()
        return account

    def get_account_by_id(self, account_id: str) -> Optional[FinancialAccount]:
        """Retrieve an account by ID."""
        return db.session.get(FinancialAccount, account_id)

    def list_accounts_for_user(
        self,
        user_id: str,
        include_archived: bool = False
    ) -> List[FinancialAccount]:
        """List accounts belonging to user ordered by default status and name."""
        query = FinancialAccount.query.filter_by(user_id=user_id)
        if not include_archived:
            query = query.filter_by(is_archived=False)
        return query.order_by(FinancialAccount.is_default.desc(), FinancialAccount.name.asc()).all()

    def update_account(self, account: FinancialAccount, updates: Dict[str, Any]) -> FinancialAccount:
        """Update mutable fields of an account."""
        if updates.get("is_default") is True:
            FinancialAccount.query.filter_by(user_id=account.user_id, is_default=True).update({"is_default": False})

        for k, v in updates.items():
            if hasattr(account, k) and v is not None:
                setattr(account, k, v)
        account.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return account

    # ---------------------------------------------------------
    # Category Management
    # ---------------------------------------------------------

    def create_category(
        self,
        user_id: str,
        name: str,
        category_type: str = "expense",
        icon: Optional[str] = "pricetag",
        color_hex: str = "#6C63FF",
        monthly_budget: Optional[Decimal] = None,
        is_system: bool = False
    ) -> FinancialCategory:
        """Create a new income or expense category."""
        category = FinancialCategory(
            user_id=user_id,
            name=name,
            category_type=category_type,
            icon=icon,
            color_hex=color_hex,
            monthly_budget=monthly_budget,
            is_system=is_system
        )
        db.session.add(category)
        db.session.commit()
        return category

    def get_category_by_id(self, category_id: str) -> Optional[FinancialCategory]:
        """Retrieve a category by ID."""
        return db.session.get(FinancialCategory, category_id)

    def list_categories_for_user(
        self,
        user_id: str,
        category_type: Optional[str] = None
    ) -> List[FinancialCategory]:
        """List categories belonging to user (including seeded defaults)."""
        query = FinancialCategory.query.filter_by(user_id=user_id)
        if category_type:
            query = query.filter_by(category_type=category_type)
        return query.order_by(FinancialCategory.category_type.asc(), FinancialCategory.name.asc()).all()

    def update_category(self, category: FinancialCategory, updates: Dict[str, Any]) -> FinancialCategory:
        """Update mutable fields of a category."""
        for k, v in updates.items():
            if hasattr(category, k) and v is not None:
                setattr(category, k, v)
        category.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return category

    def delete_category(self, category: FinancialCategory) -> None:
        """Delete a category."""
        db.session.delete(category)
        db.session.commit()

    # ---------------------------------------------------------
    # Transaction Management
    # ---------------------------------------------------------

    def create_transaction(
        self,
        user_id: str,
        account_id: str,
        amount: Decimal,
        transaction_type: str,
        description: str,
        category_id: Optional[str] = None,
        transaction_date: Optional[datetime] = None,
        is_recurring: bool = False
    ) -> FinancialTransaction:
        """Create and persist a financial transaction record and update account balance."""
        tx_date = transaction_date or datetime.now(timezone.utc)
        tx = FinancialTransaction(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            transaction_date=tx_date,
            is_recurring=is_recurring,
            is_deleted=False
        )
        db.session.add(tx)

        # Update account balance transactionally
        account = db.session.get(FinancialAccount, account_id)
        if account:
            if transaction_type == "income":
                account.balance += amount
            elif transaction_type == "expense":
                account.balance -= amount
            # For transfers, handled at service layer if paired

        db.session.commit()
        return tx

    def get_transaction_by_id(self, transaction_id: str) -> Optional[FinancialTransaction]:
        """Retrieve a transaction by ID."""
        return db.session.get(FinancialTransaction, transaction_id)

    def list_transactions_for_user(
        self,
        user_id: str,
        account_id: Optional[str] = None,
        category_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[FinancialTransaction], int]:
        """List active transactions with multi-criteria filtering and pagination."""
        query = FinancialTransaction.query.filter_by(user_id=user_id, is_deleted=False)

        if account_id:
            query = query.filter_by(account_id=account_id)
        if category_id:
            query = query.filter_by(category_id=category_id)
        if transaction_type:
            query = query.filter_by(transaction_type=transaction_type)
        if date_from:
            query = query.filter(FinancialTransaction.transaction_date >= date_from)
        if date_to:
            query = query.filter(FinancialTransaction.transaction_date <= date_to)

        total = query.count()
        items = (
            query
            .order_by(desc(FinancialTransaction.transaction_date), desc(FinancialTransaction.created_at))
            .offset(offset)
            .limit(limit)
            .all()
        )
        return items, total

    def update_transaction(
        self,
        transaction: FinancialTransaction,
        updates: Dict[str, Any]
    ) -> FinancialTransaction:
        """Update transaction fields and adjust account balance if amount/type changed."""
        old_amount = transaction.amount
        old_type = transaction.transaction_type
        old_account_id = transaction.account_id

        new_amount = updates.get("amount", old_amount)
        new_type = updates.get("transaction_type", old_type)
        new_account_id = updates.get("account_id", old_account_id)

        # Reverse old transaction impact on old account
        old_acc = db.session.get(FinancialAccount, old_account_id)
        if old_acc:
            if old_type == "income":
                old_acc.balance -= old_amount
            elif old_type == "expense":
                old_acc.balance += old_amount

        # Apply new transaction impact on new account
        new_acc = db.session.get(FinancialAccount, new_account_id)
        if new_acc:
            if new_type == "income":
                new_acc.balance += new_amount
            elif new_type == "expense":
                new_acc.balance -= new_amount

        for k, v in updates.items():
            if hasattr(transaction, k) and v is not None:
                setattr(transaction, k, v)

        transaction.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return transaction

    def soft_delete_transaction(self, transaction: FinancialTransaction) -> None:
        """Soft-delete a transaction and reverse its effect on account balance."""
        if transaction.is_deleted:
            return

        account = db.session.get(FinancialAccount, transaction.account_id)
        if account:
            if transaction.transaction_type == "income":
                account.balance -= transaction.amount
            elif transaction.transaction_type == "expense":
                account.balance += transaction.amount

        transaction.is_deleted = True
        transaction.deleted_at = datetime.now(timezone.utc)
        db.session.commit()

    # ---------------------------------------------------------
    # Budget Management
    # ---------------------------------------------------------

    def create_or_update_budget(
        self,
        user_id: str,
        month: str,
        amount: Decimal,
        category_id: Optional[str] = None,
        currency: str = "USD"
    ) -> Budget:
        """Create a monthly budget or update existing budget for category/month."""
        budget = Budget.query.filter_by(
            user_id=user_id,
            category_id=category_id,
            month=month
        ).first()

        if budget:
            budget.amount = amount
            budget.currency = currency
            budget.updated_at = datetime.now(timezone.utc)
        else:
            budget = Budget(
                user_id=user_id,
                category_id=category_id,
                month=month,
                amount=amount,
                currency=currency
            )
            db.session.add(budget)

        db.session.commit()
        return budget

    def get_budget_by_id(self, budget_id: str) -> Optional[Budget]:
        """Retrieve budget by ID."""
        return db.session.get(Budget, budget_id)

    def list_budgets_for_month(self, user_id: str, month: str) -> List[Budget]:
        """List all category and overall budgets defined for a given month YYYY-MM."""
        return Budget.query.filter_by(user_id=user_id, month=month).all()

    def delete_budget(self, budget: Budget) -> None:
        """Delete a budget."""
        db.session.delete(budget)
        db.session.commit()

    # ---------------------------------------------------------
    # Savings Goals Management
    # ---------------------------------------------------------

    def create_savings_goal(
        self,
        user_id: str,
        title: str,
        target_amount: Decimal,
        initial_deposit: Decimal = Decimal("0.00"),
        target_date: Optional[datetime] = None,
        currency: str = "USD",
        color_hex: str = "#6C63FF",
        icon: str = "flag",
        notes: Optional[str] = None
    ) -> SavingsGoal:
        """Create a new savings goal with optional initial deposit."""
        goal = SavingsGoal(
            user_id=user_id,
            title=title,
            target_amount=target_amount,
            current_amount=initial_deposit,
            target_date=target_date,
            status="completed" if initial_deposit >= target_amount else "in_progress",
            currency=currency,
            color_hex=color_hex,
            icon=icon,
            notes=notes
        )
        db.session.add(goal)
        db.session.flush()

        if initial_deposit > 0:
            contribution = SavingsGoalContribution(
                savings_goal_id=goal.id,
                user_id=user_id,
                amount=initial_deposit,
                contribution_date=datetime.now(timezone.utc),
                note="Initial deposit"
            )
            db.session.add(contribution)

        db.session.commit()
        return goal

    def get_savings_goal_by_id(self, goal_id: str) -> Optional[SavingsGoal]:
        """Retrieve a savings goal by ID."""
        return db.session.get(SavingsGoal, goal_id)

    def list_savings_goals_for_user(
        self,
        user_id: str,
        status: Optional[str] = None
    ) -> List[SavingsGoal]:
        """List savings goals belonging to user."""
        query = SavingsGoal.query.filter_by(user_id=user_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(SavingsGoal.status.asc(), SavingsGoal.created_at.desc()).all()

    def update_savings_goal(self, goal: SavingsGoal, updates: Dict[str, Any]) -> SavingsGoal:
        """Update mutable fields of a savings goal."""
        for k, v in updates.items():
            if hasattr(goal, k) and v is not None:
                setattr(goal, k, v)

        # Auto-update status if current_amount >= target_amount and was in_progress
        if goal.status == "in_progress" and goal.current_amount >= goal.target_amount:
            goal.status = "completed"

        goal.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return goal

    def add_savings_contribution(
        self,
        goal: SavingsGoal,
        amount: Decimal,
        account_id: Optional[str] = None,
        note: Optional[str] = None,
        deduct_from_account: bool = False
    ) -> SavingsGoalContribution:
        """Record contribution toward a savings goal, updating current amount transactionally."""
        contribution = SavingsGoalContribution(
            savings_goal_id=goal.id,
            user_id=goal.user_id,
            account_id=account_id,
            amount=amount,
            contribution_date=datetime.now(timezone.utc),
            note=note
        )
        db.session.add(contribution)

        # Update goal progress
        goal.current_amount += amount
        if goal.status == "in_progress" and goal.current_amount >= goal.target_amount:
            goal.status = "completed"
        goal.updated_at = datetime.now(timezone.utc)

        # Deduct from account if requested
        if deduct_from_account and account_id:
            account = db.session.get(FinancialAccount, account_id)
            if account:
                account.balance -= amount

        db.session.commit()
        return contribution

    def list_contributions_for_goal(self, goal_id: str) -> List[SavingsGoalContribution]:
        """List historical ledger contributions for a savings goal."""
        return (
            SavingsGoalContribution.query
            .filter_by(savings_goal_id=goal_id)
            .order_by(desc(SavingsGoalContribution.contribution_date))
            .all()
        )

