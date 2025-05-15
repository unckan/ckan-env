import pytest


@pytest.fixture
def clean_db(reset_db):
    reset_db()
