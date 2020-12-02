import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery

event_log = pm4py.read_xes("/home/pascal/Downloads/running-example.xes")
dfg = dfg_discovery.apply(event_log)
sdt = {}
frequencies = {}

# Find frequencies of each one
for trace in event_log:
    for event in trace:
        event_name = event['concept:name']
        if event_name not in frequencies:
            frequencies[event_name] = 0
        frequencies[event_name] += 1

# Build standard sdt
for event_a in frequencies:
    for event_b in frequencies:
        df_counter = dfg[(event_a, event_b)]
        if event_b not in sdt:
            sdt[event_b] = {}
        sdt[event_b][event_a] = df_counter / frequencies[event_a]

#print(sdt)


def find_concurrent_activities(sdt, act_a):
    conc = [act_a]
    for event_b in frequencies:
        if act_a != event_b:
            if sdt[event_b][act_a] != 0 and sdt[act_a][event_b] != 0:
                conc.append(event_b)

    return conc

#Creates powerset without y
def powerset(s):
    x = len(s)
    powerset = list()
    for i in range(1 << x):
        powerset.append([s[j] for j in range(x) if (i & (1 << j))])
    return powerset


def check_mutual_exclusion(sdt, dfg):
    pws = powerset(list(frequencies.keys()))
    for event_a in frequencies:
        freq = frequencies[event_a]
        for set in pws:
            if event_a in set:
                continue
            works = True
            if len(set) > 1:
                dfg_sum = 0
                sdt_sum = 0
                for event in set:
                    if dfg[(event_a, event)] != 0:
                        #dfg_sum += dfg[(event_a, event)]
                        dfg_sum += frequencies[event]
                        sdt_sum += sdt[event][event_a]
                    else:
                        works = False
                        break
                if not works:
                    continue
                if dfg_sum == freq and sdt_sum == 1:
                    print("Found Mut Excl")
                    print(set)
                    print(event_a)

def check_mutual_exclusion_join(sdt, dfg):
    pws = powerset(list(frequencies.keys()))
    for event_a in frequencies:
        freq = frequencies[event_a]
        for set in pws:
            if event_a in set:
                continue
            works = True
            if len(set) > 1:
                dfg_sum = 0
                sdt_sum = 0
                for event in set:
                    if dfg[(event, event_a)] != 0:
                        #dfg_sum += dfg[(event, event_a)]
                        dfg_sum += frequencies[event]
                        sdt_sum += sdt[event_a][event]
                    else:
                        works = False
                        break
                if not works:
                    continue
                if dfg_sum == freq and sdt_sum == 1:
                    print("Found Mut Excl Join")
                    print(set)
                    print(event_a)


def check_sequence(sdt, dfg):
    for event_a in frequencies:
        for event_b in frequencies:
            if event_b != event_a and sdt[event_b][event_a] == 1 and frequencies[event_a] == dfg[(event_a, event_b)]:
                print(event_a + ' --> ' + event_b)


concs = {}
for event_a in frequencies:
    concs[event_a] = find_concurrent_activities(sdt, event_a)
    for event_b in concs[event_a]:
        if event_b != event_a:
            sdt[event_a][event_b] = -1
            sdt[event_b][event_a] = -1

for event_a in frequencies:
    for event_c in concs[event_a]:
        df_counter = dfg[(event_a, event_b)]
        if df_counter > 0 and event_b not in concs[event_a]:
            df_counter = 0
            for event_b in frequencies:
                df_counter += dfg[(event_c, event_b)]
        for event_b in frequencies:
            if df_counter != 0:
                sdt[event_b][event_c] = dfg[(event_c, event_b)] / df_counter

for line in sdt:
    print(line)
    print(sdt[line])
print(dfg)

check_sequence(sdt, dfg)
check_mutual_exclusion(sdt, dfg)
check_mutual_exclusion_join(sdt, dfg)

from pm4py.objects.conversion.dfg import converter as dfg_mining

net, im, fm = dfg_mining.apply(dfg)
pm4py.view_petri_net(net, im, fm)
