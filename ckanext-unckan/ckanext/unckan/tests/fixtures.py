import pytest


# Use 'with_plugins' fixture in ALL tests
@pytest.fixture(autouse=True)
def load_standard_plugins(with_plugins):
    pass
