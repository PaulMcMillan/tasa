import argparse
import sys
import time


def _get_argparser():
    parser = argparse.ArgumentParser()
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

    worker_module = __import__(args.worker[0])
    try:
        WorkerClass = getattr(worker_module, args.worker[1] or 'Worker')
    except AttributeError:
        raise Exception('Worker not found')
    worker = WorkerClass()

    try:
        for job in worker():
            if job:
                print "Doing job:", job
            # FIXME: do something better here
            time.sleep(.1)
    except KeyboardInterrupt:
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

