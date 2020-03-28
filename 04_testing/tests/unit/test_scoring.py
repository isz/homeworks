#!/usr/bin/env python
# # -*- coding: utf-8 -*-
import json
import hashlib
from unittest import TestCase
from datetime import datetime

from tests import cases

from scoring import get_interests, get_score


class Store(object):
    def __init__(self, interests=None, score=0):
        self.interests = interests
        self.score = score

    def cache_get(self, *args, **kwargs):
        return self.score

    def cache_set(self, *args, **kwargs):
        pass

    def get(self, key):
        return self.interests.get(key)


class TestScoring(TestCase):
    @cases([
        ({
            'phone': '5555555',
            'email': 'my@email.com',
            'birthday': datetime(2020, 1, 1),
            'gender': 1,
            'first_name': 'first',
            'last_name': 'last'
        }, 5),
        ({
            'email': 'my@email.com',
            'birthday': datetime(2020, 1, 1),
            'gender': 1,
            'first_name': 'first',
            'last_name': 'last'
        }, 3.5),
        ({
            'birthday': datetime(2020, 1, 1),
            'gender': 1,
            'first_name': 'first',
            'last_name': 'last'
        }, 2),
        ({
            'gender': 1,
            'first_name': 'first',
            'last_name': 'last'
        }, 0.5),
        ({
            'birthday': datetime(2020, 1, 1),
            'first_name': 'first',
            'last_name': 'last'
        }, 0.5),
        ({
            'birthday': datetime(2020, 1, 1),
            'gender': 1,
            'last_name': 'last'
        }, 1.5),
        ({
            'birthday': datetime(2020, 1, 1),
            'gender': 1,
            'first_name': 'first',
        }, 1.5),
        ({}, 0),
    ])
    def test_get_score(self, (field_set, score_value)):
        store = Store()
        self.assertEqual(get_score(store, **field_set), score_value)

        store = Store(score=1)

        self.assertEqual(get_score(store, **field_set), 1)

    def test_get_interests(self):
        cid = 1
        interests = ['interest']

        interest_dict = {
            'i:%s' % cid: json.dumps(interests),
        }
        store = Store(interests=interest_dict)

        self.assertEqual(get_interests(store, cid), interests)
        self.assertEqual(get_interests(store, cid+1), [])

