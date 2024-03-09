from enum import Enum
from typing import TypeVar

import typing_extensions
from pydantic import BaseModel

from common.models import DefaultBase, EBMSBase

ModelType = TypeVar("ModelType", bound=DefaultBase)
OriginModelType = TypeVar("OriginModelType", bound=EBMSBase)
InputSchemaType = TypeVar("InputSchemaType", bound=BaseModel)

IncEx: typing_extensions.TypeAlias = 'set[int] | set[str] | dict[int, Any] | dict[str, Any] | None'


class Role(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    WORKER = "worker"

    ROLE_CHOICES = [
        (ADMIN, "admin"),
        (MANAGER, "manager"),
        (WORKER, "worker"),
    ]
