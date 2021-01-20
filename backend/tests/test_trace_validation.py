import unittest

from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from importer import import_file
from trace_validation import validate_multi_merge_in_trace, get_m_in_discriminator


class TestTraceValidation(unittest.TestCase):

    def test_multi_merge_true(self):
        log = import_file('../test-data/multi-merge.csv')
        ptree = inductive_miner.apply_tree(log)
        #
        self.assertTrue(validate_multi_merge_in_trace(log, ['c', 'b'], ['d']))

    def test_multi_merge_false(self):
        log = import_file('../test-data/LOOP2.csv')
        ptree = inductive_miner.apply_tree(log)
        #
        self.assertFalse(validate_multi_merge_in_trace(log, ['c', 'b'], ['d']))

    def test_discr(self):
        log = import_file('../test-data/2-out-of-3.csv')
        ptree = inductive_miner.apply_tree(log)
        #
        self.assertEqual(get_m_in_discriminator(log, ['b1', 'b2', 'b3'], ['c']), 2)

    def test_discr2(self):
        log = import_file('../test-data/1-out-of-4.csv')
        ptree = inductive_miner.apply_tree(log)
        #
        self.assertEqual(get_m_in_discriminator(log, ['B1', 'B2', 'B3', 'B0'], ['C']), 1)

    def test_discr3(self):
        log = import_file('../test-data/3-out-of-4.csv')
        ptree = inductive_miner.apply_tree(log)
        #
        self.assertEqual(get_m_in_discriminator(log, ['B1', 'B2', 'B3', 'B0'], ['C']), 3)

    def test_discr4(self):
        log = import_file('../test-data/3-out-of-4.csv')
        ptree = inductive_miner.apply_tree(log)
        #
        self.assertEqual(get_m_in_discriminator(log, ['b1', 'b2', 'b3', 'b5'], ['c']), 'F')


if __name__ == '__main__':
    unittest.main()
