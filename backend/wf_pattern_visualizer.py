import tempfile

from graphviz import Digraph


def graphviz_visualization(wf_model, pattern_to_merge=[], loop_nodes=[], multi_merges=[], pattern_to_color={}):
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
        node_color = None
        if node.get_name() in pattern_to_color:
            node_color = pattern_to_color[node.get_name()]
        if isinstance(node, WF.StartEvent):
            viz.node(node.get_id(), "Start", style='filled', shape='circle', fillcolor='green')
        elif isinstance(node, WF.EndEvent):
            viz.node(node.get_id(), "End", style='filled', shape='circle', fillcolor='orange')
        elif isinstance(node, WF.ExclusiveGateway):
            if node.get_name().endswith('split'):
                name = 'XOR-Split \n'+node.get_name()
                if node.get_name() in loop_nodes:
                    name = 'LOOP-End \n'+node.get_name()
                viz.node(node.get_id(), name, style='filled', shape='diamond', color=node_color)
            else:
                name = 'XOR-Join \n'+node.get_name()
                if node.get_name() in loop_nodes:
                    name = 'LOOP-Start \n'+node.get_name()
                viz.node(node.get_id(), name, style='filled', shape='diamond', color=node_color)
        elif isinstance(node, WF.ParallelGateway):
            if node.get_name().endswith('split'):
                viz.node(node.get_id(), "AND-Split \n"+node.get_name(), style='filled', shape='diamond', color=node_color)
            else:
                name = "AND-Join \n"+node.get_name()
                if node.get_name() in multi_merges:
                    name = 'Multi-Merge \n'+node.get_name()
                viz.node(node.get_id(), name, style='filled', shape='diamond', color=node_color)
        elif isinstance(node, WF.InclusiveGateway):
            if node.get_name().endswith('split'):
                viz.node(node.get_id(), "OR-Split \n"+node.get_name(), style='filled', shape='diamond', color=node_color)
            else:
                viz.node(node.get_id(), "OR-Join \n"+node.get_name(), style='filled', shape='diamond', color=node_color)
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
