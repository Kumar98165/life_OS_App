"""LifeOS - Personal Finance Business Service Layer.

Orchestrates business logic, strict ownership validations, decimal calculations,
budget utilization metrics, savings tracking, and local AI financial insights.
"""
from typing import Optional, List, Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timezone, date
import calendar
from app.extensions import db
from app.repositories.finance_repository import FinanceRepository
from app.models.finance import (
    FinancialAccount,
    FinancialCategory,
    FinancialTransaction,
    Budget,
    SavingsGoal,
    SavingsGoalContribution,
)
from app.core.exceptions import NotFoundException, BadRequestException, ForbiddenException
from app.core.security import check_resource_ownership

DEFAULT_SYSTEM_CATEGORIES = [
    # Expense categories
    {"name": "Food & Dining", "category_type": "expense", "icon": "restaurant", "color_hex": "#FF6B6B"},
    {"name": "Groceries", "category_type": "expense", "icon": "cart", "color_hex": "#4ECDC4"},
    {"name": "Housing & Rent", "category_type": "expense", "icon": "home", "color_hex": "#45B7D1"},
    {"name": "Transportation", "category_type": "expense", "icon": "car", "color_hex": "#FFA07A"},
    {"name": "Utilities & Bills", "category_type": "expense", "icon": "flash", "color_hex": "#98D8C8"},
    {"name": "Entertainment", "category_type": "expense", "icon": "film", "color_hex": "#F7B731"},
    {"name": "Health & Medical", "category_type": "expense", "icon": "medkit", "color_hex": "#EB3B5A"},
    {"name": "Shopping", "category_type": "expense", "icon": "bag-handle", "color_hex": "#20BF6B"},
    {"name": "Personal Care", "category_type": "expense", "icon": "sparkles", "color_hex": "#A55EEA"},
    {"name": "General Expense", "category_type": "expense", "icon": "pricetag", "color_hex": "#8854D0"},
    # Income categories
    {"name": "Salary & Wages", "category_type": "income", "icon": "cash", "color_hex": "#26DE81"},
    {"name": "Freelance & Consulting", "category_type": "income", "icon": "laptop", "color_hex": "#2BCBBA"},
    {"name": "Investments & Dividends", "category_type": "income", "icon": "trending-up", "color_hex": "#0FB9B1"},
    {"name": "Gifts & Grants", "category_type": "income", "icon": "gift", "color_hex": "#45AAF2"},
    {"name": "General Income", "category_type": "income", "icon": "wallet", "color_hex": "#4B7BEC"},
]


class FinanceService:
    """Service orchestrating accounts, transactions, budgets, savings goals, and insights."""

    def __init__(self, finance_repo: Optional[FinanceRepository] = None):
        self.repo = finance_repo or FinanceRepository()

    # ---------------------------------------------------------
    # Account Operations
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
        """Create a new financial account for user."""
        return self.repo.create_account(
            user_id=user_id,
            name=name,
            account_type=account_type,
            balance=balance,
            currency=currency,
            color_hex=color_hex,
            icon=icon,
            is_default=is_default
        )

    def get_account(self, account_id: str, user_id: str) -> FinancialAccount:
        """Retrieve account ensuring ownership."""
        account = self.repo.get_account_by_id(account_id)
        if not account:
            raise NotFoundException(f"Account with ID '{account_id}' not found")
        check_resource_ownership(account.user_id, user_id)
        return account

    def list_accounts(self, user_id: str, include_archived: bool = False) -> List[FinancialAccount]:
        """List accounts for user, auto-creating a primary Cash Wallet if none exist."""
        accounts = self.repo.list_accounts_for_user(user_id=user_id, include_archived=include_archived)
        if not accounts and not include_archived:
            # Seed initial default Cash Wallet
            default_acc = self.repo.create_account(
                user_id=user_id,
                name="Cash Wallet",
                account_type="cash",
                balance=Decimal("0.00"),
                currency="USD",
                color_hex="#26DE81",
                icon="wallet",
                is_default=True
            )
            return [default_acc]
        return accounts

    def update_account(self, account_id: str, user_id: str, updates: Dict[str, Any]) -> FinancialAccount:
        """Update account ensuring ownership."""
        account = self.get_account(account_id, user_id)
        return self.repo.update_account(account, updates)

    def archive_account(self, account_id: str, user_id: str) -> FinancialAccount:
        """Archive an account."""
        account = self.get_account(account_id, user_id)
        return self.repo.update_account(account, {"is_archived": True, "is_active": False})

    # ---------------------------------------------------------
    # Category Operations
    # ---------------------------------------------------------

    def seed_default_categories(self, user_id: str) -> List[FinancialCategory]:
        """Seed default categories for a user if they have none."""
        existing = self.repo.list_categories_for_user(user_id)
        if existing:
            return existing

        created = []
        for cat in DEFAULT_SYSTEM_CATEGORIES:
            c = self.repo.create_category(
                user_id=user_id,
                name=cat["name"],
                category_type=cat["category_type"],
                icon=cat["icon"],
                color_hex=cat["color_hex"],
                is_system=True
            )
            created.append(c)
        return created

    def list_categories(self, user_id: str, category_type: Optional[str] = None) -> List[FinancialCategory]:
        """List categories belonging to user, seeding system defaults if empty."""
        cats = self.repo.list_categories_for_user(user_id=user_id, category_type=category_type)
        if not cats:
            self.seed_default_categories(user_id)
            cats = self.repo.list_categories_for_user(user_id=user_id, category_type=category_type)
        return cats

    def create_category(
        self,
        user_id: str,
        name: str,
        category_type: str = "expense",
        icon: Optional[str] = "pricetag",
        color_hex: str = "#6C63FF",
        monthly_budget: Optional[Decimal] = None
    ) -> FinancialCategory:
        """Create a custom user category."""
        return self.repo.create_category(
            user_id=user_id,
            name=name,
            category_type=category_type,
            icon=icon,
            color_hex=color_hex,
            monthly_budget=monthly_budget,
            is_system=False
        )

    def update_category(self, category_id: str, user_id: str, updates: Dict[str, Any]) -> FinancialCategory:
        """Update category ensuring ownership."""
        cat = self.repo.get_category_by_id(category_id)
        if not cat:
            raise NotFoundException("Category not found")
        check_resource_ownership(cat.user_id, user_id)
        return self.repo.update_category(cat, updates)

    def delete_category(self, category_id: str, user_id: str) -> None:
        """Delete custom category ensuring ownership and checking transaction references."""
        cat = self.repo.get_category_by_id(category_id)
        if not cat:
            raise NotFoundException("Category not found")
        check_resource_ownership(cat.user_id, user_id)

        # Disallow deleting if non-deleted transactions use this category
        has_tx = (
            db.session.query(FinancialTransaction.id)
            .filter_by(category_id=cat.id, is_deleted=False)
            .first()
            is not None
        )
        if has_tx:
            raise BadRequestException("Cannot delete category because active transactions reference it")

        self.repo.delete_category(cat)

    # ---------------------------------------------------------
    # Transaction Operations
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
        """Create income or expense transaction with strict ownership and decimal safety."""
        # 1. Verify account ownership
        account = self.get_account(account_id, user_id)
        if account.is_archived:
            raise BadRequestException("Cannot log transactions against an archived account")

        # 2. Verify category ownership if provided
        if category_id:
            cat = self.repo.get_category_by_id(category_id)
            if not cat:
                raise NotFoundException("Category not found")
            check_resource_ownership(cat.user_id, user_id)

        # 3. Create transaction & adjust balance
        return self.repo.create_transaction(
            user_id=user_id,
            account_id=account.id,
            amount=amount,
            transaction_type=transaction_type,
            description=description,
            category_id=category_id,
            transaction_date=transaction_date,
            is_recurring=is_recurring
        )

    def get_transaction(self, transaction_id: str, user_id: str) -> FinancialTransaction:
        """Retrieve a transaction ensuring ownership."""
        tx = self.repo.get_transaction_by_id(transaction_id)
        if not tx or tx.is_deleted:
            raise NotFoundException("Transaction not found")
        check_resource_ownership(tx.user_id, user_id)
        return tx

    def list_transactions(
        self,
        user_id: str,
        account_id: Optional[str] = None,
        category_id: Optional[str] = None,
        transaction_type: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """List transactions with multi-criteria filtering and pagination."""
        items, total = self.repo.list_transactions_for_user(
            user_id=user_id,
            account_id=account_id,
            category_id=category_id,
            transaction_type=transaction_type,
            date_from=date_from,
            date_to=date_to,
            limit=min(max(limit, 1), 100),
            offset=max(offset, 0)
        )
        return {
            "transactions": [t.to_dict() for t in items],
            "total": total,
            "limit": limit,
            "offset": offset,
        }

    def update_transaction(
        self,
        transaction_id: str,
        user_id: str,
        updates: Dict[str, Any]
    ) -> FinancialTransaction:
        """Update transaction fields, verifying account/category ownership and balance effects."""
        tx = self.get_transaction(transaction_id, user_id)

        if "account_id" in updates and updates["account_id"]:
            self.get_account(updates["account_id"], user_id)

        if "category_id" in updates and updates["category_id"]:
            cat = self.repo.get_category_by_id(updates["category_id"])
            if not cat:
                raise NotFoundException("Category not found")
            check_resource_ownership(cat.user_id, user_id)

        return self.repo.update_transaction(tx, updates)

    def delete_transaction(self, transaction_id: str, user_id: str) -> None:
        """Soft-delete transaction and reverse account balance."""
        tx = self.get_transaction(transaction_id, user_id)
        self.repo.soft_delete_transaction(tx)

    # ---------------------------------------------------------
    # Budget Operations & Utilization
    # ---------------------------------------------------------

    def set_budget(
        self,
        user_id: str,
        month: str,
        amount: Decimal,
        category_id: Optional[str] = None,
        currency: str = "USD"
    ) -> Budget:
        """Create or update monthly budget."""
        if category_id:
            cat = self.repo.get_category_by_id(category_id)
            if not cat:
                raise NotFoundException("Category not found")
            check_resource_ownership(cat.user_id, user_id)

        return self.repo.create_or_update_budget(
            user_id=user_id,
            month=month,
            amount=amount,
            category_id=category_id,
            currency=currency
        )

    def list_budgets_with_utilization(self, user_id: str, month: str) -> List[Dict[str, Any]]:
        """List budgets for given month with live calculation of spent amount, remaining, and %."""
        budgets = self.repo.list_budgets_for_month(user_id=user_id, month=month)
        year_str, month_str = month.split("-")
        y, m = int(year_str), int(month_str)
        num_days = calendar.monthrange(y, m)[1]
        start_dt = datetime(y, m, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_dt = datetime(y, m, num_days, 23, 59, 59, tzinfo=timezone.utc)

        # Fetch expense transactions in this month
        txs, _ = self.repo.list_transactions_for_user(
            user_id=user_id,
            transaction_type="expense",
            date_from=start_dt,
            date_to=end_dt,
            limit=1000
        )

        results = []
        for b in budgets:
            if b.category_id:
                spent = sum((t.amount for t in txs if t.category_id == b.category_id), start=Decimal("0.00"))
            else:
                # Overall budget
                spent = sum((t.amount for t in txs), start=Decimal("0.00"))

            spent = spent.quantize(Decimal("0.01"))
            remaining = (b.amount - spent).quantize(Decimal("0.01"))
            utilization_pct = min(100.0, float(round((spent / b.amount) * 100, 1))) if b.amount > 0 else 0.0

            d = b.to_dict()
            d["spent_amount"] = str(spent)
            d["remaining_amount"] = str(remaining)
            d["utilization_percentage"] = utilization_pct
            d["is_over_budget"] = spent > b.amount
            results.append(d)

        return results

    # ---------------------------------------------------------
    # Savings Goals Operations
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
        """Create a savings goal."""
        return self.repo.create_savings_goal(
            user_id=user_id,
            title=title,
            target_amount=target_amount,
            initial_deposit=initial_deposit,
            target_date=target_date,
            currency=currency,
            color_hex=color_hex,
            icon=icon,
            notes=notes
        )

    def get_savings_goal(self, goal_id: str, user_id: str) -> SavingsGoal:
        """Retrieve a savings goal ensuring ownership."""
        goal = self.repo.get_savings_goal_by_id(goal_id)
        if not goal:
            raise NotFoundException("Savings goal not found")
        check_resource_ownership(goal.user_id, user_id)
        return goal

    def list_savings_goals(self, user_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List savings goals with detailed progress."""
        goals = self.repo.list_savings_goals_for_user(user_id=user_id, status=status)
        return [g.to_dict() for g in goals]

    def update_savings_goal(self, goal_id: str, user_id: str, updates: Dict[str, Any]) -> SavingsGoal:
        """Update savings goal."""
        goal = self.get_savings_goal(goal_id, user_id)
        return self.repo.update_savings_goal(goal, updates)

    def add_savings_contribution(
        self,
        goal_id: str,
        user_id: str,
        amount: Decimal,
        account_id: Optional[str] = None,
        note: Optional[str] = None,
        deduct_from_account: bool = False
    ) -> SavingsGoalContribution:
        """Add contribution toward a savings goal."""
        goal = self.get_savings_goal(goal_id, user_id)
        if account_id:
            acc = self.get_account(account_id, user_id)
            if deduct_from_account and acc.balance < amount:
                raise BadRequestException(f"Insufficient funds in account '{acc.name}' for contribution")

        return self.repo.add_savings_contribution(
            goal=goal,
            amount=amount,
            account_id=account_id,
            note=note,
            deduct_from_account=deduct_from_account
        )

    def list_savings_contributions(self, goal_id: str, user_id: str) -> List[Dict[str, Any]]:
        """List contribution history for a savings goal."""
        goal = self.get_savings_goal(goal_id, user_id)
        contributions = self.repo.list_contributions_for_goal(goal.id)
        return [c.to_dict() for c in contributions]

    # ---------------------------------------------------------
    # Financial Analytics & Dashboard Aggregates (Phase 4 & 6)
    # ---------------------------------------------------------

    def get_dashboard_summary(self, user_id: str, month: Optional[str] = None) -> Dict[str, Any]:
        """Compute verified financial metrics: balances, periodic income, expense, savings, and category splits."""
        if not month:
            month = datetime.now(timezone.utc).strftime("%Y-%m")

        y, m = int(month.split("-")[0]), int(month.split("-")[1])
        num_days = calendar.monthrange(y, m)[1]
        start_dt = datetime(y, m, 1, 0, 0, 0, tzinfo=timezone.utc)
        end_dt = datetime(y, m, num_days, 23, 59, 59, tzinfo=timezone.utc)

        # 1. Total Balance across active accounts
        accounts = self.repo.list_accounts_for_user(user_id=user_id, include_archived=False)
        total_balance = sum((a.balance for a in accounts), start=Decimal("0.00")).quantize(Decimal("0.01"))

        # 2. Transactions for target month
        month_txs, _ = self.repo.list_transactions_for_user(
            user_id=user_id,
            date_from=start_dt,
            date_to=end_dt,
            limit=2000
        )

        monthly_income = sum((t.amount for t in month_txs if t.transaction_type == "income"), start=Decimal("0.00")).quantize(Decimal("0.01"))
        monthly_expense = sum((t.amount for t in month_txs if t.transaction_type == "expense"), start=Decimal("0.00")).quantize(Decimal("0.01"))
        monthly_net_savings = (monthly_income - monthly_expense).quantize(Decimal("0.01"))

        # 3. Category Breakdown (Expenses)
        categories = {c.id: c for c in self.repo.list_categories_for_user(user_id)}
        cat_expense_map: Dict[str, Decimal] = {}

        for t in month_txs:
            if t.transaction_type == "expense":
                cid = t.category_id or "uncategorized"
                cat_expense_map[cid] = cat_expense_map.get(cid, Decimal("0.00")) + t.amount

        category_breakdown = []
        for cid, total_cat in cat_expense_map.items():
            cat_obj = categories.get(cid)
            name = cat_obj.name if cat_obj else "Uncategorized"
            color = cat_obj.color_hex if cat_obj else "#6C63FF"
            icon = cat_obj.icon if cat_obj else "pricetag"
            pct = float(round((total_cat / monthly_expense) * 100, 1)) if monthly_expense > 0 else 0.0

            category_breakdown.append({
                "category_id": cid,
                "name": name,
                "color_hex": color,
                "icon": icon,
                "total_amount": str(total_cat.quantize(Decimal("0.01"))),
                "percentage": pct
            })

        category_breakdown.sort(key=lambda x: float(x["total_amount"]), reverse=True)

        # 4. Recent Transactions (latest 6)
        recent_txs, _ = self.repo.list_transactions_for_user(user_id=user_id, limit=6)

        # 5. Budgets for month
        budgets_with_util = self.list_budgets_with_utilization(user_id=user_id, month=month)

        # 6. Active Savings Goals
        savings_goals = self.repo.list_savings_goals_for_user(user_id=user_id, status="in_progress")

        return {
            "month": month,
            "total_balance": str(total_balance),
            "monthly_income": str(monthly_income),
            "monthly_expenses": str(monthly_expense),
            "monthly_net_savings": str(monthly_net_savings),
            "accounts_count": len(accounts),
            "accounts": [a.to_dict() for a in accounts],
            "category_breakdown": category_breakdown,
            "recent_transactions": [t.to_dict() for t in recent_txs],
            "budgets": budgets_with_util,
            "savings_goals": [g.to_dict() for g in savings_goals],
        }

    # ---------------------------------------------------------
    # Local AI Finance Insights (Phase 7)
    # ---------------------------------------------------------

    def get_ai_insights(self, user_id: str, month: Optional[str] = None) -> Dict[str, Any]:
        """Generate verified read-only financial insights using deterministic calculations."""
        summary = self.get_dashboard_summary(user_id, month)

        # Synthesize verified financial facts
        month = summary["month"]
        income = summary["monthly_income"]
        expenses = summary["monthly_expenses"]
        savings = summary["monthly_net_savings"]
        balance = summary["total_balance"]
        top_cats = summary["category_breakdown"][:3]
        top_cats_str = ", ".join(f"{c['name']}: ${c['total_amount']} ({c['percentage']}%)" for c in top_cats) or "None recorded"

        over_budgets = [b for b in summary["budgets"] if b.get("is_over_budget")]
        over_budget_str = ", ".join(f"{b['category_name']} (Over by ${float(b['spent_amount']) - float(b['amount']):.2f})" for b in over_budgets) or "None"

        prompt = (
            f"You are LifeOS Money Management Advisor. Analyze the user's verified financial aggregates below.\n"
            f"MONTH: {month}\n"
            f"CURRENT TOTAL BALANCE: ${balance}\n"
            f"MONTHLY INCOME: ${income}\n"
            f"MONTHLY EXPENSES: ${expenses}\n"
            f"NET SAVINGS: ${savings}\n"
            f"TOP EXPENSE CATEGORIES: {top_cats_str}\n"
            f"OVER BUDGET ALERTS: {over_budget_str}\n\n"
            f"RULES:\n"
            f"1. Base observations strictly on the numbers provided above. Never fabricate numbers.\n"
            f"2. You cannot move money, make payments, or alter transactions.\n"
            f"3. Provide: (a) Spending Summary, (b) Highest Category Observations, (c) Budget Alerts, (d) Savings Recommendations.\n"
            f"Keep your tone encouraging, professional, and concise with bullet points."
        )

        insights_text = (
            f"### Monthly Financial Summary ({month})\n"
            f"- **Net Savings**: ${savings} (Income: ${income}, Expenses: ${expenses})\n"
            f"- **Top Spending**: {top_cats_str}\n"
            f"- **Budget Status**: {'All categories on track.' if not over_budgets else 'Warning: Over budget in ' + over_budget_str}\n"
            f"- **Recommendation**: Continue monitoring your primary expenses to maximize your monthly savings rate."
        )

        # Verified deterministic insights based on user financial transactions
        return {
            "month": month,
            "metrics": {
                "total_balance": balance,
                "monthly_income": income,
                "monthly_expenses": expenses,
                "monthly_net_savings": savings,
            },
            "top_categories": top_cats,
            "over_budget_count": len(over_budgets),
            "insights": insights_text,
            "disclaimer": "Financial insights are educational and read-only. LifeOS never executes transactions or payments."
        }
