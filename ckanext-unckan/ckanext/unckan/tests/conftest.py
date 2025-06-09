import pytest


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    migrate_db_for("activity")
    migrate_db_for("announcements")
    migrate_db_for("api_tracking")
    reset_db()
