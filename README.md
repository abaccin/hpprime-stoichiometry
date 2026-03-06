# Stoichiometry — HP Prime App

**Chemical equation balancer, molar mass calculator, and reaction library for the HP Prime graphing calculator.**

---

## Features

### Core Chemistry
- **Balance chemical equations** — automatically finds integer stoichiometric coefficients using matrix nullspace computation.
- **Verify balance** — element-by-element atom count table confirms both sides match (pass/fail per element).
- **Molar mass calculator** — enter any formula to get the total molar mass with per-element breakdown (element, count, atomic mass, subtotal).
- **Mass percent composition** — visual bar-chart showing each element's contribution by mass.
- **Colored equation display** — balanced equations render with coefficients in red, formulas in blue, and the arrow in gray.

### Equation Library
- **273 built-in equations** across 7 reaction categories, ready to browse and use.
- **Two-level browser** — pick a category, then scroll through its equations.
- **Add to saved list** — tap Add to copy a library equation into your personal collection (duplicates are detected automatically).

### Categories

Equations can be tagged with a color-coded reaction type:

| Category | Color | Description |
|---|---|---|
| Combustion | Orange | Hydrocarbon and alcohol combustion |
| Synthesis | Blue | Formation / combination reactions |
| Double Replacement | Green | Precipitation, acid-base metathesis |
| Single Replacement | Olive | Metal-acid, halogen displacement |
| Neutralization | Teal | Acid + base reactions |
| Redox | Purple | Oxidation-reduction reactions |
| Decomposition | Red | Thermal decomposition, electrolysis |

Category badges appear in the browser list and on the balance result screen.

### Equation Management
- **Equation browser** — sortable, filterable list of saved equations.
- **Sort by column** — tap a column header to sort by #, star, equation name, or category (tap again to reverse).
- **Filter** — filter by category, starred-only (★), or custom text search.
- **Star / favourite** — mark frequently used equations for quick access.
- **Aliases** — give equations a friendly display name (category prefix is stripped in the display).
- **Persistent storage** — equations are saved to the app's data file and survive restarts.
- **Auto-initialization** — on first launch, the saved list is seeded from the built-in library; version tracking forces re-init when the library is updated.

### Editors
- **Periodic table equation editor** — visual on-screen periodic table keyboard (72 elements, color-coded by block: warm for s-block, blue for d-block, green for p-block) with symbol row `( ) + =`, number row 0–9, and cursor navigation.
- **Category picker** — tap the category button in the periodic table gap to assign a reaction type via a color-coded popup.
- **Text editor for aliases** — full A-Z keyboard with upper/lowercase toggle, digits, and special characters.
- **Physical keyboard support** — HP Prime hardware keys are mapped for digits, symbols, alpha characters, and shift.

### UI & Theming
- **Light / dark theme** — auto-detects system theme on launch; toggle with one tap. 50+ color tokens covering every UI element.
- **Bitmap menu icons** — 16 custom 9×9 pixel icons for all menu actions (Edit, Star, Mol, Theme, Back, New, OK, About, %, Exit, Library, ←, →, Del, Clear, Aa).
- **Popup menus** — context-sensitive dropdowns with color-coded category dots, keyboard/touch navigation, and non-destructive overlay rendering.
- **Scrollbar drag** — touch-drag scrollbar for fast navigation in all list views.
- **Double-buffered rendering** — off-screen GROB buffers for smooth scrolling on result screens.
- **Alternating row colors** — for readability in all list views.

---

## Demo

https://github.com/user-attachments/assets/8834f168-dbae-47d4-8596-16ad56265e7f

## Screens

| Screen | Access | Description |
|---|---|---|
| Browser | App start | List of saved equations with category badges. Tap or Enter to balance. |
| Balance result | Enter on selected eq / Edit → Add | Balanced equation with colored formatting + verification table. |
| Molar mass | Mol button from browser or result | Breakdown table (element, count, mass, subtotal). |
| Mass percent | Mass% button from molar screen | Per-element % with bar chart. |
| Library | Library button | Two-level category → equation browser with 273 built-in equations. |
| Equation editor | Edit → Add / Edit | Periodic table keyboard for entering equations. |
| About | About button | Version, algorithm info, and links. |

---

## Controls

The soft menu bar at the bottom of each screen is **touch-only** (tap the button).
The physical keyboard handles navigation and common shortcuts.

### Browser (main screen)

| Key / Touch | Action |
|---|---|
| ↑ / ↓ | Move selection |
| Enter | Balance selected equation |
| Backspace | Delete selected equation |
| ESC | Exit app |
| Tap **Edit** | Submenu: Add / Edit / Delete / Filter / Clear Filter |
| Tap **Star** | Toggle star on selected equation |
| Tap **Mol** | Open molar mass calculator |
| Tap **About** | Show about screen |
| Tap **Theme** (◐) | Toggle light / dark theme |
| Tap **Exit** | Exit app |
| Tap column header | Sort by #, Star, Equation, or Category (tap again to reverse) |
| Tap row | Select; tap again to open |
| Drag scrollbar | Scroll list |

### Edit submenu

| Choice | Action |
|---|---|
| Add | Open periodic table editor → enter equation → set alias → assign category |
| Edit | Edit the selected equation, alias, and category |
| Delete | Delete the selected equation |
| Filter | Pick a filter: ★ Starred, a category name, or type custom text |
| Clear Filter | Remove active filter (only shown when a filter is active) |

### Balance result screen

| Key / Touch | Action |
|---|---|
| ↑ / ↓ | Scroll result |
| ESC | Return to browser |
| Tap **New** | Enter a new equation to balance |
| Tap **Mol** | Pick a compound from the equation → open molar mass |
| Tap **Save** | Save equation to browser (only shown if not already saved) |
| Tap **Back** | Return to browser |

### Molar mass screen

| Key / Touch | Action |
|---|---|
| ESC | Return |
| Tap **New** | Enter a new formula |
| Tap **Mass%** | Show mass percent breakdown |
| Tap **Back** | Return |

### Equation editor

| Key / Touch | Action |
|---|---|
| Tap element | Append element symbol to input |
| Tap `( ) + = 0-9` | Append character |
| Tap **Category** button | Open category picker popup |
| Tap **← →** | Move cursor |
| Tap **Del** | Delete character at cursor |
| Tap **Clear** | Clear entire input |
| Tap **ESC** | Cancel |
| Tap **OK** | Confirm input |
| Physical digits/shift | Mapped to numbers and `=` |

### Library browser

| Key / Touch | Action |
|---|---|
| ↑ / ↓ | Move selection |
| Enter | Open category / add equation |
| ESC | Back to categories / exit library |
| Tap **Add** | Add selected equation to saved list |
| Tap **Back** | Return |
| Drag scrollbar | Scroll list |

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
| `main.py` | App entry point, browser UI, and main event loop |
| `balancer.py` | Matrix nullspace balancing algorithm |
| `parser.py` | Chemical formula and equation parser |
| `molar.py` | Molar mass and mass percent calculations |
| `storage.py` | Persistent equation list (load / save / CRUD / auto-init from library) |
| `library.py` | Built-in equation library browser (two-level category → equation picker) |
| `equations.lib` | 273 pre-balanced equations in 7 categories (plain-text `Category\|Name\|Equation`) |
| `ui.py` | Drawing helpers, menus, popup menus, input dialogs, result screens |
| `editor.py` | Periodic table equation editor and text editor for aliases |
| `elements.py` | Atomic mass table |
| `constants.py` | Screen dimensions, fonts, GROB constants |
| `keycodes.py` | HP Prime keyboard bitmask bit positions |
| `theme.py` | Light / dark color palettes (50+ tokens, auto-detect + toggle) |
| `icons.py` | 16 bitmap menu icons (9×9 pixel art) |
| `input_helpers.py` | Keyboard edge-detect, touch helpers, DAS repeat |
| `ppl_guard.py` | PPL environment save / restore on app entry / exit |

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
