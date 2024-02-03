from datetime import datetime
from typing import List, Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from stages.schemas import ItemSchema


class CategorySchema(BaseModel):
    id: str = Field(default=None, alias="autoid", serialization_alias="id")
    guid: str = Field(default=None, alias="inprodtype_guid", serialization_alias="guid")
    capacity: int | None = Field(default=None, alias="capacity", serialization_alias="capacity")
    capacity_id: int | None = Field(default=None, alias="capacity_id", serialization_alias="capacity_id")
    total_capacity: int | None = Field(default=None, alias="total_capacity", serialization_alias="total_capacity")
    prod_type: str = Field(default=None)
    ar_aid: str = Field(default=None)
    autoid: str = Field(default=None)
    flow_count: int | None = Field(default=None, alias="flow_count", serialization_alias="flow_count")

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
    id: int = Field(default=None, alias="autoid", serialization_alias="id")
    customer: str = Field(default=None, serialization_alias="customer", alias="name")
    invoice: str = Field(default=None)

    @field_validator('invoice')
    @classmethod
    def validate_invoice(cls, v: str):
        return v.strip()


class ArinvRelatedArinvDetSchema(BaseModel):
    id: int = Field(default=None, alias="autoid", serialization_alias="id")
    count_items: int = Field(default=0, serialization_alias="count_items")
    customer: str = Field(default=None, serialization_alias="customer", alias="name")
    invoice: str = Field(default=None)
    origin_items: List[ArinvDetSchema] = Field(default=None, alias="details", serialization_alias="origin_items")

    class Config:
        orm_mode = True
        # populate_by_name = True