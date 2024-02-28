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

    def related_field(self, filter_field):
        if related_fields := getattr(self.Constants, "related_fields", None):
            return related_fields.get(filter_field, filter_field)
        return filter_field

    def filter(self, query: Union[Query, Select]):
        for field_name, value in self.filtering_fields:
            if field_value := getattr(self, field_name, None):
                if isinstance(field_value, Filter):
                    query = field_value.filter(query)
                else:
                    if "__" in field_name:
                        field_name, operator = field_name.split("__")
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
