import json

from wf_graph import WF


class pattern_finder:
    def __init__(self, wf_model):
        self.wf_model = wf_model
        self.patterns = {}
        self.discover_patterns()
        self.make_ors()
        self.make_multi_merges()
        self.rediscover_patterns()
        self.check_patterns_for_discriminator()
        self.make_discr()
       # self.rediscover_patterns()
        print(self.patterns)

    def rediscover_patterns(self):
        """
        Rediscovers patterns after something has changed
        Returns
        -------
        object
        """
        multi_merges = self.get_multi_merges()
        self.patterns = {}
        self.discover_patterns()
        for pattern in self.patterns:
            pattern = self.patterns[pattern]
            if pattern['partner'] in multi_merges:
                pattern['is_multi_merge'] = True

    def create_pattern(self, name, incoming_nodes, outgoing_nodes, partner, inner_nodes, is_loop=False, is_or=False):
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
            "is_or": is_or,
            "is_multi_merge": False,
            "post_merge": None,
            "is_discriminator": False,
            "post_discriminator": None
        }
        self.patterns[name] = pattern
        return pattern

    def find_split_join_pattern(self, node, end):
        """
        Finds split_join pattern that starts at node
        Parameters
        ----------
        node : pattern start
        end : pattern end

        Returns
        -------

        """
        out_arcs = node.get_out_arcs()
        if isinstance(node, WF.ExclusiveGateway):
            if node.get_name() in self.patterns:
                return [node.get_name()]
            if node.get_name().endswith('split'):
                seen = set()
                join_node, isLoop = self.find_join_for_XOR_Split(node, node.get_name(), seen)
                inner_patterns = []
                for arc in out_arcs:
                    target = arc.get_target()
                    inner_pattern = self.find_split_join_pattern(target, join_node.get_name())
                    inner_patterns.extend(inner_pattern)
                self.create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns, isLoop)
                return [node.get_name()]

        if isinstance(node, WF.ParallelGateway):
            if node.get_name() in self.patterns:
                return [node.get_name()]
            if node.get_name().endswith('split'):
                join_node = self.find_join_for_And_Split(node, 0)
                inner_patterns = []
                for arc in out_arcs:
                    target = arc.get_target()
                    inner_pattern = self.find_split_join_pattern(target, join_node.get_name())
                    inner_patterns.extend(inner_pattern)
                self.create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns)
                return [node.get_name()]

        if isinstance(node, WF.InclusiveGateway):
            if node.get_name() in self.patterns:
                return [node.get_name()]
            if node.get_name().endswith('split'):
                join_node = self.find_join_for_Or_Split(node, 0)
                inner_patterns = []
                for arc in out_arcs:
                    target = arc.get_target()
                    inner_pattern = self.find_split_join_pattern(target, join_node.get_name())
                    inner_patterns.extend(inner_pattern)
                self.create_pattern(node.get_name(), [], [], join_node.get_name(), inner_patterns)
                return [node.get_name()]

        if node.get_name() != end:
            inner_patterns = [node.get_name()]
            for arc in out_arcs:
                target = arc.get_target()
                inner_patterns.extend(self.find_split_join_pattern(target, end))
            return inner_patterns

        return []

    def find_join_for_XOR_Split(self, node, split_name, seen):
        """
                       Finds Join for XOR Split
                       Returns join node name
                       -------
                       object
                       """
        if node in seen:
            return None, True
        out_arcs = node.get_out_arcs()
        seen.add(node)
        if isinstance(node, WF.ExclusiveGateway):
            if node.get_name().endswith('join') and split_name[:5] == node.get_name()[:5]:
                seen.remove(node)
                return node, False
        join_node = None
        isLoop = False
        if len(out_arcs) == 0:
            isLoop = True
        for arc in out_arcs:
            arc_node = arc.get_target()
            x_join, is_loop = self.find_join_for_XOR_Split(arc_node, split_name, seen)
            if is_loop:
                isLoop = True
            if x_join != None:
                join_node = x_join  # TODO: This probably is a loop
            else:
                isLoop = True
        return join_node, isLoop

    def find_join_for_And_Split(self, node, openSplits):
        """
                Finds Join for AND Split
                Returns join node name
                -------
                object
                """
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
            x_join = self.find_join_for_And_Split(arc_node, openSplits)
            return x_join
        return None

    def find_join_for_Or_Split(self, node, openSplits):
        """
        Finds Join for Or Split
        Returns join node name
        -------
        object
        """
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
            x_join = self.find_join_for_Or_Split(arc_node, openSplits)
            return x_join
        return None

    def check_patterns_for_or(self):
        """
               Checks if patterns for or and marks them
               Returns
               -------

               """
        for pattern in self.patterns:
            pattern = self.patterns[pattern]
            if pattern['name'].startswith('parallel'):
                is_or = True
                for node in pattern['inner_nodes']:
                    if node in self.patterns:
                        node = self.patterns[node]
                        targets = [arc.get_target() for arc in self.get_node_by_name(node['partner']).get_out_arcs()]
                        if not node['name'].startswith('xor') or len(node['inner_nodes']) > 1 or targets[
                            0].get_name() != pattern['partner']:
                            is_or = False
                            break
                    else:
                        is_or = False
                        break
                pattern['is_or'] = is_or

    def check_patterns_for_multi_merge(self):
        """
        Checks if patterns for multi merges and marks them
        Returns
        -------

        """
        for pattern in self.patterns:
            pattern = self.patterns[pattern]
            if pattern['name'].startswith('parallel'):
                partner_node = self.get_node_by_name(pattern['partner'])
                if not (len(partner_node.get_out_arcs()) == 1 and isinstance(
                        partner_node.get_out_arcs()[0].get_target(), WF.EndEvent)):  # Cant be Multi Merge
                    continue
                node = self.get_node_by_name(pattern['name'])
                post_merge = None
                for arc in node.get_out_arcs():
                    out_node_join = arc.get_target()
                    out_name_split = out_node_join.get_name()[:-4] + 'split'
                    if out_name_split in self.patterns and self.patterns[out_name_split]['isLoop']:
                        out_node_split = self.get_node_by_name(out_name_split)
                        if len(out_node_split.get_out_arcs()) == 2:
                            for out_arc in out_node_split.get_out_arcs():
                                if out_arc.get_target() == partner_node:
                                    if post_merge is None:
                                        post_merge = out_name_split
                                    else:
                                        continue
                if post_merge != None:
                    pattern['is_multi_merge'] = True
                    pattern['post_merge'] = post_merge

    def check_patterns_for_discriminator(self):
        """
        Checks if patterns for Discriminators and marks them
        Returns
        -------

        """
        for pattern in self.patterns:
            pattern = self.patterns[pattern]
            if pattern['name'].startswith('xor') and pattern['isLoop']:
                partner_node = self.get_node_by_name(pattern['partner'])
                node = self.get_node_by_name(pattern['name'])
                partnerGoesToEnd = False
                counter = 0
                notGoingToEnd = 0
                if len(node.get_out_arcs()) == 2:
                    for arc in node.get_out_arcs():
                        if isinstance(arc.get_target(), WF.EndEvent):
                            partnerGoesToEnd = True
                            notGoingToEnd = (counter+1)%2
                        counter = counter + 1
                notGoingToEnd = node.get_out_arcs()[notGoingToEnd].get_target()
                if partnerGoesToEnd:
                    for arc in partner_node.get_out_arcs():
                        out_node_split = arc.get_target()
                        out_name_split = out_node_split.get_name()
                        out_name_join = out_node_split.get_name()[:-5] + 'join'
                        if out_name_split in self.patterns and out_name_split.startswith('or'):
                            out_node_join = self.get_node_by_name(out_name_join)
                            if len(out_node_join.get_out_arcs()) == 1:
                                 if out_node_join.get_out_arcs()[0].get_target() == node:
                                     pattern['is_discriminator'] = True
                                     pattern['post_discriminator'] = partner_node.get_out_arcs()[0].get_target().get_name()


    def recreate_sequences(self, node, seen):
        if (node not in seen):
            sequence = self.find_split_join_pattern(node, None)

            seen.add(node)
            if sequence[-1] != 'end':
                pattern = self.patterns[sequence[-1]]
                partner = pattern['partner']
                if pattern['isLoop']:
                    print('Found Loop')
                    for node_2 in self.wf_model.get_nodes():
                        if node_2.get_name() == pattern['inner_nodes'][1]:
                            sequence.append(self.recreate_sequences(node_2, seen))
                        if node_2.get_name() == pattern['inner_nodes'][0]:
                            sequence.append(self.recreate_sequences(node_2, seen))
                else:
                    for node_2 in self.wf_model.get_nodes():
                        if node_2.get_name() == partner:
                            for target in node_2.get_out_arcs():
                                sequence.extend(self.recreate_sequences(target.get_target(), seen))
            return sequence
        return []

    def expand_inner_nodes(self, pattern):
        """
        Returns all inner nodes of a pattern (Nodes between join and split)
        Parameters
        ----------
        pattern : name of split node of pattern

        Returns
        -------

        """
        found = True
        seen = []
        nodes = []
        currentNodes = [self.get_node_by_name(pattern)]
        while found:
            found = False
            c2 = currentNodes[:]
            for node in c2:
                if node not in seen:
                    currentNodes.remove(node)
                    if node.get_name() != self.patterns[pattern]['partner']:
                        for arc in node.get_out_arcs():
                            currentNodes.append(arc.get_target())
                        seen.append(node)
                        nodes.append(node)
                        found = True
        nodes.remove(self.get_node_by_name(pattern))
        nnames = []
        for node in nodes:
            nnames.append(node.get_name())
        return nnames

    def get_node_by_name(self, name):
        """
        Returns
        -------
        Node with given name
        """
        for node in self.wf_model.get_nodes():
            if node.get_name() == name:
                return node
        return None

    def make_ors(self):
        """
        Rewires And and Xor to or in wf_model
        """
        or_count = 1
        for pattern in self.patterns:
            pattern = self.patterns[pattern]
            if pattern['is_or']:
                and_split_node = self.get_node_by_name(pattern['name'])
                and_join_node = self.get_node_by_name(pattern['partner'])
                xors = []
                for node in and_split_node.get_out_arcs():
                    node = node.get_target()
                    xors.append((node, self.get_node_by_name(self.patterns[node.get_name()]['partner'])))

                change_and_xor_to_or(self.wf_model, and_split_node, and_join_node, xors, or_count)
                or_count += 1

    def make_multi_merges(self):
        """
        Rewires the multi merges in wf_model
        """
        for pattern in self.patterns:
            pattern = self.patterns[pattern]
            if pattern['is_multi_merge']:
                and_split_node = self.get_node_by_name(pattern['name'])
                and_join_node = self.get_node_by_name(pattern['partner'])
                loop_split_node = self.get_node_by_name(pattern['post_merge'])
                loop_join_node = self.get_node_by_name(self.patterns[pattern['post_merge']]['partner'])
                change_and_to_multi_merge(self.wf_model, and_split_node, and_join_node, loop_split_node, loop_join_node)

    def make_discr(self):
        """
        Rewires the multi merges in wf_model
        """
        for pattern in self.patterns:
            counter = 1
            pattern = self.patterns[pattern]
            if pattern['is_discriminator']:
                loop_split_node = self.get_node_by_name(pattern['name'])
                loop_join_node = self.get_node_by_name(pattern['partner'])
                or_split_node = self.get_node_by_name(pattern['post_discriminator'])
                or_join_node = self.get_node_by_name(self.patterns[pattern['post_discriminator']]['partner'])
                change_loop_or_to_discriminator(self.wf_model, or_split_node, or_join_node, loop_split_node, loop_join_node, counter)
                counter += 1

    def discover_patterns(self):
        """
        Discovers patterns and finds or and multi merges
        """
        for node in self.wf_model.get_nodes():
            self.find_split_join_pattern(node, None)

        self.check_patterns_for_or()
        self.check_patterns_for_multi_merge()
        print(self.patterns)

    def merge_join(self, pattern_name):
        """
        Merges join with pattern_name as split node
        Parameters
        ----------
        pattern_name : Split node name of pattern to merge
        """
        merge_split_join(self.wf_model, self.get_node_by_name(pattern_name),
                         self.get_node_by_name(self.patterns[pattern_name]['partner']),
                         self.expand_inner_nodes(pattern_name))
        self.patterns = {}
        self.discover_patterns()

    def get_loops(self):
        """

        Returns node names of split and join xors that are indedd loops
        -------

        """
        loop_nodes = []
        for pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]
            if pattern['isLoop']:
                loop_nodes.extend([pattern_name, pattern['partner']])
        return loop_nodes

    def get_multi_merges(self):
        """
        Returns List of And Join node names, which are multi merges
        -------

        """
        multi_merges = []
        for pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]
            if pattern['is_multi_merge']:
                multi_merges.append(pattern['partner'])
        return multi_merges

    def patterns_to_json(self):
        """
        Returns JSON Representation of Patterns
        -------

        """
        patterns_list = []
        seen = set()
        for pattern_name in self.patterns:
            for pattern in [pattern_name, self.patterns[pattern_name]['partner']]:
                is_multi_merge = self.patterns[pattern_name]['is_multi_merge']
                post_merge = self.patterns[pattern_name]['post_merge']

                incoming_nodes = []
                outgoing_nodes = []
                seen.add(pattern)
                node = self.get_node_by_name(pattern)
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
                    if is_multi_merge:
                        pattern_type = 'Multi Merge'

                if self.patterns[pattern_name]['isLoop'] and pattern.endswith('join'):
                    pattern_type = 'Loop Start'
                elif self.patterns[pattern_name]['isLoop'] and pattern.endswith('split'):
                    pattern_type = 'Loop End'
                pattern_as_json = {
                    'pattern_node': pattern,
                    'incoming_nodes': incoming_nodes,
                    'outgoing_nodes': outgoing_nodes,
                    'pattern_type': pattern_type
                }
                patterns_list.append(pattern_as_json)

        for node in self.wf_model.get_nodes():
            if node.get_name() not in seen:
                incoming_nodes = []
                outgoing_nodes = []
                for arc in node.get_in_arcs():
                    if arc.get_source().get_name() not in seen:
                        incoming_nodes.append(arc.get_source().get_name())
                for arc in node.get_out_arcs():
                    if arc.get_target().get_name() not in seen:
                        outgoing_nodes.append(arc.get_target().get_name())
                if len(outgoing_nodes) > 0:
                    pattern_as_json = {
                        'pattern_node': node.get_name(),
                        'incoming_nodes': incoming_nodes,
                        'outgoing_nodes': outgoing_nodes,
                        'pattern_type': 'Sequence'
                    }
                    patterns_list.append(pattern_as_json)

        return json.dumps(patterns_list)

# log = xes_import.apply('test-data/LOOP2.csv')
import pandas as pd
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
import create_wf_model as pt_converter
from create_wf_model import change_and_xor_to_or, merge_split_join, change_and_to_multi_merge, change_loop_or_to_discriminator
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.visualization.common import save as gsave
from wf_graph import WF
from wf_pattern_visualizer import graphviz_visualization as wf_visualizer

#
log_csv = pd.read_csv('test-data/3-out-of-4.csv', sep=',')
log_csv = dataframe_utils.convert_timestamp_columns_in_df(log_csv)
log_csv = log_csv.sort_values('time:timestamp')
log = log_converter.apply(log_csv)
ptree = inductive_miner.apply_tree(log)
#
wf_model = pt_converter.apply(ptree)

p_finder = pattern_finder(wf_model)
#print(p_finder.patterns_to_json())
gviz = wf_visualizer(wf_model)
model_path = 'models/' + 'test' + '.png'
#
gsave.save(gviz, model_path)
