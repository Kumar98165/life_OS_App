# LifeOS Personal Finance REST API Reference

Base URL: `/api/v1/finance`  
Authentication: `Authorization: Bearer <access_token>`

## 1. Dashboard & AI Insights

### GET `/api/v1/finance/dashboard`
Returns the verified high-level financial summary for a month.
- **Query Params**: `month` (optional, format: `YYYY-MM`, default: current month)
- **Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "month": "2026-11",
    "total_balance": "5420.50",
    "monthly_income": "3500.00",
    "monthly_expenses": "1820.25",
    "monthly_net_savings": "1679.75",
    "accounts": [...],
    "category_breakdown": [
      {
        "category_id": "...",
        "name": "Groceries",
        "color_hex": "#48BB78",
        "icon": "basket",
        "total_amount": "450.00",
        "percentage": 24.7
      }
    ],
    "recent_transactions": [...],
    "budgets": [...],
    "savings_goals": [...]
  }
}
```

### GET `/api/v1/finance/insights`
Returns local AI-synthesized financial observations and verified metric ratios.
- **Query Params**: `month` (optional, format `YYYY-MM`)
- **Response**: `200 OK`
```json
{
  "success": true,
  "data": {
    "month": "2026-11",
    "total_balance": "5420.50",
    "monthly_income": "3500.00",
    "monthly_expenses": "1820.25",
    "monthly_net_savings": "1679.75",
    "savings_rate": 48.0,
    "top_spending_category": {
      "name": "Housing & Rent",
      "amount": "1200.00",
      "percentage": 65.9
    },
    "budget_status": {
      "total_budgets": 3,
      "over_budget_count": 0
    },
    "savings_status": {
      "active_goals_count": 2,
      "total_target": "5000.00",
      "total_saved": "1800.00"
    },
    "ai_observations": "Your savings rate is a robust 48.0% this month. All budgets are currently within limits.",
    "generated_at": "2026-11-08T14:00:00Z"
  }
}
```

---

## 2. Accounts Endpoints

### GET `/api/v1/finance/accounts`
- **Query Params**: `include_archived` (boolean, default: `false`)
- **Response**: `200 OK` with `{ "accounts": [...] }`

### POST `/api/v1/finance/accounts`
- **Request Body**:
```json
{
  "name": "Checking Account",
  "account_type": "bank",
  "balance": "1000.00",
  "currency": "USD",
  "color_hex": "#6C63FF",
  "icon": "card",
  "is_default": true
}
```
- **Response**: `201 Created` with `{ "account": { ... } }`

### PUT `/api/v1/finance/accounts/{id}`
- **Request Body**: Partial update (`name`, `account_type`, `color_hex`, `icon`, `is_archived`, `is_default`)
- **Response**: `200 OK`

### DELETE `/api/v1/finance/accounts/{id}`
- **Response**: `200 OK`

---

## 3. Categories Endpoints

### GET `/api/v1/finance/categories`
- **Query Params**: `category_type` (optional: `income` | `expense` | `transfer`)
- **Response**: `200 OK` with `{ "categories": [...] }`

### POST `/api/v1/finance/categories`
- **Request Body**:
```json
{
  "name": "Streaming & Entertainment",
  "category_type": "expense",
  "color_hex": "#ED8936",
  "icon": "tv"
}
```
- **Response**: `201 Created`

### PUT `/api/v1/finance/categories/{id}`
- **Request Body**: `name`, `color_hex`, `icon`
- **Response**: `200 OK`

### DELETE `/api/v1/finance/categories/{id}`
- **Response**: `200 OK` (HTTP 400 if active transactions reference this category, or if system category)

---

## 4. Transactions Endpoints

### GET `/api/v1/finance/transactions`
- **Query Params**: `account_id`, `category_id`, `transaction_type`, `date_from`, `date_to`, `page`, `limit`
- **Response**: `200 OK` with `{ "transactions": [...], "total": 45, "page": 1, "limit": 20 }`

### GET `/api/v1/finance/transactions/{id}`
- **Response**: `200 OK` with `{ "transaction": { ... } }`

### POST `/api/v1/finance/transactions`
- **Request Body**:
```json
{
  "account_id": "uuid-account-id",
  "category_id": "uuid-category-id",
  "amount": "45.99",
  "transaction_type": "expense",
  "description": "Weekly groceries",
  "transaction_date": "2026-11-08T12:00:00Z",
  "is_recurring": false
}
```
- **Response**: `201 Created`

### PUT `/api/v1/finance/transactions/{id}`
- **Request Body**: Partial update
- **Response**: `200 OK`

### DELETE `/api/v1/finance/transactions/{id}`
- Soft deletes transaction and restores parent account balance.
- **Response**: `200 OK`

---

## 5. Budgets Endpoints

### GET `/api/v1/finance/budgets`
- **Query Params**: `month` (format: `YYYY-MM`)
- **Response**: `200 OK` with `{ "budgets": [...] }` including live `spent_amount`, `remaining_amount`, `utilization_percentage`, `is_over_budget`.

### POST `/api/v1/finance/budgets`
- **Request Body**:
```json
{
  "category_id": "uuid-category-id",
  "month": "2026-11",
  "amount": "500.00"
}
```
- **Response**: `201 Created`

### PUT `/api/v1/finance/budgets/{id}`
- **Request Body**: `{ "amount": "600.00" }`
- **Response**: `200 OK`

### DELETE `/api/v1/finance/budgets/{id}`
- **Response**: `200 OK`

---

## 6. Savings Goals Endpoints

### GET `/api/v1/finance/savings-goals`
- **Query Params**: `status` (optional: `in_progress` | `completed` | `archived`)
- **Response**: `200 OK` with `{ "savings_goals": [...] }`

### GET `/api/v1/finance/savings-goals/{id}`
- **Response**: `200 OK` with goal detail and nested contribution history.

### POST `/api/v1/finance/savings-goals`
- **Request Body**:
```json
{
  "title": "New Tech Setup",
  "target_amount": "2500.00",
  "initial_deposit": "200.00",
  "target_date": "2026-12-31T23:59:59Z",
  "notes": "Monitor, keyboard, ergonomic chair"
}
```
- **Response**: `201 Created`

### PUT `/api/v1/finance/savings-goals/{id}`
- **Request Body**: Partial update
- **Response**: `200 OK`

### DELETE `/api/v1/finance/savings-goals/{id}`
- **Response**: `200 OK`

### POST `/api/v1/finance/savings-goals/{id}/contributions`
- **Request Body**:
```json
{
  "amount": "150.00",
  "account_id": "uuid-account-id",
  "note": "Bi-weekly savings deposit"
}
```
- **Response**: `201 Created` with updated goal and contribution ledger entry.

