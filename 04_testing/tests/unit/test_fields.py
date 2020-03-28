#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from tests import cases

import api


class TestFields(TestCase):
    @cases([
        (api.CharField, '', ''),
        (api.CharField, 'good text', 'good text'),
        (api.ArgumentsField, {}, {}),
        (api.ArgumentsField, {'argument': 'value'}, {'argument': 'value'}),
        (api.EmailField, 'email@example.com', 'email@example.com'),
        (api.EmailField, 'my.mail@yandex.ru', 'my.mail@yandex.ru'),
        (api.EmailField, 'email@example.co.jp', 'email@example.co.jp'),
        (api.PhoneField, '79222569873', '79222569873'),
        (api.PhoneField, '+79222569873', '+79222569873'),
        (api.PhoneField, 79222569873, '79222569873'),
        (api.PhoneField, '89222569873', '89222569873'),
        (api.DateField, '', ''),
        (api.DateField, '01.01.2020', datetime(year=2020, month=1, day=1)),
        (api.DateField, '01.01.1900', datetime(year=1900, month=1, day=1)),
        (api.BirthDayField, '01.01.2020', datetime(year=2020, month=1, day=1)),
        (api.GenderField, 0, api.UNKNOWN),
        (api.GenderField, 1, api.MALE),
        (api.GenderField, 2, api.FEMALE),
        (api.ClientIDsField, [], []),
        (api.ClientIDsField, [1], [1]),
        (api.ClientIDsField, [1, 2, 3], [1, 2, 3]),
    ])
    def test_good_nullable_field(self, (field_class, val, target_val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, target_val)

    @cases([
        (api.CharField, 'good text', 'good text'),
        (api.ArgumentsField, {'argument': 'value'}, {'argument': 'value'}),
        (api.EmailField, 'email@example.com', 'email@example.com'),
        (api.EmailField, 'my.mail@yandex.ru', 'my.mail@yandex.ru'),
        (api.EmailField, 'email@example.co.jp', 'email@example.co.jp'),
        (api.PhoneField, '79222569873', '79222569873'),
        (api.PhoneField, '+79222569873', '+79222569873'),
        (api.PhoneField, 79222569873, '79222569873'),
        (api.PhoneField, '89222569873', '89222569873'),
        (api.DateField, '01.01.2020', datetime(year=2020, month=1, day=1)),
        (api.DateField, '01.01.1900', datetime(year=1900, month=1, day=1)),
        (api.BirthDayField, '01.01.2020', datetime(year=2020, month=1, day=1)),
        (api.GenderField, 1, api.MALE),
        (api.GenderField, 2, api.FEMALE),
        (api.ClientIDsField, [1], [1]),
        (api.ClientIDsField, [1, 2, 3], [1, 2, 3]),
    ])
    def test_good_not_nullable_field(self, (field_class, val, target_val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, target_val)

    @cases([
        (api.CharField, 1),
        (api.ArgumentsField, 1),
        (api.ArgumentsField, 'test'),
        (api.ArgumentsField, []),
        (api.ArgumentsField, ()),
        (api.EmailField, 'plainaddress'),
        (api.EmailField, '#@%^%#$@#$@#.com'),
        (api.EmailField, '@example.com'),
        (api.EmailField, 'Joe Smith <email@example.com>'),
        (api.EmailField, 'email.example.com'),
        (api.EmailField, 'email@example@example.com'),
        (api.EmailField, '.email@example.com'),
        (api.EmailField, 'email.@example.com'),
        (api.EmailField, 'email..email@example.com'),
        (api.EmailField, 'email@example'),
        (api.EmailField, 'email@-example.com'),
        (api.EmailField, 'email@example..com'),
        (api.EmailField, 'Abc..123@example.com'),
        (api.PhoneField, '7922O569873'),
        (api.PhoneField, ''),
        (api.PhoneField, 1),
        (api.DateField, '01.13.2020'),
        (api.DateField, '30.02.2020'),
        (api.DateField, '32.03.2020'),
        (api.DateField, 'aaaaaa'),
        (api.DateField, 1),
        (api.BirthDayField, '01.01.1900'),
        (api.GenderField, 3),
        (api.GenderField, 'male'),
        (api.ClientIDsField, 1),
        (api.ClientIDsField, ['1']),
        (api.ClientIDsField, '1'),
    ])
    def test_bad_nullable_field(self, (field_class, val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([
        (api.CharField, ''),
        (api.ArgumentsField, {}),
        (api.EmailField, 'plainaddress'),
        (api.EmailField, '#@%^%#$@#$@#.com'),
        (api.EmailField, '@example.com'),
        (api.EmailField, 'Joe Smith <email@example.com>'),
        (api.EmailField, 'email.example.com'),
        (api.EmailField, 'email@example@example.com'),
        (api.EmailField, '.email@example.com'),
        (api.EmailField, 'email.@example.com'),
        (api.EmailField, 'email..email@example.com'),
        (api.EmailField, 'email@example'),
        (api.EmailField, 'email@-example.com'),
        (api.EmailField, 'email@example..com'),
        (api.EmailField, 'Abc..123@example.com'),
        (api.PhoneField, '7922O569873'),
        (api.PhoneField, ''),
        (api.PhoneField, 1),
        (api.DateField, ''),
        (api.DateField, '01.13.2020'),
        (api.DateField, '30.02.2020'),
        (api.DateField, '32.03.2020'),
        (api.DateField, 'aaaaaa'),
        (api.DateField, 1),
        (api.BirthDayField, ''),
        (api.BirthDayField, '01.01.1900'),
        (api.GenderField, 0),
        (api.GenderField, 3),
        (api.GenderField, 'male'),
        (api.ClientIDsField, []),
        (api.ClientIDsField, 1),
        (api.ClientIDsField, ['1']),
        (api.ClientIDsField, '1'),
    ])
    def test_bad_not_nullable_field(self, (field_class, val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)
