from pydantic import BaseModel, ConfigDict, EmailStr


class UserIn(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserIn):
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str


class UserInDB(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    role: str
