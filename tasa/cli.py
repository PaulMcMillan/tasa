import argparse
import sys
import time

import tasa

def _get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version='Tasa %s on Python %s' % (
            tasa.__version__, sys.version),
                        )
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
        raise Exception('Worker not found')
    worker = WorkerClass()
    print 'Running worker: %s:%s' % (args.worker[0],
                                     worker.__class__.__name__)
    try:
        for job in worker:
            if job:
                print "Doing job:", job
            # FIXME: do something better here
            time.sleep(.1)
    except KeyboardInterrupt:
        print 'Exiting worker.'
        sys.exit()


def log():
    parser = _get_argparser()
    parser.description = 'Follow logs from a running tasa system.'
    args = parser.parse_args()


if __name__=='__main__':
    # deal with being run directly rather than as an installed script
    cmd = 'undefined' if len(sys.argv) < 2 else sys.argv.pop(1)
    if cmd == 'run':
        run()
    elif cmd == 'log':
        log()
    else:
        print "First argument must be 'run' or 'log'"

