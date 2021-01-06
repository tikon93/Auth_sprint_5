from pydantic import BaseModel, constr


class UserData(BaseModel):
    login: constr(min_length=6, max_length=40)
    password: constr(min_length=8)


class ChangePasswordData(BaseModel):
    login: str
    old_password: str
    new_password: constr(min_length=8)


class SessionData(BaseModel):
    nonce: str
    digest: str
    token: str
