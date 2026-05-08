import os
import logging
from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from firebase_admin import auth as firebase_auth
from .firebase_admin import get_firebase_app

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__, template_folder='templates')


@auth_bp.route('/auth/login')
def login():
    return render_template(
        'auth/login.html',
        firebase_api_key=os.environ.get('FIREBASE_API_KEY', ''),
        firebase_auth_domain=os.environ.get('FIREBASE_AUTH_DOMAIN', ''),
        firebase_project_id=os.environ.get('FIREBASE_PROJECT_ID', ''),
    )


@auth_bp.route('/auth/verify', methods=['POST'])
def verify():
    get_firebase_app()
    data = request.get_json()
    if not data or 'idToken' not in data:
        return jsonify({'status': 'error', 'message': 'Token não fornecido.'}), 400
    try:
        decoded = firebase_auth.verify_id_token(data['idToken'], clock_skew_seconds=60)
        session['user'] = {
            'uid': decoded['uid'],
            'email': decoded.get('email', ''),
            'name': decoded.get('name', ''),
            'photo': decoded.get('picture', ''),
        }
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        logger.error("verify_id_token falhou: %s", e, exc_info=True)
        return jsonify({'status': 'error', 'message': 'Token inválido. Tente novamente.'}), 401


@auth_bp.route('/auth/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))
