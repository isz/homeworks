import redis
import json
from time import sleep


CONFIG = {
    "host": "localhost",
    "port": 6379,
    "retries": 3,
    "retry_timeout": 0.5,
    "connect_timeout": 0.5,
    "read_write_timeout": 0.5
}


class Store(object):
    def __init__(self, *args, **kwargs):
        try:
            with open(CONFIG["creds_file"]) as f:
                conf = json.loads(f.read(), encoding="UTF-8")

            if not isinstance(conf, dict):
                raise Exception("Wrong config")
        except:
            conf = {}

        password = conf.get("password", None)

        self._redis = redis.Redis(host=CONFIG["host"], port=CONFIG["port"], password=password,
                                       socket_connect_timeout=CONFIG["connect_timeout"],
                                       socket_timeout=CONFIG["read_write_timeout"])

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
        for i in range(CONFIG["retries"]):
            try:
                self._redis.set(key, value, ex=lifetime)
            except:
                sleep(CONFIG['retry_timeout'])
                continue
            else:
                return

    def get(self, key):
        for i in range(CONFIG["retries"]):
            try:
                value = self._redis.get(key)
            except:
                sleep(CONFIG['retry_timeout'])
                continue
            else:
                return value

        raise Exception("Can't read storage")