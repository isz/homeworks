import redis
import json


CONFIG = {
    "host": "localhost",
    "port": 6379,
    "conf_file": "conf.json",
    "retries": 3,
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
        for i in range(CONFIG["retries"]):
            try:
                value = self._redis.get(key)
            except:
                continue
            else:
                try:
                    value = float(value)
                except:
                    pass
                return value

        return None

    def cache_set(self, key, value, lifetime):
        for i in range(CONFIG["retries"]):
            try:
                self._redis.set(key, value, ex=lifetime)
            except:
                continue
            else:
                return

    def get(self, key):
        for i in range(CONFIG["retries"]):
            try:
                value = self._redis.get(key)
            except:
                continue
            else:
                return value

        raise Exception("Can't read storage")

from time import sleep

if __name__ == "__main__":
    store = Store()
    store.cache_set("test", "hello world", 10)
    try:
        print store.get("test")
    except Exception, e:
        print (str(e))

    sleep(5)
    print store.get("test")
    print store.cache_get("test")
    sleep(5)
    print store.get("test")
