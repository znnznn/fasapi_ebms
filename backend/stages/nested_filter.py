from datetime import datetime
from typing import Optional, Literal, Any

from common.constants import IncEx
from common.filters import RenameFieldFilter
from stages.models import Item, Stage, Flow


class NestedItemFilter(RenameFieldFilter):
    completed: Optional[bool] = None
    over_due: Optional[bool] = None

    class Constants(RenameFieldFilter.Constants):
        model = Item
        ordering_fields = ('comments', 'production_date', 'priority', 'flow', 'status',)
        revert_values_fields = ('production_date__isnull', 'comments__isnull')
        default_ordering = ['production_date']
        related_fields = {
            'is_scheduled': 'production_date__isnull',
        }
        model_related_fields = {
            'status': 'stage_id__isnull',
            'flow': 'flow_id__isnull',
        }
        join_tables = {
            'status': Stage,
            'flow': Flow,
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
        if completed := fields.pop('completed', None):
            fields['status'] = 'Done'
        over_due = fields.pop('over_due', None)
        if isinstance(over_due, bool):
            if over_due:
                fields['production_date__lt'] = datetime.now().date()
                fields['status_not_in'] = 'Done,'
            else:
                fields['production_date__lt'] = datetime.now().date()
                fields['status_not_in'] = 'Done,'
                self.Constants.exclude = True

        return fields
