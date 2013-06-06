import itertools
import json
import os

import redis

# LPOP RPush

def get_redis():
    # ugh, fixme this is horrible
    # This should become a shared pool once we have worker management
    redis_address = os.environ.get('REDIS_ADDRESS')
    if redis_address:
        return redis.StrictRedis.from_url(redis_address)
    else:
        return redis.StrictRedis()


class Queue(object):
    # Queues are LPOP RPUSH by convention
    def __init__(self, name=None):
        # You can either init with a name,
        # or subclass and define self.queue_name
        if name:
            self.queue_name = name
        self.redis = get_redis()

    def __iter__(self):
        return self

    def finite(self):
        """ Get a finite version of this queue. Useful for looping
        over existing items in the queue and then stopping.

        You can call this as many times as you like to get an object
        that will stop when there are no more items in the queue, but
        you need a new one each time you iterate over it.
        """
        return itertools.takewhile(lambda x: x is not None, self)

    def next(self):
        res = self.redis.lpop(self.queue_name)
        return self.deserialize(res)

    def send(self, value):
        return self.redis.rpush(self.queue_name, self.serialize(value))

    def serialize(self, value):
        """ A default data serializer """
        return json.dumps(value)

    def deserialize(self, value):
        """ A default data deserializer.

        Doesn't attempt to deserialize None.
        """
        if value:
            return json.loads(value)

    def clear(self):
        return self.redis.delete(self.queue_name)

    def __len__(self):
        return self.redis.llen(self.queue_name)
