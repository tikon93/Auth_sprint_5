import logging
from typing import Optional

from pydantic.error_wrappers import ValidationError

from src.db import redis_db, db
from src.models.data_models import EncryptedToken, DecryptedToken, UserSignIn, User
from src.settings import TOKEN_LIFETIME_SEC
from src.utils.encryption import decrypt_token, encrypt_token
from src.utils.encryption import get_random_string

logger = logging.getLogger(__name__)


def get_redis_key_for_token(token: DecryptedToken) -> str:
    return f"{token.user_id}_{token.user_agent}"


def put_token_to_storage(token: DecryptedToken):
    key = get_redis_key_for_token(token)
    redis_db.setex(key, TOKEN_LIFETIME_SEC, token.token_body)
    logger.debug("Token successfully put to database")


def get_token_from_db(reference_token: DecryptedToken) -> Optional[DecryptedToken]:
    key = get_redis_key_for_token(reference_token)
    if not (database_token := redis_db.get(key)):
        logger.debug("Corresponding token is not found in database")
        return None

    token = DecryptedToken(
        user_id=reference_token.user_id,
        user_agent=reference_token.user_agent,
        token_body=database_token
    )
    return token


def invalidate_session(encrypted_token: EncryptedToken):
    if (decrypted_token := decrypt_and_validate_token(encrypted_token)) is None:
        logger.debug("Nothing to invalidate - session is not valid already")

    redis_db.delete(get_redis_key_for_token(decrypted_token))
    logger.debug("Successfully invalidated session")


def user_sign_in(user: User, user_agent: str):
    session_log = UserSignIn(user_agent=user_agent, user_id=user.id, user_device_type="mobile")
    db.session.add(session_log)
    db.session.commit()


def start_session(user: User, user_agent: str) -> EncryptedToken:
    user_sign_in(user, user_agent)
    token = DecryptedToken(user_id=user.id, user_agent=user_agent, token_body=get_random_string(24))
    put_token_to_storage(token)
    return encrypt_token(token.json())


def decrypt_and_validate_token(token: EncryptedToken) -> Optional[DecryptedToken]:
    try:
        decrypted_token_data = decrypt_token(token)
    except ValueError:
        logger.error("Token decryption failed")
        return None

    try:
        decrypted_token = DecryptedToken.parse_raw(decrypted_token_data)
    except ValidationError:
        logger.error("Invalid token structure")
        return None

    if (storage_token := get_token_from_db(decrypted_token)) is None:
        logger.info("Token for this user is not found in storage - probably it's expired or never created")
        return None

    if storage_token.token_body != decrypted_token.token_body:
        logger.error("Token body is invalid")
        return None

    return decrypted_token


def is_token_valid(token: EncryptedToken) -> bool:
    return decrypt_and_validate_token(token) is not None
