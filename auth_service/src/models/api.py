from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class UserData(BaseModel):
    login: str = Field(min_length=6, max_length=40)
    password: str = Field(min_length=8)


class ChangePasswordData(BaseModel):
    login: str
    old_password: str
    new_password: str = Field(min_length=8)


class HistoryEntry(BaseModel):
    logged_in_at: datetime
    user_agent: str


class HistoryLog(BaseModel):
    log: List[HistoryEntry]


class SerializedToken(BaseModel):
    token: str
