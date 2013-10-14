

class BaseWorker(object):
    qinput = None
    qoutput = None

    def jobs(self):
        """ Iterator that produces jobs to run in this worker.

        This returns None (a non-job) when there is nothing in the queue.
        """
        return self.qinput

    def handle(self, job):
        # should handle decide about None here?
        result = self.run(job)
        if result:
            # this should group up send(*result[:n]) since we're breaking the
            # generator here
            for r in result:
                self.qoutput.send(r)

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
