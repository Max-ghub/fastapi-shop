from pydantic import BaseModel, ConfigDict


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    parent_id: int | None


class CategoryCreate(BaseModel):
    name: str
    slug: str
    parent_id: int | None
