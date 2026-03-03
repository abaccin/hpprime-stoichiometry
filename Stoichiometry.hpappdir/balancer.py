"""Chemical equation balancer for HP Prime MicroPython.

Uses matrix nullspace approach with the built-in `linalg` module.
No numpy/sympy — pure HP Prime compatible.

Algorithm:
1. Parse equation into element-by-compound matrix.
2. Find nullspace (solution that satisfies Ax = 0).
3. Scale to smallest positive integers via GCD.
"""

from parser import parse_equation


def _gcd(a, b):
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return a


def _lcm(a, b):
    """Least common multiple."""
    return a * b // _gcd(a, b)


def _gcd_list(lst):
    """GCD of a list of integers."""
    result = lst[0]
    for i in range(1, len(lst)):
        result = _gcd(result, lst[i])
    return result


def _build_matrix(lhs, rhs):
    """Build the element-by-compound matrix from parsed equation sides.

    Each compound gets a column. LHS columns are positive, RHS negative.
    Each element gets a row.

    Returns (matrix as list-of-lists, element_list, n_compounds).
    """
    # Collect all unique elements
    all_elements = []
    seen = set()
    for _, edict in lhs + rhs:
        for el in edict:
            if el not in seen:
                all_elements.append(el)
                seen.add(el)

    n_elements = len(all_elements)
    n_compounds = len(lhs) + len(rhs)

    # Build matrix: rows = elements, cols = compounds
    # LHS positive, RHS negative
    matrix = []
    for el in all_elements:
        row = []
        for _, edict in lhs:
            row.append(edict.get(el, 0))
        for _, edict in rhs:
            row.append(-edict.get(el, 0))
        matrix.append(row)

    return matrix, all_elements, n_compounds


def _rref(matrix, nrows, ncols):
    """Row-reduce to echelon form (in-place) using fractions as (num, den) pairs.

    Works with integer arithmetic to avoid floating point issues.
    Returns the matrix converted to fractions.
    """
    # Convert to fractions: each entry becomes [numerator, denominator]
    fmat = []
    for r in range(nrows):
        frow = []
        for c in range(ncols):
            frow.append([matrix[r][c], 1])
        fmat.append(frow)

    pivot_row = 0
    pivot_cols = []

    for col in range(ncols):
        # Find pivot in this column
        found = -1
        for r in range(pivot_row, nrows):
            if fmat[r][col][0] != 0:
                found = r
                break
        if found < 0:
            continue

        # Swap rows
        if found != pivot_row:
            fmat[pivot_row], fmat[found] = fmat[found], fmat[pivot_row]

        pivot_cols.append(col)

        # Scale pivot row so pivot = 1
        pn, pd = fmat[pivot_row][col]
        for c2 in range(ncols):
            # entry / pivot = (en*pd) / (ed*pn)
            en, ed = fmat[pivot_row][c2]
            fmat[pivot_row][c2] = [en * pd, ed * pn]

        # Simplify pivot row
        for c2 in range(ncols):
            n, d = fmat[pivot_row][c2]
            if n == 0:
                fmat[pivot_row][c2] = [0, 1]
            else:
                g = _gcd(abs(n), abs(d))
                if d < 0:
                    n, d = -n, -d
                fmat[pivot_row][c2] = [n // g, d // g]

        # Eliminate other rows
        for r in range(nrows):
            if r == pivot_row:
                continue
            fn, fd = fmat[r][col]
            if fn == 0:
                continue
            # Subtract (fn/fd) * pivot_row from row r
            for c2 in range(ncols):
                pn2, pd2 = fmat[pivot_row][c2]
                en, ed = fmat[r][c2]
                # new = en/ed - (fn/fd)*(pn2/pd2)
                # = (en*ed2 - fn*pn2*ed/(fd*pd2)) ... simpler:
                # = (en * fd * pd2 - fn * pn2 * ed) / (ed * fd * pd2)
                nn = en * fd * pd2 - fn * pn2 * ed
                nd = ed * fd * pd2
                if nn == 0:
                    fmat[r][c2] = [0, 1]
                else:
                    g = _gcd(abs(nn), abs(nd))
                    if nd < 0:
                        nn, nd = -nn, -nd
                    fmat[r][c2] = [nn // g, nd // g]

        pivot_row += 1

    return fmat, pivot_cols


def _find_nullspace_vector(matrix, nrows, ncols):
    """Find a single nullspace vector of the matrix.

    Returns list of integer coefficients, or None if no solution.
    Uses RREF then back-substitution with the free variable set to LCM
    of denominators to get integer results.
    """
    fmat, pivot_cols = _rref(matrix, nrows, ncols)

    # Free variables = columns not in pivot_cols
    free_cols = []
    for c in range(ncols):
        if c not in pivot_cols:
            free_cols.append(c)

    if not free_cols:
        return None  # Only trivial solution

    # Set the first free variable to 1, others to 0
    # Then solve for pivot variables
    free_col = free_cols[0]

    # For each pivot row, the solution for pivot var =
    #   -sum(fmat[row][free_col] * free_val) for each free variable
    # With only one free variable set to 1:
    #   pivot_var = -fmat[row][free_col]

    solution = [0] * ncols
    solution[free_col] = [1, 1]  # fraction

    for i in range(len(pivot_cols)):
        pc = pivot_cols[i]
        n, d = fmat[i][free_col]
        # pivot_var = -n/d
        if n == 0:
            solution[pc] = [0, 1]
        else:
            solution[pc] = [-n, d]

    # Find LCM of all denominators to scale to integers
    denoms = []
    for s in solution:
        if isinstance(s, list):
            denoms.append(abs(s[1]))
        else:
            denoms.append(1)

    scale = 1
    for d in denoms:
        scale = _lcm(scale, d)

    # Convert to integers
    int_solution = []
    for s in solution:
        if isinstance(s, list):
            val = s[0] * (scale // s[1])
        else:
            val = s * scale
        int_solution.append(val)

    # Ensure all positive (flip sign if needed)
    if any(v < 0 for v in int_solution):
        # Check if flipping all signs makes them positive
        flipped = [-v for v in int_solution]
        if all(v >= 0 for v in flipped):
            int_solution = flipped
        else:
            # Mixed signs — try to make majority positive
            neg_count = sum(1 for v in int_solution if v < 0)
            if neg_count > len(int_solution) // 2:
                int_solution = [-v for v in int_solution]

    # Make all non-negative
    int_solution = [abs(v) for v in int_solution]

    # Reduce by GCD
    nonzero = [v for v in int_solution if v > 0]
    if nonzero:
        g = _gcd_list(nonzero)
        int_solution = [v // g for v in int_solution]

    return int_solution


def balance(equation_str):
    """Balance a chemical equation.

    Args:
        equation_str: e.g. 'Fe + O2 -> Fe2O3'

    Returns:
        dict with keys:
            'lhs': list of (coefficient, formula_str, element_dict)
            'rhs': list of (coefficient, formula_str, element_dict)
            'balanced_str': human-readable balanced equation
            'elements': list of element symbols involved

    Raises ValueError if equation can't be parsed or balanced.
    """
    lhs, rhs = parse_equation(equation_str)
    matrix, elements, n_compounds = _build_matrix(lhs, rhs)
    nrows = len(elements)
    ncols = n_compounds

    coeffs = _find_nullspace_vector(matrix, nrows, ncols)

    if coeffs is None or any(c == 0 for c in coeffs):
        raise ValueError('Cannot balance this equation')

    # Split coefficients into LHS and RHS
    n_lhs = len(lhs)
    lhs_result = []
    for i, (formula, edict) in enumerate(lhs):
        lhs_result.append((coeffs[i], formula, edict))

    rhs_result = []
    for i, (formula, edict) in enumerate(rhs):
        rhs_result.append((coeffs[n_lhs + i], formula, edict))

    # Build readable string
    def side_str(terms):
        parts = []
        for coeff, formula, _ in terms:
            if coeff == 1:
                parts.append(formula)
            else:
                parts.append(str(coeff) + formula)
        return ' + '.join(parts)

    balanced = side_str(lhs_result) + ' -> ' + side_str(rhs_result)

    return {
        'lhs': lhs_result,
        'rhs': rhs_result,
        'balanced_str': balanced,
        'elements': elements,
    }


def verify_balance(result):
    """Verify that a balance result is correct.

    Returns (is_balanced, element_counts_lhs, element_counts_rhs).
    """
    lhs_counts = {}
    for coeff, _, edict in result['lhs']:
        for el, cnt in edict.items():
            lhs_counts[el] = lhs_counts.get(el, 0) + coeff * cnt

    rhs_counts = {}
    for coeff, _, edict in result['rhs']:
        for el, cnt in edict.items():
            rhs_counts[el] = rhs_counts.get(el, 0) + coeff * cnt

    is_balanced = lhs_counts == rhs_counts
    return is_balanced, lhs_counts, rhs_counts
