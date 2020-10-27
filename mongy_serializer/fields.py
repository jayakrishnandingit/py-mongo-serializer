import logging
import datetime
from abc import ABCMeta, abstractmethod
from functools import singledispatch

LOGGER = logging.getLogger(__name__)


class SerializerField(metaclass=ABCMeta):
    """
    Class that defines how to serialize a data type/field in a MongoDB document.
    Composite design pattern implementation.
        1. There can be simple fields that just serializes itself or
        2. There can be fields with nested structure which will
           call the children to serialize themselves.
    """
    field_type = None

    def __init__(
            self,
            date_format='%Y-%m-%d',
            datetime_format='%Y-%m-%d',
            depth=0,
            max_depth=1,
            exclude_fields=None):
        self.date_format = date_format
        self.datetime_format = datetime_format
        self.depth = depth
        self.max_depth = max_depth
        if exclude_fields is None:
            exclude_fields = []
        # TODO: exclude nested fields.
        self.exclude_fields = exclude_fields

    @abstractmethod
    def serialize(self, value):
        pass


class SimpleField(SerializerField):
    def serialize(self, value):
        if not value:
            return value
        try:
            return self.field_type(value)
        except (TypeError, ValueError) as e:
            return value


class StringField(SimpleField):
    field_type = str


class IDField(StringField):
    pass


class IntField(SimpleField):
    field_type = int


class DateField(SerializerField):
    """
    Special case simple field.
    """
    field_type = datetime.date

    def serialize(self, value):
        if not value:
            return value
        try:
            return value.strftime(self.date_format)
        except (TypeError, ValueError) as e:
            return value


class DateTimeField(SerializerField):
    """
    Special case simple field.
    """
    field_type = datetime.datetime

    def serialize(self, value):
        if not value:
            return value
        try:
            return value.strftime(self.datetime_format)
        except (TypeError, ValueError) as e:
            return value


class CompositeField(SerializerField):
    """
    Composite field base class.
    """
    def serialize(self, value):
        if not value:
            return value
        if self.depth > self.max_depth:
            return None
        return value


class DictField(CompositeField):
    """
    Composite field.
    """
    field_type = dict

    def serialize(self, value):
        value = super().serialize(value)
        if not value:
            return value
        serialized_data = {}
        ef = self.exclude_fields
        for k, v in filter(lambda x: x[0] not in ef, value.items()):
            field = field_dispatch(
                v,
                # TODO: alternative for passing these arguments for field construction.
                date_format=self.date_format,
                datetime_format=self.datetime_format,
                depth=self.depth + 1,
                max_depth=self.max_depth,
                # TODO: exclude nested fields.
                exclude_fields=self.exclude_fields
            )
            serialized_data[k] = field.serialize(v)
        return serialized_data


class ListField(CompositeField):
    """
    Composite field.
    """
    field_type = list

    def serialize(self, value):
        value = super().serialize(value)
        if not value:
            return value
        serialized_data = []
        for v in value:
            field = field_dispatch(
                v,
                # TODO: alternative for passing these arguments for field construction.
                date_format=self.date_format,
                datetime_format=self.datetime_format,
                depth=self.depth + 1,
                max_depth=self.max_depth,
                exclude_fields=self.exclude_fields
            )
            serialized_data.append(field.serialize(v))
        return serialized_data if all(serialized_data) else []


# Dispatch the appropriate field according to the type of value.
# This is useful for identifying fields dynamically for nested data.

@singledispatch
def field_dispatch(value, **kwargs):
    return StringField(*kwargs)


@field_dispatch.register(int)
def _(value, **kwargs):
    return IntField(**kwargs)


@field_dispatch.register(datetime.date)
def _(value, **kwargs):
    return DateField(**kwargs)


@field_dispatch.register(datetime.datetime)
def _(value, **kwargs):
    return DateTimeField(**kwargs)


@field_dispatch.register(dict)
def _(value, **kwargs):
    return DictField(**kwargs)


@field_dispatch.register(list)
def _(value, **kwargs):
    return ListField(**kwargs)
