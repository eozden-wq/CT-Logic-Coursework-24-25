import time
from functools import lru_cache


def load_dimacs(file_name: str) -> list[list[int]]:
    # file_name will be of the form "problem_name.txt"
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


def simple_sat_solve(clause_set: list[list[int]]) -> list[int] | bool:
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
                    clause_result |= not (assignment[abs(var) - 1])
                else:
                    clause_result |= assignment[abs(var) - 1]

            if clause_result == 0:
                satisfied = False
                break
            else:
                continue

        if satisfied:
            for i, val in enumerate(assignment):
                if not val:
                    res.append(-1 * (i + 1))
                else:
                    res.append(i + 1)
            return res

    return False


def branching_sat_solve(clause_set: list[list[int]], partial_assignment: list[int] = None, current_var=1) -> list[int] | bool:
    if partial_assignment is None:
        partial_assignment = []

    if not clause_set:
        return partial_assignment
    elif [] in clause_set:
        return False
    else:
        if res := branching_sat_solve([[val for val in clause if val != -current_var] for clause in clause_set if current_var not in clause], partial_assignment + [current_var], current_var + 1):
            return res
        elif res := branching_sat_solve([[val for val in clause if val != current_var] for clause in clause_set if -current_var not in clause], partial_assignment + [-current_var], current_var + 1):
            return res
        else:
            return False


def get_unit_clause(clause_set: list[list[int]]) -> int | bool:
    for clause in clause_set:
        if len(clause) == 1:
            for e in clause:
                break
            return e

    return False


def unit_propagate(clause_set: list[list[int]]) -> list[list[int]]:
    while unit_clause := get_unit_clause(clause_set):
        clause_set = [[val for val in clause if val != -1 * unit_clause]
                      for clause in clause_set if unit_clause not in clause]

    return clause_set


def unit_propagate_dpll(clause_set: list[list[int]], partial_assignment: list[int]) -> list[list[int]]:
    while unit_clause := get_unit_clause(clause_set):
        clause_set = frozenset(frozenset(val for val in clause if val != -1 * unit_clause)
                               for clause in clause_set if unit_clause not in clause)
        partial_assignment += [unit_clause]

    return clause_set, partial_assignment

# Dynamic Largest Individual Sum - I'm not quite sure why, but this decision heuristic seems to work pretty well. Went from 25ms to 10ms for 8queens


def choose_var(clause_set: list[list[int]]) -> int:
    literals = {}
    for clause in clause_set:
        for var in clause:
            if abs(var) not in literals:
                literals[abs(var)] = 1
            else:
                literals[abs(var)] += 1

    return max(literals, key=literals.get)


memo = {}


def dpll_sat_solve(clause_set, partial_assignment: list[int] = None) -> list[int] | bool:
    if partial_assignment is None or partial_assignment == []:
        clause_set = frozenset(frozenset(clause) for clause in clause_set)
        partial_assignment = []

    clause_set, partial_assignment = unit_propagate_dpll(
        clause_set, partial_assignment)

    if clause_set in memo:
        return memo[clause_set]

    if not clause_set:
        return partial_assignment
    elif any(not clause for clause in clause_set):
        memo[clause_set] = False
        return False
    else:
        # Clever little heuristic to get the next variable to branch on
        # current_var = clause_set[0][0]
        current_var = choose_var(clause_set)
        # I love the walrus operator
        if res := dpll_sat_solve(frozenset(frozenset(val for val in clause if val != -current_var) for clause in clause_set if current_var not in clause), partial_assignment + [current_var]):
            memo[clause_set] = True
            return res
        elif res := dpll_sat_solve(frozenset(frozenset(val for val in clause if val != current_var) for clause in clause_set if -current_var not in clause), partial_assignment + [-current_var]):
            memo[clause_set] = True
            return res
        else:
            memo[clause_set] = False
            return False


def clause_satisfied(clause, assignment):
    assignment_set = set(assignment)
    return any(literal in assignment_set for literal in clause)


def clause_set_satisfied(clause_set, assignment):
    return all(clause_satisfied(clause, assignment) for clause in clause_set)


def test():
    print("Testing load_dimacs")
    try:
        dimacs = load_dimacs("tests/sat.txt")
        assert dimacs == [[1], [1, -1], [-1, -2]]
        print("Test passed")
    except:
        print("Failed to correctly load DIMACS file")

    print("Testing simple_sat_solve")
    try:
        sat1 = [[1], [1, -1], [-1, -2]]
        check = simple_sat_solve(sat1)
        assert check == [1, -2] or check == [-2, 1]
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
        sat1 = [[1], [1, -1], [-1, -2]]
        check = branching_sat_solve(sat1, [])
        assert check == [1, -2] or check == [-2, 1]
        print("Test (SAT) passed")
    except:
        print("branching_sat_solve did not work correctly a sat instance")

    try:
        unsat1 = [[1, -2], [-1, 2], [-1, -2], [1, 2]]
        check = branching_sat_solve(unsat1, [])
        assert (not check)
        print("Test (UNSAT) passed")
    except:
        print("branching_sat_solve did not work correctly an unsat instance")

    print("Testing unit_propagate")
    try:
        clause_set = [[1], [-1, 2]]
        check = unit_propagate(clause_set)
        assert check == []
        print("Test passed")
    except:
        print("unit_propagate did not work correctly")

    print("Testing DPLL")  # Note, this requires load_dimacs to work correctly
    problem_names = ["tests/sat.txt", "tests/unsat.txt"]
    for problem in problem_names:
        try:
            clause_set = load_dimacs(problem)
            check = dpll_sat_solve(clause_set, [])
            if problem == problem_names[1]:
                assert (not check)
                print("Test (UNSAT) passed")
            else:
                assert check == [1, -2] or check == [-2, 1]
                print("Test (SAT) passed")
        except:
            print("Failed problem " + str(problem))
    print("Finished tests")


if __name__ == "__main__":
    test()
