from datetime import date
from decimal import Decimal
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field, field_validator

from stages.schemas import ItemSchema, SalesOrderSchema


class CategorySchema(BaseModel):
    id: str = Field(default=None, alias="autoid", serialization_alias="id")
    capacity: int | None = Field(default=None, alias="capacity", serialization_alias="capacity")
    capacity_id: int | None = Field(default=None, alias="capacity_id", serialization_alias="capacity_id")
    total_capacity: Annotated[Decimal, Field()] | None = None
    name: str = Field(default=None, alias="prod_type", serialization_alias="name")
    flow_count: int | None = Field(default=None, alias="flow_count", serialization_alias="flow_count")

    class Config:
        orm_mode = True
        populate_by_name = True
        from_attributes = True

    @field_validator('total_capacity')
    @classmethod
    def validate_total_capacity(cls, v: Decimal):
        return round(v, 0)


class CategoryPaginateSchema(BaseModel):
    count: int
    results: List[CategorySchema]


class ArinvDetSchema(BaseModel):
    id: str = Field(default=None, alias="autoid", serialization_alias="id")
    category: str = Field(default=None)
    description: str = Field(default=None, serialization_alias="description", alias="descr")
    quantity: float = Field(default=0, serialization_alias='quantity', alias="quan")
    shipped: float = Field(default=0, serialization_alias="shipped", alias="ship")
    ship_date: date | None | str = Field(default=None, serialization_alias="ship_date")
    width: float = Field(default=0, serialization_alias="width", alias="widthd")
    weight: float = Field(default=0, serialization_alias="weight")
    length: float = Field(default=0, serialization_alias="length", alias="heightd")
    bends: float = Field(default=0, serialization_alias="bends", alias="demd")
    customer: str = Field(default=None)
    order: str = Field(default=None, serialization_alias="order", alias="invoice",)
    id_inven: str = Field(default=None, serialization_alias="id_inven", alias="inven")
    origin_order: str = Field(default=None, serialization_alias="origin_order", alias="doc_aid")
    completed: bool = Field(default=False)  # TODO: check this
    profile: bool = Field(default=False)
    color: str = Field(default=None)
    item: ItemSchema | None = Field(default=None)

    class Config:
        orm_mode = True
        from_attributes = True
        # populate_by_name = True

    @field_validator('order')
    @classmethod
    def validate_order(cls, v: str):
        return v.strip()

    @field_validator('ship_date')
    @classmethod
    def validate_ship_date(cls, v: date):
        if not v:
            return v
        return v.strftime("%Y-%m-%d")


class ArinvSchema(BaseModel):
    id: str = Field(default=None, alias="autoid", serialization_alias="id")
    customer: str = Field(default=None, serialization_alias="customer", alias="name")
    invoice: str = Field(default=None)
    ship_date: date | None | str = Field(default=None, serialization_alias="ship_date")
    c_name: str = Field(default=None, serialization_alias="c_name")
    c_city: str = Field(default=None, serialization_alias="c_city")
    start_date: date | None | str = Field(default=None, serialization_alias="start_date")
    end_date: date | None | str = Field(default=None, serialization_alias="end_date")

    @field_validator('invoice')
    @classmethod
    def validate_invoice(cls, v: str):
        return v.strip()

    @field_validator('start_date', 'end_date', 'ship_date')
    @classmethod
    def validate_production_date(cls, v: date):
        if not v:
            return v
        return v.strftime("%Y-%m-%d")


class ArinvRelatedArinvDetSchema(ArinvSchema):
    count_items: int = Field(default=0, serialization_alias="count_items")
    completed: bool = Field(default=False)
    sales_order: SalesOrderSchema | None = Field(default=None)
    origin_items: List[ArinvDetSchema] = Field(default=None, alias="details", serialization_alias="origin_items")

    class Config:
        orm_mode = True
        from_attributes = True
        # populate_by_name = True


class ArinPaginateSchema(BaseModel):
    count: int
    results: List[ArinvRelatedArinvDetSchema]


class ArinvDetPaginateSchema(BaseModel):
    count: int
    results: List[ArinvDetSchema]


class InventrySchema(BaseModel):
    autoid: str = Field(default=None)
    prod_type: str = Field(default=None)


class CapacitiesCalendarSchema(BaseModel):
    capacity: int


class ChangeShipDateSchema(BaseModel):
    ship_date: date

    @field_validator('ship_date')
    @classmethod
    def validate_ship_date(cls, v: date):
        return v.strftime("%Y-%m-%d")
