from itertools import islice


class BaseWorker(object):
    qinput = None
    qoutput = None

    output_chunk_size = 1

    def jobs(self):
        """ Iterator that produces jobs to run in this worker.

        This returns None (a non-job) when there is nothing in the queue.
        """
        return self.qinput

    def handle(self, job):
        result = self.run(job)
        # don't do anything if result is None
        chunk = result and list(islice(result, self.output_chunk_size))
        while chunk:
            self.qoutput.send(*chunk)
            chunk = list(islice(result, self.output_chunk_size))

    def run(self, job):
        """ The actual work of the class.

        To take advantage of the result queuing, yield values rather
        than returning them.
        """
        raise NotImplementedError

    def __iter__(self, *args, **kwargs):
        """ Iterate through available jobs, handling each one.  Note
        that this construction leaves the blocking/non-blocking
        decision up to the job itself:
         - if jobs is finite, this handles each item once
         - if jobs is infinite, this yields None when a job is not available
        This works because None is never a valid job.
        """
        for job in self.jobs(*args, **kwargs):
            if job is not None:
                self.handle(job)
            yield job
