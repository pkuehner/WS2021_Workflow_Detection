import tempfile

from graphviz import Digraph


def graphviz_visualization(bpmn):
    """
    Do GraphViz visualization for a BPMN
    Parameters
    -----------
    bpmn
        BPMN Model
    Returns
    -----------
    viz
        Digraph object
    """
    from pm4py.objects.bpmn.bpmn_graph import BPMN
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot', graph_attr={'bgcolor': 'transparent'})
    # represent nodes
    viz.attr('node', shape='box')
    for node in bpmn.get_nodes():
        if isinstance(node, BPMN.StartEvent):
            viz.node(node.get_id(), "Start", style='filled', shape='circle')
        elif isinstance(node, BPMN.EndEvent):
            viz.node(node.get_id(), "End", style='filled', shape='circle')
        elif isinstance(node, BPMN.ExclusiveGateway):
            viz.node(node.get_id(), label=u'\u00d7', style='filled', shape='diamond')
        elif isinstance(node, BPMN.ParallelGateway):
            viz.node(node.get_id(), label=u'\u002b', style='filled', shape='diamond')
        else:
            viz.node(node.get_id(), node.get_name(), style='filled')

    for flow in bpmn.get_flows():
        viz.edge(flow.get_source().get_id(), flow.get_target().get_id(), label="")

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = "png"

    return viz
