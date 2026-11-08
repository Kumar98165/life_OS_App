# LifeOS – Authorization & Access Control Guidelines

## 1. Zero Trust User Isolation
In LifeOS, **User A cannot access or mutate User B's resources under any circumstances**.

### Rules of Authorization:
1. **Never Accept Client-Supplied User IDs for Authorization**:
   - The user ID passed in route parameters or request JSON is never trusted.
   - The authoritative user identity is extracted strictly from the cryptographically verified JWT payload (`get_jwt_identity()`).
2. **Resource Ownership Verification**:
   - All repositories and services verify that the entity's `user_id` matches the authenticated `current_user_id`:
     ```python
     from app.core.security import check_resource_ownership

     # Raises ForbiddenException if mismatch
     check_resource_ownership(resource_user_id=task.user_id, current_user_id=current_user_id)
     ```
3. **Privacy-Preserving Not Found**:
   - For single-resource queries (e.g. `GET /tasks/<id>`), services query using both the resource ID and user ID:
     ```python
     stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user_id)
     ```
   - If an unauthorized user guesses an ID, the API returns `404 Not Found`, denying attackers knowledge of whether the resource exists in another account.

---

## 2. Protected Profile Attributes
In `PATCH /api/v1/users/me`, clients may only update permitted public attributes:
- **Permitted**: `full_name`, `avatar_url`.
- **Protected (Forbidden)**: `id`, `email`, `password_hash`, `is_active`, `created_at`, `updated_at`.
- Schema enforcement uses Pydantic's `model_config = ConfigDict(extra="forbid")`, automatically returning `422 Unprocessable Entity` if extraneous fields are submitted.

