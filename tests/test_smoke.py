"""Minimal smoke test — verifies app can be imported."""
from app.main import app


def test_app_exists():
    assert app is not None
