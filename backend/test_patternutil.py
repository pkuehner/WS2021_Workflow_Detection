import unittest

import pandas as pd
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils

import create_wf_model as pt_converter
from pattern_util import pattern_finder


class TestPatternUtil(unittest.TestCase):

    def test_or(self):
        log_csv = pd.read_csv('test-data/OR.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('or_1_split', patterns)

    def test_loop(self):
        log_csv = pd.read_csv('test-data/LOOP.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('xor_1_split', patterns)
        self.assertEqual(patterns['xor_1_split']['isLoop'], True)

    def test_and(self):
        log_csv = pd.read_csv('test-data/AND.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('parallel_1_split', patterns)

    def test_multimerge(self):
        log_csv = pd.read_csv('test-data/multi-merge.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('parallel_1_split', patterns)
        self.assertEqual(patterns['parallel_1_split']['is_multi_merge'], True)

    def test_multimerge_tracevalidation(self):
        log_csv = pd.read_csv('test-data/LOOP2.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('parallel_1_split', patterns)
        self.assertEqual(patterns['parallel_1_split']['is_multi_merge'], False)

    def test_XOR(self):
        log_csv = pd.read_csv('test-data/XOR.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('xor_1_split', patterns)

    def test_discriminator(self):
        log_csv = pd.read_csv('test-data/1-out-of-4.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('parallel_discr_1_of_4_1_split', patterns)

    def test_discriminator(self):
        log_csv = pd.read_csv('test-data/2-out-of-4.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('parallel_discr_2_of_4_1_split', patterns)

    def test_merge(self):
        log_csv = pd.read_csv('test-data/XOR.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)
        patterns = p_finder.patterns

        self.assertIn('xor_1_split', patterns)
        p_finder.merge_join('xor_1_split')
        patterns = p_finder.patterns
        self.assertNotIn('xor_1_split', patterns)

    def test_patterns_to_json(self):
        log_csv = pd.read_csv('test-data/or_loop.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)

        p_finder = pattern_finder(log, wf_model)

        patterns = p_finder.patterns_to_json()
        self.assertEqual(patterns,
                         '[{"pattern_node": "or_1_split", "incoming_nodes": ["a"], "outgoing_nodes": ["b", "c"], '
                         '"pattern_type": "OR Split"}, {"pattern_node": "or_1_join", "incoming_nodes": ["b", "c"], '
                         '"outgoing_nodes": ["e"], "pattern_type": "OR Join"}, {"pattern_node": "xor_1_split", '
                         '"incoming_nodes": ["f"], "outgoing_nodes": ["end", "xor_1_join"], "pattern_type": "Loop '
                         'End"}, {"pattern_node": "xor_1_join", "incoming_nodes": ["start", "xor_1_split"], '
                         '"outgoing_nodes": ["a"], "pattern_type": "Loop Start"}, {"pattern_node": "e", '
                         '"incoming_nodes": [], "outgoing_nodes": ["f"], "pattern_type": "Sequence"}]')


if __name__ == '__main__':
    unittest.main()
