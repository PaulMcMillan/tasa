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
 #) configure `/etc/tassa/tasa.conf` to contain a configuration line like
    `redis='redis://password@example.org:6379/0'`
 #) tasa tnmap:Runner

Then run the results worker and inject jobs from the master
machine. Experiment with changing values in the script - the example
is actually general enough to run any process, not just nmap.

Don't forget to configure your redis server to listen on an ip
accessible to your clients, and set a password even if you are on a
private network. If you're on an untrusted network, you're responsible
for encryption - either tunnel over an SSH port forward, or wrap redis
in TLS using stud/stunnel.

How does it work?
-----------------

Tasa is primarily a thin framework to help you build composable work
flows. Break your problem into small chunks, run workers on several
machines, and insert jobs into the worker's input queue, and consume
them from the output.

FAQ
---

* I get a traceback with "redis.exceptions.ResponseError: operation
  not permitted"

  Did you remember to set a `redis` setting in `/etc/tasa/tasa.conf`?
  This will happen if you added a redis password and did not set a
  connection string.

* What version of redis-server do I need?

  Tasa is developed with redis 2.6.16. Older versions aren't explicitly
  tested, though the 2.4 branch will probably work with reduced
  functionality. Newer versions should work without trouble.

Security
--------

The security of tasa depends entirely on how you use it. If you use a
password and tunnel redis communications over an encrypted and
authenticated transport, you'll do pretty well. The easiest way to do
this is to use SSH port forwarding or ipsec to transport redis
traffic. You can also put stud in front of redis to do TLS, though
this is more complex.

The author uses tasa workers primary on disposable cloud hosts.
