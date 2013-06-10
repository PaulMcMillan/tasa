import itertools
import json
import os

import redis

# LPOP RPush

class LazyRedis(object):
    def __getattr__(self, name):
        # ugh, fixme this is not a good way to do this
        redis_address = os.environ.get('REDIS_ADDRESS')
        if redis_address:
            obj = redis.StrictRedis.from_url(redis_address)
        else:
            obj = redis.StrictRedis()
        self.__class__ = obj.__class__
        self.__dict__ = obj.__dict__
        return getattr(obj, name)

connection = LazyRedis()


class Queue(object):
    # Queues are LPOP RPUSH by convention
    def __init__(self, name=None):
        # You can either init with a name,
        # or subclass and define self.name
        if name:
            self.name = name
        self.redis = connection

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


class BaseLog(object):
    # Note that log objects are blocking read, unlike queue objects
    def __init__(self, name=None):
        # You can either init with a name,
        # or subclass and define self.name
        if name:
            self.name = name
        self.redis = connection

    def send(self, message):
        return self.redis.publish(self.name, message)

    def next(self):
        pass

class DebugLog(BaseLog):
    name = 'log:debug'

class Log(BaseLog):
    name = 'log:default'
