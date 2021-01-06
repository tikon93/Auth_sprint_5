import logging
from typing import Optional

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from src.db import db
from src.models import User

logger = logging.getLogger(__name__)
ph = PasswordHasher()


def create_user(login: str, password: str):
    logger.debug(f"Creating user {login}")
    user = User(login=login, password=ph.hash(password))
    #todo: handle duplicated login
    db.session.add(user)
    db.session.commit()


def validate_credentials(login: str, password: str) -> Optional[User]:
    logger.debug(f"Validating {login} data correctness")
    user = User.query.filter_by(login=login).first()
    if not user:
        logger.error(f"Provided user {login} not found")
        return None

    try:
        ph.verify(user.password, password)
    except VerifyMismatchError:
        logger.error(f"Provided password for {login} not found")
        return None

    if ph.check_needs_rehash(user.password):
        logger.debug(f"Updating password hash for {login}")
        user.password = ph.hash(password)
        db.session.commit()

    return user


def change_password(login: str, old_password: str, new_password: str) -> bool:
    if (user := validate_credentials(login=login, password=old_password)) is None:
        return False

    logger.debug(f"Changing password for {login}")
    user.password = ph.hash(new_password)
    db.session.commit()
    return True





