"""Molar mass calculator for HP Prime MicroPython.

Computes molar mass from a chemical formula string,
with element-by-element breakdown.
"""

from parser import parse_formula
from elements import WEIGHTS, NAMES


def molar_mass(formula_str):
    """Calculate molar mass of a compound.

    Args:
        formula_str: e.g. 'H2SO4', 'Ca(OH)2'

    Returns dict:
        'formula': original string
        'total_mass': total molar mass (g/mol)
        'breakdown': list of (element, count, mass_each, mass_total)
        'elements': parsed element dict
    """
    elements = parse_formula(formula_str)

    breakdown = []
    total = 0.0
    for el in sorted(elements.keys()):
        count = elements[el]
        if el not in WEIGHTS:
            raise ValueError('Unknown element: ' + el)
        mass_each = WEIGHTS[el]
        mass_total = mass_each * count
        total += mass_total
        breakdown.append((el, count, mass_each, mass_total))

    return {
        'formula': formula_str,
        'total_mass': total,
        'breakdown': breakdown,
        'elements': elements,
    }


def mass_percent(formula_str):
    """Calculate mass percent of each element in compound.

    Returns list of (element, count, mass_percent, mass_total).
    """
    result = molar_mass(formula_str)
    total = result['total_mass']
    if total == 0:
        return []

    percents = []
    for el, count, mass_each, mass_total in result['breakdown']:
        pct = (mass_total / total) * 100.0
        percents.append((el, count, pct, mass_total))

    return percents


def format_mass(formula_str):
    """Return a formatted string showing molar mass calculation."""
    result = molar_mass(formula_str)
    lines = []
    lines.append(formula_str + '  =  ' + _fmt(result['total_mass']) + ' g/mol')
    lines.append('')
    for el, count, mass_each, mass_total in result['breakdown']:
        name = NAMES.get(el, el)
        if count == 1:
            lines.append('  ' + el + ' (' + name + '): ' +
                         _fmt(mass_each) + ' g/mol')
        else:
            lines.append('  ' + el + ' x' + str(count) + ' (' + name + '): ' +
                         str(count) + ' x ' + _fmt(mass_each) +
                         ' = ' + _fmt(mass_total) + ' g/mol')
    return lines


def _fmt(val):
    """Format float to 3 decimal places."""
    # MicroPython-compatible formatting
    s = str(int(val * 1000))
    if len(s) <= 3:
        s = '0' * (3 - len(s) + 1) + s
    return s[:-3] + '.' + s[-3:]
