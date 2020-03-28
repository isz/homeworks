import redis
import json
from time import sleep


class Store(object):
    def __init__(self, host='localhost', port=6379, password=None, retries=3, retry_timeout=0.5, connect_timeout=0.5, read_write_timeout=0.5):
        self.retries = retries
        self.retry_timeout = retry_timeout
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

    def cache_set(self, key, value, lifetime):
        for i in range(self.retries):
            try:
                self._redis.set(key, value, ex=lifetime)
            except:
                sleep(self.retry_timeout)
                continue
            else:
                return

    def get(self, key):
        for i in range(self.retries):
            try:
                value = self._redis.get(key)
            except:
                sleep(self.retry_timeout)
                continue
            else:
                return value

        raise Exception("Can't read storage")
