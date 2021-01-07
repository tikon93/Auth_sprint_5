from flask import Flask
from flask import request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request

from src.db import db
from src.utils.wrappers import check_auth
from src.models.api import UserData, ChangePasswordData, SerializedToken, HistoryLog
from src.models.data_models import EncryptedToken
from src.services.session_management import start_session, is_session_valid, invalidate_session, get_login_history, \
    decrypt_and_validate_token
from src.services.user_management import create_user, change_password, validate_credentials
from src.settings import POSTGRES_DB, POSTGRES_USER, POSTGRES_HOST, POSTGRES_PASSWORD

app = Flask(__name__)
api = FlaskPydanticSpec("Auth")

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}'
db.init_app(app)


@app.route('/user', methods=['POST'])
@api.validate(body=Request(UserData))
def create_user_handle():

    user_data = UserData(**request.json)
    create_user(user_data.login, user_data.password)
    return jsonify(text="User created")


@app.route('/user', methods=['PATCH'])
@api.validate(body=Request(ChangePasswordData))
def change_password_handle():
    data = ChangePasswordData(**request.json)
    if not change_password(login=data.login, old_password=data.old_password, new_password=data.new_password):
        return "Invalid credentials", 401

    return jsonify(text="Password changed")


@app.route('/login', methods=['POST'])
@api.validate(body=Request(UserData), resp=Response(HTTP_200=SerializedToken))
def start_session_handle():
    user_data = UserData(**request.json)
    trusted_user = validate_credentials(user_data.login, user_data.password)
    if not trusted_user:
        return "Invalid credentials", 401

    user_agent = request.headers.get('User-Agent')
    token = start_session(trusted_user, user_agent)
    return jsonify(token=token.serialize())


@app.route('/session', methods=['GET'])
@api.validate(body=Request(SerializedToken))
def validate_session_handle():
    if is_session_valid(request.json["token"]):
        return "OK"

    return "Invalid session data", 401


@app.route('/logout', methods=['POST'])
@check_auth
def end_session_handle():
    token = EncryptedToken.deserialize(request.headers.get('Authorization'))
    invalidate_session(token)
    return "OK"


@app.route('/login/history', methods=['GET'])
@api.validate(resp=Response(HTTP_200=HistoryLog))
@check_auth
def get_login_history_handle():
    user_id = decrypt_and_validate_token(request.headers.get('Authorization')).user_id
    history_entries = get_login_history(user_id=user_id)
    return jsonify(log=[
        {"user_agent": entry.user_agent, "login_time": entry.logged_in_by} for entry in history_entries
    ])


if __name__ == '__main__':
    api.register(app)
    app.run(host='0.0.0.0')
