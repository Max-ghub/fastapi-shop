from pydantic import BaseModel, ConfigDict, EmailStr


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: str


class UserIn(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserIn):
    password: str
