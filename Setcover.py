import subprocess
from argparse import ArgumentParser

# Global variables describing the instance
NR_ELEMENTS = 0       # size of the universe
NR_SETS = 0           # number of available sets
K_VALUE = 0           # allowed size of the cover
SETS = []             # list of sets, each is a list of element indices


def load_instance(input_file_name):
    """
    Function reads the instance from the input file.

    """
    global NR_ELEMENTS, NR_SETS, K_VALUE, SETS

    with open(input_file_name, "r") as f:
        first = f.readline().split()
        while first == []:
            first = f.readline().split()
        NR_ELEMENTS = int(first[0])

        second = f.readline().split()
        while second == []:
            second = f.readline().split()
        NR_SETS = int(second[0])

        third = f.readline().split()
        while third == []:
            third = f.readline().split()
        K_VALUE = int(third[0])

        sets = []
        for line in f:
            parts = line.split()
            if not parts:
                continue
            s = int(parts[0])
            elems = [int(x) for x in parts[1:1 + s]]
            sets.append(elems)

    if len(sets) != NR_SETS:
        print("Warning: expected", NR_SETS, "sets, but read", len(sets))

    SETS = sets
    return NR_ELEMENTS, NR_SETS, K_VALUE, SETS


def at_most_k_seq(x_vars, k, start_var):
    """
    Function makes sure that we do not pick more than k sets.

    """
    n = len(x_vars)
    cnf = []
    next_var = start_var

    if k < 0:
        raise ValueError("k must be >= 0")

    if n == 0:
        return cnf, start_var - 1

    # k = 0 means all x must be false
    if k == 0:
        for x in x_vars:
            cnf.append([-x, 0])
        return cnf, start_var - 1

    # if k >= n  we can choose all sets
    if k >= n:
        return cnf, start_var - 1

    s = {}
    for i in range(1, n + 1):
        for j in range(1, k + 1):
            s[(i, j)] = next_var
            next_var += 1

    cnf.append([-x_vars[0], s[(1, 1)], 0])

    for j in range(2, k + 1):
        cnf.append([-s[(1, j)], 0])

    for i in range(2, n + 1):
        xi = x_vars[i - 1]
        cnf.append([-xi, s[(i, 1)], 0])
        cnf.append([-s[(i - 1, 1)], s[(i, 1)], 0])

        for j in range(2, k + 1):
            cnf.append([-xi, -s[(i - 1, j - 1)], s[(i, j)], 0])
            cnf.append([-s[(i - 1, j)], s[(i, j)], 0])

        cnf.append([-xi, -s[(i - 1, k)], 0])

    return cnf, next_var - 1


def encode(instance):
    """
    Function creates the CNF formula for one set cover instance.

    """
    nr_elements, nr_sets, k_val, sets_list = instance

    cnf = []

    x_vars = list(range(1, nr_sets + 1))
    nr_vars = nr_sets

    for elem in range(1, nr_elements + 1):
        clause = []
        for idx, s in enumerate(sets_list):
            if elem in s:
                clause.append(idx + 1)    
        clause.append(0)
        cnf.append(clause)

   
    aux_clauses, last_var = at_most_k_seq(x_vars, k_val, nr_vars + 1)
    cnf.extend(aux_clauses)
    nr_vars = max(nr_vars, last_var)

    return cnf, nr_vars


def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
    """
    Function prints CNF into a file in DIMACS format and calls the SAT solver.

    """
    with open(output_name, "w") as file:
        file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + "\n")
        for clause in cnf:
            file.write(" ".join(str(lit) for lit in clause) + "\n")

    return subprocess.run(
        ["./" + solver_name, "-model", "-verb=" + str(verbosity), output_name],
        stdout=subprocess.PIPE,
    )


def print_result(result):
    """
    Function reads the solver output, prints it, and if satisfiable,decodes which sets were chosen.

    """
    global NR_ELEMENTS, NR_SETS, K_VALUE, SETS

    for line in result.stdout.decode("utf-8").split("\n"):
        print(line)

    if result.returncode == 20:
        print("UNSAT: no set cover of size <=", K_VALUE, "exists for this instance.")
        return

    if result.returncode != 10:
        print("Solver returned unexpected code:", result.returncode)
        return

    model_lits = []
    for line in result.stdout.decode("utf-8").split("\n"):
        if line.startswith("v"):
            parts = line.split()
            parts = parts[1:]
            model_lits.extend(int(v) for v in parts)

    if 0 in model_lits:
        model_lits.remove(0)

    model = {}
    for lit in model_lits:
        var = abs(lit)
        model[var] = (lit > 0)

    chosen = []
    for j in range(1, NR_SETS + 1):
        if model.get(j, False):
            chosen.append(j)

    print()
    print("Chosen sets (indices):", " ".join(str(j) for j in chosen) if chosen else "(none)")

    covered = set()
    for j in chosen:
        covered.update(SETS[j - 1])

    print("Covered elements:", " ".join(str(e) for e in sorted(covered)) if covered else "(none)")

    missing = set(range(1, NR_ELEMENTS + 1)) - covered
    if missing:
        print("WARNING: some elements are not covered:", " ".join(str(e) for e in sorted(missing)))
    else:
        print("All elements are covered.")


if __name__ == "__main__":

    parser = ArgumentParser()

    parser.add_argument(
        "-i",
        "--input",
        default="input.in",
        type=str,
        help=(
            "The instance file."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default="formula.cnf",
        type=str,
        help=(
            "Output file for the DIMACS format (i.e. the CNF formula)."
        ),
    )
    parser.add_argument(
        "-s",
        "--solver",
        default="glucose-syrup",
        type=str,
        help=(
            "The SAT solver to be used."
        ),
    )
    parser.add_argument(
        "-v",
        "--verb",
        default=1,
        type=int,
        choices=range(0, 2),
        help=(
            "Verbosity of the SAT solver used."
        ),
    )
    args = parser.parse_args()

    # get the input instance
    instance = load_instance(args.input)

    # encode the problem to create CNF formula
    cnf, nr_vars = encode(instance)

    # call the SAT solver and get the result
    result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

    print_result(result)
