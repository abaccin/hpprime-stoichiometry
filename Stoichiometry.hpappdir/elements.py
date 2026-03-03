"""Periodic table data: atomic weights for molar mass calculation.

Covers first 86 elements (through Radon) — sufficient for all
common chemistry coursework. Weights are average atomic mass in g/mol.
"""

# Symbol -> atomic mass (g/mol), truncated to 3 decimals to save memory
WEIGHTS = {
    'H': 1.008, 'He': 4.003,
    'Li': 6.941, 'Be': 9.012, 'B': 10.81, 'C': 12.011,
    'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180,
    'Na': 22.990, 'Mg': 24.305, 'Al': 26.982, 'Si': 28.086,
    'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948,
    'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867,
    'V': 50.942, 'Cr': 51.996, 'Mn': 54.938, 'Fe': 55.845,
    'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38,
    'Ga': 69.723, 'Ge': 72.64, 'As': 74.922, 'Se': 78.96,
    'Br': 79.904, 'Kr': 83.798,
    'Rb': 85.468, 'Sr': 87.62, 'Y': 88.906, 'Zr': 91.224,
    'Nb': 92.906, 'Mo': 95.96, 'Ru': 101.07, 'Rh': 102.906,
    'Pd': 106.42, 'Ag': 107.868, 'Cd': 112.411, 'In': 114.818,
    'Sn': 118.710, 'Sb': 121.760, 'Te': 127.60, 'I': 126.904,
    'Xe': 131.293,
    'Cs': 132.905, 'Ba': 137.327, 'La': 138.905, 'Ce': 140.116,
    'Pr': 140.908, 'Nd': 144.242, 'Sm': 150.36, 'Eu': 151.964,
    'Gd': 157.25, 'Tb': 158.925, 'Dy': 162.500, 'Ho': 164.930,
    'Er': 167.259, 'Tm': 168.934, 'Yb': 173.054, 'Lu': 174.967,
    'Hf': 178.49, 'Ta': 180.948, 'W': 183.84, 'Re': 186.207,
    'Os': 190.23, 'Ir': 192.217, 'Pt': 195.084, 'Au': 196.967,
    'Hg': 200.59, 'Tl': 204.383, 'Pb': 207.2, 'Bi': 208.980,
    'Rn': 222.0,
}

# Element names for display (optional)
NAMES = {
    'H': 'Hydrogen', 'He': 'Helium', 'Li': 'Lithium', 'Be': 'Beryllium',
    'B': 'Boron', 'C': 'Carbon', 'N': 'Nitrogen', 'O': 'Oxygen',
    'F': 'Fluorine', 'Ne': 'Neon', 'Na': 'Sodium', 'Mg': 'Magnesium',
    'Al': 'Aluminium', 'Si': 'Silicon', 'P': 'Phosphorus', 'S': 'Sulfur',
    'Cl': 'Chlorine', 'Ar': 'Argon', 'K': 'Potassium', 'Ca': 'Calcium',
    'Fe': 'Iron', 'Cu': 'Copper', 'Zn': 'Zinc', 'Ag': 'Silver',
    'Au': 'Gold', 'Pt': 'Platinum', 'Hg': 'Mercury', 'Pb': 'Lead',
    'Sn': 'Tin', 'Br': 'Bromine', 'I': 'Iodine', 'Mn': 'Manganese',
    'Cr': 'Chromium', 'Co': 'Cobalt', 'Ni': 'Nickel', 'Ba': 'Barium',
    'Sr': 'Strontium',
}
