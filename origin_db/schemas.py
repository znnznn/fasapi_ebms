from datetime import datetime
from typing import List, Any

from pydantic import BaseModel, ConfigDict, Field


class CommentSchema(BaseModel):
    id: int = Field(default=None)
    user: int = Field(default=None)
    item: int = Field(default=None)
    text: str = Field(default=None)
    created_at: str = Field(default=None)


class StageSchema(BaseModel):
    id: int = Field(default=None)
    name: str = Field(default=None)
    description: str | None = Field(default=None)
    position: int = Field(default=None)
    default: bool = Field(default=None)
    color: str = Field(default=None)
    flow_id: int = Field(default=None)
    # stage_count: str = Field(default=None)


class FlowSchema(BaseModel):
    id: int = Field(default=None)
    name: str | None = Field(default=None)
    description: str | None = Field(default=None)
    position: int = Field(default=None)
    category_id: str = Field(default=None)
    stages: List[StageSchema] | None
    created_at: datetime = Field(default=None)


class CapacitySchema(BaseModel):
    id: int = Field(default=None)
    per_day: int = Field(default=None)
    category_id: int = Field(default=None)


class CategorySchema(BaseModel):
    id: str = Field(default=None, alias="autoid", serialization_alias="id")
    guid: str = Field(default=None, alias="inprodtype_guid", serialization_alias="guid")
    # flows: int = Field(default=0)
    # flows: List[FlowSchema] | None
    # capacity: int | None = Field(default=None)
    # total_capacity: int | None = Field(default=None)
    prod_type: str = Field(default=None)
    ar_aid: str = Field(default=None)
    autoid: str = Field(default=None)
    # flow_count: int | None = Field(default=None, alias="flow_count", serialization_alias="flow_count")

    class Config:
        orm_mode = True
        populate_by_name = True


class SalesOrderSchema(BaseModel):
    id: int = Field(default=None)
    order: int = Field(default=None)
    packages: int = Field(default=None)
    location: int = Field(default=None)
    production_date: str = Field(default=None)
    priority: int = Field(default=None)


class ItemSchema(BaseModel):
    id: int = Field(default=None)
    flow: int = Field(default=None)
    origin_item: int = Field(default=None)
    production_date: str = Field(default=None)
    priority: int = Field(default=None)
    # comments: List[CommentSchema] = Field(default=None)

    class Config:
        orm_mode = True
        populate_by_name = True


class ArinvDetSchema(BaseModel):
    id_det: int = Field(default=None, alias="recno5", serialization_alias="id_det")
    description: str = Field(default=None, serialization_alias="description", alias="descr")
    item: ItemSchema = Field(default=None)
    # category: str = Field(default=None)
    bends: float = Field(default=0, serialization_alias="bends", alias="demd")
    length: float = Field(default=0, serialization_alias="length", alias="heightd")
    width_d: float = Field(default=0, serialization_alias="width_d", alias="widthd")
    quantity: float = Field(default=0, serialization_alias='quantity', alias="quan")
    # customer: str = Field(default=None)  # TODO: add customer  as arinv.name
    # order: str = Field(default=None)   # TODO: add order
    id_inventory: str = Field(default=None, serialization_alias="id_inventory", alias="inven")
    origin_order: int = Field(default=None, serialization_alias="origin_order", alias="Arinv.recno5")   # TODO: add origin_order as arinv.recno5
    # completed: bool = Field(default=False)
    # profile: bool = Field(default=False)  # TODO: add profile as inven.rol_profile
    # color: str = Field(default=None)  # TODO: add color as inven.rol_color

    class Config:
        orm_mode = True
        # populate_by_name = True


class ArinvSchema(BaseModel):
    recno5: int = Field(default=None, arbitrary_types_allowed=True)


class ArinvRelatedArinvDetSchema(BaseModel):
    id_det: int = Field(default=None, alias="recno5", serialization_alias="id_det")
    autoid: str = Field(default=None, arbitrary_types_allowed=True)
    details: List[ArinvDetSchema] = Field(default=None, arbitrary_types_allowed=True)

    class Config:
        orm_mode = True
        # populate_by_name = True