import logging
from typing import Optional, Union, List
from uuid import UUID

import backoff
from pydantic.error_wrappers import ValidationError
from redis.exceptions import ConnectionError
from sqlalchemy.exc import OperationalError
from user_agents import parse

from src.db import redis_db, db
from src.models.data_models import EncryptedToken, DecryptedToken, UserSignIn, User, UserDeviceTypes
from src.settings import TOKEN_LIFETIME_SEC, SERVICE_BACKOFF_TIMEOUT
from src.utils.encryption import decrypt_token, encrypt_token
from src.utils.encryption import get_random_string

logger = logging.getLogger(__name__)


def _get_redis_key_for_token(token: DecryptedToken) -> str:
    return f"{token.user_id}_{token.user_agent}"


def _put_token_to_storage(token: DecryptedToken):
    key = _get_redis_key_for_token(token)
    redis_db.setex(key, TOKEN_LIFETIME_SEC, token.token_body)
    logger.debug("Token successfully put to database")


def _get_token_from_db(reference_token: DecryptedToken) -> Optional[DecryptedToken]:
    key = _get_redis_key_for_token(reference_token)
    if not (database_token := redis_db.get(key)):
        logger.debug("Corresponding token is not found in database")
        return None

    token = DecryptedToken(
        user_id=reference_token.user_id,
        user_agent=reference_token.user_agent,
        token_body=database_token
    )
    return token


@backoff.on_exception(backoff.expo, exception=(ConnectionError,), max_time=SERVICE_BACKOFF_TIMEOUT)
def invalidate_session(token_data: Union[bytes, str]):
    if (decrypted_token := decrypt_and_validate_token(token_data)) is None:
        logger.debug("Nothing to invalidate - session is not valid already")

    redis_db.delete(_get_redis_key_for_token(decrypted_token))
    logger.debug("Successfully invalidated session")


def _add_user_sign_in(user: User, user_agent: str):
    parsed_ua = parse(user_agent)
    if parsed_ua.is_pc:
        device_type = UserDeviceTypes.pc.value
    elif parsed_ua.is_mobile:
        device_type = UserDeviceTypes.mobile.value
    else:
        device_type = UserDeviceTypes.smart_tv.value
    session_log = UserSignIn(user_agent=user_agent, user_id=user.id, user_device_type=device_type)
    db.session.add(session_log)
    db.session.commit()


@backoff.on_exception(backoff.expo, exception=(ConnectionError, OperationalError), max_time=SERVICE_BACKOFF_TIMEOUT)
def start_session(user: User, user_agent: str) -> EncryptedToken:
    _add_user_sign_in(user, user_agent)
    token = DecryptedToken(user_id=user.id, user_agent=user_agent, token_body=get_random_string(24))
    _put_token_to_storage(token)
    return encrypt_token(token.json())


@backoff.on_exception(backoff.expo, exception=(ConnectionError,), max_time=SERVICE_BACKOFF_TIMEOUT)
def decrypt_and_validate_token(token_data: Union[bytes, str]) -> Optional[DecryptedToken]:
    token = EncryptedToken.deserialize(token_data)
    if token is None:
        logger.info("Token deserialization failed")
        return None

    try:
        decrypted_token_data = decrypt_token(token)
    except ValueError:
        logger.info("Token decryption failed")
        return None

    try:
        decrypted_token = DecryptedToken.parse_raw(decrypted_token_data)
    except ValidationError:
        logger.info("Invalid token structure")
        return None

    if (storage_token := _get_token_from_db(decrypted_token)) is None:
        logger.info("Token for this user is not found in storage - probably it's expired or never created")
        return None

    if storage_token.token_body != decrypted_token.token_body:
        logger.info("Token body is invalid")
        return None

    return decrypted_token


def is_session_valid(token_data: Union[bytes, str]) -> bool:
    return decrypt_and_validate_token(token_data) is not None


@backoff.on_exception(backoff.expo, exception=(OperationalError,), max_time=SERVICE_BACKOFF_TIMEOUT)
def get_login_history(user_id: UUID, page: int = 1, per_page: int = 10) -> List[UserSignIn]:
    history_log = UserSignIn.query.filter_by(user_id=user_id).order_by(
        UserSignIn.logged_in_by.desc()).paginate(page, per_page, error_out=False).items

    return history_log
