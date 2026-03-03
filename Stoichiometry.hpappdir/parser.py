"""Chemical formula parser for HP Prime MicroPython.

Parses formulas like:  Fe2O3, Ca(OH)2, Al2(SO4)3, Mg3(PO4)2
Returns a dict of {element_symbol: count}.

Also parses full equations like:
  Fe + O2 -> Fe2O3
  CH4 + O2 = CO2 + H2O

No regex dependency — uses character-by-character parsing.
"""


def parse_formula(formula):
    """Parse a chemical formula string into {element: count} dict.

    Handles:
      - Multi-char element symbols: Fe, Ca, Na, Al
      - Subscript numbers: O2, Fe2O3
      - Parenthesized groups with subscripts: Ca(OH)2, Al2(SO4)3
      - Nested parentheses (rare but supported)

    Returns dict, e.g. parse_formula('Ca(OH)2') -> {'Ca':1, 'O':2, 'H':2}
    Raises ValueError on bad input.
    """
    tokens = _tokenize(formula)
    result, _ = _parse_tokens(tokens, 0)
    return result


def _tokenize(formula):
    """Split formula into tokens: element symbols, numbers, '(', ')'."""
    tokens = []
    i = 0
    n = len(formula)
    while i < n:
        c = formula[i]
        if c == '(' or c == ')':
            tokens.append(c)
            i += 1
        elif c.isupper():
            # Element symbol: uppercase optionally followed by lowercase
            sym = c
            i += 1
            while i < n and formula[i].islower():
                sym += formula[i]
                i += 1
            tokens.append(sym)
        elif c.isdigit():
            num = ''
            while i < n and formula[i].isdigit():
                num += formula[i]
                i += 1
            tokens.append(int(num))
        elif c in (' ', '\t'):
            i += 1  # skip whitespace
        else:
            raise ValueError('Bad char: ' + c)
    return tokens


def _parse_tokens(tokens, pos):
    """Recursive descent parser for tokenized formula.

    Returns (element_dict, new_pos).
    """
    result = {}
    n = len(tokens)
    while pos < n:
        tok = tokens[pos]
        if tok == '(':
            # Parse sub-group recursively
            sub, pos = _parse_tokens(tokens, pos + 1)
            # Check for subscript after ')'
            mult = 1
            if pos < n and isinstance(tokens[pos], int):
                mult = tokens[pos]
                pos += 1
            for el, cnt in sub.items():
                result[el] = result.get(el, 0) + cnt * mult
        elif tok == ')':
            return result, pos + 1
        elif isinstance(tok, str):
            # Element symbol
            pos += 1
            count = 1
            if pos < n and isinstance(tokens[pos], int):
                count = tokens[pos]
                pos += 1
            result[tok] = result.get(tok, 0) + count
        else:
            # Unexpected number without preceding element
            pos += 1
    return result, pos


def parse_equation(equation):
    """Parse a chemical equation string.

    Accepted separators: '->', '→', '=', '=>'
    Terms separated by '+'

    Returns (lhs_terms, rhs_terms) where each term is a tuple:
        (original_formula_string, {element: count})

    Example:
        parse_equation('CH4 + O2 -> CO2 + H2O')
        -> ( [('CH4', {'C':1,'H':4}), ('O2', {'O':2})],
             [('CO2', {'C':1,'O':2}), ('H2O', {'H':2,'O':1})] )
    """
    # Normalize separator
    eq = equation.strip()
    sep = None
    for s in ['->', '=>', '=']:
        if s in eq:
            sep = s
            break
    if sep is None:
        raise ValueError('No arrow/= found. Use -> or =')

    parts = eq.split(sep)
    if len(parts) != 2:
        raise ValueError('Equation must have exactly one arrow')

    lhs_str, rhs_str = parts[0].strip(), parts[1].strip()

    def parse_side(side_str):
        terms = []
        for term in side_str.split('+'):
            t = term.strip()
            if not t:
                continue
            d = parse_formula(t)
            terms.append((t, d))
        return terms

    lhs = parse_side(lhs_str)
    rhs = parse_side(rhs_str)

    if not lhs:
        raise ValueError('No reactants found')
    if not rhs:
        raise ValueError('No products found')

    return lhs, rhs


def formula_to_str(formula_dict):
    """Convert element dict back to readable formula string."""
    parts = []
    for el in sorted(formula_dict.keys()):
        c = formula_dict[el]
        if c == 1:
            parts.append(el)
        else:
            parts.append(el + str(c))
    return ''.join(parts)
