import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery



class StandardDependencyTable:
    """A simple example class"""
    def __init__(self, event_log):
        self.event_log = event_log
        self.dfg = dfg_discovery.apply(event_log)
        self.sdt = {}
        self.frequencies = {}
        self.concs = {}
        self.find_frequencies()
        self.find_standard_sdt()
        self.find_and_mark_concurrents()
        self.build_final_sdt()


    def find_frequencies(self):
        for trace in self.event_log:
            for event in trace:
                event_name = event['concept:name']
                if event_name not in self.frequencies:
                    self.frequencies[event_name] = 0
                self.frequencies[event_name] += 1

    def find_standard_sdt(self):
        for event_a in self.frequencies:
            for event_b in self.frequencies:
                df_counter = self.dfg[(event_a, event_b)]
                if event_b not in self.sdt:
                    self.sdt[event_b] = {}
                self.sdt[event_b][event_a] = df_counter / self.frequencies[event_a]

    def find_and_mark_concurrents(self):
        for event_a in self.frequencies:
            self.concs[event_a] = self.find_concurrent_activities(event_a)
            for event_b in self.concs[event_a]:
                if event_b != event_a:
                    self.sdt[event_a][event_b] = -1
                    self.sdt[event_b][event_a] = -1

    def find_concurrent_activities(self, act_a):
        conc = [act_a]
        for event_b in self.frequencies:
            if act_a != event_b:
                if self.sdt[event_b][act_a] != 0 and self.sdt[act_a][event_b] != 0:
                    conc.append(event_b)

        return conc

    def build_final_sdt(self):
        for event_a in self.frequencies:
            for event_c in self.concs[event_a]:
                df_counter = 0
                for event_b in self.frequencies:
                    df_2 = self.dfg[(event_a, event_b)]
                    if df_2 > 0 and event_b not in self.concs[event_a]:
                        df_counter += self.dfg[(event_c, event_b)]
                for event_b in self.frequencies:
                    if df_counter != 0:
                        self.sdt[event_b][event_c] = self.dfg[(event_c, event_b)] / df_counter

    def print_std(self):
        for line in self.sdt:
            print(line)
            print(self.sdt[line])

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
                    sdt_sum = 0
                    for event in set:
                        if self.dfg[(event_a, event)] != 0:
                            # dfg_sum += dfg[(event_a, event)]
                            dfg_sum += self.frequencies[event]
                            sdt_sum += self.sdt[event][event_a]
                        else:
                            works = False
                            break
                    if not works:
                        continue
                    if dfg_sum == freq and sdt_sum == 1:
                        print("Found Mut Excl")
                        print(set)
                        print(event_a)

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
                    sdt_sum = 0
                    for event in set:
                        if self.dfg[(event, event_a)] != 0:
                            # dfg_sum += dfg[(event, event_a)]
                            dfg_sum += self.frequencies[event]
                            sdt_sum += self.sdt[event_a][event]
                        else:
                            works = False
                            break
                    if not works:
                        continue
                    if dfg_sum == freq and sdt_sum == 1:
                        print("Found Mut Excl Join")
                        print(set)
                        print(event_a)

    def check_sequence(self):
        for event_a in self.frequencies:
            for event_b in self.frequencies:
                if event_b != event_a and self.sdt[event_b][event_a] == 1 and self.frequencies[event_a] == self.dfg[
                    (event_a, event_b)]:
                    print(event_a + ' --> ' + event_b)


#Creates powerset without y
def powerset(s):
    x = len(s)
    powerset = list()
    for i in range(1 << x):
        powerset.append([s[j] for j in range(x) if (i & (1 << j))])
    return powerset

eventLog = pm4py.read_xes("/home/pascal/Downloads/running-example.xes")
table = StandardDependencyTable(eventLog)
table.print_std()
table.check_mutual_exclusion()
table.check_sequence()
table.check_mutual_exclusion_join()




