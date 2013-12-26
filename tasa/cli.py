"""
This should probably be rewritten at some point. It's not taking good
advantage of argparse.
"""

import argparse
import sys
import time
import inspect
import logging
import signal
import sys
from multiprocessing import Process

import tasa
from tasa.worker import BaseWorker


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def signal_handler(signal, frame):
    sys.exit(0)


def _get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-v', '--version', action='version',
        version='Tasa %s on Python %s' % (
            tasa.__version__, sys.version))
    # add common argparser arguments here
    return parser


def run():
    sys.path.insert(0, '')
    parser = _get_argparser()
    parser.description = 'Run a tasa worker.'
    parser.add_argument('worker',
                        type=lambda w: w.partition(':')[::2],
                        help='Worker module. In the form: '
                        '"path.to.my.module:MyWorkerClass". Relative to '
                        'the current directory.')
    args = parser.parse_args()

    worker_class_name = args.worker[1] or 'Worker'
    worker_module = __import__(args.worker[0], globals(), locals(),
                               [worker_class_name])
    try:
        WorkerClass = getattr(worker_module, worker_class_name)
    except AttributeError:
        print "No matching workers found.\n"
        potential_workers = inspect.getmembers(
            worker_module,
            lambda x: type(x) == type and issubclass(x, BaseWorker))
        if potential_workers:
            print "Found potential workers:"
            for name, value in potential_workers:
                print ':'.join([args.worker[0], name])
        exit(1)
    worker = WorkerClass()
    print 'Running worker: %s:%s' % (args.worker[0],
                                     worker.__class__.__name__)
    try:
        for job in worker:
            if job:
                logger.info("Doing job: %s:%s",
                            worker.__class__.__name__,
                            str(job)[:50])
            else:
                # FIXME: do something better here
                time.sleep(.3)
    except KeyboardInterrupt:
        print 'Exiting worker.'


def runm():
    """ This is super minimal and pretty hacky, but it counts as a first pass.
    """
    signal.signal(signal.SIGINT, signal_handler)
    count = int(sys.argv.pop(1))
    processes = [Process(target=run, args=()) for x in range(count)]
    try:
        for p in processes:
            p.start()
    except KeyError:
        # Not sure why we see a keyerror here. Weird.
        pass
    finally:
        for p in processes:
            p.join()


def log():
    parser = _get_argparser()
    parser.description = 'Follow logs from a running tasa system.'
    args = parser.parse_args()
    raise NotImplemented()


if __name__ == '__main__':
    # deal with being run directly rather than as an installed script
    cmd = 'undefined' if len(sys.argv) < 2 else sys.argv.pop(1)
    if cmd == 'run':
        run()
    elif cmd == 'log':
        log()
    else:
        print "First argument must be 'run' or 'log'"
