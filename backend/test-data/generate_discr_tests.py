import itertools

import pandas as pd


def generate_test(m, n, saveas=''):
    """This function creates a test file for a m out of n discriminator pattern and saves it as csv

                Parameters:
                m (Int): number of branches that have to be completed before activating the subsequent activity
                n (Int): max number of incoming branches
                saveas (String): prefix of saved dataname (e.g. saveas=tmp -> tmp-2-out-of-4.csv)

               """

    if (m >= n):
        print('Error: ' + str(n) + ' is bigger/equal than ' + str(n))
        exit(0)
    start = 'A'
    end = 'C'
    inner = []
    for i in range(n):
        inner.append('B' + str(i))

    perm_inner = list(itertools.permutations(inner, m))

    # convert elements from tuple to list
    perm_inner = [list(i) for i in perm_inner]

    sol = []
    for case in perm_inner:
        case.append(end)
        case.insert(0, start)
        not_in_perm = get_not_in(inner, case)
        # append activities which are not in the main part in any order
        for j in not_in_perm:
            sol.append(case + j)

    merged_perm = perm_inner

    print(sol)

    # create df and save it as csv
    cases = []
    activities = []
    for caseid in range(len(sol)):
        for j in range(len(sol[caseid])):
            cases.append(caseid + 1)
            activities.append(sol[caseid][j])

    timestamps = pd.date_range(start='1/1/2018', freq='H', periods=len(cases))
    data = {'case:concept:name': cases,
            'concept:name': activities,
            'time:timestamp': timestamps
            }
    df = pd.DataFrame(data, columns=['case:concept:name', 'concept:name', 'time:timestamp'])
    df.to_csv(saveas + str(m) + '-out-of-' + str(n) + '.csv', index=False)
    return sol


def get_not_in(inner, case):
    res = []
    for b_inner in inner:
        # append activities which are not in the main part in any order
        if b_inner not in case:
            res.append(b_inner)
    perm_res = list(itertools.permutations(res))
    perm_res = [list(i) for i in perm_res]
    return perm_res


test = generate_test(2, 4)
