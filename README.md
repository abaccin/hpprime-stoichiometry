# Stoichiometry — HP Prime App

**Chemical equation balancer and molar mass calculator for the HP Prime graphing calculator.**

---

## Features

- **Balance chemical equations** — automatically finds integer stoichiometric coefficients for any valid equation.
- **Verify balance** — element-by-element atom count table confirms both sides are balanced.
- **Molar mass calculator** — enter any chemical formula to get the total molar mass and per-element breakdown.
- **Mass percent composition** — visual bar-chart breakdown of each element's contribution by mass.
- **Equation browser** — sortable, filterable list of saved equations with timestamps.
- **Star / favourite** — mark frequently used equations for quick access.
- **Aliases** — give equations a friendly display name.
- **Persistent storage** — equations are saved to the app's data file and survive restarts.

---
## Demo
https://github.com/user-attachments/assets/8834f168-dbae-47d4-8596-16ad56265e7f

## Screens

| Screen | Access | Description |
|---|---|---|
| Browser | App start | List of saved equations. Tap or press Enter to balance. |
| Balance result | Enter on selected eq / F1 Add | Balanced equation + verification table. |
| Molar mass | F3 (Mol) from browser or result | Breakdown table for a formula. |
| Mass percent | F2 (Mass%) from molar screen | Per-element % with bar chart. |
| About | (from Help menu) | Version and algorithm info. |

---

## Controls

### Browser (main screen)

| Key / Touch | Action |
|---|---|
| ↑ / ↓ | Move selection |
| Enter | Balance selected equation |
| F1 (Edit) | Submenu: Add / Edit / Delete / Filter |
| F2 (Star) | Toggle star on selected equation |
| F3 (Mol) | Open molar mass calculator |
| Backspace | Delete selected equation |
| F6 (Exit) / ESC | Exit app |
| Tap column header | Sort by that column (tap again to reverse) |
| Tap row | Select; tap again to open |
| Drag scrollbar | Scroll list |

### Balance result screen

| Key / Touch | Action |
|---|---|
| ↑ / ↓ | Scroll result |
| F1 (New) | Enter a new equation to balance |
| F2 (Mol) | Open molar mass for a compound from the equation |
| F5 (Save) | Save equation to browser (only shown if not already saved) |
| F6 (Back) / ESC | Return to browser |

### Molar mass screen

| Key / Touch | Action |
|---|---|
| F1 (New) | Enter a new formula |
| F2 (Mass%) | Show mass percent breakdown |
| F6 (Back) / ESC | Return |

---

## Input Format

### Equations

Use `=`, `->`, or `=>` as the reaction separator. Compounds on each side are separated by `+`.

```
Fe + O2 = Fe2O3
CH4 + O2 -> CO2 + H2O
H2 + Cl2 => HCl
Ca(OH)2 + H3PO4 = Ca3(PO4)2 + H2O
Al2(SO4)3 + NaOH = Al(OH)3 + Na2SO4
```

- Coefficients in your input are **ignored** — the balancer computes them.
- Spaces around operators and `+` are optional.
- Parenthesised groups (e.g. `Ca(OH)2`, `Al2(SO4)3`) are supported.
- Element symbols are case-sensitive: `Fe` not `fe`.

### Formulas (molar mass)

```
H2SO4
Ca(OH)2
NaCl
Al2(SO4)3
C6H12O6
```

---

## Algorithm

Balancing is solved as a **matrix nullspace** problem:

1. Parse the equation into an element × compound stoichiometry matrix **A**, with LHS columns positive and RHS columns negated.
2. Find a vector **x** such that **Ax = 0** (the nullspace of **A**).
3. Scale **x** to the smallest positive integers using GCD reduction.

This is the same approach described in detail at:  
**https://scipython.com/chem/articles/balancing-a-chemical-reaction/**

The HP Prime implementation uses the built-in `linalg` module in place of NumPy/SymPy, making it fully self-contained with no external dependencies.

---

## Files

| File | Purpose |
|---|---|
| `main.py` | App entry point, browser UI and main event loop |
| `balancer.py` | Matrix nullspace balancing algorithm |
| `parser.py` | Chemical formula and equation parser |
| `molar.py` | Molar mass and mass percent calculations |
| `storage.py` | Persistent equation list (load / save / CRUD) |
| `ui.py` | Drawing helpers, menus, input dialogs |
| `editor.py` | On-screen text editor widget |
| `elements.py` | Atomic mass table |
| `constants.py` | Colors, fonts, screen dimensions |
| `keycodes.py` | HP Prime key code constants |

---

## Deployment

1. Copy the `Stoichiometry.hpappdir` folder to your calculator using the **HP Connectivity Kit**.
2. The app appears in the App Library as **Stoichiometry**.
3. Launch it; if the screen stays blank, press the **Clear** soft key once.

Alternatively use the included `deploy.ps1` script if the Connectivity Kit CLI is configured on your machine.

---

## Requirements

- HP Prime running firmware **2.1.14730** or later (MicroPython enabled).
- No additional libraries — uses only built-in HP Prime Python modules (`hpprime`, `linalg`, `micropython`, `gc`).
