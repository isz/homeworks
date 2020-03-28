#!/usr/bin/env python
# # -*- coding: utf-8 -*-
import json
import hashlib
from unittest import TestCase
from datetime import datetime

from tests import cases

import api

class ApiFuncTest(TestCase):
    def test_get_interests_response(self):
        client_id = 1
        ctx = {}
        interests = ['books']
        store = {
            'i:%s'%client_id: json.dumps(interests)
        }

        request = api.ClientsInterestsRequest()
        request.parse_request({'client_ids':[client_id]})
        resp = api.get_interests_response(request, ctx, store, is_admin=False)

        self.assertEqual(ctx['nclients'], 1)
        self.assertEqual(resp[client_id], interests)

    def test_get_score_response(self):
        ctx = {}
        request = {'phone': '89222569873', 'email': 'my@email.com', 'first_name': 'Vasya', 'last_name': 'Pupkin', 'gender': 1, 'birthday': '26.04.1986'}

        validated_request = api.OnlineScoreRequest()
        validated_request.parse_request(request)

        class Store(object):
            def cache_get(self, *args, **kwargs):
                return 0

            def cache_set(self, *args, **kwargs):
                pass

        store = Store()

        resp = api.get_score_response(validated_request, ctx, store, True)
        self.assertEqual(set(ctx['has']), set(request.keys()))
        self.assertEqual(resp['score'], 42)

        resp = api.get_score_response(validated_request, ctx, Store(), False)
        self.assertEqual(set(ctx['has']), set(request.keys()))
        self.assertEqual(resp['score'], 5)

    def test_check_auth(self):
        request = {
            'account': 'google',
            'login': 'Vasya',
            'method': 'clients_interests',
            'token':  'token',
            'arguments': {}
        }
        validated_request = api.MethodRequest()
        validated_request.parse_request(request)

        self.assertFalse(api.check_auth(validated_request))

        request['token'] = hashlib.sha512("googleVasya" + api.SALT).hexdigest()
        validated_request.parse_request(request)

        self.assertTrue(api.check_auth(validated_request))
        request['account'] = 'admin'
        request['token'] = 'token'
        
        self.assertTrue(api.check_auth(validated_request))
        request['token'] = hashlib.sha512(datetime.now().strftime("%Y%m%d%H") + api.ADMIN_SALT).hexdigest()
        
        