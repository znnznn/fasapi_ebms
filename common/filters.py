from typing import Union

from fastapi_filter.contrib.sqlalchemy.filter import _backward_compatible_value_for_like_and_ilike, Filter
from sqlalchemy import Select, or_
from sqlalchemy.orm import Query

_orm_operator_transformer = {
    "neq": lambda value: ("__ne__", value),
    "gt": lambda value: ("__gt__", value),
    "gte": lambda value: ("__ge__", value),
    "in": lambda value: ("in_", value),
    "isnull": lambda value: ("is_", None) if value is True else ("is_not", None),
    "lt": lambda value: ("__lt__", value),
    "lte": lambda value: ("__le__", value),
    "like": lambda value: ("like", _backward_compatible_value_for_like_and_ilike(value)),
    "ilike": lambda value: ("ilike", _backward_compatible_value_for_like_and_ilike(value)),
    # XXX(arthurio): Mysql excludes None values when using `in` or `not in` filters.
    "not": lambda value: ("is_not", value),
    "not_in": lambda value: ("not_in", value),
}


class RenameFieldFilter(Filter):
    """ Base filter for orm related filters.
        For example:
            class MyFilter(RenameFieldFilter):
                name = Optional[str] | None

                class Constants(Filter.Constants):
                    model = MyModel
                    related_fields = {
                        'name': 'my_model_field',
                    }
    """

    class Constants(Filter.Constants):
        model = None
        # related_fields = {}
        model_related_fields = {}
        revert_values_fields = ()
        exclude = False
        excluded_fields = ()

    @property
    def is_exclude(self):
        excluded = []
        for field_name, value in self.filtering_fields:
            field_value = getattr(self, field_name, None)
            if isinstance(field_value, RenameFieldFilter):
                excluded.append(field_value.Constants.exclude)
        return any(excluded)

    def get_value(self, field_name, value):
        print(field_name, value)
        revert_values_fields = getattr(self.Constants, "revert_values_fields", None)
        if field_name in self.Constants.excluded_fields and value is False:
            self.Constants.exclude = True
            value = True
        if field_name in revert_values_fields and isinstance(value, bool):
            return not value
        return value

    @property
    def filtering_fields(self):
        fields = self.model_dump(exclude_none=True, exclude_unset=True)
        fields.pop(self.Constants.ordering_field_name, None)
        if model_related_fields := getattr(self.Constants, "model_related_fields", None):
            foreign_fields = {}
            for field_name, value in fields.items():
                if value:
                    if foreign_field := model_related_fields.get(field_name):
                        setattr(self, foreign_field, False)
                        foreign_fields[foreign_field] = False  # two times nested filter
            if foreign_fields:
                fields.update(foreign_fields)
        return fields.items()

    @property
    def is_filtering_values(self):
        fields = self.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)
        fields.pop(self.Constants.ordering_field_name, None)
        values = []
        for field_name, value in self.filtering_fields:
            if value or isinstance(value, bool):
                values.append(value)
        if values:
            return True
        return False

    def related_field(self, filter_field):
        if related_fields := getattr(self.Constants, "related_fields", None):
            return related_fields.get(filter_field, filter_field)
        return filter_field

    def filter(self, query: Union[Query, Select]):
        for field_name, value in self.filtering_fields:
            field_value = getattr(self, field_name, None)
            if isinstance(field_value, Filter):
                query = field_value.filter(query)
            else:
                field_name = self.related_field(field_name)
                value = self.get_value(field_name, value)
                if "__" in field_name:
                    field_name, operator = field_name.split("__")
                    if operator in ("in", "not_in") and isinstance(value, str):
                        value = value.split(",")
                    operator, value = _orm_operator_transformer[operator](value)

                else:
                    operator = "__eq__"

                if field_name == self.Constants.search_field_name and hasattr(self.Constants, "search_model_fields"):
                    search_filters = [
                        getattr(self.Constants.model, self.related_field(field)).ilike(f"%{value}%")
                        for field in self.Constants.search_model_fields
                    ]
                    query = query.filter(or_(*search_filters))
                else:
                    model_field = getattr(self.Constants.model, self.related_field(field_name))
                    query = query.filter(getattr(model_field, operator)(value))
        return query
