from sqlalchemy import inspect

from app.db.session import engine


def test_tables_exist():
    insp = inspect(engine)
    for t in ["users", "cards", "reviews"]:
        assert insp.has_table(t)
