import unittest
import datetime

from mongy_serializer.fields import StringField, DateTimeField, DictField
from mongy_serializer.serializer import Serializer


STATIC_NOW = datetime.datetime.now()

def get_dummy_data():
    return [
        {
            '_id': 'abcdef12345',
            'name': 'abc',
            'created_date': STATIC_NOW,
            'nested': {
                '1': {
                    '1.1': 'abc.1.1',
                    '1.2': {
                        '1.2.1': [1, 2]
                    },
                    '1.3': [1, 2, 3, 4]
                }
            }
        }
    ]


def get_dummy_serializer(max_depth=1):
    class DummySerializer(Serializer):
        name = StringField()
        created_date = DateTimeField(datetime_format='%Y-%m-%d %H:%M:%S')
        nested = DictField(depth=0, max_depth=max_depth)
    return DummySerializer


class TestDummySerializer(unittest.TestCase):
    def setUp(self):
        self.objs = get_dummy_data()

    def tearDown(self):
        self.objs = None

    def test_zero_level_serialization(self):
        DummySerializer = get_dummy_serializer(max_depth=0)
        serialized_data = DummySerializer(self.objs).data
        self.assertEqual(
            list(serialized_data),
            [
                {
                    '_id': 'abcdef12345',
                    'name': 'abc',
                    'created_date': STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S'),
                    'nested': {
                        '1': None
                    }
                }
            ]
        )

    def test_one_level_serialization(self):
        DummySerializer = get_dummy_serializer()
        serialized_data = DummySerializer(self.objs).data
        self.assertEqual(
            list(serialized_data),
            [
                {
                    '_id': 'abcdef12345',
                    'name': 'abc',
                    'created_date': STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S'),
                    'nested': {
                        '1': {
                            '1.1': 'abc.1.1',
                            '1.2': None,
                            '1.3': None
                        }
                    }
                }
            ]
        )

    def test_second_level_serialization(self):
        DummySerializer = get_dummy_serializer(max_depth=2)
        serialized_data = DummySerializer(self.objs).data
        self.assertEqual(
            list(serialized_data),
            [
                {
                    '_id': 'abcdef12345',
                    'name': 'abc',
                    'created_date': STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S'),
                    'nested': {
                        '1': {
                            '1.1': 'abc.1.1',
                            '1.2': {
                                '1.2.1': None
                            },
                            '1.3': [1, 2, 3, 4]
                        }
                    }
                }
            ]
        )

    def test_third_level_serialization(self):
        DummySerializer = get_dummy_serializer(max_depth=3)
        serialized_data = DummySerializer(self.objs).data
        self.assertEqual(
            list(serialized_data),
            [
                {
                    '_id': 'abcdef12345',
                    'name': 'abc',
                    'created_date': STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S'),
                    'nested': {
                        '1': {
                            '1.1': 'abc.1.1',
                            '1.2': {
                                '1.2.1': [1, 2]
                            },
                            '1.3': [1, 2, 3, 4]
                        }
                    }
                }
            ]
        )
