from wf_graph import WF
import create_wf_model as pt_converter
from wf_pattern_visualizer import graphviz_visualization as wf_visualizer
from pm4py.algo.discovery.inductive import algorithm as inductive_miner

from pm4py.objects.log.importer.xes import importer as xes_import
from pm4py.visualization.common import save as gsave

from backend.create_wf_model import change_and_xor_to_or

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

    if isinstance(node, WF.InclusiveGateway):
        if node.get_name() in patterns:
            return [node.get_name()]
        if node.get_name().endswith('split'):
            join_node = find_join_for_Or_Split(node, 0)
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

def find_join_for_Or_Split(node, openSplits):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.InclusiveGateway):
        if node.get_name().endswith('split'):
            openSplits += 1
        else:
            openSplits -= 1
        if openSplits == 0:
            return node
    for arc in out_arcs:
        arc_node = arc.get_target()
        x_join = find_join_for_Or_Split(arc_node, openSplits)
        return x_join
    return None


def check_patterns_for_or():
    for pattern in patterns:
        pattern = patterns[pattern]
        if pattern['name'].startswith('parallel'):
            is_or = True
            for node in pattern['inner_nodes']:
                if node in patterns:
                    node = patterns[node]
                    if not node['name'].startswith('xor') or len(node['inner_nodes']) > 1:
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

def merge_pattern(pattern, wf_model):
    pass

def get_node_by_name(name):
    for node in wf_model.get_nodes():
        if node.get_name() == name:
            return node



def make_ors(wf_model):
    for pattern in patterns:
        pattern = patterns[pattern]
        if pattern['is_or']:
            inner_nodes = []
            and_split_node = get_node_by_name(pattern['name'])
            and_join_node = get_node_by_name(pattern['partner'])
            xors = []
            for node in and_split_node.get_out_arcs():
                node = node.get_target()
                xors.append((node, get_node_by_name(patterns[node.get_name()]['partner'])))

            change_and_xor_to_or(wf_model, and_split_node, and_join_node, xors)


def discover_patterns(wf_model):
    for node in wf_model.get_nodes():
        find_split_join_pattern(node, None)

    check_patterns_for_or()
    print(patterns)

    for node in wf_model.get_nodes():
        if isinstance(node, WF.StartEvent):
            print(recreate_sequences(node, set()))

def patterns_to_json():
    patterns_list = []
    seen = set()
    seen.add('end')
    for pattern_name in patterns:
        for pattern in [pattern_name, patterns[pattern_name]['partner']]:
            incoming_nodes = []
            outgoing_nodes = []
            seen.add(pattern)
            node = get_node_by_name(pattern)
            for arc in node.get_in_arcs():
                incoming_nodes.append(arc.get_source().get_name())
            for arc in node.get_out_arcs():
                outgoing_nodes.append(arc.get_target().get_name())
            pattern_type = 'None'

            if pattern.startswith('xor') and pattern.endswith('split'):
                pattern_type = 'XOR Split'
            elif pattern.startswith('xor') and pattern.endswith('join'):
                pattern_type = 'XOR Join'
            elif pattern.startswith('or') and pattern.endswith('split'):
                pattern_type = 'OR Split'
            elif pattern.startswith('or') and pattern.endswith('join'):
                pattern_type = 'OR Join'
            elif pattern.startswith('parallel') and pattern.endswith('split'):
                pattern_type = 'AND Split'
            elif pattern.startswith('parallel') and pattern.endswith('join'):
                pattern_type = 'AND Join'

            if patterns[pattern_name]['isLoop'] and pattern.endswith('join'):
                pattern_type = 'Loop Join'
            elif patterns[pattern_name]['isLoop'] and pattern.endswith('split'):
                pattern_type = 'Loop Split'
            pattern_as_json = {
                'pattern_node': pattern,
                'incoming_nodes': incoming_nodes,
                'outgoing_nodes': outgoing_nodes,
                'pattern_type': pattern_type
            }
            patterns_list.append(pattern_as_json)

    for node in wf_model.get_nodes():
        if node.get_name() not in seen:
            incoming_nodes = []
            outgoing_nodes = []
            for arc in node.get_in_arcs():
                incoming_nodes.append(arc.get_source().get_name())
            for arc in node.get_out_arcs():
                outgoing_nodes.append(arc.get_target().get_name())

            pattern_as_json = {
                'pattern_node': node.get_name(),
                'incoming_nodes': incoming_nodes,
                'outgoing_nodes': outgoing_nodes,
                'pattern_type': 'Sequence'
            }
            patterns_list.append(pattern_as_json)

    return patterns_list




log = xes_import.apply('logs/running-example.xes')
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter

log_csv = pd.read_csv('test-data/OR.csv', sep=',')
log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
log_csv = log_csv.sort_values('time:timestamp')
#log = log_converter.apply(log_csv)
ptree = inductive_miner.apply_tree(log)

from pm4py.visualization.process_tree import visualizer as pt_vis_factory
wf_model = pt_converter.apply(ptree)

discover_patterns(wf_model)

make_ors(wf_model)
patterns = {}
discover_patterns(wf_model)
for pattern in patterns_to_json():
    print(pattern)

#print(recreate_sequences(get_node_by_name('xor_2_split'), set()))
# pattern_to_merge = 'parallel_1_split'
# expand_inner_nodes(patterns[pattern_to_merge])
# print(patterns[pattern_to_merge])
gviz = wf_visualizer(wf_model)
model_path = 'models/' + 'test' + '.png'
gsave.save(gviz, model_path)
# for node in wf_model.get_nodes():
# print(find_pattern(node))
