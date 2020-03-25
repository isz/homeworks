from unittest import TestCase
from functools import wraps

import api


def cases(cases_list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            for case in cases_list:
                new_args = args+(case,)
                func(*new_args)

        return wrapper

    return decorator


class TestFields(TestCase):
    @cases([
        (api.CharField, ''),
        (api.CharField, 'good text'),
        (api.ArgumentsField, {}),
        (api.ArgumentsField, {'argument': 'value'}),
        (api.EmailField, 'email@example.com'),
        (api.EmailField, 'my.mail@yandex.ru'),
        (api.EmailField, 'email@example.co.jp'),
    ])
    def test_good_nullable_field(self, (field_class, val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=True)

        test_obj = HelperClass()
        self.assertEqual(test_obj.field, None)
        test_obj.field = val
        self.assertEqual(test_obj.field, val)

    @cases([
        (api.CharField, 'good text'),
        (api.ArgumentsField, {'argument': 'value'}),
        (api.EmailField, 'email@example.com'),
        (api.EmailField, 'my.mail@yandex.ru'),
        (api.EmailField, 'email@example.co.jp'),
    ])
    def test_good_not_nullable_field(self, (field_class, val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=False)

        test_obj = HelperClass()
        test_obj.field = val
        self.assertEqual(test_obj.field, val)

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
    ])
    def test_bad_not_nullable_field(self, (field_class, val)):
        field_class.name = '_field'

        class HelperClass(object):
            field = field_class(nullable=False)

        test_obj = HelperClass()

        def assign():
            test_obj.field = val

        self.assertRaises(Exception, assign)
