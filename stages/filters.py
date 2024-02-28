from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from common.filters import RenameFieldFilter
from stages.models import Item


class ItemFilter(RenameFieldFilter):
    production_date: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Item
