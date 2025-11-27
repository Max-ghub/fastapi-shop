from pydantic import BaseModel


class ProductImageUploadResponse(BaseModel):
    object_key: str
    is_main: bool
    upload_url: str


class ProductImageRead(BaseModel):
    id: int
    object_key: str
    is_main: bool
    url: str
