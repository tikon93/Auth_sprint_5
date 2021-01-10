import base64
import datetime
import enum
import json
import logging
import uuid
from dataclasses import dataclass, asdict
from typing import Union

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Enum

from src.db import db

logger = logging.getLogger(__name__)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    login = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __init__(self, login, password):
        self.login = login
        self.password = password

    def __repr__(self):
        return f'<User {self.login}>'


class UserDeviceTypes(enum.Enum):
    mobile = "mobile"
    pc = "pc"
    smart_tv = "smart_tv"


class UserSignIn(db.Model):
    __tablename__ = 'users_sign_in'

    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('users.id'))
    logged_in_by = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_agent = db.Column(db.Text)
    user_device_type = db.Column(
        Enum(*[device_type.value for device_type in UserDeviceTypes], name="device_types_enum")
    )
    __mapper_args__ = {'primary_key': [user_id, logged_in_by]}

    def __repr__(self):
        return f'<UserSignIn {self.user_id}:{self.logged_in_by}>'


@dataclass
class EncryptedToken:
    nonce: bytes
    digest: bytes
    token: bytes

    def serialize(self) -> str:
        str_dict = {k: base64.b64encode(v).decode("ascii") for k, v in asdict(self).items()}
        dumped_string = json.dumps(str_dict)
        return base64.b64encode(dumped_string.encode('ascii')).decode('ascii')  # ready-to-transfer string

    @classmethod
    def deserialize(cls, data: Union[bytes, str]):
        try:
            if isinstance(data, str):
                data = data.encode("ascii")

            message_bytes = base64.b64decode(data)
            data_dict = json.loads(message_bytes.decode('ascii'))
            bytes_dict = {k: base64.b64decode(v) for k, v in data_dict.items()}
            return cls(**bytes_dict)
        except Exception as e:
            logger.error(f"Token deserialization error: {type(e)} {e}")


class DecryptedToken(BaseModel):
    user_id: uuid.UUID
    user_agent: str
    token_body: str
