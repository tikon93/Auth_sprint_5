from functools import wraps

from flask import request, abort

from src.services.session_management import is_session_valid


def check_auth(api_method):
    @wraps(api_method)
    def check_session(*args, **kwargs):
        session_data = request.headers.get('Authorization')
        if session_data is not None and is_session_valid(session_data):
            return api_method(*args, **kwargs)

        else:
            abort(401)

    return check_session
