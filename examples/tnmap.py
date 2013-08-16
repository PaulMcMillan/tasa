#!/usr/bin/python
"""
A script using tasa to distribute nmap workloads.

Usage:
$tasa tnmap:Runner &
$mkdir out
$tasa tnamp:Results &
$chmod +x tnmap.py
$./tnmap.py 10.0.0.0/24

"""

import subprocess
import sys
import time

import netaddr

from tasa.store import Queue
from tasa.worker import BaseWorker


class Runner(BaseWorker):
    qinput = Queue('job:raw')
    qoutput = Queue('result:raw')

    def run(self, job):
        outfile, command = job
        command = map(str, command)
        print "Running command: %s" % ' '.join(command)
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        yield [outfile, stdout]


class Results(BaseWorker):
    qinput = Queue('result:raw')

    def run(self, job):
        output_template, result = job
        output_filename = output_template.format(
            timestamp=time.time())
        with open(output_filename, 'w') as f:
            f.write(result)


class Monitor(BaseWorker):
    def jobs(self):
        while True:
            yield time.ctime()
            time.sleep(10)

    def run(self, job):
        queues = [Queue('job:raw'), Queue('result:raw')]
        for q in queues:
            print 'Queue:', q.name, len(q)


if __name__ == '__main__':
    SUBNET_PREFIXLEN = 27
    portlist = '80,443'
    ip = netaddr.IPNetwork(sys.argv[1])
    qinput = Queue('job:raw')

    if SUBNET_PREFIXLEN < ip.prefixlen:
        subnet_list = [ip,]
    else:
        subnet_list = ip.subnet(SUBNET_PREFIXLEN)

    for sub in subnet_list:
        cmd = ['nmap',
               '-T4',       # use aggressive timings
               '--open',    # only return open ports
               '-sS',       # SYN scan
               '-n',        # don't attempt DNS resolution
               '-PN',       # Treat all hosts as online (don't ping)
               '-oX', '-',  # XML output to stdout
               '-p', portlist,  # ports to scan
               str(sub)     # Target specification (hostname, IP
                            # addresses, ranges, subnets, etc.)
               ]
        qinput.send(['out/%s_%s_{timestamp}.xml' % (sub.ip, sub.prefixlen),
                     cmd])
