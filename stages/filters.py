from datetime import date, datetime, timedelta
from typing import Optional, Union, Any

from typing_extensions import Literal

from fastapi_filter import FilterDepends
from pydantic import Field
from sqlalchemy import Select
from sqlalchemy.orm import Query

from common.constants import IncEx
from common.filters import RenameFieldFilter
from stages.models import Item, Stage, Flow, Comment


class CommentFilter(RenameFieldFilter):
    has_comments: Optional[bool] = None

    class Constants(RenameFieldFilter.Constants):
        model = Comment
        related_fields = {
            'has_comments': 'user_id__isnull',
        }
        revert_values_fields = ('user_id__isnull',)
        excluded_fields = ('user_id__isnull',)

    # def get_value(self, field_name, value):
    #     if field_name == 'user_id__isnull' and value is False:
    #         value = True
    #         self.Constants.exclude = True
    #     return super().get_value(field_name, value)


class FlowFilter(RenameFieldFilter):
    flow: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Flow
        related_fields = {
            'flow': 'name',
        }


class StageFilter(RenameFieldFilter):
    status: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Stage
        related_fields = {
            'status': 'name',
        }


class ItemFilter(RenameFieldFilter):
    production_date: Optional[date] = None
    status: Optional[StageFilter] = FilterDepends(StageFilter)
    is_scheduled: Optional[bool] = None
    # flow: Optional[FlowFilter] = FilterDepends(FlowFilter)
    stage_id__isnull: Optional[bool] = None
    date_range: Optional[str] = None
    timedelta: Optional[int] = None
    completed: Optional[bool] = None
    has_comments: Optional[CommentFilter] = FilterDepends(CommentFilter)

    class Constants(RenameFieldFilter.Constants):
        model = Item
        revert_values_fields = ('production_date__isnull', 'comments__isnull')
        related_fields = {
            'is_scheduled': 'production_date__isnull',
            # 'has_comments': 'comments__is_not',
        }
        model_related_fields = {
            'status': 'stage_id__isnull',
        }

    def get_value(self, field_name, value):
        if field_name == 'production_date__isnull' and value is False:
            value = True
            self.Constants.exclude = True
        return super().get_value(field_name, value)

    def model_dump(
            self,
            *,
            mode: Literal['json', 'python'] | str = 'python',
            include: IncEx = None,
            exclude: IncEx = None,
            by_alias: bool = False,
            exclude_unset: bool = False,
            exclude_defaults: bool = False,
            exclude_none: bool = False,
            round_trip: bool = False,
            warnings: bool = True,
    ) -> dict[str, Any]:
        fields = super().model_dump(
            mode=mode,
            include=include,
            exclude=exclude,
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_defaults=exclude_defaults,
            exclude_none=exclude_none,
            round_trip=round_trip,
            warnings=warnings,
        )
        if date_range := fields.pop('date_range', None):
            try:
                min_date, max_date = str(date_range).split(',')
                fields['production_date__gte'] = datetime.strptime(min_date, '%Y-%m-%d')
                fields['production_date__lte'] = datetime.strptime(max_date, '%Y-%m-%d')
            except ValueError:
                pass
        if shift_date := fields.pop('timedelta', 0):
            today = datetime.now().date()
            fields['production_date__gte'] = today
            fields['production_date__lte'] = today + timedelta(days=int(shift_date))
        if completed := fields.pop('completed', None):
            fields['status'] = 'Done'
            fields['is_scheduled'] = True
        # if has_comments := fields.pop('has_comments', None):
        #     fields['comments__exists'] = True

        return fields
