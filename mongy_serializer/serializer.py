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
        self.objects = objects
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.total:
            raise StopIteration
        obj = self.objects[self.index]
        self.index += 1
        return obj

    @property
    def total(self):
        """
        We expect either a pymongo.cursor.Cursor or an iterable object.
        """
        try:
            return self.objects.count()
        except (AttributeError, TypeError, ValueError) as e:
            try:
                return len(self.objects)
            except:
                raise SerializerException("Data in invalid format. Expected a pymongo Cursor or an iterable object.")
        except:
            raise SerializerException("Data in invalid format. Expected a pymongo Cursor or an iterable object.")

    @property
    def data(self):
        for obj in self:
            yield self.serialize_object(obj)

    def serialize_object(self, obj):
        serialized_data = {}
        for attr_name, field in self.fields:
            # TODO: concurrency.
            serialized_data[attr_name] = field.serialize(obj.get(attr_name))
        return serialized_data
