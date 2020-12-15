import tempfile

from graphviz import Digraph


def graphviz_visualization(wf_model, pattern_to_merge=[], loop_nodes=[]):
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
    viz.graph_attr['rankdir'] = 'LR'
    # inner_nodes = pattern_to_merge['inner_nodes']
    # split_name = pattern_to_merge['name']
    # join_name = pattern_to_merge['partner']
    # represent nodes
    viz.attr('node', shape='box')
    for node in wf_model.get_nodes():
        # if node.get_name() not in inner_nodes:
        if isinstance(node, WF.StartEvent):
            viz.node(node.get_id(), "Start", style='filled', shape='circle', fillcolor='green')
        elif isinstance(node, WF.EndEvent):
            viz.node(node.get_id(), "End", style='filled', shape='circle', fillcolor='orange')
        elif isinstance(node, WF.ExclusiveGateway):
            if node.get_name().endswith('split'):
                name = 'OR-Split'
                if node.get_name() in loop_nodes:
                    name = 'LOOP-End'
                viz.node(node.get_id(), name, style='filled', shape='diamond')
            else:
                name = 'OR-Join'
                if node.get_name() in loop_nodes:
                    name = 'LOOP-Start'
                viz.node(node.get_id(), name, style='filled', shape='diamond')
        elif isinstance(node, WF.ParallelGateway):
            if node.get_name().endswith('split'):
                viz.node(node.get_id(), "AND-Split", style='filled', shape='diamond')
            else:
                viz.node(node.get_id(), "AND-Join", style='filled', shape='diamond')
        elif isinstance(node, WF.InclusiveGateway):
            if node.get_name().endswith('split'):
                viz.node(node.get_id(), "OR-Split", style='filled', shape='diamond')
            else:
                viz.node(node.get_id(), "OR-Join", style='filled', shape='diamond')
        else:
            viz.node(node.get_id(), node.get_name(), style='filled')

    for flow in wf_model.get_flows():
        viz.edge(flow.get_source().get_id(), flow.get_target().get_id(), label="")
    # for node in wf_model.get_nodes():
    #     for node_2 in wf_model.get_nodes():
    #         if node.get_name() == split_name and node_2.get_name() == join_name:
    #             viz.edge(node.get_id(), node_2.get_id(), label="")

    viz.attr(overlap='false')
    viz.attr(fontsize='11')

    viz.format = "png"

    return viz
