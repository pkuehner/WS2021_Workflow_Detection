import pandas as pd
import itertools

def generate_test(m, n, saveas=''):
    """This function creates a test file for a m out of n discriminator pattern and saves it as csv

                Parameters:
                m (Int): number of branches that have to be completed before activating the subsequent activity
                n (Int): max number of incoming branches
                saveas (String): prefix of saved dataname (e.g. saveas=tmp -> tmp-2-out-of-4.csv)

               """

    if (m >= n):
        print('Error: '+str(n)+' is bigger/equal than '+str(n))
        exit(0)
    start = 'A'
    end = 'C'
    inner = []
    for i in range(n):
        inner.append('B'+str(i))

    perm_inner = list(itertools.permutations(inner, m))
    # convert elements from tuple to list
    perm_inner = [list(i) for i in perm_inner]
    for case in perm_inner:
        case.append(end)
        case.insert(0,start)
        for b_inner in inner:
            if b_inner not in case:
                case.append(b_inner)
    print(perm_inner)

    # create df and save it as csv
    cases = []
    activities = []
    for caseid in range(len(perm_inner)):
        for j in range(len(perm_inner[caseid])):
            cases.append(caseid+1)
            activities.append(perm_inner[caseid][j])

    timestamps = pd.date_range(start='1/1/2018', freq='H', periods=len(cases))
    data = {'case:concept:name': cases,
            'concept:name': activities,
            'time:timestamp': timestamps
            }
    df = pd.DataFrame(data, columns=['case:concept:name', 'concept:name', 'time:timestamp'])
    df.to_csv(saveas+str(m)+'-out-of-'+str(n)+'.csv', index=False)
    return inner


test = generate_test(2,4)