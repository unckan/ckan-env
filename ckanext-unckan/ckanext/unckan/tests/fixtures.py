import pytest


# Use 'with_plugins' fixture in ALL tests
@pytest.fixture(autouse=True)
def load_standard_plugins(with_plugins):
    pass


@pytest.fixture
def clean_db(reset_db, migrate_db_for):
    migrate_db_for("activity")
    migrate_db_for("announcements")
    migrate_db_for("api_tracking")
    reset_db()
