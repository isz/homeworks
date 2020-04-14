from functools import wraps
from unittest import TestCase


def cases(cases_list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            for case in cases_list:
                new_args = args+(case,)
                try:
                    func(*new_args)
                except TestCase.failureException, e:
                    print '\nTest not passed in case: %s' % str(case)
                    raise e

        return wrapper

    return decorator
