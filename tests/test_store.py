from tasa.store import Queue


def test_queue():
    myq = Queue('my_queue')
    # clean up anything that might be lingering
    myq.clear()
    assert len(myq) == 0
    assert myq.next() == None
    myq.send('foo')
    assert len(myq) == 1
    assert myq.next() == 'foo'
    assert len(myq) == 0


def test_clear():
    cq = Queue('clear_queue')
    cq.clear()
    assert len(cq) == 0
    cq.send('baz')
    assert len(cq) == 1
    assert cq.clear() == 1
    assert len(cq) == 0
    assert cq.next() == None


def test_iterq():
    iq = Queue('iter_queue')
    iq.clear()
    for x in range(10):
        iq.send(x)
    for x, y in zip(range(10), iq):
        assert x == y
    assert len(iq) == 0


def test_finite():
    iq = Queue('finite_test_queue')
    iq.clear()
    for x in range(10):
        iq.send(x)

    for x, y in zip(range(10) + [None] * 10, iq):
        assert x == y

    for x in range(10):
        iq.send(x)

    fq = iq.finite()
    assert len(iq) == 10
    assert range(10) == [x for x in fq]
    assert len(iq) == 0


def test_subclass():
    class NewQueue(Queue):
        name = 'new_queue_test'

    nq = NewQueue()
    nq.clear()
    nq.send('stuff')
    assert nq.next() == 'stuff'
