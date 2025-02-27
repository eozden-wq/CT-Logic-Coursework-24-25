
def load_dimacs(file_name):
    #file_name will be of the form "problem_name.txt"
    clause_set = []
    with open(file_name, 'r') as dimacs_file:
        raw_clause_set = [line.split() for line in dimacs_file]
        raw_clause_set.pop(0)
        for clause in raw_clause_set:
            if clause[-1] == '0':
                clause.pop()
            else:
                raise Exception("Invalid DIMACS format")
            clause_set.append(list(map(int, clause)))
        
    return clause_set


def simple_sat_solve(clause_set):
    num_vars = 0
    for clause in clause_set:
        max_num_in_clause = abs(max(clause, key=abs))
        if max_num_in_clause > num_vars:
            num_vars = max_num_in_clause
    
    res = []
    for i in range(2**num_vars):
        assignment = list(map(int, format(i, f'0{num_vars}b')))
        satisfied = True
        for clause in clause_set:
            clause_result = 0
            # compute disjunction of literals in given clause
            for var in clause:
                if var < 0:
                    clause_result |= not(assignment[abs(var) - 1]) 
                else:
                    clause_result |= assignment[abs(var) - 1]
            
            if clause_result == 0:
                satisfied = False
                break
            else:
                continue
        
        if satisfied:
            for i,val in enumerate(assignment):
                if not val:
                    res.append(-1 * (i + 1))
                else:
                    res.append(i + 1)
            return res

    return False

def branching_sat_solve(clause_set,partial_assignment):
    ...


def unit_propagate(clause_set):
    ...


def dpll_sat_solve(clause_set,partial_assignment):
    ...



def test():
    print("Testing load_dimacs")
    try:
        dimacs = load_dimacs("tests/sat.txt")
        assert dimacs == [[1],[1,-1],[-1,-2]]
        print("Test passed")
    except:
        print("Failed to correctly load DIMACS file")

    print("Testing simple_sat_solve")
    try:
        sat1 = [[1],[1,-1],[-1,-2]]
        check = simple_sat_solve(sat1)
        assert check == [1,-2] or check == [-2,1]
        print("Test (SAT) passed")
    except:
        print("simple_sat_solve did not work correctly a sat instance")

    try:
        unsat1 = [[1, -2], [-1, 2], [-1, -2], [1, 2]]
        check = simple_sat_solve(unsat1)
        assert (not check)
        print("Test (UNSAT) passed")
    except:
        print("simple_sat_solve did not work correctly an unsat instance")

    print("Testing branching_sat_solve")
    try:
        sat1 = [[1],[1,-1],[-1,-2]]
        check = branching_sat_solve(sat1,[])
        assert check == [1,-2] or check == [-2,1]
        print("Test (SAT) passed")
    except:
        print("branching_sat_solve did not work correctly a sat instance")

    try:
        unsat1 = [[1, -2], [-1, 2], [-1, -2], [1, 2]]
        check = branching_sat_solve(unsat1,[])
        assert (not check)
        print("Test (UNSAT) passed")
    except:
        print("branching_sat_solve did not work correctly an unsat instance")


    print("Testing unit_propagate")
    try:
        clause_set = [[1],[-1,2]]
        check = unit_propagate(clause_set)
        assert check == []
        print("Test passed")
    except:
        print("unit_propagate did not work correctly")


    print("Testing DPLL") #Note, this requires load_dimacs to work correctly
    problem_names = ["sat.txt","unsat.txt"]
    for problem in problem_names:
        try:
            clause_set = load_dimacs(problem)
            check = dpll_sat_solve(clause_set,[])
            if problem == problem_names[1]:
                assert (not check)
                print("Test (UNSAT) passed")
            else:
                assert check == [1,-2] or check == [-2,1]
                print("Test (SAT) passed")
        except:
            print("Failed problem " + str(problem))
    print("Finished tests")

test()