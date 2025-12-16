from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    slug: str = Field(min_length=1, max_length=255)
    parent_id: int | None = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    slug: str | None = Field(default=None, min_length=1, max_length=255)
    parent_id: int | None = None


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class CategoryList(BaseModel):
    items: list[CategoryRead]
