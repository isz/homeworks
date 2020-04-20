#!/usr/bin/env python
# -*- coding: utf-8 -*-

from functools import update_wrapper, wraps


def disable(func):
    '''
    Disable a decorator by re-assigning the decorator's name
    to this function. For example, to turn off memoization:

    >>> memo = disable

    '''

    return func


def decorator(dec):
    '''
    Decorate a decorator so that it inherits the docstrings
    and stuff from the function it's decorating.
    '''
    def wrapper(func):
        return update_wrapper(dec(func), func)

    return wrapper


def countcalls(func):
    '''Decorator that counts calls made to the function decorated.'''
    @wraps(func)
    def wrapper(*args):
        wrapper.calls += 1
        return func(*args)
    wrapper.calls = 0
    return wrapper


def memo(func):
    '''
    Memoize a function so that it caches all return values for
    faster future lookups.
    '''
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            result = func(*args)
            cache[args] = result
        else:
            result = cache[args]
        update_wrapper(wrapper, func)
        return result

    return wrapper


def n_ary(func):
    '''
    Given binary function f(x, y), return an n_ary function such
    that f(x, y, z) = f(x, f(y,z)), etc. Also allow f(x) = x.
    '''
    @wraps(func)
    def wrapper (x, *args):
        return x if args else wrapper(x, *args)
    return wrapper

def format_func(func, args):
    args = ", ".join([str(i) for i in args])
    return "%s(%s)"%(func.__name__, args)

def trace(filler):
    '''Trace calls made to function decorated.

    @trace("____")
    def fib(n):
        ....

    >>> fib(3)
     --> fib(3)
    ____ --> fib(2)
    ________ --> fib(1)
    ________ <-- fib(1) == 1
    ________ --> fib(0)
    ________ <-- fib(0) == 1
    ____ <-- fib(2) == 2
    ____ --> fib(1)
    ____ <-- fib(1) == 1
     <-- fib(3) == 3

    '''

    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            filler_str = filler * wrapper.nesting
            func_str = format_func(func, args)
            print filler_str, "-->", func_str

            wrapper.nesting += 1
            result = func(*args)
            wrapper.nesting -= 1
            
            print filler_str, "-->", func_str, "-->", result
            return result
        
        wrapper.nesting = 0
        return wrapper
    return decorator


@memo
@countcalls
@n_ary
def foo(a, b):
    return a + b


@countcalls
@memo
@n_ary
def bar(a, b):
    return a * b


@countcalls
@trace("####")
@memo
def fib(n):
    """Some doc"""
    return 1 if n <= 1 else fib(n-1) + fib(n-2)


def main():
    print foo(4, 3)
    print foo(4, 3, 2)
    print foo(4, 3)
    print "foo was called", foo.calls, "times"

    print bar(4, 3)
    print bar(4, 3, 2)
    print bar(4, 3, 2, 1)
    print "bar was called", bar.calls, "times"

    print fib.__doc__
    fib(3)
    print fib.calls, 'calls made'


if __name__ == '__main__':
    main()
