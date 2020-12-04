import tempfile
from graphviz import Digraph

def graphviz_visualization(wf_model):
    """
    Do GraphViz visualization of a WF Model
    Parameters
    -----------
    wf_model
        Model containing Workflow pattern
    Returns
    -----------
    viz
        Digraph object
    """
    from wf_graph import WF
    filename = tempfile.NamedTemporaryFile(suffix='.gv')
    viz = Digraph("", filename=filename.name, engine='dot', graph_attr={'bgcolor': 'transparent'})

    # represent nodes
    viz.attr('node', shape='box')

    for node in wf_model.get_nodes():
        if isinstance(node, WF.StartEvent):
            viz.node(node.get_id(), "Start", style='filled', shape='circle')
        elif isinstance(node, WF.EndEvent):
            viz.node(node.get_id(), "End", style='filled', shape='circle')
        elif isinstance(node, WF.ExclusiveGateway):
            if node.get_name().endswith('split'):
                viz.node(node.get_id(), "XOR-Split", style='filled', shape='diamond')
            else:
                viz.node(node.get_id(), "XOR-Join", style='filled', shape='diamond')
        elif isinstance(node, WF.ParallelGateway):
            if node.get_name().endswith('split'):
                viz.node(node.get_id(), "AND-Split", style='filled', shape='diamond')
            else:
                viz.node(node.get_id(), "AND-Join", style='filled', shape='diamond')
        else:
            viz.node(node.get_id(), node.get_name(), style='filled')

    for flow in wf_model.get_flows():
        viz.edge(flow.get_source().get_id(), flow.get_target().get_id(), label="")

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = "png"

    return viz