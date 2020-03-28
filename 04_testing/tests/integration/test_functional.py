# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
import sys
import json
import shlex
import hashlib
import subprocess
import logging
import unittest
from datetime import datetime

import redis

from tests import cases

import api
import store

REDIS_PORT = 7777

logging.getLogger().setLevel(logging.CRITICAL)


class TestMethodHandler(unittest.TestCase):
    def setUp(self):
        self.context = {}
        self.headers = {}
        self.redis_server = subprocess.Popen(shlex.split(
            'redis-server --port %s' % REDIS_PORT), shell=False, stdout=subprocess.PIPE, stderr=sys.stderr)
        self.store = store.Store(port=7777)

    def tearDown(self):
        self.redis_server.terminate()
        self.redis_server.wait()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    def test_empty_request(self):
        _, code = self.get_response({})
        self.assertEqual(api.INVALID_REQUEST, code)

    @cases([
        {"account": "google", "method": "online_score", "arguments": {}},
        {"account": "google", "login": "Vasya", "arguments": {}},
        {"account": "google", "login": "Vasya", "method": "online_score"},
        {"account": "google", "login": "Vasya",
            "method": "bad_method", "arguments": {}},
    ])
    def test_bad_method_request(self, req):
        req["token"] = hashlib.sha512(
            req.get("account", "") + req.get("login", "") + api.SALT).hexdigest()

        resp, code = self.get_response(req)
        self.assertEqual(code, api.INVALID_REQUEST,
                         "Invalid Request was expected, but %s received" % resp)

    @cases([
        {"account": "google", "login": "Vasya", "token": "",
            "method": "online_score", "arguments": {}},
        {"account": "google", "login": "Vasya", "token": "tryam123",
            "method": "online_score", "arguments": {}},
        {"account": "google", "login": "admin", "token": "",
            "method": "online_score", "arguments": {}},
    ])
    def test_bad_auth(self, req):
        resp, code = self.get_response(req)
        self.assertEqual(code, api.FORBIDDEN,
                         "Forbidden was expected, but %s received" % resp)

    @cases([
        {},
        [],
        1,
        "phone",
        {"phone": "79222569873"},
        {"phone": "79222569873", "first_name": "Vasya"},
        {"phone": "79222569873", "last_name": "Pupkin"},
        {"phone": "79222569873", "gender": 1},
        {"phone": "79222569873", "birthday": "26.04.1986"},
        {"phone": "79222569873", "first_name": "Vasya", "birthday": "26.04.1986"},
        {"phone": "79222569873a", "email": "my@email.com"},
        {"phone": "79222569873", "email": "myemail.com"},
        {"first_name": "Vasya", "gender": 1},
        {"gender": "1", "birthday": "26.04.1986"},
        {"gender": 1, "birthday": "2604.1986"}
    ])
    def test_bad_score_request(self, args):
        req = {
            "account": "google",
            "login": "vasya",
            "token": hashlib.sha512("googlevasya" + api.SALT).hexdigest(),
            "method": "online_score",
            "arguments": args
        }
        resp, code = self.get_response(req)
        self.assertEqual(code, api.INVALID_REQUEST,
                         "Invalid Request was expected, but %s received" % resp)
        self.assertTrue(len(resp) != 0)

    @cases([
        {"phone": "79222569873", "email": "my@email.com"},
        {"phone": "+79222569873", "email": "my@email.com"},
        {"phone": 79222569873, "email": "my@email.com"},
        {"phone": "89222569873", "email": "my@email.com", "first_name": "Vasya"},
        {"first_name": "Vasya", "last_name": "Pupkin"},
        {"gender": 1, "birthday": "26.04.1986"}
    ])
    def test_valid_request(self, args):
        req = {
            "account": "google",
            "login": "Vasya",
            "token": hashlib.sha512("googleVasya" + api.SALT).hexdigest(),
            "method": "online_score",
            "arguments": args
        }
        resp, code = self.get_response(req)
        self.assertEqual(code, api.OK)
        score = resp["score"]
        self.assertTrue(isinstance(score, (int, float)) and score >= 0)
        self.assertEqual(set(args.keys()), set(self.context["has"]))

    def test_valid_admin_score(self):
        req = {
            "account": "google",
            "login": "admin",
            "method": "online_score",
            "token": hashlib.sha512(datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest(),
            "arguments":
            {
                "phone": "89222583625",
                "email": "my@email.com"
            }
        }
        resp, code = self.get_response(req)
        self.assertEqual(api.OK, code)
        score = resp["score"]
        self.assertEqual(score, 42)

    @cases([
        {},
        [],
        1,
        "bad",
        {"date": "31.12.2019"},
        {"client_ids": [], "date": "31.12.2019"},
        {"client_ids": 123, "date": "31.12.2019"},
        {"client_ids": "1,2", "date": "31.12.2019"},
        {"client_ids": {1: 2}, "date": "31.12.2019"},
        {"client_ids": ["1", "2"], "date": "31.12.2019"},
        {"client_ids": [1, 2], "date": 3112.2019},
    ])
    def test_bad_interest_request(self, args):
        req = {
            "account": "google",
            "login": "Vasya",
            "method": "clients_interests",
            "token": hashlib.sha512("googleVasya" + api.SALT).hexdigest(),
            "arguments": args
        }
        resp, code = self.get_response(req)
        self.assertEqual(api.INVALID_REQUEST, code,
                         "Invalid Request was expected, but %s received" % resp)
        self.assertTrue(len(resp) != 0)


class TestMethodInterest(unittest.TestCase):
    interests = {
        0: ["cars", "pets"],
        1: ["travel", "hi-tech"],
        2: ["sport", "music"],
        3: ["books", "tv"]
    }

    def setUp(self):
        self.context = {}
        self.headers = {}

        self.redis_server = subprocess.Popen(shlex.split(
            'redis-server --port %s' % REDIS_PORT), shell=False, stdout=subprocess.PIPE, stderr=sys.stderr)
        self.store = store.Store(port=REDIS_PORT)
        self.redis = self.redis = redis.Redis(
            host='localhost', port=REDIS_PORT, socket_connect_timeout=0.5, socket_timeout=0.5)

        for id, value in self.interests.items():
            self.redis.set("i:%s" % id, json.dumps(value))

    def tearDown(self):
        for id in self.interests.keys():
            self.redis.delete("i:%s" % id)

        self.redis_server.terminate()
        self.redis_server.wait()

    def get_response(self, request):
        return api.method_handler({"body": request, "headers": self.headers}, self.context, self.store)

    @cases([
        {"client_ids": [1, 2, 3],
            "date": datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "31.12.2019"},
        {"client_ids": [0]},
    ])
    def test_valid_interest_request(self, args):
        req = {
            "account": "google",
            "login": "Vasya",
            "method": "clients_interests",
            "token": hashlib.sha512("googleVasya" + api.SALT).hexdigest(),
            "arguments": args
        }

        ids = args['client_ids']

        resp, code = self.get_response(req)
        self.assertEqual(api.OK, code)
        self.assertEqual(len(args["client_ids"]), len(resp))
        self.assertEqual(self.context.get("nclients"), len(ids))

        for id, value in resp.items():
            self.assertEqual(value, self.interests[id])


if __name__ == "__main__":
    unittest.main()
