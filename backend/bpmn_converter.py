from pm4py.objects.bpmn.bpmn_graph import BPMN

from wf_graph import WF


def convert_wf_to_bpmn(wf_model):
    bpmn = BPMN()
    for node in wf_model.get_nodes():
        if isinstance(node, WF.StartEvent):
            converted_node = BPMN.StartEvent(name=node.get_name(), isInterrupting=True)
            bpmn.add_node(converted_node)
        elif isinstance(node, WF.EndEvent):
            converted_node = BPMN.EndEvent(name=node.get_name())
            bpmn.add_node(converted_node)
        elif isinstance(node, WF.ExclusiveGateway):
            converted_node = BPMN.ExclusiveGateway(name=node.get_name())
            bpmn.add_node(converted_node)
        elif isinstance(node, WF.ParallelGateway):
            converted_node = BPMN.ParallelGateway(name=node.get_name())
            bpmn.add_node(converted_node)
        elif isinstance(node, WF.InclusiveGateway):
            converted_node = BPMN.InclusiveGateway(name=node.get_name())
            bpmn.add_node(converted_node)
        else:
            converted_node = BPMN.Task(name=node.get_name())
            bpmn.add_node(converted_node)

    for flow in wf_model.get_flows():
        source_node = None
        target_node = None
        source_node_name = flow.get_source().get_name()
        target_node_name = flow.get_target().get_name()
        for bpmn_node in bpmn.get_nodes():
            if bpmn_node.get_name() == source_node_name:
                source_node = bpmn_node
            if bpmn_node.get_name() == target_node_name:
                target_node = bpmn_node
        bpmn.add_flow(BPMN.Flow(source_node, target_node))

    return bpmn
