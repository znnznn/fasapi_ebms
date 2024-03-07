from datetime import datetime
from typing import Optional, List

from fastapi_filter import FilterDepends

from common.filters import RenameFieldFilter
from origin_db.models import Inprodtype, Arinvdet, Inventry, Arinv


class OrderFilter(RenameFieldFilter):
    order: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Arinv
        related_fields = {
            'order': 'autoid',
        }


class InventryFilter(RenameFieldFilter):
    category: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inventry
        related_fields = {
            'category': 'prod_type',
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
    order: Optional[OrderFilter] = FilterDepends(OrderFilter)
    category: Optional[InventryFilter] = FilterDepends(InventryFilter)
    bends: Optional[float] = None
    length: Optional[float] = None
    width: Optional[float] = None
    quantity: Optional[float] = None
    autoid__in: Optional[List[str]] = None
    autoid__not_in: Optional[List[str]] = None

    class Constants(RenameFieldFilter.Constants):
        model = Arinvdet
        related_fields = {
            'bends': 'demd',
            'length': 'heightd',
            'width': 'widthd',
            'quantity': 'quan',
        }