import copy
from pm4py.objects.process_tree.pt_operator import Operator


class Counts(object):
    """
    Shared variables among executions
    """

    def __init__(self):
        """
        Constructor
        """
        self.num_xor_gateways = 0
        self.num_para_gateways = 0
        self.num_tau_trans = 0
        self.tau_trans = []

    def inc_xor_gateways(self):
        """
        Increase the number of xor gateways (split + join)
        """
        self.num_xor_gateways += 1

    def inc_tau_trans(self):
        """
        Increase the number of tau transitions
        """
        self.num_tau_trans += 1

    def inc_para_gateways(self):
        """
        Increase the number of xor gateways (split + join)
        """
        self.num_para_gateways += 1

    def append_tau(self, tau_id):
        self.tau_trans.append(tau_id)


def add_task(wf, counts, label):
    """
    Create a task with the specified label in the wf
    """
    from wf_graph import WF
    task = WF.Task(name=label)
    wf.add_node(task)
    return wf, task, counts


def add_tau_task(wf, counts):
    """
    Create a dummy task in the wf
    """
    from wf_graph import WF
    counts.inc_tau_trans()
    tau_name = "tau_" + str(counts.num_tau_trans)
    tau_task = WF.Task(name=tau_name)
    wf.add_node(tau_task)
    counts.append_tau(tau_task)
    return wf, tau_task, counts


def add_xor_gateway(wf, counts):
    from wf_graph import WF
    counts.inc_xor_gateways()
    split_name = "xor_" + str(counts.num_xor_gateways) + "_split"
    join_name = "xor_" + str(counts.num_xor_gateways) + "_join"

    split = WF.ExclusiveGateway(name=split_name)
    join = WF.ExclusiveGateway(name=join_name)
    wf.add_node(split)
    wf.add_node(join)

    return wf, split, join, counts


def add_parallel_gateway(wf, counts):
    from wf_graph import WF
    counts.inc_para_gateways()
    split_name = "parallel_" + str(counts.num_para_gateways) + "_split"
    join_name = "parallel_" + str(counts.num_para_gateways) + "_join"

    split = WF.ParallelGateway(name=split_name)
    join = WF.ParallelGateway(name=join_name)
    wf.add_node(split)
    wf.add_node(join)
    return wf, split, join, counts

def change_and_xor_to_or(wf, and_split, and_join, xors):
    from wf_graph import WF
    split_name = "Or_split"
    join_name = "Or_join"

    flows_in = []
    flows_out = []
    flows_to_remove = []
    for flow in wf.get_flows():
        if flow.get_target() == and_split:
            flows_in.append(flow.get_source())
            flows_to_remove.append(flow)
        elif flow.get_source() == and_join:
            flows_out.append(flow.get_target())
            flows_to_remove.append(flow)
        elif flow.get_source() == and_split:
            flows_to_remove.append(flow)
        elif flow.get_target() == and_join:
            flows_to_remove.append(flow)

    xor_out = []
    xor_in = []
    for (xor_split, xor_join) in xors:
        for flow in wf.get_flows():
            if flow.get_source() == xor_split:
                if flow.get_target() != xor_join:
                    xor_out.append(flow.get_target())
                flows_to_remove.append(flow)
            elif flow.get_target() == xor_join:
                if flow.get_source() != xor_split:
                    xor_in.append(flow.get_source())
                flows_to_remove.append(flow)


    for flow in flows_to_remove:
        wf.remove_flow(flow)
    for (xor_split, xor_join) in xors:
        wf.remove_node(xor_join)
        wf.remove_node(xor_split)
    wf.remove_node(and_split)
    wf.remove_node(and_join)

    split = WF.InclusiveGateway(name=split_name)
    join = WF.InclusiveGateway(name=join_name)
    wf.add_node(split)
    wf.add_node(join)

    for nodes in flows_in:
        wf.add_flow(WF.Flow(nodes, split))

    for nodes in flows_out:
        wf.add_flow(WF.Flow(join, nodes))

    for nodes in xor_in:
        wf.add_flow(WF.Flow(nodes, join))

    for nodes in xor_out:
        wf.add_flow(WF.Flow(split, nodes))

    return wf


def recursively_add_tree(parent_tree, tree, wf, initial_event, final_event, counts, rec_depth):
    from wf_graph import WF
    tree_childs = [child for child in tree.children]
    initial_connector = None
    final_connector = None

    if tree.operator is None:
        trans = tree
        if trans.label is None:
            wf, task, counts = add_tau_task(wf, counts)
            wf.add_flow(WF.Flow(initial_event, task))
            wf.add_flow(WF.Flow(task, final_event))
            initial_connector = task
            final_connector = task
        else:
            wf, task, counts = add_task(wf, counts, trans.label)
            wf.add_flow(WF.Flow(initial_event, task))
            wf.add_flow(WF.Flow(task, final_event))
            initial_connector = task
            final_connector = task

    elif tree.operator == Operator.XOR:
        wf, split_gateway, join_gateway, counts = add_xor_gateway(wf, counts)
        for subtree in tree_childs:
            wf, counts, x, y = recursively_add_tree(tree, subtree, wf, split_gateway, join_gateway, counts, rec_depth + 1)
        wf.add_flow(WF.Flow(initial_event, split_gateway))
        wf.add_flow(WF.Flow(join_gateway, final_event))
        initial_connector = split_gateway
        final_connector = join_gateway

    elif tree.operator == Operator.PARALLEL:
        wf, split_gateway, join_gateway, counts = add_parallel_gateway(wf, counts)
        for subtree in tree_childs:
            wf, counts, x, y = recursively_add_tree(tree, subtree, wf, split_gateway, join_gateway, counts, rec_depth + 1)
        wf.add_flow(WF.Flow(initial_event, split_gateway))
        wf.add_flow(WF.Flow(join_gateway, final_event))
        initial_connector = split_gateway
        final_connector = join_gateway

    elif tree.operator == Operator.SEQUENCE:
        initial_intermediate_task = initial_event
        wf, final_intermediate_task, counts = add_tau_task(wf, counts)
        for i in range(len(tree_childs)):
            wf, counts, initial_connect, final_connect = recursively_add_tree(tree, tree_childs[i], wf, initial_intermediate_task, final_intermediate_task, counts, rec_depth + 1)
            initial_intermediate_task = final_connect
            if i == 0:
                initial_connector = initial_connect
            if i == len(tree_childs) - 2:
                final_intermediate_task = final_event
            else:
                wf, final_intermediate_task, counts = add_tau_task(wf, counts)
            final_connector = final_connect

    elif tree.operator == Operator.LOOP:
        if len(tree_childs) != 2:
            raise Exception("Loop doesn't have 2 childs")
        else:
            do = tree_childs[0]
            redo = tree_childs[1]
            wf, split, join, counts = add_xor_gateway(wf, counts)
            wf, counts, i, y = recursively_add_tree(tree, do, wf, join, split, counts, rec_depth + 1)
            wf, counts, x, y = recursively_add_tree(tree, redo, wf, split, join, counts, rec_depth + 1)
            wf.add_flow(WF.Flow(initial_event, join))
            wf.add_flow(WF.Flow(split, final_event))
            initial_connector = join
            final_connector = split

    return wf, counts, initial_connector, final_connector


def delete_tau_transitions(wf, counts):
    from wf_graph import WF
    for tau_tran in counts.tau_trans:
        in_arcs = tau_tran.get_in_arcs()
        out_arcs = tau_tran.get_out_arcs()
        if len(in_arcs) > 1 or len(out_arcs) > 1:
            raise Exception("Tau transition has more than one incoming or outgoing edge!")
        if in_arcs and out_arcs:
            out_flow = out_arcs[0]
            in_flow = in_arcs[0]
            source = in_flow.get_source()
            target = out_flow.get_target()
            wf.remove_flow(out_flow)
            wf.remove_flow(in_flow)
            wf.add_flow(WF.Flow(source, target))
        else:
            for in_flow in copy.copy(in_arcs):
                wf.remove_flow(in_flow)
            for out_flow in copy.copy(out_arcs):
                wf.remove_flow(out_flow)
        wf.remove_node(tau_tran)

    return wf


def apply(tree, parameters=None):
    """
    Converts the process tree into a WF Pattern models
    Parameters
    --------------
    tree
        Process tree
    parameters
        Parameters of the algorithm
    Returns
    --------------
    wf
        WF Pattern graph
    """
    from wf_graph import WF
    counts = Counts()
    wf = WF()
    start_event = WF.StartEvent(name="start", isInterrupting=True)
    end_event = WF.EndEvent(name="end")
    wf.add_node(start_event)
    wf.add_node(end_event)
    wf, counts, _, _ = recursively_add_tree(tree, tree, wf, start_event, end_event, counts, 0)
    wf = delete_tau_transitions(wf, counts)

    return wf
