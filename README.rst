========
T-A S.A.
========

A simple framework for distributed task workflow using redis. Designed
to be easily extensible with code, rather than excessively featureful
out of the box.

Getting Started
---------------

Tasa requires a version of Python 2.7. If you're using an older
version, now is an excellent time to upgrade. If you're running Python
3, compatibility patches are welcome.

Make sure you have redis and the python redis bindings installed. If
you're using a remote redis instance, you can set the `REDIS_ADDRESS`
environment variable.

FAQ
---

 * I get a traceback like "redis.exceptions.ResponseError: operation
   not permitted"
   - Did you remember to set `REDIS_ADDRESS` env var? This will happen
     if you added a redis password and did not set a connection
     string.
