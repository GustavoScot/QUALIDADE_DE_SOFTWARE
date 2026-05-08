import os
import firebase_admin
from firebase_admin import credentials


def get_firebase_app():
    if not firebase_admin._apps:
        cred_path = os.path.join(
            os.path.dirname(__file__), '..', 'firebase-credentials.json'
        )
        cred = credentials.Certificate(os.path.abspath(cred_path))
        firebase_admin.initialize_app(cred)
    return firebase_admin.get_app()
