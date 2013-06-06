""" Welcome to the basic tasa example.

The easiest way to get this demo running is to install redis on this
machine, and make sure tasa is available on your pythonpath.

In our (contrived) example, we want to accept jobs consisting of 3
numbers as input (a, b, c) and do this operation to them in two
separate steps:
(a + b) * c

You'll understand this better if you open tasa/worker.py while you're
reading.

The entire example is contained in this file - in a real deployment
multiple workers would be running simultaneously as separate processes
for each stage.
"""

from tasa.worker import BaseWorker
from tasa.store import Queue


# Our first worker is going to take care of the addition part of our job.
class AddWorker(BaseWorker):
    # First we define our input and output queues
    # This worker is going to process items it finds in the 'add_input' queue
    qinput = Queue('add_input')
    # and when it's done with them, it puts them in the multiply_input
    # queue to be handled by the multiply worker.
    qoutput = Queue('multiply_input')

    # the only method we have to define is run, tasa takes care of
    # everything else.
    def run(self, job):
        # unpack the values passed in for the job
        a, b, c = job
        # do our operation
        added = a + b
        # and *YIELD* our result. The run method can a) return nothing
        # b) return a list of results, or c) yield each result as it
        # is calculated. In many cases, a run takes one input and
        # produces one output, as in this example. However, sometimes
        # one input results in multiple output jobs, which is why we
        # have this flexibilty.
        yield [added, c]
        # Note that the value we yield here is pushed into self.qoutput by
        # BaseWorker.handle(). If we need to send results to more than
        # one output queue, run can push results directly into queues.


# Now we define our multiply worker
class MultWorker(BaseWorker):
    # we take the queue used as output from add for our input
    qinput = Queue('multiply_input')
    # and since this is an example, we're going to print the result
    # rather than pushing it back into an output queue, so we can skip
    # defining qoutput.

    def run(self, job):
        # unpack the job again. Note that we could pass a more complex
        # data structure here - a dict is commonly useful.
        added, c = job
        result = added * c
        print "Result: %d" % result
        # and now we don't return anything, which is just fine. In a
        # real job, we might store our result in an object store here,
        # and yield a job complete message.


# Now we're going to stick some jobs in the queue for the
# workers. We'll make new instances to work with:
add_input = Queue('add_input')
multiply_input = Queue('multiply_input')
# There's nothing special about instances of Queue objects - as long
# as they have the same name, they point to the same queue. We could
# have defined these at the top and used them throughout the file, but
# it's often more convenient to be slightly redundant.

# Since this is an example, the first thing we're going to do is clear
# out the queues in case there's stale data in them.
add_input.clear()
multiply_input.clear()

# Now let's put some jobs in the queue
add_input.send([1,2,3])
add_input.send([3,5,9])
add_input.send([1,10,100])
# Each of these calls serializes the argument to json, and then sends
# it to the redis instance. Once they're sent, they're available to
# any worker polling that input queue
print "We have %d items in add_input" % len(add_input)

# However, since this is a demo, we don't have any workers
# running. Let's make one.
add_worker = AddWorker()
# Now we have an instance of the AddWorker, we call it to get a generator.
for job in add_worker():
    # This iterates over each job, and when it gets to the end of the
    # jobs, it starts returning None. This signal (returning None when
    # there is no work to do) is why you can't have a job consisting
    # of None.
    if not job:
        # so we break out
        break
    # If you write workers that run forever and don't break here, it
    # allows you to catch new jobs when are pushed into the system

    print "AddWorker processed job: %s" % job
# Keep in mind that the for loop is what iterated over the inputs and
# caused the jobs to be run. At this point, all the add jobs have
# finished and are waiting in the multiply queue.

print "We have %d items in add_input" % len(add_input)
print "We have %d items in multiply_input" % len(multiply_input)

# so we create an instance of MultWorker...
mult_worker = MultWorker()

# and iterate over it in a slightly different manner for the sake of
# example
current_job = True
while current_job:
    # remember, calling the worker class returns a generator, and
    # as you iterate over that, each call to next() does the actual
    # work for a job.
    print "Processing mult_job:",
    current_job = mult_worker().next()
    print "We have %d items in multiply_input" % len(multiply_input)

# at this point, the results from the mult worker should be printed
# above and there are no more jobs waiting in the queue

print "We have %d items in add_input" % len(add_input)
print "We have %d items in multiply_input" % len(multiply_input)

# As noted earlier, in a deployment you'd have individual processes
# iterating over each of these queues endlessly, taking input in, and
# if appropriate, putting results back out into one or more other
# queues.

