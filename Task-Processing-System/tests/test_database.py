from app import database


def test_database_uses_parameterized_queries() -> None:
    source = open("app/database.py", encoding="utf-8").read()
    assert "WHERE id = %s" in source
    assert "INSERT INTO jobs" in source
    assert "sqlite" not in source.lower()