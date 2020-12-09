from wf_graph import WF
import create_wf_model as pt_converter
from pm4py.objects.conversion.process_tree import converter as bpmn_converter
from wf_pattern_visualizer import graphviz_visualization as wf_visualizer
from bpmn_visualizer import graphviz_visualization as bpmn_visualizer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.petrinet import visualizer as pn_visualizer
from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.visualization.common import save as gsave
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.process_tree.pt_operator import Operator

patterns = {}


def create_pattern(name, incoming_nodes, outgoing_nodes, partner, inner_nodes, is_loop = False):
    """This function creates a pattern object that can then be easily uses as JSON object

        Parameters:
        name (String): Name of the pattern (e.G, XOR-Split),
        incoming_nodes (List<String>): List of ids of incoming nodes into the pattern node
        outgoing_nodes (List<String>): List of ids of outgoing nodes into the pattern node
        inner_nodes (List<String>): List of ids of nodes inside the pattern (between split and merge e.G)
        partner (String): Partner node id (e.G for a split this would be the join or vice versa)

        Returns:
        {
            "name": name,
            "incoming_nodes": incoming_nodes,
            "outgoing_nodes": outgoing_nodes,
            "partner": partner,
            "inner_nodes": inner_nodes
        }

       """

    pattern = {
        "name": name,
        "incoming_nodes": incoming_nodes,
        "outgoing_nodes": outgoing_nodes,
        "partner": partner,
        "inner_nodes": inner_nodes,
        "isLoop": is_loop
    }
    patterns[name] = pattern
    return pattern


def find_patterns(wf_model):
    for node in wf_model.get_nodes():
        if isinstance(node, WF.ExclusiveGateway):
            if node.get_name().endswith('split'):
                print(find_join_for_XOR_Split(node, 0))


def find_pattern(node, end):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.ExclusiveGateway):
        if node.get_name() in patterns:
            return [node.get_name()]
        if node.get_name().endswith('split'):
            join_node, isLoop = find_join_for_XOR_Split(node, 0)
            inner_patterns = []
            for arc in out_arcs:
                target = arc.get_target()
                inner_pattern = find_pattern(target, join_node.get_name())
                inner_patterns.extend(inner_pattern)
            create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns, isLoop)
            return [node.get_name()]

    if isinstance(node, WF.ParallelGateway):
        if node.get_name() in patterns:
            return [node.get_name()]
        if node.get_name().endswith('split'):
            join_node = find_join_for_And_Split(node, 0)
            inner_patterns = []
            for arc in out_arcs:
                target = arc.get_target()
                inner_pattern = find_pattern(target, join_node.get_name())
                inner_patterns.extend(inner_pattern)
            create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns)
            return [node.get_name()]

    if node.get_name() != end:
        inner_patterns = [node.get_name()]
        for arc in out_arcs:
            target = arc.get_target()
            inner_patterns.extend(find_pattern(target, end))
        return inner_patterns

    return []


def find_join_for_XOR_Split(node, openSplits):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.ExclusiveGateway):
        if node.get_name().endswith('split'):
            openSplits += 1
        else:
            openSplits -= 1
        if openSplits == 0:
            return node, False
    join_node = None
    isLoop = False
    for arc in out_arcs:
        arc_node = arc.get_target()
        x_join, is_loop = find_join_for_XOR_Split(arc_node, openSplits)
        if x_join != None:
            join_node = x_join  # TODO: This probably is a loop
        else:
            isLoop = True
    return join_node, isLoop

def find_join_for_And_Split(node, openSplits):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.ParallelGateway):
        if node.get_name().endswith('split'):
            openSplits += 1
        else:
            openSplits -= 1
        if openSplits == 0:
            return node
    for arc in out_arcs:
        arc_node = arc.get_target()
        x_join = find_join_for_And_Split(arc_node, openSplits)
        return x_join
    return None


#log = xes_import.apply('logs/running-example.xes')
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter

log_csv = pd.read_csv('test-data/OR.csv', sep=',')
log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
log_csv = log_csv.sort_values('time:timestamp')
log = log_converter.apply(log_csv)
ptree = inductive_miner.apply_tree(log)

from pm4py.visualization.process_tree import visualizer as pt_vis_factory
gviz = pt_vis_factory.apply(ptree, parameters={"format": "png"})
pt_vis_factory.view(gviz)
wf_model = pt_converter.apply(ptree)
for node in wf_model.get_nodes():
    find_pattern(node, None)


def check_patterns_for_or():
    for pattern in patterns:
        pattern = patterns[pattern]
        if pattern['name'].startswith('parallel'):
            for node in pattern['inner_nodes']:
                is_or = True
                if 'inner_nodes' in node:
                    if not node['name'].startswith('xor') or node['inner_nodes'] > 1:
                        is_or = False
                        break
                pattern['is_or'] = is_or


check_patterns_for_or()
print(patterns)
for node in wf_model.get_nodes():
    if isinstance(node, WF.StartEvent):
        print(find_pattern(node, None))

# for node in wf_model.get_nodes():
# print(find_pattern(node))
