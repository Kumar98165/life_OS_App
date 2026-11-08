import math
from typing import Tuple, List, Any, Dict
from sqlalchemy.orm import Query


def paginate_query(
    query: Query,
    page: int = 1,
    per_page: int = 20,
    max_per_page: int = 100
) -> Tuple[List[Any], Dict[str, Any]]:
    """Safely paginate a SQLAlchemy query, returning (items, meta)."""
    # Guard against invalid inputs
    page = max(1, int(page or 1))
    per_page = min(max_per_page, max(1, int(per_page or 20)))

    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1
    items = query.offset((page - 1) * per_page).limit(per_page).all()

    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }

    return items, meta

