import sys
import json
import redis
import shlex
import hashlib
import subprocess
from unittest import TestCase
from datetime import datetime

from scoring import get_interests, get_score
import store


store.CONFIG.update({
    "host": "localhost",
    "port": 7777,
})


class TestStorageGoodConnection(TestCase):
    def setUp(self):
        # start redis server
        self.redis_server = subprocess.Popen(shlex.split(
            'redis-server --port %s' % store.CONFIG['port']), shell=False, stdout=subprocess.PIPE, stderr=sys.stderr)
        self.redis = redis.Redis(host=store.CONFIG["host"], port=store.CONFIG["port"],
                                 socket_connect_timeout=store.CONFIG["connect_timeout"], socket_timeout=store.CONFIG["read_write_timeout"])
        self.store = store.Store()

    def tearDown(self):
        self.redis_server.terminate()
        self.redis_server.wait()

    def test_get_score(self):
        fields = {
            'phone': '5555555',
            'email': 'my@email.com',
        }

        key = "uid:" + hashlib.md5(fields['phone']).hexdigest()
        value = 1

        self.redis.set(key, value)
        self.assertEqual(get_score(self.store, **fields), value)

        self.redis.delete(key)
        self.assertEqual(get_score(self.store, **fields), 3)

    def test_get_interests(self):
        cid = 1
        interests = ['interest']
        key = 'i:%s' % cid

        self.redis.set(key, json.dumps(interests))
        self.assertEqual(get_interests(self.store, cid), interests)

        self.redis.delete(key)
        self.assertEqual(get_interests(self.store, cid), [])


class TestStorageBadConnection(TestCase):
    def test_get_score(self):
        fields = {
            'phone': '5555555',
            'email': 'my@email.com',
        }

        st = store.Store()
        self.assertEqual(get_score(st, **fields), 3)

    def test_get_interests(self):
        cid = 1
        st = store.Store()

        self.assertEqual(get_interests(st, cid), [])
