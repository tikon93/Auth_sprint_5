from flask import request, jsonify
from flask_pydantic_spec import Request
from pydantic import BaseModel, constr

from app import app, api_spec
from src.services.user_management import create_user


class UserData(BaseModel):
    login: constr(min_length=6, max_length=40)
    password: constr(min_length=8)


@app.route('/user', methods=['GET'])
def create_user_handle():
    return "FOO"

@app.route('/user', methods=['POST'])
@api_spec.validate(body=Request(UserData))
def create_user_handle():
    user_data = UserData(**request.json)
    create_user(user_data.login, user_data.password)
    return jsonify(text="User created")


