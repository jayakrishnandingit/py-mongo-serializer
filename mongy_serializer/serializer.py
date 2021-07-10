import logging

from .fields import SerializerField, IDField

LOGGER = logging.getLogger(__name__)


class SerializerException(Exception):
    pass


class SerializerMeta(type):
    @staticmethod
    def _get_fields(the_class):
        return list(filter(lambda x: isinstance(x[1], SerializerField), the_class.__dict__.items()))

    def __call__(cls, *args, **kwargs):
        instance = super().__call__(*args, **kwargs)
        fields = cls._get_fields(instance.__class__)
        for base_cls in instance.__class__.__bases__:
            fields.extend(cls._get_fields(base_cls))
        instance.fields = list(set(fields))
        return instance


class Serializer(metaclass=SerializerMeta):
    _id = IDField()

    def __init__(self, objects):
        self.objects = iter(objects)

    @property
    def total(self):
        return len(self.objects)

    @property
    def data(self):
        for obj in self.objects:
            yield self.serialize_object(obj)

    def obj_has_field(self, obj, field_name):
        return field_name in obj

    def get_field_value(self, obj, field_name):
        return obj.get(field_name)

    def filter_obj_fields(self, obj):
        return filter(lambda x: self.obj_has_field(obj, x[0]), self.fields)

    def serialize_object(self, obj):
        fields = self.filter_obj_fields(obj)
        serialized_data = {}

        for attr_name, field in fields:
            serialized_data[attr_name] = field.serialize(self.get_field_value(obj, attr_name))
        return serialized_data
