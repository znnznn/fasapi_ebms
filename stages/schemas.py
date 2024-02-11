from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, model_validator


class CapacitySchema(BaseModel):
    id: int = Field(default=None)
    per_day: int = Field(default=None)
    category_autoid: str = Field(default=None)


class CapacitySchemaIn(BaseModel):
    per_day: Optional[int] = Field(default=None)
    category_autoid: Optional[str] = Field(default=None)


class CommentSchema(BaseModel):
    id: int = Field(default=None)
    user: int = Field(default=None)
    item: int = Field(default=None)
    text: str = Field(default=None)
    created_at: str = Field(default=None)


class CommentSchemaIn(BaseModel):
    user: Optional[int] = Field(default=None)
    item: Optional[int] = Field(default=None)
    text: Optional[str] = Field(default=None)


class StageSchemaIn(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    position: Optional[int] = Field(default=None)
    default: Optional[bool] = Field(default=None)
    color: Optional[str] = Field(default=None)
    flow_id: Optional[int] = Field(default=None, alias="flow")

    class Config:
        allow_population_by_field_name = True


class StageSchema(StageSchemaIn):
    id: int = Field(default=None)
    flow_id: int | None = Field(default=None, serialization_alias="flow")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class FlowSchema(BaseModel):
    id: int = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    position: int = Field(default=None)
    category_autoid: str = Field(default=None)
    stages: List[StageSchema] | None
    created_at: datetime = Field(default=None)


class FlowSchemaIn(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    position: Optional[int] = Field(default=None)
    category_autoid: Optional[str] = Field(default=None)


class FlowSchemaOut(FlowSchemaIn):
    id: int


class ItemSchema(BaseModel):
    id: int = Field(default=None)
    order: str = Field(default=None)
    origin_item: str = Field(default=None)
    flow: FlowSchema | None = Field(default=None)
    priority: int = Field(default=None)
    production_date: datetime | None = Field(default=None)
    stage: StageSchema | None = Field(default=None)
    comments: List[CommentSchema] | None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class ItemSchemaIn(BaseModel):
    order: Optional[str] = Field(default=None)
    origin_item: Optional[str] = Field(default=None)
    flow_id: Optional[int] = Field(default=None, alias="flow")
    priority: Optional[int] = Field(default=None)
    production_date: Optional[datetime] = Field(default=None)
    stage_id: Optional[int] = Field(default=None, alias="stage")

    class Config:
        arbitrary_types_allowed = True


class ItemSchemaOut(ItemSchemaIn):
    id: int
    flow_id: int = Field(None, serialization_alias="flow")
    stage_id: int = Field(None, serialization_alias="stage")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class SalesOrderSchema(BaseModel):
    id: int = Field(default=None)
    order: str = Field(default=None)
    packages: int = Field(default=None)
    location: int = Field(default=None)
    priority: int = Field(default=None)
    created_at: datetime = Field(default=None)


class SalesOrderSchemaIn(BaseModel):
    order: Optional[str] = Field(default=None)
    packages: Optional[int] = Field(default=None)
    location: Optional[int] = Field(default=None)
    priority: Optional[int] = Field(default=None)
    created_at: datetime = Field(default=datetime.now())
