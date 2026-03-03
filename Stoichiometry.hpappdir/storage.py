"""Equation storage for Stoichiometry HP Prime app.

Persists a list of user equations to a simple text file.
One equation per line. Format: [*] [alias | ] equation[\ttimestamp]
Starred equations prefixed with '*'. Alias separated by '|'.
Timestamp separated by tab character.
Supports add, edit, delete, star/unstar, alias, timestamps.
"""

_FILENAME = '.equations'

# Default starter equations: (alias, equation)
_DEFAULTS = [
    ('Rust', 'Fe + O2 = Fe2O3'),
    ('Combustion CH4', 'CH4 + O2 = CO2 + H2O'),
    ('', 'Al + HCl = AlCl3 + H2'),
    ('', 'Na + H2O = NaOH + H2'),
    ('Neutralization', 'Ca(OH)2 + H3PO4 = Ca3(PO4)2 + H2O'),
    ('Haber process', 'N2 + H2 = NH3'),
    ('', 'KMnO4 + HCl = KCl + MnCl2 + H2O + Cl2'),
    ('Combustion C2H6', 'C2H6 + O2 = CO2 + H2O'),
    ('Iron reduction', 'Fe2O3 + CO = Fe + CO2'),
    ('Decomposition', 'H2O2 = H2O + O2'),
    ('', 'Zn + HCl = ZnCl2 + H2'),
    ('Combustion C3H8', 'C3H8 + O2 = CO2 + H2O'),
    ('Precipitation', 'AgNO3 + NaCl = AgCl + NaNO3'),
    ('', 'Mg + O2 = MgO'),
    ('Calcium oxide', 'CaCO3 = CaO + CO2'),
    ('Acid-base', 'NaOH + H2SO4 = Na2SO4 + H2O'),
    ('', 'Cu + AgNO3 = Cu(NO3)2 + Ag'),
    ('Glucose combustion', 'C6H12O6 + O2 = CO2 + H2O'),
    ('', 'P + O2 = P2O5'),
    ('', 'BaCl2 + Na2SO4 = BaSO4 + NaCl'),
    ('', 'Fe + CuSO4 = FeSO4 + Cu'),
    ('', 'KClO3 = KCl + O2'),
    ('Thermite', 'Al + Fe2O3 = Al2O3 + Fe'),
    ('Ethanol combustion', 'C2H5OH + O2 = CO2 + H2O'),
    ('Catalytic oxidation', 'NH3 + O2 = NO + H2O'),
    ('', 'Pb(NO3)2 + KI = PbI2 + KNO3'),
    ('Complex redox', 'K2Cr2O7 + FeSO4 + H2SO4 = K2SO4 + Cr2(SO4)3 + Fe2(SO4)3 + H2O'),
    ('Photosynthesis', 'CO2 + H2O = C6H12O6 + O2'),
    ('Copper sulfate', 'Cu + H2SO4 = CuSO4 + SO2 + H2O'),
]


def _parse_line(line):
    """Parse a line into (starred, equation, alias, timestamp) tuple."""
    line = line.strip()
    starred = False
    ts = ''
    # Extract timestamp (after tab)
    if '\t' in line:
        parts = line.split('\t', 1)
        line = parts[0].strip()
        ts = parts[1].strip()
    if line.startswith('*'):
        starred = True
        line = line[1:].strip()
    # Check for alias (pipe separator)
    if '|' in line:
        parts = line.split('|', 1)
        alias = parts[0].strip()
        eq = parts[1].strip()
        return (starred, eq, alias, ts)
    return (starred, line, '', ts)


def _format_line(starred, equation, alias='', ts=''):
    """Format an entry for storage."""
    parts = []
    if starred:
        parts.append('*')
    if alias:
        parts.append(alias + ' | ' + equation)
    else:
        parts.append(equation)
    line = ' '.join(parts) if starred else parts[0]
    if ts:
        line += '\t' + ts
    return line


def load():
    """Load equations from file.

    Returns list of (starred, equation, alias) tuples.
    Creates default list on first run.
    """
    try:
        with open(_FILENAME, 'r') as f:
            lines = f.read().strip().split('\n')
            result = []
            for l in lines:
                l = l.strip()
                if l:
                    result.append(_parse_line(l))
            return result
    except:
        # First run — save defaults
        defaults = [(False, eq, al, '') for al, eq in _DEFAULTS]
        save(defaults)
        return list(defaults)


def save(equations):
    """Save equation list. equations = list of (starred, eq, alias, ts) tuples."""
    try:
        with open(_FILENAME, 'w') as f:
            for entry in equations:
                starred = entry[0]
                eq = entry[1]
                alias = entry[2] if len(entry) > 2 else ''
                ts = entry[3] if len(entry) > 3 else ''
                f.write(_format_line(starred, eq, alias, ts) + '\n')
    except:
        pass


def add(equation, alias='', ts=''):
    """Add equation to list (unstarred). Returns updated list."""
    eqs = load()
    eq = equation.strip()
    # Check if already exists (ignore star status)
    for entry in eqs:
        if entry[1] == eq:
            return eqs
    if eq:
        eqs.insert(0, (False, eq, alias.strip(), ts))
        save(eqs)
    return eqs


def delete(index):
    """Delete equation at index. Returns updated list."""
    eqs = load()
    if 0 <= index < len(eqs):
        eqs.pop(index)
        save(eqs)
    return eqs


def update(index, new_equation, new_alias=None, ts=''):
    """Update equation at index (keep star status). Returns updated list."""
    eqs = load()
    if 0 <= index < len(eqs):
        starred = eqs[index][0]
        alias = eqs[index][2] if len(eqs[index]) > 2 else ''
        if new_alias is not None:
            alias = new_alias.strip()
        eqs[index] = (starred, new_equation.strip(), alias, ts)
        save(eqs)
    return eqs


def toggle_star(index, ts=''):
    """Toggle star on equation at index. Returns updated list."""
    eqs = load()
    if 0 <= index < len(eqs):
        starred = eqs[index][0]
        eq = eqs[index][1]
        alias = eqs[index][2] if len(eqs[index]) > 2 else ''
        eqs[index] = (not starred, eq, alias, ts)
        save(eqs)
    return eqs


def get_equation(index):
    """Get just the equation string at index."""
    eqs = load()
    if 0 <= index < len(eqs):
        return eqs[index][1]
    return ''


def get_alias(index):
    """Get the alias at index."""
    eqs = load()
    if 0 <= index < len(eqs) and len(eqs[index]) > 2:
        return eqs[index][2]
    return ''


def set_alias(index, alias, ts=''):
    """Set alias on equation at index. Returns updated list."""
    eqs = load()
    if 0 <= index < len(eqs):
        starred = eqs[index][0]
        eq = eqs[index][1]
        eqs[index] = (starred, eq, alias.strip(), ts)
        save(eqs)
    return eqs


def is_starred(index):
    """Check if equation at index is starred."""
    eqs = load()
    if 0 <= index < len(eqs):
        return eqs[index][0]
    return False


def contains(equation):
    """Check if equation exists in storage (ignoring star status)."""
    eq = equation.strip()
    for entry in load():
        if entry[1] == eq:
            return True
    return False
