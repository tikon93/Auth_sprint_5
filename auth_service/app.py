import json

from flask import Flask
from flask import request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec

from src.db import db
from src.models.api import UserData, ChangePasswordData, SessionData
from src.models.data_models import EncryptedToken
from src.services.session_management import start_session, is_token_valid
from src.services.user_management import create_user, change_password, validate_credentials
from src.settings import POSTGRES_DB, POSTGRES_USER, POSTGRES_HOST, POSTGRES_PASSWORD

app = Flask(__name__)
api_spec = FlaskPydanticSpec("flask")

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'
db.init_app(app)


@app.route('/user', methods=['POST'])
def create_user_handle():
    user_data = UserData(**request.json)
    create_user(user_data.login, user_data.password)
    return jsonify(text="User created")


@app.route('/user', methods=['PATCH'])
def change_password_handle():
    data = ChangePasswordData(**request.json)
    if not change_password(login=data.login, old_password=data.old_password, new_password=data.new_password):
        return "Invalid credentials", 401

    return jsonify(text="Password changed")


@app.route('/session', methods=['POST'])
def start_session_handle():
    user_data = UserData(**request.json)
    trusted_user = validate_credentials(user_data.login, user_data.password)
    if not trusted_user:
        return "Invalid credentials", 401

    user_agent = request.headers.get('User-Agent')
    token = start_session(trusted_user, user_agent)
    return token.serialize()


@app.route('/session', methods=['GET'])
def validate_token_handle():
    token = EncryptedToken.from_bytes(request.data)
    if token is None or not is_token_valid(token):
        return "Invalid session", 401

    return "Session is valid"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
