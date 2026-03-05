"""Equation library browser for Stoichiometry HP Prime app.

Reads equations from equations.lib — a compact text file organized by
category.  Format:
    #Category Name
    Alias|equation
    Alias|equation
    ...

Categories are loaded lazily; only one category's equations are in
memory at a time to conserve RAM on the HP Prime.
"""

import gc
import hpprime as hp
from constants import (GR_AFF, SCREEN_W, MENU_Y,
    FONT_SM, FONT_MD, FONT_LG, FONT_TITLE)
from theme import colors
from keycodes import KEY_ESC, KEY_UP, KEY_DOWN, KEY_ENTER
from input_helpers import get_key, mouse_clear, get_touch, get_menu_tap
from ui import clear_screen, draw_title, draw_menu, _textout
from icons import ICON_BACK, ICON_CHECK

_LIB_FILE = 'equations.lib'

# Layout constants
_ITEM_Y0 = 26         # below title bar
_ITEM_H = 22          # row height
_FOOTER_Y = MENU_Y - 12
_MAX_VIS = (_FOOTER_Y - _ITEM_Y0) // _ITEM_H


def _categories():
    """Return list of category names from the library file.

    Scans only lines starting with '#'. Minimal memory use.
    """
    cats = []
    try:
        with open(_LIB_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    cats.append(line[1:])
    except:
        pass
    return cats


def _load_category(cat_name):
    """Load equations for a single category.

    Returns list of (alias, equation) tuples.
    Only one category is kept in memory.
    """
    entries = []
    found = False
    try:
        with open(_LIB_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('#'):
                    if found:
                        break  # next category — done
                    if line[1:] == cat_name:
                        found = True
                    continue
                if found and '|' in line:
                    parts = line.split('|', 1)
                    entries.append((parts[0].strip(),
                                   parts[1].strip()))
    except:
        pass
    return entries


def _draw_list(title, items, selected, scroll, total, menu,
               get_label=None):
    """Draw a scrollable list screen (reused for categories and equations)."""
    clear_screen()
    draw_title(title)
    n = len(items)
    for i in range(_MAX_VIS):
        vi = scroll + i
        if vi >= n:
            break
        y = _ITEM_Y0 + i * _ITEM_H
        label = get_label(items[vi]) if get_label else str(items[vi])
        if vi == selected:
            hp.fillrect(GR_AFF, 2, y, SCREEN_W - 4, _ITEM_H - 2,
                        colors['sel_bg'], colors['sel_bg'])
            _textout(GR_AFF, 12, y + 3, label, FONT_LG,
                     colors['sel_text'], SCREEN_W - 24)
        else:
            if i % 2 == 1:
                hp.fillrect(GR_AFF, 2, y, SCREEN_W - 4, _ITEM_H - 2,
                            colors['alt_row'], colors['alt_row'])
            _textout(GR_AFF, 12, y + 3, label, FONT_LG,
                     colors['text'], SCREEN_W - 24)
    # Footer — count
    _textout(GR_AFF, 10, _FOOTER_Y, str(total) + ' items',
             FONT_SM, colors['gray'], 120)
    # Scrollbar
    if n > _MAX_VIS:
        sb_x = SCREEN_W - 6
        sb_h = _FOOTER_Y - _ITEM_Y0
        th = max(12, sb_h * _MAX_VIS // n)
        ty = _ITEM_Y0 + (sb_h - th) * scroll // max(1, n - _MAX_VIS)
        hp.fillrect(GR_AFF, sb_x, _ITEM_Y0, 4, sb_h,
                    colors['light_gray'], colors['light_gray'])
        hp.fillrect(GR_AFF, sb_x, ty, 4, th,
                    colors['gray'], colors['gray'])
    draw_menu(menu)


def _ensure_vis(sel, scr):
    if sel < scr:
        scr = sel
    elif sel >= scr + _MAX_VIS:
        scr = sel - _MAX_VIS + 1
    return max(0, scr)


def _row_from_y(y, scroll, total):
    if y < _ITEM_Y0 or y >= _FOOTER_Y:
        return -1
    row = (y - _ITEM_Y0) // _ITEM_H
    idx = scroll + row
    return idx if idx < total else -1


def _pick_from_list(title, items, total, menu, get_label=None,
                    on_select=None):
    """Generic scrollable list picker.

    on_select(index) is called when an item is confirmed.
    Returns the index chosen, or -1 if cancelled.
    """
    sel = 0
    scr = 0
    _draw_list(title, items, sel, scr, total, menu, get_label)
    down = False
    tx0 = -1
    ty0 = -1

    while True:
        key = get_key()
        if key == KEY_ESC:
            return -1
        if key == KEY_UP and sel > 0:
            sel -= 1
            scr = _ensure_vis(sel, scr)
            _draw_list(title, items, sel, scr, total, menu, get_label)
        elif key == KEY_DOWN and sel < len(items) - 1:
            sel += 1
            scr = _ensure_vis(sel, scr)
            _draw_list(title, items, sel, scr, total, menu, get_label)
        elif key == KEY_ENTER:
            if on_select:
                on_select(sel)
            return sel

        tx, ty = get_touch()
        if tx >= 0:
            if not down:
                down = True
                tx0 = tx
                ty0 = ty
            # Live scrollbar drag
            if tx0 >= SCREEN_W - 14 and len(items) > _MAX_VIS:
                sb_h = _FOOTER_Y - _ITEM_Y0
                ratio = (ty - _ITEM_Y0) / max(1, sb_h)
                ms = len(items) - _MAX_VIS
                ns = max(0, min(int(ratio * ms), ms))
                if ns != scr:
                    scr = ns
                    sel = max(scr, min(sel, scr + _MAX_VIS - 1))
                    _draw_list(title, items, sel, scr, total,
                               menu, get_label)
        elif down:
            down = False
            btn = get_menu_tap(tx0, ty0)
            if btn == 5:
                return -1
            if btn == 4 and on_select:
                on_select(sel)
                return sel
            idx = _row_from_y(ty0, scr, len(items))
            if idx >= 0:
                if idx == sel:
                    if on_select:
                        on_select(sel)
                    return sel
                else:
                    sel = idx
                    scr = _ensure_vis(sel, scr)
                    _draw_list(title, items, sel, scr, total,
                               menu, get_label)


def browse_library(storage_mod, get_timestamp):
    """Open the equation library browser.

    Two-level: pick category -> pick equation -> add to user list.
    storage_mod:   the storage module (for .add / .contains)
    get_timestamp: callable returning current timestamp string
    """
    cats = _categories()
    if not cats:
        from ui import show_error
        show_error('equations.lib not found')
        return

    # --- Level 1: category picker ---
    cat_menu = ["", "", "", "", "", ("Back", ICON_BACK)]

    def _cat_label(c):
        return c

    while True:
        choice = _pick_from_list("Library", cats, len(cats),
                                 cat_menu, _cat_label)
        if choice < 0:
            return  # user cancelled
        gc.collect()

        # --- Level 2: equations in category ---
        cat = cats[choice]
        entries = _load_category(cat)
        if not entries:
            continue

        added_set = set()

        def _eq_label(e):
            a, eq = e
            prefix = '+ ' if eq in added_set else ''
            return prefix + (a if a else eq)

        eq_menu = ["", "", "", "",
                   ("Add", ICON_CHECK), ("Back", ICON_BACK)]

        def _on_add(idx):
            a, eq = entries[idx]
            if not storage_mod.contains(eq):
                storage_mod.add(eq, a, get_timestamp())
                added_set.add(eq)

        while True:
            r = _pick_from_list(cat, entries, len(entries),
                                eq_menu, _eq_label, _on_add)
            if r < 0:
                break  # back to categories
            # Stay in equation list after adding
            gc.collect()

        # Free category data
        del entries
        gc.collect()
