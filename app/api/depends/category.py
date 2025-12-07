from typing import Annotated

from fastapi import Depends

from app.api.depends.db import SessionDep
from app.services.category import CategoryService


def _get_categories_service(db_session: SessionDep) -> CategoryService:
    return CategoryService(db_session)


CategoryServiceDep = Annotated[CategoryService, Depends(_get_categories_service)]

__all__ = ["CategoryServiceDep"]
