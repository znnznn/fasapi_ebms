from datetime import date, datetime, timedelta
from typing import Optional, Any, List, Union

from pydantic import Field
from sqlalchemy import Select
from sqlalchemy.orm import Query
from typing_extensions import Literal

from fastapi_filter import FilterDepends

from common.constants import IncEx
from common.filters import RenameFieldFilter
from stages.models import Item, Stage, Flow, Comment, SalesOrder


class CommentFilter(RenameFieldFilter):
    order_by: Optional[List[str]] = Field(default=["id"], description="")
    has_comments: Optional[bool] = None

    class Constants(RenameFieldFilter.Constants):
        model = Comment
        default_ordering = ['id']
        related_fields = {
            'has_comments': 'user_id__isnull',
        }
        revert_values_fields = ('user_id__isnull',)
        excluded_fields = ('user_id__isnull',)


class FlowFilter(RenameFieldFilter):
    order_by: Optional[List[str]] = Field(default=["id"], description="")
    flow: Optional[str] = None
    category__prod_type: Optional[str] = None

    class Constants(RenameFieldFilter.Constants):
        model = Flow
        default_ordering = ['id']
        related_fields = {
            'flow': 'name',
            'category__prod_type': 'category_autoid',
        }
        order_by_related_fields = {
            'category__prod_type': 'category__autoid',
            'flow': 'name',
        }


class StageFilter(RenameFieldFilter):
    order_by: Optional[List[str]] = Field(default=["id"], description="")
    status: Optional[str] = None
    status_not_in: Optional[str] = None
    flow: Optional[int] = None

    class Constants(RenameFieldFilter.Constants):
        model = Stage
        default_ordering = ['id']
        related_fields = {
            'status': 'name',
            'status_not_in': 'name__not_in',
            'flow': 'flow_id',
        }


class ItemFilter(RenameFieldFilter):
    production_date: Optional[date] = None
    production_date__lt: Optional[date] = None
    status: Optional[StageFilter] = FilterDepends(StageFilter)
    status_not_in: Optional[StageFilter] = FilterDepends(StageFilter)
    is_scheduled: Optional[bool] = None
    flow: Optional[FlowFilter] = FilterDepends(FlowFilter)
    stage_id__isnull: Optional[bool] = None
    flow_id__isnull: Optional[bool] = None
    date_range: Optional[str] = None
    timedelta: Optional[int] = None
    completed: Optional[bool] = None
    has_comments: Optional[CommentFilter] = FilterDepends(CommentFilter)
    over_due: Optional[bool] = None

    class Constants(RenameFieldFilter.Constants):
        model = Item
        ordering_fields = ('comments', 'production_date', 'priority', 'flow', 'status', 'stage')
        revert_values_fields = ('production_date__isnull', 'comments__isnull')
        default_ordering = ('production_date',)
        # related_fields = {
        #     'is_scheduled': 'production_date__isnull',
        # }
        # model_related_fields = {
        #     'status': 'stage_id__isnull',
        #     'flow': 'flow_id__isnull',
        # }
        join_tables = {
            'status': Stage,
            'flow': Flow,
            'over_due': Stage,
        }
        order_by_related_fields = {
            'flow': 'name',
            'comments': 'count_comments',
        }
        excluded_fields = ('status', 'completed', 'is_scheduled', 'over_due')

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
            time_shift = today + timedelta(days=int(shift_date))
            fields['production_date__gte'] = today.strftime('%Y-%m-%d')
            fields['production_date__lte'] = today + timedelta(days=int(shift_date))
        return fields


class NestedItemFilter(RenameFieldFilter):
    status: Optional[StageFilter] = FilterDepends(StageFilter)
    status_not_in: Optional[StageFilter] = FilterDepends(StageFilter)
    flow: Optional[FlowFilter] = FilterDepends(FlowFilter)
    stage_id__isnull: Optional[bool] = None
    flow_id__isnull: Optional[bool] = None
    date_range: Optional[str] = None
    timedelta: Optional[int] = None
    completed: Optional[bool] = None
    has_comments: Optional[CommentFilter] = FilterDepends(CommentFilter)
    over_due: Optional[bool] = None

    class Constants(RenameFieldFilter.Constants):
        model = Item
        ordering_fields = ('comments', 'production_date', 'priority', 'flow', 'status',)
        revert_values_fields = ('production_date__isnull', 'comments__isnull')
        default_ordering = ['production_date']
        excluded_fields = ('status', 'completed', 'is_scheduled', 'over_due')
        # related_fields = {
        #     'is_scheduled': 'production_date__isnull',
        # }
        join_tables = {
            'status': Stage,
            'flow': Flow,
        }

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
        return fields


class SalesOrderFilter(RenameFieldFilter):
    production_date: Optional[date] = None
    production_date__isnull: Optional[bool] = None
    priority: Optional[int] = None
    is_scheduled: Optional[bool] = None
    over_due: Optional[bool] = None
    completed: Optional[NestedItemFilter] = FilterDepends(NestedItemFilter)
    status: Optional[NestedItemFilter] = FilterDepends(NestedItemFilter)
    status_not_in: Optional[NestedItemFilter] = FilterDepends(NestedItemFilter)
    stage_id__isnull: Optional[NestedItemFilter] = FilterDepends(NestedItemFilter)

    class Constants(RenameFieldFilter.Constants):
        model = SalesOrder
        default_ordering = ('id',)
        related_fields = {
            'start_date': 'production_date',
            'end_date': 'production_date',
        }
        revert_values_fields = ('production_date__isnull',)
        ordering_fields = ('production_date', 'priority',)
        join_tables = {
            'over_due': SalesOrder.items,
            'status': SalesOrder.items,
            'status_not_in': SalesOrder.items,
            'completed': SalesOrder.items,
        }
        excluded_fields = ('production_date__isnull', 'status', 'completed', 'is_scheduled', 'over_due')