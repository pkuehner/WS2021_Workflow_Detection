import pm4py

def validate_multi_merge_in_trace(log, incoming, outgoing):
    """
        Checks if multi-merge pattern is a multi-merge in log
        Returns
        -------

    """
    # criterium 1 : occurency of outgoing has to be equal the sum of incoming in each trace ignoring xor
    # criterium 2: no outgoing activity can occure before all incoming
    sol = True
    variants = pm4py.statistics.traces.log.case_statistics.get_variant_statistics(log)
    for trace in variants:
        # print(trace['variant'])
        trace = trace['variant'].split(',')
        merged = incoming + outgoing
        check = all(item in trace for item in merged)
        a_in_index = []
        a_out_index = []
        if check:
            sum_incoming = 0
            for a_in in incoming:
                sum_incoming += trace.count(a_in)
                a_in_index.append(trace.index(a_in))
            for a_out in outgoing:
                a_out_index.append(trace.index(a_out))
                if trace.count(a_out) != sum_incoming:  # criterium 1
                    sol = False
                    break
            if min(a_out_index) < min(a_in_index):  # criterium 2
                sol = False
                break

    return sol

def get_m_in_discriminator(log, incoming, outgoing, xor=False):
    """
            Finds the m of a potential m-out-of-n discriminator
            ----------
            log : the log containing the discriminator
            incoming : incoming activities into the discriminator
            outgoing : outgoing activities from the discriminator
            xor      : in case of outgoing contains a xor set True

            Returns
            -------
    """
    sol = []
    variants = pm4py.statistics.traces.log.case_statistics.get_variant_statistics(log)
    for trace in variants:
        #print(trace['variant'])
        trace = trace['variant'].split(',')
        if xor:
            # only check for one element
            outgoing = outgoing[0]
        merged = incoming + outgoing
        check = all(item in trace for item in merged)
        if check:
            counter = 0
            for a_in in incoming:
                if all(trace.index(a_in) < trace.index(a_out) for a_out in outgoing):
                    counter +=1
            sol.append(counter)
    if len(set(sol)) == 1:
        return sol[0]
    else:
        return 'F'