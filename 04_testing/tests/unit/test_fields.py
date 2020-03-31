#!/usr/bin/env python
# -*- coding: utf-8 -*-
from unittest import TestCase
from datetime import datetime

from tests import cases

import api


class TestCharField(TestCase):
    @cases(['', 'good text', ])
    def test_good_nullable_field(self, val):
        api.CharField.name = '_field'

        class HelperClass(object):
            field = api.CharField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases(['good text', ])
    def test_good_not_nullable_field(self, val):
        api.CharField.name = '_field'

        class HelperClass(object):
            field = api.CharField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([1, {}, [], ])
    def test_bad_nullable_field(self, val):
        api.CharField.name = '_field'

        class HelperClass(object):
            field = api.CharField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases(['', 1, {}, [1]])
    def test_bad_not_nullable_field(self, val):
        api.CharField.name = '_field'

        class HelperClass(object):
            field = api.CharField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestArgumentsField(TestCase):
    @cases([
        {},
        {'argument': 'value'},
    ])
    def test_good_nullable_field(self, val):
        api.ArgumentsField.name = '_field'

        class HelperClass(object):
            field = api.ArgumentsField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([
        {'argument': 'value'},
    ])
    def test_good_not_nullable_field(self, val):
        api.ArgumentsField.name = '_field'

        class HelperClass(object):
            field = api.ArgumentsField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([
        1,
        'test',
        [],
        ()
    ])
    def test_bad_nullable_field(self, val):
        api.ArgumentsField.name = '_field'

        class HelperClass(object):
            field = api.ArgumentsField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([{}, ])
    def test_bad_not_nullable_field(self, val):
        api.ArgumentsField.name = '_field'

        class HelperClass(object):
            field = api.ArgumentsField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestEmailField(TestCase):
    @cases([
        'email@example.com',
        'my.mail@yandex.ru',
        'email@example.co.jp',
    ])
    def test_good_nullable_field(self, val):
        api.EmailField.name = '_field'

        class HelperClass(object):
            field = api.EmailField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([
        'email@example.com',
        'my.mail@yandex.ru',
        'email@example.co.jp',
    ])
    def test_good_not_nullable_field(self, val):
        api.EmailField.name = '_field'

        class HelperClass(object):
            field = api.EmailField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, val)

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
    def test_bad_nullable_field(self, val):
        api.EmailField.name = '_field'

        class HelperClass(object):
            field = api.EmailField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

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
    def test_bad_not_nullable_field(self, val):
        api.EmailField.name = '_field'

        class HelperClass(object):
            field = api.EmailField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestPhoneField(TestCase):
    @cases([
        '79222569873',
        '+79222569873',
        79222569873,
        '89222569873',
    ])
    def test_good_nullable_field(self, val):
        api.PhoneField.name = '_field'

        class HelperClass(object):
            field = api.PhoneField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, str(val))

    @cases([
        '79222569873',
        '+79222569873',
        79222569873,
        '89222569873',
    ])
    def test_good_not_nullable_field(self, val):
        api.PhoneField.name = '_field'

        class HelperClass(object):
            field = api.PhoneField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, str(val))

    @cases([
        '7922O569873',
        '',
        1,
    ])
    def test_bad_nullable_field(self, val):
        api.PhoneField.name = '_field'

        class HelperClass(object):
            field = api.PhoneField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([
        '7922O569873',
        '',
        1,
    ])
    def test_bad_not_nullable_field(self, val):
        api.PhoneField.name = '_field'

        class HelperClass(object):
            field = api.PhoneField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestDateField(TestCase):
    @cases([
        '01.01.2020',
        '01.01.1900',
    ])
    def test_good_nullable_field(self, val):
        api.DateField.name = '_field'

        class HelperClass(object):
            field = api.DateField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, datetime.strptime(val, '%d.%m.%Y'))

    @cases([
        '01.01.2020',
        '01.01.1900',
    ])
    def test_good_not_nullable_field(self, val):
        api.DateField.name = '_field'

        class HelperClass(object):
            field = api.DateField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, datetime.strptime(val, '%d.%m.%Y'))

    @cases([
        '01.13.2020',
        '30.02.2020',
        '32.03.2020',
        'aaaaaa',
        1,
    ])
    def test_bad_nullable_field(self, val):
        api.DateField.name = '_field'

        class HelperClass(object):
            field = api.DateField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([
        '',
        '01.13.2020',
        '30.02.2020',
        '32.03.2020',
        'aaaaaa',
        1,
    ])
    def test_bad_not_nullable_field(self, val):
        api.DateField.name = '_field'

        class HelperClass(object):
            field = api.DateField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestBirthDayField(TestCase):
    @cases([
        '01.01.2020',
    ])
    def test_good_nullable_field(self, val):
        api.BirthDayField.name = '_field'

        class HelperClass(object):
            field = api.BirthDayField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, datetime.strptime(val, '%d.%m.%Y'))

    @cases([
        '01.01.2020',
    ])
    def test_good_not_nullable_field(self, val):
        api.BirthDayField.name = '_field'

        class HelperClass(object):
            field = api.BirthDayField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, datetime.strptime(val, '%d.%m.%Y'))

    @cases([
        '01.01.1900',
    ])
    def test_bad_nullable_field(self, val):
        api.BirthDayField.name = '_field'

        class HelperClass(object):
            field = api.BirthDayField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([
        '',
        '01.01.1900',
    ])
    def test_bad_not_nullable_field(self, val):
        api.BirthDayField.name = '_field'

        class HelperClass(object):
            field = api.BirthDayField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestGenderField(TestCase):
    @cases([
        0,
        1,
        2,
    ])
    def test_good_nullable_field(self, val):
        api.GenderField.name = '_field'

        class HelperClass(object):
            field = api.GenderField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, val)
        self.assertIn(test_obj.field, api.GENDERS.keys())

    @cases([
        1,
        2,
    ])
    def test_good_not_nullable_field(self, val):
        api.GenderField.name = '_field'

        class HelperClass(object):
            field = api.GenderField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, val)
        self.assertIn(test_obj.field, api.GENDERS.keys())

    @cases([
        3,
        'male',
    ])
    def test_bad_nullable_field(self, val):
        api.GenderField.name = '_field'

        class HelperClass(object):
            field = api.GenderField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([
        0,
        3,
        'male',
    ])
    def test_bad_not_nullable_field(self, val):
        api.GenderField.name = '_field'

        class HelperClass(object):
            field = api.GenderField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)


class TestClientIDsField(TestCase):
    @cases([
        [],
        [1],
        [1, 2, 3],
    ])
    def test_good_nullable_field(self, val):
        api.ClientIDsField.name = '_field'

        class HelperClass(object):
            field = api.ClientIDsField(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)

        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([
        [1],
        [1, 2, 3],
    ])
    def test_good_not_nullable_field(self, val):
        api.ClientIDsField.name = '_field'

        class HelperClass(object):
            field = api.ClientIDsField(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([
        1,
        ['1'],
        '1, 2',
    ])
    def test_bad_nullable_field(self,val):
        api.ClientIDsField.name = '_field'

        class HelperClass(object):
            field = api.ClientIDsField(nullable=True)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)

    @cases([
        [],
        1,
        ['1'],
        '1, 2',
    ])
    def test_bad_not_nullable_field(self, val):
        api.ClientIDsField.name = '_field'

        class HelperClass(object):
            field = api.ClientIDsField(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)
