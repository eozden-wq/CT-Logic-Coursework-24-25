import time


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


memo = set()


def branching_sat_solve(clause_set: list[list[int]], partial_assignment: list[int] = None, current_var=1) -> list | bool:
    if partial_assignment is None:
        partial_assignment = []

    if ''.join(map(str, partial_assignment)) in memo:
        return False

    if not clause_set:
        return partial_assignment
    elif [] in clause_set:
        memo.add(''.join(map(str, partial_assignment)))
        return False
    else:
        if res := branching_sat_solve([[val for val in clause if val != -current_var] for clause in clause_set if current_var not in clause], partial_assignment + [current_var], current_var + 1):
            return res
        elif res := branching_sat_solve([[val for val in clause if val != current_var] for clause in clause_set if -current_var not in clause], partial_assignment + [-current_var], current_var + 1):
            return res
        else:
            memo.add(''.join(map(str, partial_assignment)))
            return False


def get_unit_clause(clause_set: list[list[int]]) -> int | bool:
    for clause in clause_set:
        if len(clause) == 1:
            return clause[0]

    return False


def unit_propagate(clause_set: list[list[int]]) -> list[list[int]]:
    while unit_clause := get_unit_clause(clause_set):
        clause_set = [[val for val in clause if val != -1 * unit_clause]
                      for clause in clause_set if unit_clause not in clause]

    return clause_set


def dpll_sat_solve(clause_set, partial_assignment=None, current_var=1):
    if partial_assignment is None:
        partial_assignment = []

    clause_set = unit_propagate(clause_set)
    if not clause_set:
        return partial_assignment
    elif [] in clause_set:
        return False
    else:
        # I love the walrus operator
        if res := dpll_sat_solve([[val for val in clause if val != -current_var] for clause in clause_set if current_var not in clause], partial_assignment + [current_var], current_var + 1):
            return res
        elif res := dpll_sat_solve([[val for val in clause if val != current_var] for clause in clause_set if -current_var not in clause], partial_assignment + [-current_var], current_var + 1):
            return res
        else:
            return False


def clause_satisfied(clause, assignment):
    assignment_set = set(assignment)
    return any(literal in assignment_set for literal in clause)


def clause_set_satisfied(clause_set, assignment):
    return all(clause_satisfied(clause, assignment) for clause in clause_set)


if __name__ == "__main__":
    clause_set = load_dimacs(input("Name of the DIMACS file: "))
    s = time.time()
    assignment = dpll_sat_solve(clause_set)
    e = time.time()
    print(e-s)
    print(assignment)
    if assignment:
        print(clause_set_satisfied(clause_set, assignment))
