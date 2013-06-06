

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
            for r in result:
                self.qoutput.send(r)

    def run(self, job):
        """ The actual work of the class.

        To take advantage of the result queuing, yield values rather
        than returning them.
        """
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
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


# This is... under construction.
# class SupervisorWorker(BaseWorker):
#     # This is really just for running Tasa worker processes. Don't
#     # pass things in here that expect reading or writing on stdio. If
#     # you need different behavior, subclass or write your own.
#     qinput = Queue('new_jobs')

#     workers = []

#     def run(self, job):
#         self.workers.append(subprocess.Popen(job))

#     def update(self):
#         # update any workers which may have been closed
#         for worker in self.workers[:]:
#             if worker.poll() is not None:
#                 self.workers.remove(worker)

#     def handle_signal(self):
#         pass
