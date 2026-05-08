"""
Install a firebase_admin mock into sys.modules at collection time —
before any test module is imported — so no test ever touches real credentials
and no firebase-credentials.json is required.

The auth attribute is set explicitly on the firebase_admin mock
so that `from firebase_admin import auth as firebase_auth` in auth/__init__.py
binds to the same MagicMock object that tests later configure.
"""
import sys
from unittest.mock import MagicMock

_mock_firebase_admin = MagicMock()
_mock_firebase_admin._apps = {}
_mock_firebase_auth = MagicMock()
_mock_firebase_admin.auth = _mock_firebase_auth  # same object as sys.modules entry

sys.modules['firebase_admin'] = _mock_firebase_admin
sys.modules['firebase_admin.auth'] = _mock_firebase_auth
sys.modules['firebase_admin.credentials'] = MagicMock()
