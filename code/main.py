
def load_dimacs(file_name):
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


def flip_assignment(partial_assignment, assignment):
    partial_assignment[assignment - 1] *= -1
    return partial_assignment

# блять
def branching_sat_solve(clause_set: list[list[int]], partial_assignment: list[int] = None, current_var=1) -> list | bool:
    if partial_assignment is None:
        num_vars = 0
        for clause in clause_set:
            if abs(max(clause, key=abs)) > num_vars:
                num_vars = abs(max(clause, key=abs))
        partial_assignment = [x + 1 for x in range(num_vars)]

    if not clause_set:
        return partial_assignment
    elif [] in clause_set:
        return False
    else:
        clause_set1 = [[val for val in clause if val != -current_var] for clause in clause_set if current_var not in clause]
        clause_set2 = [[val for val in clause if val != current_var] for clause in clause_set if -current_var not in clause]
        if branching_sat_solve(clause_set1, partial_assignment, current_var + 1):
            return partial_assignment
        elif branching_sat_solve(clause_set2, flip_assignment(partial_assignment, current_var), current_var + 1):
            partial_assignment = flip_assignment(partial_assignment, current_var)
            return flip_assignment(partial_assignment, current_var)
        else:
            return False




def unit_propagate(clause_set):
    ...


def dpll_sat_solve(clause_set, partial_assignment):
    ...


sat1 = [[1, -2, -5], [-1, 6], [-2, -3], [3, -4], [-4, 5, -6]]
sat2 = [[1], [1,-1], [-1,-2]]
unsat1 = [[1, -2], [1, 2], [-1, -2], [-1, 2]]
print(branching_sat_solve(unsat1))
