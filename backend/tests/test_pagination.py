from app.models import User
from app.core.pagination import paginate_query


def test_pagination_helper(app):
    """Test safe pagination on query."""
    with app.app_context():
        # Create dummy users
        for i in range(15):
            u = User(email=f"page_user_{i}@lifeos.io", full_name=f"User {i}")
            u.set_password("Password123!")
            app.extensions["sqlalchemy"].session.add(u)
        app.extensions["sqlalchemy"].session.commit()

        # Query page 1 with per_page 5
        items, meta = paginate_query(User.query, page=1, per_page=5)
        assert len(items) == 5
        assert meta["page"] == 1
        assert meta["per_page"] == 5
        assert meta["total"] >= 15
        assert meta["total_pages"] >= 3
        assert meta["has_next"] is True
        assert meta["has_prev"] is False

        # Query page 2
        items2, meta2 = paginate_query(User.query, page=2, per_page=5)
        assert len(items2) == 5
        assert meta2["page"] == 2
        assert meta2["has_prev"] is True

        # Query with extreme per_page capped by max_per_page
        _, meta_capped = paginate_query(User.query, page=1, per_page=500, max_per_page=50)
        assert meta_capped["per_page"] == 50

