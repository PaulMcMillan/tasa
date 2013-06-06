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
        # or subclass and define self.name
        if name:
            self.name = name
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
        """ Retrieve the next item in the queue.

        Returns deserialized value, or None if there were no entries
        in the Queue.
        """
        # we could use blpop here if we were ok with a minimum of an
        # entire second of blocking. For now, I think we're better off
        # polling and allowing adjustment for rate elsewhere.
        res = self.redis.lpop(self.name)
        return self.deserialize(res)

    def send(self, value):
        """ Send a value to this LIFO Queue.

        Provided argument is serialized and pushed out. Don't send None.
        """
        if value is None:
            raise TypeError('None is not a valid queue item.')
        return self.redis.rpush(self.name, self.serialize(value))

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
        """ Clear any existing values from this queue. """
        return self.redis.delete(self.name)

    def __len__(self):
        """ Return the length of this queue. """
        return self.redis.llen(self.name)


class Log(object):
    def __init__(self, name=None):
        # You can either init with a name,
        # or subclass and define self.name
        if name:
            self.name = name
        self.redis = get_redis()

    def send(self, message):
        return self.redis.publish(self.name, message)
