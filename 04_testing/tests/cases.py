from functools import wraps

def cases(cases_list):
    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            for case in cases_list:
                new_args = args+(case,)
                func(*new_args)

        return wrapper

    return decorator

