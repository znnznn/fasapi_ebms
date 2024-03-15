from datetime import datetime, date
from typing import Optional, List, Union

from fastapi_filter import FilterDepends
from sqlalchemy import Select, or_
from sqlalchemy.orm import Query

from common.filters import RenameFieldFilter
from origin_db.models import Inprodtype, Arinvdet, Inventry, Arinv
from origin_db.nested_filters import NestedOrderFilter, NestedOriginItemFilter


class InventryFilter(RenameFieldFilter):
    category: Optional[str] = None
    categories: Optional[List[str]] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inventry
        related_fields = {
            'category': 'prod_type',
            'categories': 'prod_type',
        }


class CategoryFilter(RenameFieldFilter):
    name: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inprodtype
        related_fields = {
            'name': 'prod_type',
        }


class OriginItemFilter(RenameFieldFilter):
    ship_date: Optional[datetime] = None
    weight: Optional[float] = None
    order: Optional[NestedOrderFilter] = FilterDepends(NestedOrderFilter)
    category: Optional[InventryFilter] = FilterDepends(InventryFilter)
    categories: Optional[InventryFilter] = FilterDepends(InventryFilter)
    bends: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    quantity: Optional[float] = None
    autoid__in: Optional[List[str]] = None
    autoid__not_in: Optional[List[str]] = None

    class Constants(RenameFieldFilter.Constants):
        model = Arinvdet
        search_fields_by_models = {
            Arinv: ('invoice', 'name'),
        }
        related_fields = {
            'bends': 'demd',
            'length': 'heightd',
            'width': 'widthd',
            'quantity': 'quan',
        }
        ordering_fields = (
            'quan', 'weight', 'width', 'widthd', 'height', 'heightd', 'ship_date', "category", 'bends', 'length', 'width', 'quantity',
            'id_inven', 'order',
        )


class OrderFilter(RenameFieldFilter):
    order: Optional[str] = None
    invoice: Optional[str] = None
    name: Optional[str] = None
    date: Optional[date] = None
    categories: Optional[NestedOriginItemFilter] = FilterDepends(NestedOriginItemFilter)

    class Constants(RenameFieldFilter.Constants):
        model = Arinv
        related_fields = {
            'order': 'autoid',
            'invoice': 'invoice__like',
            'date': 'inv_date__gte',
            'created_at': 'crea_at',
        }
        search_fields_by_models = {
            Arinv: ('invoice', 'name'),
        }
