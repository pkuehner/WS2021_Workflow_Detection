import unittest

import pandas as pd
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.bpmn.bpmn_graph import BPMN
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.log.util import dataframe_utils

import create_wf_model as pt_converter
from bpmn_converter import convert_wf_to_bpmn
from pattern_util import pattern_finder


class TestPatternUtil(unittest.TestCase):

    def test_or(self):
        log_csv = pd.read_csv('../test-data/OR.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)
        pattern_finder(log, wf_model)
        bpmn_model = convert_wf_to_bpmn(wf_model)
        found_one = False
        for node in bpmn_model.get_nodes():
            if isinstance(node, BPMN.InclusiveGateway):
                self.assertTrue(node.get_name().startswith('or_1'))
                found_one = True
        self.assertTrue(found_one)

    def test_and(self):
        log_csv = pd.read_csv('../test-data/AND.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)
        pattern_finder(log, wf_model)
        bpmn_model = convert_wf_to_bpmn(wf_model)
        found_one = False
        for node in bpmn_model.get_nodes():
            if isinstance(node, BPMN.ParallelGateway):
                self.assertTrue(node.get_name().startswith('parallel_1'))
                found_one = True
        self.assertTrue(found_one)

    def test_xor(self):
        log_csv = pd.read_csv('../test-data/XOR.csv', sep=',')
        log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
        log_csv = log_csv.sort_values('time:timestamp')
        log = log_converter.apply(log_csv)
        ptree = inductive_miner.apply_tree(log)
        #
        wf_model = pt_converter.apply(ptree)
        pattern_finder(log, wf_model)
        bpmn_model = convert_wf_to_bpmn(wf_model)
        found_one = False
        for node in bpmn_model.get_nodes():
            if isinstance(node, BPMN.ExclusiveGateway):
                self.assertTrue(node.get_name().startswith('xor_1'))
                found_one = True
        self.assertTrue(found_one)


if __name__ == '__main__':
    unittest.main()
