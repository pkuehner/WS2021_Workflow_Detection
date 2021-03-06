import uuid

import networkx as nx

DEFAULT_PROCESS = str(uuid.uuid4())


class WF(object):
    class WFNode(object):
        def __init__(self, name="", in_arcs=None, out_arcs=None):
            self.__id = str(uuid.uuid4())
            self.__name = name
            self.__in_arcs = list() if in_arcs is None else in_arcs
            self.__out_arcs = list() if out_arcs is None else out_arcs
            self.__process = DEFAULT_PROCESS

        def get_id(self):
            return "id" + self.__id

        def get_name(self):
            return self.__name

        def get_in_arcs(self):
            return self.__in_arcs

        def get_out_arcs(self):
            return self.__out_arcs

        def add_in_arc(self, in_arc):
            if in_arc not in self.__in_arcs:
                self.__in_arcs.append(in_arc)

        def add_out_arc(self, out_arc):
            if out_arc not in self.__out_arcs:
                self.__out_arcs.append(out_arc)

        def remove_in_arc(self, in_arc):
            self.__in_arcs.remove(in_arc)

        def remove_out_arc(self, out_arc):
            self.__out_arcs.remove(out_arc)

        def get_process(self):
            return self.__process

        def set_process(self, process):
            self.__process = process

        def __repr__(self):
            return str(self.__id + "@" + self.__name)

        def __str__(self):
            return self.__repr__()

    class StartEvent(WFNode):
        def __init__(self, isInterrupting=False, name="", parallelMultiple=False, in_arcs=None, out_arcs=None):
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)
            self.__isInterrupting = isInterrupting
            self.__parallelMultiple = parallelMultiple

        def get_isInterrupting(self):
            return self.__isInterrupting

        def get_parallelMultiple(self):
            return self.__parallelMultiple

    class EndEvent(WFNode):
        def __init__(self, name="", in_arcs=None, out_arcs=None):
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)

    class OtherEvent(WFNode):
        def __init__(self, name="", type="", in_arcs=None, out_arcs=None):
            self.type = type
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)

    class Task(WFNode):
        def __init__(self, name="", type="task", in_arcs=None, out_arcs=None):
            self.type = type
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)

    class ParallelGateway(WFNode):
        def __init__(self, name="", gatewayDirection="Unspecified", in_arcs=None, out_arcs=None):
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)
            self.__gatewayDirection = gatewayDirection

    class ExclusiveGateway(WFNode):
        def __init__(self, name="", gatewayDirection="Unspecified", in_arcs=None, out_arcs=None):
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)
            self.__gatewayDirection = gatewayDirection

    class InclusiveGateway(WFNode):
        def __init__(self, name="", gatewayDirection="Unspecified", in_arcs=None, out_arcs=None):
            WF.WFNode.__init__(self, name, in_arcs, out_arcs)
            self.__gatewayDirection = gatewayDirection

    class Flow(object):
        def __init__(self, source, target, name=""):
            self.__id = uuid.uuid4()
            self.__name = name
            self.__source = source
            source.add_out_arc(self)
            self.__target = target
            target.add_in_arc(self)
            self.__process = DEFAULT_PROCESS

        def get_id(self):
            return self.__id

        def get_name(self):
            return self.__name

        def get_source(self):
            return self.__source

        def get_target(self):
            return self.__target

        def get_process(self):
            return self.__process

        def set_process(self, process):
            self.__process = process

        def __repr__(self):
            u_id = str(self.__source.get_id()) + "@" + str(self.__source.get_name())
            v_id = str(self.__target.get_id()) + "@" + str(self.__target.get_name())
            return u_id + " -> " + v_id

        def __str__(self):
            return self.__repr__()

    def __init__(self, name="", nodes=None, flows=None):
        self.__id = uuid.uuid4()
        self.__name = name
        self.__graph = nx.DiGraph()
        self.__nodes = set() if nodes is None else nodes
        self.__flows = set() if flows is None else flows

        if nodes is not None:
            for node in nodes:
                self.__graph.add_node(node)
        if flows is not None:
            for flow in flows:
                self.__graph.add_edge(flow.get_source(), flow.get_target())

    def get_nodes(self):
        return self.__nodes

    def get_flows(self):
        return self.__flows

    def get_graph(self):
        return self.__graph

    def get_name(self):
        return self.__name

    def add_node(self, node):
        self.__nodes.add(node)
        self.__graph.add_node(node)

    def remove_node(self, node):
        if node in self.__nodes:
            self.__nodes.remove(node)
            self.__graph.remove_node(node)

    def remove_flow(self, flow):
        source = flow.get_source()
        target = flow.get_target()
        if source in self.__nodes:
            source.remove_out_arc(flow)
        if target in self.__nodes:
            target.remove_in_arc(flow)
        self.__flows.remove(flow)

    def add_flow(self, flow):
        if type(flow) != WF.Flow:
            raise Exception()
        source = flow.get_source()
        target = flow.get_target()
        if source not in self.__nodes:
            self.add_node(source)
        if target not in self.__nodes:
            self.add_node(target)
        self.__flows.add(flow)
        self.__graph.add_edge(source, target)
        source.add_out_arc(flow)
        target.add_in_arc(flow)
