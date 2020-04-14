#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from tests import cases

import api


class TestCharField(TestCase):
    field = api.CharField()

    @cases(['good text', ])
    def test_field(self, val):
        api.CharField.name = '_field'
        
        self.field = val
        self.assertEqual(self.field, val)


    @cases([1, {}, [], ])
    def test_bad_field(self, val):

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)


class TestArgumentsField(TestCase):
    field =  api.ArgumentsField()
    @cases([
        {'argument': 'value'},
    ])
    def test_good_field(self, val):
        api.ArgumentsField.name = '_field'

        self.field = val
        self.assertEqual(self.field, val)

    @cases([
        1,
        'test',
        [],
        ()
    ])
    def test_bad_field(self, val):
        api.ArgumentsField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)



class TestEmailField(TestCase):
    field = api.EmailField()
    @cases([
        'email@example.com',
        'my.mail@yandex.ru',
        'email@example.co.jp',
    ])
    def test_good_field(self, val):
        api.EmailField.name = '_field'

        self.field = val
        self.assertEqual(self.field, val)


    @cases([
        'plainaddress',
        '#@%^%#$@#$@#.com',
        '@example.com',
        'Joe Smith <email@example.com>',
        'email.example.com',
        'email@example@example.com',
        '.email@example.com',
        'email.@example.com',
        'email..email@example.com',
        'email@example',
        'email@-example.com',
        'email@example..com',
        'Abc..123@example.com',
    ])
    def test_bad_field(self, val):
        api.EmailField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)


class TestPhoneField(TestCase):
    field = api.PhoneField()

    @cases([
        '79222569873',
        '+79222569873',
        79222569873,
        '89222569873',
    ])
    def test_good_field(self, val):
        api.PhoneField.name = '_field'

        self.field = val

        self.assertEqual(self.field, str(val))

    @cases([
        '7922O569873',
        '',
        1,
    ])
    def test_bad_field(self, val):
        api.PhoneField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)

class TestDateField(TestCase):
    field = api.DateField()

    @cases([
        '01.01.2020',
        '01.01.1900',
    ])
    def test_good_field(self, val):
        api.DateField.name = '_field'

        self.field = val

        self.assertEqual(self.field, datetime.strptime(val, '%d.%m.%Y'))


    @cases([
        '',
        '01.13.2020',
        '30.02.2020',
        '32.03.2020',
        'aaaaaa',
        1,
    ])
    def test_bad_field(self, val):
        api.DateField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)


class TestBirthDayField(TestCase):
    field = api.BirthDayField()

    @cases([
        '01.01.2020',
    ])
    def test_good_field(self, val):
        api.BirthDayField.name = '_field'

        self.field = val

        self.assertEqual(self.field, datetime.strptime(val, '%d.%m.%Y'))

    @cases([
        '',
        '01.01.1900',
    ])
    def test_bad_field(self, val):
        api.BirthDayField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)


class TestGenderField(TestCase):
    field = api.GenderField()

    @cases([
        1,
        2,
    ])
    def test_good_field(self, val):
        api.GenderField.name = '_field'

        self.field = val

        self.assertEqual(self.field, val)
        self.assertIn(self.field, api.GENDERS.keys())

    @cases([
        0,
        3,
        'male',
    ])
    def test_bad_field(self, val):
        api.GenderField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)


class TestClientIDsField(TestCase):
    field = api.ClientIDsField()

    @cases([
        [1],
        [1, 2, 3],
    ])
    def test_good_field(self, val):
        api.ClientIDsField.name = '_field'

        self.field = val

        self.assertEqual(self.field, val)


    @cases([
        [],
        1,
        ['1'],
        '1, 2',
    ])
    def test_bad_field(self, val):
        api.ClientIDsField.name = '_field'

        def assign():
            self.field = val

        self.assertRaises(Exception, assign)
