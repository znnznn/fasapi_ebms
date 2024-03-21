from datetime import datetime, date
from typing import List, Optional

from pydantic import BaseModel, Field, root_validator, model_validator, field_validator


class CapacitySchema(BaseModel):
    id: int = Field(default=None)
    per_day: int = Field(default=None)
    category_autoid: str = Field(default=None)


class CapacityPaginatedSchema(BaseModel):
    count: int
    results: List[CapacitySchema]


class CapacitySchemaIn(BaseModel):
    per_day: Optional[int] = Field(default=None)
    category_autoid: Optional[str] = Field(default=None)


class CommentSchema(BaseModel):
    id: int = Field(default=None)
    user_id: int = Field(default=None, serialization_alias="user")
    item_id: int = Field(default=None, serialization_alias="item")
    text: str = Field(default=None)
    created_at: datetime = Field(default=None)


class CommentPaginatedSchema(BaseModel):
    count: int
    results: List[CommentSchema]


class CommentSchemaIn(BaseModel):
    user_id: Optional[int] = Field(default=None, alias="user")
    item_id: Optional[int] = Field(default=None, alias="item")
    text: Optional[str] = Field(default=None)

    class Config:
        arbitrary_types_allowed = True


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


class StagePaginatedSchema(BaseModel):
    count: int
    results: List[StageSchema]


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


class FlowPaginatedSchema(BaseModel):
    count: int
    results: List[FlowSchema]


class ItemSchema(BaseModel):
    id: int = Field(default=None)
    order: str | None = Field(default=None)
    origin_item: str = Field(default=None)
    flow: FlowSchema | None = Field(default=None)
    priority: int = Field(default=None)
    production_date: date | None = Field(default=None)
    packages: int | None = Field(default=None)
    location: int | None = Field(default=None)
    stage: StageSchema | None = Field(default=None)
    comments: List[CommentSchema] | None
    completed: bool = Field(default=False)

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

    @field_validator('packages', 'location')
    def positive_value(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be greater than or equal to 0.')
        return v or 0


class PaginatedItemSchema(BaseModel):
    count: int
    results: List[ItemSchema]


class ItemSchemaIn(BaseModel):
    order: Optional[str] = Field(default=None)
    origin_item: Optional[str] = Field(default=None)
    flow_id: Optional[int] = Field(default=None, alias="flow")
    priority: Optional[int] = Field(default=None)
    production_date: Optional[date] = Field(default=None)
    packages: Optional[int] = Field(default=None)
    location: Optional[int] = Field(default=None)
    stage_id: Optional[int] = Field(default=None, alias="stage")

    class Config:
        arbitrary_types_allowed = True

    @field_validator('packages', 'location')
    def positive_value(cls, v):
        if v is not None and v < 0:
            raise ValueError('Value must be greater than or equal to 0.')
        return v or 0


class ItemSchemaOut(ItemSchemaIn):
    id: int
    flow_id: Optional[int] = Field(None, serialization_alias="flow")
    stage_id: Optional[int] = Field(None, serialization_alias="stage")

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


class SalesOrderSchema(BaseModel):
    id: int = Field(default=None)
    order: str = Field(default=None)
    packages: int = Field(default=None)
    location: int = Field(default=None)
    priority: int = Field(default=None)
    production_date: date | None = Field(default=None)
    created_at: datetime | None = Field(default=None)


class SalesPaginatedSchema(BaseModel):
    count: int
    results: List[SalesOrderSchema]


class SalesOrderSchemaIn(BaseModel):
    order: Optional[str] = Field(default=None)
    packages: Optional[int] = Field(default=None)
    location: Optional[int] = Field(default=None)
    priority: Optional[int] = Field(default=None)
    created_at: Optional[date] = Field(default=datetime.now().date())


class MultiUpdateItemSchema(BaseModel):
    origin_items: List[str]
    flow_id: Optional[int] = Field(default=None, serialization_alias="flow", alias="flow")
    stage_id: Optional[int] = Field(default=None, serialization_alias="stage", alias="stage")
    packages: Optional[int] = Field(default=None)
    storage: Optional[int] = Field(default=None)
    priority: Optional[int] = Field(default=None)
    production_date: Optional[date] = Field(default=None)


class MultiUpdateSalesOrderSchema(BaseModel):
    origin_orders: List[str]
    packages: Optional[int] = Field(default=None)
    location: Optional[int] = Field(default=None)
    priority: Optional[int] = Field(default=None)
    production_date: Optional[date] = Field(default=None)
