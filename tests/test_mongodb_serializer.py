import os
import unittest
import datetime

import pymongo
from mongy_serializer.fields import StringField, DateTimeField, DictField, ListField
from mongy_serializer.serializer import Serializer

STATIC_NOW = datetime.datetime.now()
MONGO_HOST = os.environ['MONGO_HOST']
MONGO_USERNAME = os.environ['MONGO_INITDB_ROOT_USERNAME']
MONGO_PASSWORD = os.environ['MONGO_INITDB_ROOT_PASSWORD']
MONGO_DATABASE = os.environ['MONGO_INITDB_DATABASE']
CONNECTION_STRING = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:27017/?socketTimeoutMS=60000"
client = pymongo.MongoClient(CONNECTION_STRING)


def get_post_serializer(max_depth=1):
    class PostSerializer(Serializer):
        title = StringField()
        body = StringField()
        created_date = DateTimeField(datetime_format='%Y-%m-%d %H:%M:%S')
        author = DictField(depth=0, max_depth=max_depth)
        comments = ListField(depth=0, max_depth=max_depth)
    return PostSerializer


def get_posts():
    return [
        {
            "title": "ea molestias quasi exercitationem repellat qui ipsa sit aut",
            "body": "et iusto sed quo iure\nvoluptatem occaecati omnis eligendi aut ad\nvoluptatem doloribus vel accusantium quis pariatur\nmolestiae porro eius odio et labore et velit aut",
            "created_date": STATIC_NOW,
            "author": {
                "name": "Leanne Graham",
                "username": "Bret",
                "dob": datetime.datetime(1988, 8, 5),
                "email": "Sincere@april.biz",
                "address": {
                  "street": "Kulas Light",
                  "suite": "Apt. 556",
                  "city": "Gwenborough",
                  "zipcode": "92998-3874",
                  "geo": {
                    "lat": -37.3159,
                    "lng": 81.1496
                  }
                },
                "phone": "1-770-736-8031 x56442",
                "website": "hildegard.org",
                "company": {
                  "name": "Romaguera-Crona",
                  "catchPhrase": "Multi-layered client-server neural-net",
                  "bs": "harness real-time e-markets"
                }
            },
            "comments": [
                {
                    "name": "odio adipisci rerum aut animi",
                    "created_date": STATIC_NOW,
                    "email": "Nikita@garfield.biz",
                    "body": "quia molestiae reprehenderit quasi aspernatur\naut expedita occaecati aliquam eveniet laudantium\nomnis quibusdam delectus saepe quia accusamus maiores nam est\ncum et ducimus et vero voluptates excepturi deleniti ratione"
                }
            ]
        }
    ]


def create_posts(data):
    posts = client[MONGO_DATABASE]['posts']
    return posts.insert_many(data).inserted_ids


class TestPostSerializer(unittest.TestCase):
    def setUp(self):
        self.collection = client[MONGO_DATABASE]['posts']
        self.post_ids = create_posts(get_posts())

    def tearDown(self):
        self.collection.delete_many({"_id": {"$in": self.post_ids}})

    def test_zero_level_serialization(self):
        PostSerializer = get_post_serializer(max_depth=0)
        serialized_data = PostSerializer(self.collection.find({"_id": {"$in": self.post_ids}})).data
        for data in serialized_data:
            self.assertEqual(data['created_date'], STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S'))
            self.assertIsNone(data['author']['address'])
            self.assertIsNone(data['author']['company'])
            self.assertEqual(data['comments'], [None])

    def test_one_level_serialization(self):
        PostSerializer = get_post_serializer(max_depth=1)
        serialized_data = PostSerializer(self.collection.find({"_id": {"$in": self.post_ids}})).data
        for data in serialized_data:
            string_now = STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S')
            self.assertEqual(data['created_date'], string_now)
            self.assertIsNotNone(data['author']['address'])
            self.assertEqual(data['author']['dob'], datetime.datetime(1988, 8, 5).strftime('%Y-%m-%d'))
            self.assertIsNone(data['author']['address']['geo'])
            self.assertIsNotNone(data['author']['company'])
            self.assertEqual(len(data['comments']), 1)
            self.assertEqual(data['comments'][0]['created_date'], STATIC_NOW.strftime('%Y-%m-%d'))

    def test_two_level_serialization(self):
        PostSerializer = get_post_serializer(max_depth=2)
        serialized_data = PostSerializer(self.collection.find({"_id": {"$in": self.post_ids}})).data
        for data in serialized_data:
            string_now = STATIC_NOW.strftime('%Y-%m-%d %H:%M:%S')
            self.assertEqual(data['created_date'], string_now)
            self.assertIsNotNone(data['author']['address'])
            self.assertEqual(data['author']['dob'], datetime.datetime(1988, 8, 5).strftime('%Y-%m-%d'))
            self.assertIsNotNone(data['author']['address']['geo'])
            self.assertIsNotNone(data['author']['company'])
            self.assertEqual(len(data['comments']), 1)
            self.assertEqual(data['comments'][0]['created_date'], STATIC_NOW.strftime('%Y-%m-%d'))
