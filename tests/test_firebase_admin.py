"""
firebase_admin is a MagicMock installed by conftest.py — set ._apps directly
to simulate initialized/uninitialized states without real credentials.
"""
import firebase_admin  # gets the MagicMock from conftest.py


def test_get_firebase_app_initializes_on_first_call():
    """Should call initialize_app exactly once when _apps is empty."""
    firebase_admin._apps = {}
    firebase_admin.initialize_app.reset_mock()

    from auth.firebase_admin import get_firebase_app
    get_firebase_app()

    firebase_admin.initialize_app.assert_called_once()


def test_get_firebase_app_skips_init_when_already_initialized():
    """Should skip initialize_app when a Firebase app already exists."""
    from unittest.mock import MagicMock
    mock_app = MagicMock()
    firebase_admin._apps = {'[DEFAULT]': mock_app}
    firebase_admin.initialize_app.reset_mock()
    firebase_admin.get_app.return_value = mock_app

    from auth.firebase_admin import get_firebase_app
    result = get_firebase_app()

    firebase_admin.initialize_app.assert_not_called()
    assert result == mock_app
