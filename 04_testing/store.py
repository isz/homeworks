import redis
import json
from time import sleep

def retry_when_failed(attempts=3, attempt_timeout=1):
    def decorator(func):
        def wrapped(*args, **kwargs):
            for _ in range(attempts):
                try:
                    result = func(*args, **kwargs)
                except Exception, e:
                    sleep(attempt_timeout)
                else:
                    return result
            raise e
        return wrapped
    return decorator


class Store(object):
    def __init__(self, host='localhost', port=6379, password=None, connect_timeout=0.5, read_write_timeout=0.5):
        self._redis = redis.Redis(host=host, port=port, password=password,
                                  socket_connect_timeout=connect_timeout,
                                  socket_timeout=read_write_timeout)

    def cache_get(self, key):
        try:
            value = self.get(key)
        except:
            return None
        try:
            value = float(value)
        except:
            pass

        return value

    @retry_when_failed()
    def cache_set(self, key, value, lifetime):
        try:
            self._redis.set(key, value, ex=lifetime)
        except:
            pass

    @retry_when_failed()
    def get(self, key):
        return self._redis.get(key)
