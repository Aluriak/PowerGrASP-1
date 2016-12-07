
import random
import unittest

from powergrasp import observers
from powergrasp.atoms import AtomsModel
from powergrasp.motif import FoundMotif
from powergrasp.observers import (Priorities, ObserverBatch, ObjectCounter,
                                  ConnectedComponentsCounter)


class MockObserver(observers.CompressionObserver):

    def __init__(self, priority):
        assert isinstance(self, observers.CompressionObserver)
        if priority not in Priorities:
            priority = Priorities(priority)
        self._priority = priority

    @property
    def priority(self):
        return self._priority

    @staticmethod
    def bunch(priorities):
        return [MockObserver(p) for p in priorities]

    @staticmethod
    def random_priority():
        return random.choice((0, 20, 50, 80, 100))


class TestObserverBatch(unittest.TestCase):

    def compare_priorities(self, observers, expected_priorities:int):
        """Compare given list of expected priorities (int) with priorities
        found in given observers.
        Expected is reverse-sorted, in order to get bigger priority
        before the smaller ones.

        """
        for obs, p in zip(observers, sorted(expected_priorities, reverse=True)):
            self.assertEqual(obs.priority.value, p)


    def test_batch_adding(self):
        base = [MockObserver.random_priority() for _ in range(3)]
        add1 = [MockObserver.random_priority() for _ in range(3)]
        add2 = [MockObserver.random_priority() for _ in range(3)]
        add3 = [MockObserver.random_priority() for _ in range(3)]

        batch = ObserverBatch(MockObserver.bunch(base), None)
        self.compare_priorities(batch, base)

        batch += MockObserver.bunch(add1)
        self.compare_priorities(batch, base + add1)

        batch = batch + ObserverBatch(MockObserver.bunch(add2), None)
        self.compare_priorities(batch, base + add1 + add2)

        new_batch = batch + MockObserver.bunch(add3)
        self.assertIsNot(new_batch, batch)
        self.compare_priorities(new_batch, base + add1 + add2 + add3)
        self.compare_priorities(batch, base + add1 + add2)



class TestCounterObservers(unittest.TestCase):

    def test_object_counter(self):
        counter = ObjectCounter()
        obs = ObserverBatch([counter], None)
        motifs_found = [random.choice(('clique', 'biclique')) for _ in range(10)]
        for motif in motifs_found:
            obs.signal(model_found=FoundMotif(None, None, motif))
        for motif in set(motifs_found):
            with self.subTest(motif_name=motif):
                found = counter.count[motif]
                expected = motifs_found.count(motif)
                self.assertEqual(found, expected)

    def test_cc_counter(self):
        counter = ConnectedComponentsCounter()
        obs = ObserverBatch([counter], None)
        nb_ccs = random.randint(1, 10)
        ccs = tuple(random.sample(range(100), nb_ccs))
        obs.signal(cc_count_generated=nb_ccs)
        for idx, cc in enumerate(ccs):
            obs.signal(connected_component_started=(idx, cc, None, None))
            obs.signal(connected_component_stopped=AtomsModel([]))
            self.assertEqual(str(cc), counter.cc_name)
            self.assertEqual(idx, counter.cc_num)
        self.assertEqual(nb_ccs, counter.nb_ccs)
