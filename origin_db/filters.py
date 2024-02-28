from typing import Optional

from fastapi_filter.contrib.sqlalchemy import Filter

from common.filters import RenameFieldFilter
from origin_db.models import Inprodtype


class CategoryFilter(RenameFieldFilter):
    name: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Inprodtype
        related_fields = {
            'name': 'prod_type',
        }
