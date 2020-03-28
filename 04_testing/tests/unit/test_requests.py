#!/usr/bin/env python
# # -*- coding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from tests import cases

import api


class TestClientsInterestsRequest(TestCase):
    def test_parse_request(self):
        request = {'client_ids': [1], 'date': '01.01.2020'}
        validated_request = api.ClientsInterestsRequest()
        validated_request.parse_request(request)

        self.assertEqual(validated_request.client_ids,
                         request.get('client_ids'))
        self.assertEqual(validated_request.date, datetime.strptime(
            request.get('date'), '%d.%m.%Y'))

    @cases([
        {'client_ids': []},
        {'date': '01.01.2020'},
    ])
    def test_bad_parse_request(self, request):
        validated_request = api.ClientsInterestsRequest()
        self.assertRaises(Exception, validated_request.parse_request, request)

    @cases([
        {'client_ids': [1]},
        {'client_ids': [1], 'date': '01.01.2020'},
    ])
    def test_get_none_empty_fields(self, request):
        validated_request = api.ClientsInterestsRequest()
        validated_request.parse_request(request)

        fields = validated_request.get_none_empty_fields()

        self.assertEqual(set(fields.keys()), set(request.keys()))


class TestOnlineScoreRequest(TestCase):
    @cases([
        {},
        {'phone': '89222569873', 'email': 'my@email.com', 'first_name': 'Vasya',
            'last_name': 'Pupkin', 'gender': 1, 'birthday': '26.04.1986'},
    ])
    def test_parse_request(self, request):
        validated_request = api.OnlineScoreRequest()
        validated_request.parse_request(request)

        self.assertEqual(validated_request.phone, request.get('phone'))
        self.assertEqual(validated_request.email, request.get('email'))
        self.assertEqual(validated_request.first_name,
                         request.get('first_name'))
        self.assertEqual(validated_request.last_name, request.get('last_name'))
        self.assertEqual(validated_request.gender, request.get('gender'))
        date = request.get('birthday')
        if date:
            self.assertEqual(validated_request.birthday,
                             datetime.strptime(date, '%d.%m.%Y'))
        else:
            self.assertEqual(validated_request.birthday, None)

    @cases([
        {},
        {'email': 'my@email.com'},
        {'first_name': 'Vasya'},
        {'last_name': 'Pupkin'},
        {'gender': 1},
        {'birthday': '26.04.1986'},
        {'phone': '89222569873', 'first_name': 'Vasya', 'gender': 1},
        {'phone': '89222569873', 'email': 'my@email.com', 'first_name': 'Vasya',
            'last_name': 'Pupkin', 'gender': 1, 'birthday': '26.04.1986'},
    ])
    def test_get_none_empty_fields(self, request):
        validated_request = api.OnlineScoreRequest()
        validated_request.parse_request(request)

        fields = validated_request.get_none_empty_fields()

        self.assertEqual(set(fields.keys()), set(request.keys()))

    @cases([
        {'phone': '89222569873', 'email': 'my@email.com'},
        {'first_name': 'Vasya', 'last_name': 'Pupkin'},
        {'gender': 1, 'birthday': '26.04.1986'},
        {'phone': '89222569873', 'email': 'my@email.com', 'first_name': 'Vasya',
            'last_name': 'Pupkin', 'gender': 1, 'birthday': '26.04.1986'},
    ])
    def test_fieldset_valid(self, request):
        validated_request = api.OnlineScoreRequest()
        validated_request.parse_request(request)
        self.assertTrue(validated_request.fieldset_valid(), '%s' % (request,))

    @cases([
        {},
        {'phone': '89222569873'},
        {'email': 'my@email.com'},
        {'first_name': 'Vasya'},
        {'last_name': 'Pupkin'},
        {'gender': 1},
        {'birthday': '26.04.1986'},
        {'phone': '89222569873', 'first_name': 'Vasya', 'gender': 1},
    ])
    def test_fieldset_not_valid(self, request):
        validated_request = api.OnlineScoreRequest()
        validated_request.parse_request(request)
        self.assertFalse(validated_request.fieldset_valid())


class TestMethodRequest(TestCase):
    def test_parse_request(self):
        request = {'account': 'google', 'login': 'Vasya', 'method': 'clients_interests','token': 'token', 'arguments': {}}
        validated_request = api.MethodRequest()
        validated_request.parse_request(request)

        self.assertEqual(validated_request.account, request.get('account'))
        self.assertEqual(validated_request.login, request.get('login'))
        self.assertEqual(validated_request.method, request.get('method'))
        self.assertEqual(validated_request.token, request.get('token'))
        self.assertEqual(validated_request.arguments, request.get('arguments'))

    @cases([
        {},
        {'method': 'clients_interests','token': 'token', 'arguments': {}},
        {'login': 'Vasya', 'token': 'token', 'arguments': {}},
        {'login': 'Vasya', 'method': 'clients_interests', 'arguments': {}},
        {'login': 'Vasya', 'method': 'clients_interests','token': 'token', },
    ])
    def test_bad_parse_request(self, request):
        validated_request = api.MethodRequest()
        self.assertRaises(Exception, validated_request.parse_request, request)

    @cases([
        {'account': 'google', 'login': 'Vasya', 'method': 'clients_interests','token': 'token', 'arguments': {}},
        {'login': 'Vasya', 'method': 'clients_interests','token': 'token', 'arguments': {}}
    ])
    def test_get_none_empty_fields(self, request):
        validated_request = api.MethodRequest()
        validated_request.parse_request(request)

        fields = validated_request.get_none_empty_fields()

        self.assertEqual(set(fields.keys()), set(request.keys()))

    def test_is_admin(self):
        request = {'account': 'google', 'login': 'admin', 'method': 'clients_interests','token': 'token', 'arguments': {}}
        validated_request = api.MethodRequest()
        validated_request.parse_request(request)

        self.assertTrue(validated_request.is_admin)
