from datetime import datetime, date
from typing import Optional, List

from fastapi_filter import FilterDepends
from pydantic import Field

from common.filters import RenameFieldFilter
from origin_db.models import Inprodtype, Arinvdet, Inventry, Arinv
from origin_db.nested_filters import NestedOriginItemFilter


class InventryFilter(RenameFieldFilter):
    order_by: Optional[List[str]] = Field(default=["recno5"], description="")
    category: Optional[str] = None
    categories: Optional[List[str]] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inventry
        default_ordering = ('recno5',)
        related_fields = {
            'category': 'prod_type',
            'categories': 'prod_type',
        }


class CategoryFilter(RenameFieldFilter):
    order_by: Optional[List[str]] = Field(default=["recno5"], description="")
    name: Optional[str] = None
    categories: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inprodtype
        default_ordering = ('recno5',)
        related_fields = {
            'name': 'prod_type',
            'categories': 'prod_type__in',
        }


class OriginItemFilter(RenameFieldFilter):
    search: Optional[str] = None
    order_by: Optional[List[str]] = Field(default=["recno5"], description="")
    ship_date: Optional[datetime] = None
    weight: Optional[float] = None
    order: Optional[str] = None
    category: Optional[str] = None
    bends: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    quantity: Optional[float] = None
    autoid__in: Optional[List[str]] = None
    autoid__not_in: Optional[List[str]] = None

    class Constants(RenameFieldFilter.Constants):
        model = Arinvdet
        default_ordering = ('recno5',)
        search_fields_by_models = {
            Arinv: ('name', 'invoice'),
        }
        related_fields = {
            'bends': 'demd',
            'length': 'heightd',
            'width': 'widthd',
            'quantity': 'quan',
            'order': 'invoice__like',
        }
        order_by_related_fields = {
            'bends': 'demd',
            'length': 'heightd',
            'width': 'widthd',
            'quantity': 'quan',
            'order': 'doc_aid',
            'id_inven': 'inven',
            'shipped': 'ship',
        }
        ordering_fields = (
            'quan', 'weight', 'width', 'widthd', 'height', 'heightd', 'ship_date', "category", 'bends', 'length', 'width', 'quantity',
            'id_inven', 'order', 'weight', 'shipped', 'profile', 'quantity',
        )


class OrderFilter(RenameFieldFilter):
    search: Optional[str] = None
    order_by: Optional[List[str]] = None
    order: Optional[str] = None
    invoice: Optional[str] = None
    name: Optional[str] = None
    date: Optional[date] = None
    categories: Optional[NestedOriginItemFilter] = FilterDepends(NestedOriginItemFilter)
    autoid__in: Optional[List[str]] = None
    autoid__not_in: Optional[List[str]] = None

    class Constants(RenameFieldFilter.Constants):
        model = Arinv
        default_ordering = ('recno5',)
        related_fields = {
            'order': 'autoid',
            'invoice': 'invoice__like',
            'date': 'inv_date__gte',
            'created_at': 'crea_at',
        }
        order_by_related_fields = {
            'order': 'invoice',
            'date': 'inv_date',
            'created_at': 'crea_at',
            'customer': 'name',
        }
        search_fields_by_models = {
            Arinv: ('invoice', 'name'),
        }
        ordering_fields = ('order', 'invoice', 'customer', 'name', 'date', 'created_at', 'count_items', 'c_name', 'c_city', 'ship_date',)
