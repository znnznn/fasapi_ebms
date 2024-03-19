from datetime import datetime, date
from typing import Optional, List

from fastapi_filter import FilterDepends

from common.filters import RenameFieldFilter
from origin_db.models import Arinv, Arinvdet, Inventry


class NestedInventryFilter(RenameFieldFilter):
    category: Optional[str] = None
    categories: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inventry
        related_fields = {
            'category': 'prod_type',
            'categories': 'prod_type__in',
        }


class NestedOrderFilter(RenameFieldFilter):
    order: Optional[str] = None
    invoice: Optional[str] = None
    name: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Arinv
        related_fields = {
            'order': 'autoid',
        }


class NestedOriginItemFilter(RenameFieldFilter):
    ship_date: Optional[date] = None
    weight: Optional[float] = None
    categories: Optional[NestedInventryFilter] = FilterDepends(NestedInventryFilter)
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
        ordering_fields = (
            'quan', 'weight', 'width', 'widthd', 'height', 'heightd', 'ship_date', "category", 'bends', 'length', 'width', 'quantity',
            'id_inven', 'order',
        )
