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


def create_pattern(name, incoming_nodes, outgoing_nodes, partner, inner_nodes):
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

    return {
            "name": name,
            "incoming_nodes": incoming_nodes,
            "outgoing_nodes": outgoing_nodes,
            "partner": partner,
            "inner_nodes": inner_nodes
        }

def find_patterns(wf_model):
    for node in wf_model.get_nodes():
        if isinstance(node, WF.ExclusiveGateway):
            if node.get_name().endswith('split'):
                print(find_join_for_XOR_Split(node, 0))


def find_pattern(node):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.ExclusiveGateway):
        if node.get_name().endswith('split'):
            join_node = find_join_for_XOR_Split(node, 0)
            inner_patterns = []
            for arc in out_arcs:
                target = out_arcs.get_target()
                inner_pattern = find_pattern(target)
                inner_patterns.append(inner_pattern)
            create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns)




def find_join_for_XOR_Split(node, openSplits):
    out_arcs = node.get_out_arcs()
    if isinstance(node, WF.ExclusiveGateway):
        if node.get_name().endswith('split'):
            openSplits += 1
        else:
            openSplits -= 1
        if openSplits == 0:
            return [node]
    inner_nodes = []
    for arc in out_arcs:
        arc_node = arc.get_target()
        nodes = find_join_for_XOR_Split(arc_node, openSplits)
        nodes.insert(0, node)
        if len(out_arcs) > 1:
            inner_nodes.append(nodes)
        else: inner_nodes.extend(nodes)
    return inner_nodes




import tempfile
from graphviz import Digraph

def ptree_to_plist(parent_tree, tree):
    from wf_graph import WF
    tree_childs = [child for child in tree.children]
    initial_connector = None
    final_connector = None

    if tree.operator is None:
        trans = tree
        if trans.label is None:
            return ['Silent Activity']
        else:
            return [trans.label]

    elif tree.operator == Operator.XOR or tree.operator == Operator.PARALLEL or tree.operator == Operator.SEQUENCE or tree.operator == Operator.LOOP:
        inner_patterns = []
        for subtree in tree_childs:
            inner_patterns.append(ptree_to_List(tree, subtree))
        return create_pattern(tree.operator, inner_patterns)

    return None








log = xes_import.apply('logs/running-example.xes')
ptree = inductive_miner.apply_tree(log)
print(ptree_to_List(ptree, ptree))




