"""Stoichiometry for HP Prime — main entry point.

Chemical equation balancer and molar mass calculator.
Main screen has banner + equation browser with CRUD + star.
"""

import gc
import hpprime as hp
from constants import (GR_AFF, SCREEN_W, MENU_Y,
    COL_BG, COL_TEXT, COL_ACCENT, COL_GRAY, COL_LIGHT_GRAY,
    FONT_SM, FONT_MD, FONT_LG, FONT_TITLE)
from keycodes import (KEY_ESC, KEY_F1, KEY_F2, KEY_F3,
    KEY_F4, KEY_F5, KEY_F6, KEY_UP, KEY_DOWN,
    KEY_ENTER, KEY_BACKSPACE)

from ui import (clear_screen, draw_title, draw_menu, get_menu_tap,
    set_draw_target,
    draw_balanced_equation, draw_element_table,
    draw_molar_result, draw_mass_percent,
    input_equation, input_formula,
    show_error, show_help, show_about, _textout, popup_menu)
import storage


# --- Banner constants ---
_BANNER_H = 48


def _load_banner():
    """Load banner.png into GROB buffer G1 via AFiles."""
    try:
        hp.eval('IFERR G1:=AFiles("banner.png") THEN 0 END')
        return hp.grobw(1) > 0
    except:
        return False


def _esc_ppl_text(text):
    """Escape text for embedding in a PPL string literal."""
    text = str(text)
    text = text.replace('\\', '\\\\')
    text = text.replace('"', '\\"')
    return text


def _text_width(text, font):
    """Measure text width in pixels with TEXTSIZE."""
    try:
        size = hp.eval('TEXTSIZE("' + _esc_ppl_text(text)
                       + '",' + str(font) + ')')
        if isinstance(size, list) and len(size) > 0:
            return int(size[0])
    except:
        pass
    return len(str(text)) * 8


def _draw_centered(gr, y, text, font, color):
    """Draw text horizontally centered on a specific GROB."""
    w = _text_width(text, font)
    x = max(0, (SCREEN_W - w) // 2)
    _textout(gr, x, y, text, font, color, w + 2)


def _draw_banner():
    """Draw the banner on screen from G1, or fallback text."""
    if hp.grobw(1) > 0:
        bw = hp.grobw(1)
        bh = hp.grobh(1)
        hp.eval('BLIT_P(G0,0,0,320,' + str(_BANNER_H)
                + ',G1,0,0,' + str(bw) + ',' + str(bh) + ')')
    else:
        hp.fillrect(GR_AFF, 0, 0, SCREEN_W, _BANNER_H,
                    0x1A4A8A, 0x1A4A8A)
        _textout(GR_AFF, 10, 14, "Balance Formulas",
                 FONT_TITLE, 0xFFFFFF, SCREEN_W)
    # Overlay title text
    _draw_centered(GR_AFF, 14, "Chemical Equation Balancer",
                   FONT_LG, 0x303030)
    _draw_centered(GR_AFF, 30, "Molar Mass Calculator",
                   FONT_MD, 0x606060)


# --- Browser layout (below banner) ---
_FOOTER_Y = MENU_Y - 12
_HEADER_Y = _BANNER_H + 1
_HEADER_H = 14
_ITEM_Y0 = _HEADER_Y + _HEADER_H
_ITEM_H = 18
_MAX_VISIBLE = (_FOOTER_Y - _ITEM_Y0) // _ITEM_H
_SEL_COLOR = 0x2060C0
_SEL_TEXT = 0xFFFFFF
_STAR_COLOR = 0xD0A000

# Column positions
_COL0_X = 12     # divider after star column
_COL1_X = 33     # divider after star/# area
_COL2_X = 235    # divider before date column
_DATE_X = 238    # date text start x

# Sort state: 0=# 1=star 2=equation 3=date, direction 1=asc -1=desc
_sort_col = 0
_sort_dir = 1
_view = []  # maps view position -> storage index
_filter = ''  # substring filter; '' = no filter

MAIN_MENU = ["Edit", "Star", "Mol", "About", "", "Exit"]


def _get_timestamp():
    """Get current timestamp string M/D/YY H:MM."""
    try:
        d = hp.eval('Date')
        t = hp.eval('Time')
        y = int(d)
        mmdd = int(round((d - y) * 10000))
        mo = mmdd // 100
        dy = mmdd % 100
        y2 = y % 100
        hh = int(t)
        mmss = int(round((t - hh) * 10000))
        mi = mmss // 100
        return '%d/%d/%02d %d:%02d' % (mo, dy, y2, hh, mi)
    except:
        return ''


def _sort_key(item):
    """Return sort key based on current _sort_col."""
    idx, entry = item
    if _sort_col == 0:
        return idx
    elif _sort_col == 1:
        return 0 if entry[0] else 1  # starred first
    elif _sort_col == 2:
        alias = entry[2] if len(entry) > 2 else ''
        return (alias if alias else entry[1]).lower()
    else:  # date
        ts = entry[3] if len(entry) > 3 else ''
        return ts if ts else ''


def _sorted_indices(equations):
    """Return list of original indices filtered and in sort order."""
    global _view
    items = list(enumerate(equations))
    if _filter:
        flt = _filter.lower()
        def _m(e):
            txt = e[1].lower()
            al = e[2].lower() if len(e) > 2 and e[2] else ''
            return flt in txt or flt in al
        items = [(i, e) for i, e in items if _m(e)]
    rev = (_sort_dir == -1)
    if _sort_col == 1:
        rev = not rev  # starred=0 should come first in 'asc'
    try:
        items.sort(key=_sort_key, reverse=rev)
    except:
        pass
    _view = [i for i, _ in items]
    return _view


def _header_tap(tx):
    """Return column index (0-3) from header tap x, or -1."""
    if tx < _COL0_X:
        return 1   # star column
    elif tx < _COL1_X:
        return 0   # # column
    elif tx < _COL2_X:
        return 2   # equation column
    else:
        return 3   # date column


def _toggle_sort(col):
    """Toggle sort on column. Same col toggles direction."""
    global _sort_col, _sort_dir
    if _sort_col == col:
        _sort_dir = -_sort_dir
    else:
        _sort_col = col
        _sort_dir = 1


def _real(sel):
    """Map view position to storage index."""
    if _view and 0 <= sel < len(_view):
        return _view[sel]
    return sel


def _draw_browser(equations, selected, scroll):
    """Draw the banner + equation browser list (double-buffered)."""
    # Render to off-screen buffer G3, then BLIT to screen
    hp.dimgrob(3, SCREEN_W, MENU_Y, COL_BG)

    # Banner on G3
    if hp.grobw(1) > 0:
        bw = hp.grobw(1)
        bh = hp.grobh(1)
        hp.eval('BLIT_P(G3,0,0,320,' + str(_BANNER_H)
                + ',G1,0,0,' + str(bw) + ',' + str(bh) + ')')
    else:
        hp.fillrect(3, 0, 0, SCREEN_W, _BANNER_H,
                    0x1A4A8A, 0x1A4A8A)
        _textout(3, 10, 14, "Balance Formulas",
                 FONT_TITLE, 0xFFFFFF, SCREEN_W)
    # Overlay title text on G3
    _draw_centered(3, 14, "Chemical Equation Balancer",
                   FONT_LG, 0x303030)
    _draw_centered(3, 30, "Molar Mass Calculator",
                   FONT_MD, 0x606060)

    if not equations:
        _textout(3, 60, 80, "No equations yet", FONT_LG,
                 COL_GRAY, SCREEN_W)
        _textout(3, 50, 100, "Press Add to create one", FONT_MD,
                 COL_GRAY, SCREEN_W)
        hp.eval('BLIT_P(G0,0,0,320,' + str(MENU_Y)
                + ',G3,0,0,320,' + str(MENU_Y) + ')')
        draw_menu(MAIN_MENU)
        return

    # Column header
    hp.fillrect(3, 0, _HEADER_Y, SCREEN_W, _HEADER_H,
                0xE0E0E8, 0xE0E0E8)
    arrow = ' v' if _sort_dir == 1 else ' ^'
    star_lbl = (arrow.strip()) if _sort_col in (0, 1) else '*'
    star_col = COL_ACCENT if _sort_col in (0, 1) else _STAR_COLOR
    filter_tag = ' [F]' if _filter else ''
    eq_lbl = 'Equation' + filter_tag + (arrow if _sort_col == 2 else '')
    eq_col = 0xD06000 if _filter else (COL_ACCENT if _sort_col == 2 else 0x606060)
    dt_lbl = 'Modified' + (arrow if _sort_col == 3 else '')
    dt_col = COL_ACCENT if _sort_col == 3 else 0x606060
    _textout(3, 3, _HEADER_Y + 2, star_lbl, FONT_SM, star_col, 10)
    _textout(3, 14, _HEADER_Y + 2, eq_lbl, FONT_SM, eq_col, 200)
    _textout(3, _DATE_X, _HEADER_Y + 2, dt_lbl, FONT_SM, dt_col, 82)
    # Header bottom line
    hp.line(3, 0, _HEADER_Y + _HEADER_H - 1, SCREEN_W,
            _HEADER_Y + _HEADER_H - 1, COL_LIGHT_GRAY)

    max_text_w = _COL2_X - 16
    view = _sorted_indices(equations)
    total = len(view)        # filtered count (drives loop + scrollbar)
    n_total = len(equations) # full count (for footer)
    for i in range(_MAX_VISIBLE):
        vi = scroll + i
        if vi >= total:
            break
        idx = view[vi]

        y = _ITEM_Y0 + i * _ITEM_H
        entry = equations[idx]
        starred = entry[0]
        eq = entry[1]
        alias = entry[2] if len(entry) > 2 else ''
        ts = entry[3] if len(entry) > 3 else ''
        label = alias if alias else eq

        if vi == selected:
            hp.fillrect(3, 2, y, SCREEN_W - 4, _ITEM_H - 2,
                        _SEL_COLOR, _SEL_COLOR)
            if starred:
                _textout(3, 4, y + 2, '*', FONT_MD, 0xFFD040, 12)
            _textout(3, 14, y + 2, label, FONT_MD, _SEL_TEXT, max_text_w)
            if ts:
                _textout(3, _DATE_X, y + 4, ts, FONT_SM,
                         0xC0D8FF, 82)
        else:
            if i % 2 == 1:
                hp.fillrect(3, 2, y, SCREEN_W - 4, _ITEM_H - 2,
                            0xF4F4F4, 0xF4F4F4)
            if starred:
                _textout(3, 4, y + 2, '*', FONT_MD, _STAR_COLOR, 12)
            _textout(3, 14, y + 2, label, FONT_MD, COL_TEXT, max_text_w)
            if ts:
                _textout(3, _DATE_X, y + 4, ts, FONT_SM,
                         COL_GRAY, 82)

    # Separator line above footer
    hp.line(3, 5, _FOOTER_Y - 3, SCREEN_W - 5, _FOOTER_Y - 3,
            COL_LIGHT_GRAY)

    # Footer info line
    n_starred = sum(1 for e in equations if e[0])
    if _filter:
        count_str = str(total) + '/' + str(n_total) + ' eq'
    else:
        count_str = str(total) + ' eq'
    if n_starred > 0:
        count_str += ', ' + str(n_starred) + ' starred'
    _textout(3, 10, _FOOTER_Y, count_str, FONT_SM, COL_GRAY, 160)
    _textout(3, 180, _FOOTER_Y, 'Enter=Balance', FONT_SM, COL_GRAY, 140)

    # Scrollbar
    if total > _MAX_VISIBLE:
        sb_x = SCREEN_W - 6
        sb_area_h = _FOOTER_Y - 3 - _ITEM_Y0
        thumb_h = max(12, sb_area_h * _MAX_VISIBLE // total)
        thumb_y = _ITEM_Y0 + (sb_area_h - thumb_h) * scroll // max(1, total - _MAX_VISIBLE)
        hp.fillrect(3, sb_x, _ITEM_Y0, 4, sb_area_h,
                    COL_LIGHT_GRAY, COL_LIGHT_GRAY)
        hp.fillrect(3, sb_x, thumb_y, 4, thumb_h,
                    COL_GRAY, COL_GRAY)

    # BLIT all at once to screen — no flicker
    hp.eval('BLIT_P(G0,0,0,320,' + str(MENU_Y)
            + ',G3,0,0,320,' + str(MENU_Y) + ')')
    draw_menu(MAIN_MENU)


def _ensure_visible(selected, scroll):
    """Adjust scroll to keep selected item visible."""
    if selected < scroll:
        scroll = selected
    elif selected >= scroll + _MAX_VISIBLE:
        scroll = selected - _MAX_VISIBLE + 1
    return max(0, scroll)


def _row_from_y(y, scroll, total):
    """Convert touch Y to equation index, or -1."""
    if y < _ITEM_Y0 or y >= MENU_Y:
        return -1
    row = (y - _ITEM_Y0) // _ITEM_H
    idx = scroll + row
    if idx >= total:
        return -1
    return idx


_CONTENT_Y = 24   # below title bar
_VIEW_H = MENU_Y - _CONTENT_Y  # 196px visible content area


def _blit_result(scroll_y, total_h, max_scroll, menu):
    """Draw result screen: title, blit content from G2, scrollbar, menu."""
    clear_screen()
    draw_title("Balanced")
    # BLIT visible portion of content from G2 to G0
    bh = min(_VIEW_H, total_h - scroll_y)
    if bh > 0:
        cmd = ('BLIT_P(G0,0,' + str(_CONTENT_Y) + ',320,' +
               str(_CONTENT_Y + bh) + ',G2,0,' + str(scroll_y) +
               ',320,' + str(scroll_y + bh) + ')')
        hp.eval(cmd)
    # Scrollbar
    if max_scroll > 0:
        sb_x = SCREEN_W - 6
        thumb_h = max(12, _VIEW_H * _VIEW_H // total_h)
        thumb_y = _CONTENT_Y + (_VIEW_H - thumb_h) * scroll_y // max(1, max_scroll)
        hp.fillrect(GR_AFF, sb_x, _CONTENT_Y, 4, _VIEW_H,
                    COL_LIGHT_GRAY, COL_LIGHT_GRAY)
        hp.fillrect(GR_AFF, sb_x, thumb_y, 4, thumb_h,
                    COL_GRAY, COL_GRAY)
    draw_menu(menu)


def show_result(eq_str, alias=''):
    """Balance and display an equation, with Save option if new."""
    try:
        from balancer import balance, verify_balance
        result = balance(eq_str)
    except ValueError as e:
        show_error(str(e))
        return
    except Exception as e:
        show_error('Error: ' + str(e))
        return

    is_saved = storage.contains(eq_str)

    # Render content to off-screen GROB G2
    n_el = len(result['elements'])
    buf_h = 200 + n_el * 14
    hp.dimgrob(2, SCREEN_W, buf_h, COL_BG)
    set_draw_target(2)

    y = 0
    if alias:
        _textout(2, 10, y, alias, FONT_MD, COL_ACCENT, SCREEN_W - 20)
        y += 16
    y = draw_balanced_equation(result, y)
    y = draw_element_table(result, y)
    total_h = y

    set_draw_target(GR_AFF)

    max_scroll = max(0, total_h - _VIEW_H)
    scroll_y = 0
    menu = ["New", "Mol", "", "", "", "Back"]
    if not is_saved:
        menu[4] = "Save"

    _blit_result(scroll_y, total_h, max_scroll, menu)

    while True:
        hp.eval('wait(0.1)')
        key = hp.eval('GETKEY()')
        if key == KEY_ESC or key == KEY_F6:
            return
        if key == KEY_UP and scroll_y > 0:
            scroll_y = max(0, scroll_y - 20)
            _blit_result(scroll_y, total_h, max_scroll, menu)
        elif key == KEY_DOWN and scroll_y < max_scroll:
            scroll_y = min(max_scroll, scroll_y + 20)
            _blit_result(scroll_y, total_h, max_scroll, menu)
        elif key == KEY_F1:
            eq = input_equation()
            if eq:
                show_result(eq)
            return
        elif key == KEY_F2:
            _do_molar_for(eq_str)
            return
        elif key == KEY_F5 and not is_saved:
            storage.add(eq_str, ts=_get_timestamp())
            return

        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            btn = get_menu_tap(f1[0], f1[1])
            if btn == 0:
                eq = input_equation()
                if eq:
                    show_result(eq)
                return
            elif btn == 1:
                _do_molar_for(eq_str)
                return
            elif btn == 4 and not is_saved:
                storage.add(eq_str, ts=_get_timestamp())
                return
            elif btn == 5:
                return


def _do_molar_for(eq_str):
    """Show molar mass for compounds in an equation."""
    from parser import parse_equation
    try:
        lhs, rhs = parse_equation(eq_str)
    except:
        do_molar()
        return

    all_compounds = [f for f, _ in lhs] + [f for f, _ in rhs]
    if len(all_compounds) == 1:
        _show_molar(all_compounds[0])
        return

    # Graphical compound picker
    sel = 0
    total = len(all_compounds)
    pick_menu = ["", "", "", "", "", "Back"]
    _PICK_Y0 = 32
    _PICK_H = 22
    _PICK_MAX = (MENU_Y - _PICK_Y0) // _PICK_H

    def _draw_picker():
        clear_screen()
        draw_title("Pick Compound")
        for i in range(min(_PICK_MAX, total)):
            y = _PICK_Y0 + i * _PICK_H
            c = all_compounds[i]
            num = str(i + 1)
            nx = 30 - len(num) * 7
            if i == sel:
                hp.fillrect(GR_AFF, 2, y, SCREEN_W - 4, _PICK_H - 2,
                            0x2060C0, 0x2060C0)
                _textout(GR_AFF, nx, y + 3, num, FONT_LG,
                         0xFFFFFF, 30)
                _textout(GR_AFF, 38, y + 3, c, FONT_LG, 0xFFFFFF,
                         SCREEN_W - 48)
            else:
                if i % 2 == 1:
                    hp.fillrect(GR_AFF, 2, y, SCREEN_W - 4,
                                _PICK_H - 2, 0xF4F4F4, 0xF4F4F4)
                _textout(GR_AFF, nx, y + 3, num, FONT_LG,
                         COL_GRAY, 30)
                _textout(GR_AFF, 38, y + 3, c, FONT_LG, COL_TEXT,
                         SCREEN_W - 48)
        draw_menu(pick_menu)

    _draw_picker()

    while True:
        hp.eval('wait(0.1)')
        key = hp.eval('GETKEY()')
        if key == KEY_ESC or key == KEY_F6:
            return
        if key == KEY_UP and sel > 0:
            sel -= 1
            _draw_picker()
        elif key == KEY_DOWN and sel < total - 1:
            sel += 1
            _draw_picker()
        elif key == KEY_ENTER:
            _show_molar(all_compounds[sel])
            return

        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            tx, ty = f1[0], f1[1]
            btn = get_menu_tap(tx, ty)
            if btn == 5:
                return
            if _PICK_Y0 <= ty < _PICK_Y0 + total * _PICK_H:
                idx = (ty - _PICK_Y0) // _PICK_H
                if idx < total:
                    if idx == sel:
                        _show_molar(all_compounds[sel])
                        return
                    else:
                        sel = idx
                        _draw_picker()


def _show_molar(formula_str):
    """Display molar mass result screen."""
    try:
        from molar import molar_mass
        result = molar_mass(formula_str)
    except ValueError as e:
        show_error(str(e))
        return
    except Exception as e:
        show_error('Error: ' + str(e))
        return

    clear_screen()
    draw_title("Molar Mass")
    y = draw_molar_result(result, 30)

    draw_menu(["New", "Mass%", "", "", "", "Back"])

    while True:
        hp.eval('wait(0.1)')
        key = hp.eval('GETKEY()')
        if key == KEY_ESC or key == KEY_F6:
            return
        if key == KEY_F1:
            do_molar()
            return
        if key == KEY_F2:
            _show_mass_pct(formula_str)
            return

        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            btn = get_menu_tap(f1[0], f1[1])
            if btn == 0:
                do_molar()
                return
            elif btn == 1:
                _show_mass_pct(formula_str)
                return
            elif btn == 5:
                return


def _show_mass_pct(formula_str):
    """Display mass percent composition screen."""
    try:
        from molar import mass_percent
        percents = mass_percent(formula_str)
    except ValueError as e:
        show_error(str(e))
        return

    clear_screen()
    draw_title("Mass % - " + formula_str)
    y = draw_mass_percent(percents, 30)

    draw_menu(["", "", "", "", "", "Back"])

    while True:
        hp.eval('wait(0.1)')
        key = hp.eval('GETKEY()')
        if key == KEY_ESC or key == KEY_F6:
            return

        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            btn = get_menu_tap(f1[0], f1[1])
            if btn == 5:
                return


def _input_alias(current=''):
    """Prompt for alias using custom editor."""
    from editor import edit_text
    title = 'Edit Alias' if current else 'Alias'
    result = edit_text(title, current)
    if result is None:
        return current
    result = result.strip()
    if result == '-':
        return ''
    if result == '':
        return current
    return result


def do_molar():
    """Molar mass flow: input formula -> compute -> display."""
    fm = input_formula()
    if fm:
        _show_molar(fm)


_EDIT_SUBMENU_BASE = ['Add', 'Edit', 'Delete', 'Filter']


def _do_edit_menu(equations, selected, scroll):
    """Show Add / Edit / Delete / Filter submenu."""
    global _filter
    items = list(_EDIT_SUBMENU_BASE)
    if _filter:
        items.append('Clear Filter')
    choice = popup_menu(items, anchor_x=0)
    if choice == 0:
        eq = input_equation()
        if eq:
            alias = _input_alias()
            equations = storage.add(eq, alias, _get_timestamp())
            selected = 0
            scroll = 0
            show_result(eq)
            equations = storage.load()
    elif choice == 1:
        if equations:
            ri = _real(selected)
            entry = equations[ri]
            old_eq = entry[1]
            old_alias = entry[2] if len(entry) > 2 else ''
            new_eq = input_equation(old_eq)
            if new_eq:
                new_alias = _input_alias(old_alias)
                equations = storage.update(
                    ri, new_eq, new_alias, _get_timestamp())
    elif choice == 2:
        if equations:
            equations = storage.delete(_real(selected))
            if selected >= len(equations):
                selected = max(0, len(equations) - 1)
            scroll = _ensure_visible(selected, scroll)
    elif choice == 3:
        # Set / update filter
        from editor import edit_text
        new_f = edit_text('Filter', _filter)
        if new_f is not None:
            _filter = new_f.strip()
        selected = 0
        scroll = 0
    elif choice == 4:
        # Clear filter (only shown when filter active)
        _filter = ''
        selected = 0
        scroll = 0
    return equations, selected, scroll


def main():
    """Main application loop — banner + equation browser."""
    _load_banner()
    equations = storage.load()
    selected = 0
    scroll = 0
    touch_selected = False

    _draw_browser(equations, selected, scroll)

    while True:
        hp.eval('wait(0.1)')
        key = hp.eval('GETKEY()')

        if key == KEY_ESC or key == KEY_F6:
            break

        elif key == KEY_UP:
            if selected > 0:
                selected -= 1
                touch_selected = False
                scroll = _ensure_visible(selected, scroll)
                _draw_browser(equations, selected, scroll)

        elif key == KEY_DOWN:
            if _view and selected < len(_view) - 1:
                selected += 1
                touch_selected = False
                scroll = _ensure_visible(selected, scroll)
                _draw_browser(equations, selected, scroll)

        elif key == KEY_ENTER:
            if equations:
                ri = _real(selected)
                entry = equations[ri]
                al = entry[2] if len(entry) > 2 else ''
                show_result(entry[1], al)
                equations = storage.load()
                if selected >= len(_view):
                    selected = max(0, len(_view) - 1)
                touch_selected = False
                scroll = _ensure_visible(selected, scroll)
                _draw_browser(equations, selected, scroll)

        elif key == KEY_F1:
            # Edit submenu (Add / Edit / Delete)
            equations, selected, scroll = _do_edit_menu(
                equations, selected, scroll)
            _draw_browser(equations, selected, scroll)

        elif key == KEY_F2:
            # Star/unstar
            if equations:
                equations = storage.toggle_star(
                    _real(selected), _get_timestamp())
            _draw_browser(equations, selected, scroll)

        elif key == KEY_F3:
            # Molar
            do_molar()
            _draw_browser(equations, selected, scroll)

        elif key == KEY_F4:
            show_about()
            _draw_browser(equations, selected, scroll)

        elif key == KEY_BACKSPACE:
            # Quick delete
            if equations:
                equations = storage.delete(_real(selected))
                if selected >= len(_view):
                    selected = max(0, len(_view) - 1)
                scroll = _ensure_visible(selected, scroll)
                _draw_browser(equations, selected, scroll)

        # Touch handling
        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            tx, ty = f1[0], f1[1]
            evt = f1[4] if len(f1) > 4 else 3

            # long-press (4) never triggers anything
            btn = get_menu_tap(tx, ty) if evt != 4 else -1
            if btn == 0:
                # Edit submenu (Add / Edit / Delete)
                equations, selected, scroll = _do_edit_menu(
                    equations, selected, scroll)
                _draw_browser(equations, selected, scroll)
            elif btn == 1:
                # Star/unstar
                if equations:
                    equations = storage.toggle_star(
                        _real(selected), _get_timestamp())
                _draw_browser(equations, selected, scroll)
            elif btn == 2:
                # Molar
                do_molar()
                _draw_browser(equations, selected, scroll)
            elif btn == 3:
                show_about()
                _draw_browser(equations, selected, scroll)
            elif btn == 5:
                break
            else:
                # Header tap — sort (any event except long-press)
                if evt != 4 and _HEADER_Y <= ty < _ITEM_Y0 and equations:
                    col = _header_tap(tx)
                    if col >= 0:
                        _toggle_sort(col)
                        selected = 0
                        scroll = 0
                        _draw_browser(equations, selected, scroll)
                # Scrollbar — responds to any touch for smooth drag
                elif tx >= SCREEN_W - 14 and _ITEM_Y0 <= ty < _FOOTER_Y - 3 and len(_view) > _MAX_VISIBLE:
                    # Scroll to position based on touch Y
                    sb_area_h = _FOOTER_Y - 3 - _ITEM_Y0
                    ratio = (ty - _ITEM_Y0) / max(1, sb_area_h)
                    max_scroll = len(_view) - _MAX_VISIBLE
                    scroll = int(ratio * max_scroll)
                    scroll = max(0, min(scroll, max_scroll))
                    selected = max(scroll, min(selected, scroll + _MAX_VISIBLE - 1))
                    _draw_browser(equations, selected, scroll)
                # Row tap — any event except long-press
                # press(1) can select; only release/click (not press) can open
                elif evt != 4:
                    idx = _row_from_y(ty, scroll, len(_view))
                    if idx >= 0:
                        if idx != selected:
                            # Tap on a different row: select it
                            selected = idx
                            touch_selected = True
                            _draw_browser(equations, selected, scroll)
                        elif touch_selected and evt != 1:
                            # Release/click on already-selected row: open
                            ri = _real(selected)
                            entry = equations[ri]
                            al = entry[2] if len(entry) > 2 else ''
                            show_result(entry[1], al)
                            equations = storage.load()
                            if selected >= len(_view):
                                selected = max(0, len(_view) - 1)
                            touch_selected = False
                            scroll = _ensure_visible(selected, scroll)
                            _draw_browser(equations, selected, scroll)

        gc.collect()

    # Clear the Python terminal output so it doesn't show on exit
    hp.eval('print')


# Entry point
main()
