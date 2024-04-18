from collections import defaultdict
from typing import Union, Optional, List, Any

from fastapi_filter.contrib.sqlalchemy.filter import _backward_compatible_value_for_like_and_ilike, Filter
from pydantic import field_validator
from pydantic_core.core_schema import ValidationInfo
from sqlalchemy import Select, or_
from sqlalchemy.orm import Query

from common.constants import ModelType, OriginModelType

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
    order_by: Optional[List[str]] = None

    class Constants(Filter.Constants):
        extra = 'allow'
        model = None
        ordering_field_name = 'order_by'
        search_field_name = 'search'
        ordering_fields = ()  # possible fields for ordering
        search_fields_by_models = {}  # Class: [field1, field2]
        model_related_fields = {}  # excluded foreign keys with null values
        revert_values_fields = ()  # revert true to false or false to true (use to boolean fields)
        exclude = False  # exclude from query
        do_ordering = None
        excluded_fields = ()  # exclude from query by fields
        join_tables = {}  # auto join tables
        default_ordering = ['recno5']
        joins = set()

    @property
    def ordered(self):
        return self.Constants.do_ordering

    def get_join_table(self, field_name: str) -> Optional[ModelType | OriginModelType]:
        join_tables = getattr(self.Constants, "join_tables", None)
        if join_tables is not None:
            return join_tables.get(field_name, None)

    def get_search_query(self, query, value) -> Optional[Union[Select, Query]]:
        search_filters = []
        for model, fields in self.Constants.search_fields_by_models.items():
            for field in fields:
                search_filters.append(getattr(model, field).ilike(f"%{value}%"))
        query = query.filter(or_(*search_filters))
        return query

    @property
    def is_exclude(self) -> bool:
        excluded = []
        for field_name, value in self.filtering_fields:
            field_value = getattr(self, field_name, None)
            if isinstance(field_value, RenameFieldFilter):
                excluded.append(field_value.Constants.exclude)
        excluded.append(self.Constants.exclude)
        return any(excluded)

    def get_value(self, field_name, value) -> Any:
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
    def is_filtering_values(self) -> bool:
        fields = self.model_dump(exclude_none=True, exclude_unset=True, exclude_defaults=True)
        fields.pop(self.Constants.ordering_field_name, None)
        values = []
        for field_name, value in self.filtering_fields:
            if isinstance(value, dict):
                for key, nested_value in value.items():
                    if nested_value or isinstance(nested_value, bool):
                        values.append(nested_value)
            elif value or isinstance(value, bool):
                values.append(value)
        if values:
            return True
        return False

    def related_field(self, filter_field) -> str:
        if related_fields := getattr(self.Constants, "related_fields", None):
            return related_fields.get(filter_field, filter_field)
        return filter_field

    def order_by_related_field(self, order_by_field) -> str:
        if order_by_related_fields := getattr(self.Constants, "order_by_related_fields", None):
            return order_by_related_fields.get(order_by_field, order_by_field)
        return order_by_field

    def filter(self, query: Union[Query, Select], **kwargs: Optional[dict]):
        for field_name, value in self.filtering_fields:
            field_value = getattr(self, field_name, None)
            if isinstance(field_value, Filter):
                need_join_table = self.get_join_table(field_name)
                if need_join_table and not need_join_table in self.Constants.joins and value:
                    query = query.join(need_join_table)
                    self.Constants.joins.add(need_join_table)
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

                if field_name == self.Constants.search_field_name and hasattr(self.Constants, "search_fields_by_models"):
                    query = self.get_search_query(query, value)
                else:
                    model_field = getattr(self.Constants.model, field_name)
                    query = query.filter(getattr(model_field, operator)(value))
        # print(query.compile(compile_kwargs={"literal_binds": True}))
        extra_ordering = kwargs.get("extra_ordering")
        if extra_ordering is not None:
            query = query.order_by(extra_ordering)
        return query

    def sort(self, query: Union[Query, Select]):
        if not self.ordering_values:
            print('no ordering')
            return query
        else:
            self.Constants.do_ordering = True

        for field_name in self.ordering_values:
            direction = Filter.Direction.asc
            if field_name.startswith("-"):
                direction = Filter.Direction.desc
            field_name = field_name.replace("-", "").replace("+", "")
            need_join_table = self.get_join_table(field_name)
            ordering_field_name = self.order_by_related_field(field_name)
            if not need_join_table:
                order_by_field = getattr(self.Constants.model, ordering_field_name)
            else:
                if need_join_table and not need_join_table in self.Constants.joins:
                    query = query.join(need_join_table)
                    self.Constants.joins.add(need_join_table)
                order_by_field = getattr(need_join_table, ordering_field_name)
            query = query.order_by(getattr(order_by_field, direction)())
        return query

    @field_validator("*", mode="before", check_fields=False)
    def validate_order_by(cls, value, field: ValidationInfo):
        if field.field_name != cls.Constants.ordering_field_name:
            return value
        value = cls.remove_invalid_fields(value)
        if not value:
            return cls.Constants.default_ordering

        field_name_usages = defaultdict(list)
        duplicated_field_names: set = set()

        for field_name_with_direction in value:
            field_name = field_name_with_direction.replace("-", "").replace("+", "")

            field_name_usages[field_name].append(field_name_with_direction)
            if len(field_name_usages[field_name]) > 1:
                duplicated_field_names.add(field_name)

        if duplicated_field_names:
            ambiguous_field_names = ", ".join(
                [
                    field_name_with_direction
                    for field_name in sorted(duplicated_field_names)
                    for field_name_with_direction in field_name_usages[field_name]
                ]
            )
            raise ValueError(
                f"Field names can appear at most once for {cls.Constants.ordering_field_name}. "
                f"The following was ambiguous: {ambiguous_field_names}."
            )
        return value

    @classmethod
    def remove_invalid_fields(cls, fields) -> List[str]:
        if isinstance(fields, str):
            fields = fields.split(",")
        valid_fields = [item for item in cls.Constants.ordering_fields]

        def term_valid(term):
            if term.startswith("-"):
                term = term[1:]
            return term in valid_fields

        def get_field(field):
            symbol = ""
            if field.startswith("-"):
                field = field[1:]
                symbol = '-'
            return symbol + field
        return [get_field(term) for term in fields if term_valid(term)]
