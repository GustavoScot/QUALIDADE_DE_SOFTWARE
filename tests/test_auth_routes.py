"""
firebase_admin is already mocked by conftest.py.
Patch verify_id_token via firebase_admin.auth (the shared mock object) —
NOT via 'auth.firebase_auth', which is an alias, not a separate object.
"""
import pytest
import firebase_admin  # MagicMock from conftest.py


@pytest.fixture
def client():
    """Flask test client — firebase_admin already mocked by conftest.py."""
    import app as flask_module
    flask_module.app.config['TESTING'] = True
    flask_module.app.config['SECRET_KEY'] = 'test-secret'
    flask_module.app.config['WTF_CSRF_ENABLED'] = False
    with flask_module.app.test_client() as c:
        with flask_module.app.app_context():
            yield c


def test_login_page_returns_200(client):
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data


def test_verify_returns_400_when_token_missing(client):
    response = client.post('/auth/verify', json={})
    assert response.status_code == 400
    assert response.get_json()['status'] == 'error'


def test_verify_returns_401_on_invalid_token(client):
    firebase_admin.auth.verify_id_token.side_effect = Exception('bad token')
    try:
        response = client.post('/auth/verify', json={'idToken': 'bad'})
    finally:
        firebase_admin.auth.verify_id_token.side_effect = None
    assert response.status_code == 401
    assert response.get_json()['status'] == 'error'


def test_verify_sets_session_and_returns_ok(client):
    decoded = {
        'uid': 'user123',
        'email': 'test@example.com',
        'name': 'Test User',
        'picture': 'https://photo.url',
    }
    firebase_admin.auth.verify_id_token.return_value = decoded
    firebase_admin.auth.verify_id_token.side_effect = None
    response = client.post('/auth/verify', json={'idToken': 'valid-token'})
    assert response.status_code == 200
    assert response.get_json()['status'] == 'ok'


def test_logout_clears_session_and_redirects(client):
    with client.session_transaction() as sess:
        sess['user'] = {'uid': 'abc', 'email': 'x@x.com', 'name': 'X', 'photo': ''}
    response = client.get('/auth/logout')
    assert response.status_code == 302
    assert '/auth/login' in response.headers['Location']
    with client.session_transaction() as sess:
        assert 'user' not in sess
