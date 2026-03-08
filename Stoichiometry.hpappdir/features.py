"""Feature extraction for reaction type classification.

Extracts a fixed-length numeric feature vector from a parsed chemical
equation.  Works on both standard Python (for training) and HP Prime
MicroPython (for inference).

The feature vector is designed so that a small neural network can learn
to distinguish the 7 reaction categories:
  0=Combustion  1=Synthesis  2=Double Replacement
  3=Single Replacement  4=Neutralization  5=Redox  6=Decomposition
"""

# Halogens and common polyatomic-ion element sets
_HALOGENS = {'F', 'Cl', 'Br', 'I'}
_ALKALI = {'Li', 'Na', 'K', 'Rb', 'Cs', 'Fr'}
_ALKALINE = {'Be', 'Mg', 'Ca', 'Sr', 'Ba', 'Ra'}
_METALS = (_ALKALI | _ALKALINE |
           {'Al', 'Fe', 'Cu', 'Zn', 'Ag', 'Au', 'Pt', 'Pb', 'Sn',
            'Ni', 'Co', 'Mn', 'Cr', 'Ti', 'V', 'W', 'Mo', 'Hg',
            'Cd', 'Sc', 'Y', 'Zr', 'Nb', 'Ru', 'Rh', 'Pd', 'In',
            'Sb', 'Te', 'La', 'Ce', 'Ga', 'Ge', 'Bi', 'Ta', 'Hf',
            'Re', 'Os', 'Ir', 'Tl'})

# Category index mapping (must match training labels)
CATEGORIES = [
    'Combustion', 'Synthesis', 'Double Replacement',
    'Single Replacement', 'Neutralization', 'Redox',
    'Decomposition',
]
N_CLASSES = len(CATEGORIES)

# Feature vector length
N_FEATURES = 18


def _is_free_element(edict):
    """True if a compound is a single free element (e.g. Fe, O2, Cl2)."""
    return len(edict) == 1


def _has_element(terms, sym):
    """Check if any term on a side contains element sym."""
    for _, edict in terms:
        if sym in edict:
            return True
    return False


def _count_elements_side(terms):
    """Set of all elements on one side."""
    elems = set()
    for _, edict in terms:
        for el in edict:
            elems.add(el)
    return elems


def _has_hydroxide(terms):
    """Check if any term contains O and H (proxy for OH group)."""
    for _, edict in terms:
        if 'O' in edict and 'H' in edict:
            oc = edict.get('O', 0)
            hc = edict.get('H', 0)
            if hc >= 1 and oc >= 1:
                return True
    return False


def _has_acid(terms):
    """Check if any term starts with H and has non-metal anion."""
    for formula_str, edict in terms:
        if 'H' not in edict:
            continue
        # Acids typically: H + non-metal/polyatomic (Cl, SO4, NO3, PO4...)
        non_h = set(edict.keys()) - {'H'}
        if non_h and not non_h.issubset(_METALS):
            # Has H + some non-metal elements → could be acid
            if edict['H'] >= 1:
                return True
    return False


def _count_metals(terms):
    """Count distinct metal elements on a side."""
    metals = set()
    for _, edict in terms:
        for el in edict:
            if el in _METALS:
                metals.add(el)
    return len(metals)


def _count_free_elements(terms):
    """Count number of single-element species (e.g. Fe, O2, Cl2)."""
    count = 0
    for _, edict in terms:
        if _is_free_element(edict):
            count += 1
    return count


def _has_water_product(rhs):
    """Check if H2O appears as product."""
    for formula_str, edict in rhs:
        if edict == {'H': 2, 'O': 1}:
            return True
    return False


def _has_co2_product(rhs):
    """Check if CO2 appears as product."""
    for formula_str, edict in rhs:
        if edict == {'C': 1, 'O': 2}:
            return True
    return False


def _has_o2_reactant(lhs):
    """Check if O2 appears as reactant."""
    for formula_str, edict in lhs:
        if edict == {'O': 2}:
            return True
    return False


def _max_elements_in_compound(terms):
    """Max number of distinct elements in any single compound on a side."""
    mx = 0
    for _, edict in terms:
        if len(edict) > mx:
            mx = len(edict)
    return mx


def extract(lhs, rhs):
    """Extract feature vector from parsed equation sides.

    lhs, rhs: lists of (formula_string, element_dict) tuples
              as returned by parser.parse_equation().

    Returns list of floats of length N_FEATURES.
    """
    n_reactants = len(lhs)
    n_products = len(rhs)

    has_o2 = 1.0 if _has_o2_reactant(lhs) else 0.0
    has_h2o = 1.0 if _has_water_product(rhs) else 0.0
    has_co2 = 1.0 if _has_co2_product(rhs) else 0.0

    lhs_elems = _count_elements_side(lhs)
    rhs_elems = _count_elements_side(rhs)
    n_unique_elements = len(lhs_elems | rhs_elems)

    lhs_metals = _count_metals(lhs)
    rhs_metals = _count_metals(rhs)

    lhs_free = _count_free_elements(lhs)
    rhs_free = _count_free_elements(rhs)

    has_acid_lhs = 1.0 if _has_acid(lhs) else 0.0
    has_acid_rhs = 1.0 if _has_acid(rhs) else 0.0
    has_oh_lhs = 1.0 if _has_hydroxide(lhs) else 0.0
    has_oh_rhs = 1.0 if _has_hydroxide(rhs) else 0.0

    lhs_max_el = _max_elements_in_compound(lhs)
    rhs_max_el = _max_elements_in_compound(rhs)

    has_halogen_lhs = 1.0 if any(
        el in _HALOGENS for el in lhs_elems) else 0.0
    has_halogen_rhs = 1.0 if any(
        el in _HALOGENS for el in rhs_elems) else 0.0

    # Ratio features (avoid division by zero)
    prod_react_ratio = float(n_products) / max(n_reactants, 1)

    return [
        float(n_reactants),       # 0
        float(n_products),        # 1
        prod_react_ratio,         # 2
        has_o2,                   # 3
        has_h2o,                  # 4
        has_co2,                  # 5
        float(n_unique_elements), # 6
        float(lhs_metals),        # 7
        float(rhs_metals),        # 8
        float(lhs_free),          # 9
        float(rhs_free),          # 10
        has_acid_lhs,             # 11
        has_acid_rhs,             # 12
        has_oh_lhs,               # 13
        has_oh_rhs,               # 14
        float(lhs_max_el),        # 15
        float(rhs_max_el),        # 16
        has_halogen_lhs,          # 17
    ]
