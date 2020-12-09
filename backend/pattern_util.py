from wf_graph import WF
import create_wf_model as pt_converter
from wf_pattern_visualizer import graphviz_visualization as wf_visualizer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.visualization.common import save as gsave

patterns = {}


def create_pattern(name, incoming_nodes, outgoing_nodes, partner, inner_nodes, is_loop = False, is_or = False):
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
        "isLoop": is_loop,
        "is_or": is_or
    }
    patterns[name] = pattern
    return pattern

def find_split_join_pattern(node, end):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.ExclusiveGateway):
        if node.get_name() in patterns:
            return [node.get_name()]
        if node.get_name().endswith('split'):
            join_node, isLoop = find_join_for_XOR_Split(node, 0)
            inner_patterns = []
            for arc in out_arcs:
                target = arc.get_target()
                inner_pattern = find_split_join_pattern(target, join_node.get_name())
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
                inner_pattern = find_split_join_pattern(target, join_node.get_name())
                inner_patterns.extend(inner_pattern)
            create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns)
            return [node.get_name()]

    if node.get_name() != end:
        inner_patterns = [node.get_name()]
        for arc in out_arcs:
            target = arc.get_target()
            inner_patterns.extend(find_split_join_pattern(target, end))
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


def check_patterns_for_or():
    for pattern in patterns:
        pattern = patterns[pattern]
        if pattern['name'].startswith('parallel'):
            is_or = True
            for node in pattern['inner_nodes']:
                if 'inner_nodes' in node:
                    if not node['name'].startswith('xor') or node['inner_nodes'] > 1:
                        is_or = False
                        break
                else:
                    is_or = False
                    break
            pattern['is_or'] = is_or


def recreate_sequences(node, seen):
        if(node not in seen):
            sequence = find_split_join_pattern(node, None)

            seen.add(node)
            if sequence[-1] != 'end':
                pattern = patterns[sequence[-1]]
                partner = pattern['partner']
                if pattern['isLoop']:
                    print('Found Loop')
                    for node_2 in wf_model.get_nodes():
                        if node_2.get_name() == pattern['inner_nodes'][1]:
                            sequence.append(recreate_sequences(node_2, seen))
                        if node_2.get_name() == pattern['inner_nodes'][0]:
                            sequence.append(recreate_sequences(node_2, seen))
                else:
                    for node_2 in wf_model.get_nodes():
                        if node_2.get_name() == partner:
                            for target in node_2.get_out_arcs():
                                sequence.extend(recreate_sequences(target.get_target(), seen))
            return sequence
        return []

def expand_inner_nodes(pattern):
    found = True
    seen = []
    while found:
        found = False
        for node in pattern['inner_nodes']:
            if node in patterns:
                pattern['inner_nodes'].remove(node)
                seen.append(node)
                pattern['inner_nodes'].extend(patterns[node]['inner_nodes'])
                pattern['inner_nodes'].append(patterns[node]['partner'])
                found = True
    pattern['inner_nodes'].extend(seen)

def discover_patterns(wf_model):
    for node in wf_model.get_nodes():
        find_split_join_pattern(node, None)

    check_patterns_for_or()
    print(patterns)

    for node in wf_model.get_nodes():
        if isinstance(node, WF.StartEvent):
            print(recreate_sequences(node, set()))

log = xes_import.apply('logs/running-example.xes')
# import pandas as pd
# from pm4py.objects.log.util import dataframe_utils
# from pm4py.objects.conversion.log import converter as log_converter
#
# log_csv = pd.read_csv('test-data/OR.csv', sep=',')
# log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
# log_csv = log_csv.sort_values('time:timestamp')
# log = log_converter.apply(log_csv)
ptree = inductive_miner.apply_tree(log)

from pm4py.visualization.process_tree import visualizer as pt_vis_factory
wf_model = pt_converter.apply(ptree)


discover_patterns(wf_model)
expand_inner_nodes(patterns['xor_2_split'])
print(patterns['xor_2_split'])
gviz = wf_visualizer(wf_model, patterns['xor_2_split'])
model_path = 'models/' + 'test' + '.png'
gsave.save(gviz, model_path)
# for node in wf_model.get_nodes():
# print(find_pattern(node))
