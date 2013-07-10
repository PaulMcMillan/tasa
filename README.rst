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

Quickstart example for Debian:

 #) sudo apt-get install redis-server python-pip nmap
 #) sudo pip install -U tasa
 #) wget https://raw.github.com/PaulMcMillan/tasa/master/examples/tnmap.py
 #) mkdir out
 #) tasa tnmap:Runner &
 #) tasa tnamp:Results &
 #) python tnmap.py 10.0.0.0/24

This quickstart installs tasa, downloads an example script for
distributed nmap, runs one task worker and one results worker, and
then inserts a job to scan a portion of your local net.

To actually use this example to distribute a task, on each worker node:

 #) sudo apt-get install python-pip nmap
 #) sudo pip install -U tasa
 #) wget https://raw.github.com/PaulMcMillan/tasa/master/examples/tnmap.py
 #) export REDIS_ADDRESS=redis://username:password@10.0.0.5:6379/0
 #) tasa tnmap:Runner

Then run the results worker and inject jobs from the master machine.

Don't forget to configure your redis server to listen on an ip
accessible to your clients, and for the love of Kaminsky, set a
password even if you are on a private network. If you're on an
untrusted network, you're responsible for encryption - either tunnel
over an SSH port forward, or wrap redis in TLS using stud/stunnel.

FAQ
---

* I get a traceback with "redis.exceptions.ResponseError: operation
  not permitted"

  Did you remember to set `REDIS_ADDRESS` env var? This will happen if
  you added a redis password and did not set a connection string.
