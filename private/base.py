import tornado
import hashlib
import logging
import arrow
import json

class RequestHandler(tornado.web.RequestHandler):

    def write_json(self, obj, pretty=True, status_code=None, tee_to_stdout=False):
        if status_code is not None:
            self.set_status(status_code)

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        if pretty:
            self.finish(json.dumps(obj, sort_keys=True, indent=4, separators=(",", ": ")))
            return

        self.finish(json.dumps(obj))

    def set_default_headers(self):
        self.set_header("access-control-allow-origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'GET, PUT, DELETE, OPTIONS')
        # HEADERS!
        self.set_header("Access-Control-Allow-Headers", "access-control-allow-origin,authorization,content-type")


class Backend(object):

    def __init__(self):
        self.cache = {}

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def _set_cache(self, name, value, expiry=1):
        """
        Set a cache to this backend.

        key         the name of this cache
        value       the value to store in this cache
        expiry      ttl in minutes
        """
        self.cache[name] = {
            "value": value,
            "expiry": int(arrow.now("+08:00").replace(minutes=expiry).float_timestamp * 1e6),
        }

    @tornado.gen.coroutine
    def clean_cache(self, loop=None):
        """
        Clean up the cache via their expiry.

        loop        the number of minutes before looping. if None, only run once.
        """
        while True:
            logging.debug("Cleaning cache ..")
            to_clean = set()
            now = (arrow.now("+08:00").float_timestamp * 1e6)
            for key, item in self.cache.items():
                if item["expiry"] < now:
                    to_clean.add(key)

            for key in to_clean:
                self.cache.pop(key, None)
            if loop is not None:
                logging.debug("Clean cache task sleeping for {0} minutes".format(loop))
                yield tornado.gen.Task(tornado.ioloop.IOLoop.instance().add_timeout, arrow.now("+08:00").timestamp + (loop * 60))
            else:
                break

    def _get_cache(self, name):
        """
        Get a item from a cache
        This will automatically remove the item if it is expired.
        If a callback was provided, it will be called and the item will not expire.
        """
        item = self.cache.get(name)
        if item is None:
            return None

        if item["expiry"] < (arrow.now("+08:00").float_timestamp * 1e6):
            self.cache.pop(name, None)
            return None

        return item["value"]

    def hash_cells(self, cells):
        cells_ordered_keys = list(cells.items())
        cells_ordered_keys.sort(key=lambda x: x[0])
        cells_hash_string = ",".join([ "{0}:{1}".format(v[0], v[1]) for v in cells_ordered_keys ]).encode('utf-8')
        cells_hash = hashlib.md5(cells_hash_string).hexdigest()
        return cells_hash
