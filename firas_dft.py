from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.filtering.log.attributes import attributes_filter

import importer

class DependencyFrequencyTable:
    """A simple example class"""
    def __init__(self, event_log):
        self.event_log = event_log
        self.traces = {}
        self.dfg = dfg_discovery.apply(event_log)
        self.dft = {}
        self.frequencies = {}
        self.indirect_frequencies = {}  # first value counts the frequency and second the steps between a and b
        self.strength = {}
        self.concs = {}
        self.get_traces()
        self.find_frequencies()
        self.find_indirect_frequencies()
        self.find_strength()
        #self.find_standard_sdt()
        #self.find_and_mark_concurrents()
        #self.build_final_sdt()


    def find_frequencies(self):
        self.frequencies = attributes_filter.get_attribute_values(self.event_log, "concept:name")

    # calc a -> b
    def find_strength(self):
        for event_a in self.frequencies:
            for event_b in self.frequencies:
                #if self.indirect_frequencies[event_a, event_b][0] > 0:
                str_counter = 0
                # incerase with delta = 0.8
                for i in self.indirect_frequencies[event_a, event_b][1]:
                    str_counter += 0.8 ** i
                # decrease with delta = 0.8
                for j in self.indirect_frequencies[event_b, event_a][1]:
                    str_counter -= 0.8 ** j
                self.strength[event_a, event_b] = str_counter / self.frequencies[event_a]

    # find a >>> b and b <<< a.  a < b can be found in dfg variable. #b in frequencies variable
    def find_indirect_frequencies(self):
        for event_a in self.frequencies:
            for event_b in self.frequencies:
                df_counter = 0
                steps=[]
                for trace in self.traces:
                    if event_a in self.traces[trace] and event_b in self.traces[trace] and self.traces[trace].index(event_a) < self.traces[trace].index(event_b):
                        df_counter = df_counter + 1
                        steps.append(self.traces[trace].index(event_b) - self.traces[trace].index(event_a) - 1)
                self.indirect_frequencies[(event_a, event_b)] = [df_counter, steps]

    def get_traces(self):
        # iterate over all traces and get sequential activities per trace
        for i in range(len(self.event_log)):
            tmp = []
            for j in range(len(self.event_log[i])):
                tmp.append(self.event_log[i][j]['concept:name'])
            self.traces[i] = tmp

    # not used
    def find_and_mark_concurrents(self):
        for event_a in self.frequencies:
            self.concs[event_a] = self.find_concurrent_activities(event_a)
            for event_b in self.concs[event_a]:
                if event_b != event_a:
                    self.sdt[event_a][event_b] = -1
                    self.sdt[event_b][event_a] = -1

    # not used
    def find_concurrent_activities(self, act_a):
        conc = [act_a]
        for event_b in self.frequencies:
            if act_a != event_b:
                if self.sdt[event_b][act_a] != 0 and self.sdt[act_a][event_b] != 0:
                    conc.append(event_b)

        return conc

    # works
    def check_mutual_exclusion(self):
        pws = powerset(list(self.frequencies.keys()))
        for event_a in self.frequencies:
            freq = self.frequencies[event_a]
            for set in pws:
                if event_a in set:
                    continue
                works = True
                if len(set) > 1:
                    dfg_sum = 0
                    strength_sum = 0
                    for event in set:
                        if self.dfg[(event_a, event)] != 0:
                            # dfg_sum += dfg[(event_a, event)]
                            dfg_sum += self.frequencies[event]
                            strength_sum += self.strength[event_a, event]
                        else:
                            works = False
                            break
                    if not works:
                        continue
                    if dfg_sum == freq and strength_sum == 1: # how about P(i,j) = 0 for all i,j from set
                        print("Found Mut Excl")
                        print(set)
                        print(event_a)

    # works not
    def check_mutual_exclusion_join(self):
        pws = powerset(list(self.frequencies.keys()))
        for event_a in self.frequencies:
            freq = self.frequencies[event_a]
            for set in pws:
                if event_a in set:
                    continue
                works = True
                if len(set) > 1:
                    dfg_sum = 0
                    strength_sum = 0
                    for event in set:
                        if self.dfg[(event, event_a)] != 0:
                            # dfg_sum += dfg[(event, event_a)]
                            dfg_sum += self.frequencies[event]
                            strength_sum += self.strength[event, event_a]
                        else:
                            works = False
                            break
                    if not works:
                        continue
                    if dfg_sum == freq and strength_sum == 1:
                        print("Found Mut Excl Join")
                        print(set)
                        print(event_a)

    # works
    def check_sequence(self):
        for event_a in self.frequencies:
            for event_b in self.frequencies:
                if event_b != event_a and self.strength[event_a, event_b] == 1 and self.frequencies[event_a] == self.frequencies[event_b]:
                    print('Found sequence:')
                    print(event_a + ' --> ' + event_b)


#Creates powerset without y
def powerset(s):
    x = len(s)
    powerset = list()
    for i in range(1 << x):
        powerset.append([s[j] for j in range(x) if (i & (1 << j))])
    return powerset




eventLog = importer.import_csv(r"C:\Users\Firas\Process Discovery Using Python\XOR.csv")
table = DependencyFrequencyTable(eventLog)
table.check_mutual_exclusion()
table.check_sequence()
