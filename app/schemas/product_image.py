from pydantic import BaseModel, Field


class ProductImageBase(BaseModel):
    object_key: str = Field(min_length=1, max_length=255)
    is_main: bool = False

class ProductImageUploadResponse(ProductImageBase):
    upload_url: str


class ProductImageRead(ProductImageBase):
    id: int
    url: str

class ProductImageList(BaseModel):
    items: list[ProductImageRead]
