from tasa.store import Queue
from tasa.worker import BaseWorker


def test_base():
    class ExampleWorker(BaseWorker):
        qinput = Queue('test_queue')
        qoutput = Queue('test_output_queue')

        def run(self, job):
            for x in range(3):
                yield str(job) * (x + 1)

    w = ExampleWorker()
    qi = w.qinput
    qo = w.qoutput
    qi.clear()
    qo.clear()

    test_jobs = ['foo', 'bar', 'baz']
    for x in test_jobs:
        qi.send(x)

    jobs_run = []
    for job in w():
        if job is None:
            break
        jobs_run.append(job)

    assert jobs_run == test_jobs
    assert len(qo) == 3 * len(test_jobs)
    assert 'foo' in qo
    assert 'foofoo' in qo
    assert 'bar' in qo
    # skip over some values in the interator...
    assert 'bazbazbaz' in qo
    assert len(qo) == 0
