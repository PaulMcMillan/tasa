import itertools
import json
import logging
import os
import pickle

import redis

import tasa

# LPOP RPush

logger = logging.getLogger(__name__)


class LazyRedis(object):
    def __getattr__(self, name):
        redis_address = getattr(tasa.conf, 'redis', None)
        if redis_address:
            obj = redis.StrictRedis.from_url(redis_address)
        else:
            obj = redis.StrictRedis()
        self.__class__ = obj.__class__
        self.__dict__ = obj.__dict__
        return getattr(obj, name)


connection = LazyRedis()


class Queue(object):
    """ Basic queue object implemented with Redis lists. """
    # Read blocking timeout in seconds. -1 is non-blocking, 0 is
    # block forever.
    blocking = -1

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
        if self.blocking >= 0:
            # returns queue name and item, we just need item
            res = self.redis.blpop([self.name], timeout=self.blocking)
            if res:
                res = res[1]
        else:
            res = self.redis.lpop(self.name)
        value = self.deserialize(res)
        logger.debug('Popped from "%s": %s', self.name, repr(value))
        return value

    def send(self, *args):
        """ Send a value to this LIFO Queue.

        Provided argument is serialized and pushed out. Don't send None.
        """
        # this and the serializer could use some streamlining
        if None in args:
            raise TypeError('None is not a valid queue item.')
        serialized_values = [self.serialize(value) for value in args]
        logger.debug('Sending to "%s": %s', self.name, serialized_values)
        return self.redis.rpush(self.name, *serialized_values)

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
        logger.debug('Clearing queue: "%s"', self.name)
        return self.redis.delete(self.name)

    def __getitem__(self, key):
        """ Allow non-consuming slice access to queues. """
        if isinstance(key, int):
            return self.deserialize(self.redis.lindex(self.name, key))
        elif isinstance(key, slice):
            if key.step:
                raise TypeError, "Slice steps are not supported"
            start = 0 if key.start is None else key.start
            stop = -1 if key.stop is None else key.stop
            return (self.deserialize(item) for item in
                    self.redis.lrange(self.name, start, stop))
        else:
            raise TypeError, "Invalid argument type."

    def __len__(self):
        """ Return the length of this queue. """
        return self.redis.llen(self.name)


class PickleQueue(Queue):
    """ A queue you can put binary objects into. Not human readable.

    Don't unpickle untrusted data!
    """
    def serialize(self, value):
        return pickle.dumps(value)

    def deserialize(self, value):
        if value:
            return pickle.loads(value)
