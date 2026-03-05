"""UI drawing helpers for Stoichiometry HP Prime app.

Provides menu bar, title bar, text rendering, input dialogs,
and result display — all using hpprime graphics primitives.
"""

import hpprime as hp
from constants import (SCREEN_W, SCREEN_H, MENU_Y, MENU_H,
    GR_AFF, FONT_SM, FONT_MD, FONT_LG, FONT_XL, FONT_TITLE,
    APP_NAME, APP_VERSION)
from theme import colors
from icons import ICON_W, ICON_H, ICON_CHECK


# Target GROB for drawing (0=screen, 2=off-screen buffer)
_draw_target = GR_AFF


def set_draw_target(g):
    """Set target GROB for draw_text, draw_separator, etc."""
    global _draw_target
    _draw_target = g


def _escape(text):
    """Escape text for use in PPL eval strings."""
    return str(text).replace('\\', '\\\\').replace('"', '\\"')


def _rgb(color):
    """Convert 0xRRGGBB integer to PPL RGB(r,g,b) string."""
    r = (color >> 16) & 0xFF
    g = (color >> 8) & 0xFF
    b = color & 0xFF
    return 'RGB(' + str(r) + ',' + str(g) + ',' + str(b) + ')'


def _textout(gr, x, y, text, font, color, width=320):
    """Draw text using TEXTOUT_P via eval (supports color + width).

    hpprime.textout() only takes 5 args on real hardware,
    so we use TEXTOUT_P which supports color and clipping width.
    """
    t = _escape(text)
    cmd = ('TEXTOUT_P("' + t + '",G' + str(gr) + ',' +
           str(x) + ',' + str(y) + ',' + str(font) + ',' +
           _rgb(color) + ',' + str(width) + ')')
    hp.eval(cmd)


def clear_screen():
    """Fill entire screen with background color."""
    hp.fillrect(GR_AFF, 0, 0, SCREEN_W, SCREEN_H, colors['bg'], colors['bg'])


def draw_title(text):
    """Draw title bar at top of screen."""
    hp.fillrect(GR_AFF, 0, 0, SCREEN_W, 24, colors['title_bg'], colors['title_bg'])
    _textout(GR_AFF, 8, 4, text, FONT_TITLE, colors['title_fg'], SCREEN_W)


def _draw_icon(x, y, icon, color):
    """Render a 1-bit bitmap icon at (x, y) using pixon calls."""
    _pixon = hp.pixon
    for row in range(ICON_H):
        bits = icon[row]
        if bits == 0:
            continue
        mask = 1 << (ICON_W - 1)
        for col in range(ICON_W):
            if bits & mask:
                _pixon(GR_AFF, x + col, y + row, color)
            mask >>= 1


def draw_menu(labels):
    """Draw 6-button soft menu bar at bottom (native HP Prime style).

    labels: list of up to 6 items.  Each item is either:
      - a string          "Edit"         → text only
      - a tuple           ("Edit", ICON) → icon + text
      - a tuple           ("", ICON)     → icon only (centered)
    """
    btn_w = SCREEN_W // 6
    bg = colors['menu_bg']
    hi = colors['menu_hi']
    sep = colors['menu_sep']
    fg = colors['menu_fg']
    y0 = MENU_Y
    y1 = SCREEN_H - 1
    hp.fillrect(GR_AFF, 0, y0, SCREEN_W, MENU_H, bg, bg)
    for i in range(min(len(labels), 6)):
        x = i * btn_w
        # Top highlight for 3D raised look
        hp.line(GR_AFF, x + 1, y0, x + btn_w - 2, y0, hi)
        # Separator between buttons
        if i > 0:
            hp.line(GR_AFF, x, y0, x, y1, sep)

        item = labels[i]
        if not item:
            continue

        if type(item) is tuple:
            text, icon = item[0], item[1]
        else:
            text, icon = item, None

        if icon and text:
            # Icon + text: measure combined width, center them
            tw = _text_width(text, FONT_SM)
            gap = 3
            total_w = ICON_W + gap + tw
            ix = x + (btn_w - total_w) // 2
            iy = y0 + (MENU_H - ICON_H) // 2
            _draw_icon(ix, iy, icon, fg)
            _textout(GR_AFF, ix + ICON_W + gap, y0 + 5,
                     text, FONT_SM, fg, btn_w)
        elif icon:
            # Icon only: center it
            ix = x + (btn_w - ICON_W) // 2
            iy = y0 + (MENU_H - ICON_H) // 2
            _draw_icon(ix, iy, icon, fg)
        else:
            # Text only
            tw = _text_width(text, FONT_SM)
            tx = x + (btn_w - tw) // 2
            _textout(GR_AFF, tx, y0 + 5, text, FONT_SM, fg, btn_w)


def get_menu_tap(x, y):
    """Return 0-5 menu button index if tap is in menu area, else -1."""
    if y < MENU_Y:
        return -1
    return min(x // (SCREEN_W // 6), 5)


def draw_text(x, y, text, font=FONT_MD, color=None):
    """Draw text string on target GROB."""
    if color is None:
        color = colors['text']
    _textout(_draw_target, x, y, text, font, color, SCREEN_W - x)


def draw_text_centered(y, text, font=FONT_MD, color=None):
    """Draw text centered horizontally."""
    if color is None:
        color = colors['text']
    tw = _text_width(text, font)
    x = (SCREEN_W - tw) // 2
    _textout(_draw_target, x, y, text, font, color, SCREEN_W)


def draw_wrapped_text(x, y, text, font, color, max_w, line_h):
    """Draw text with word wrapping. Returns final y position."""
    words = text.split(' ')
    line = ''
    cy = y
    for word in words:
        test = (line + ' ' + word).strip()
        tw = _text_width(test, font)
        if tw > max_w and line:
            _textout(_draw_target, x, cy, line, font, color, max_w)
            cy += line_h
            line = word
        else:
            line = test
    if line:
        _textout(_draw_target, x, cy, line, font, color, max_w)
        cy += line_h
    return cy


def draw_box(x, y, w, h, border_color, fill_color):
    """Draw a filled rectangle with border."""
    hp.fillrect(GR_AFF, x, y, w, h, border_color, fill_color)


def draw_separator(y, color=None):
    """Draw horizontal separator line."""
    if color is None:
        color = colors['light_gray']
    hp.line(_draw_target, 5, y, SCREEN_W - 5, y, color)


def _text_width(text, font):
    """Get text width in pixels using PPL TEXTSIZE."""
    t = _escape(text)
    try:
        result = hp.eval('TEXTSIZE("' + t + '",' + str(font) + ')')
        if isinstance(result, list):
            return result[0]
        return len(text) * 7  # fallback
    except:
        return len(text) * 7


def text_width(text, font=FONT_MD):
    """Public text width helper."""
    return _text_width(text, font)


def show_message(title, lines, wait=True):
    """Show a message dialog with title and text lines.

    If wait=True, blocks until user taps or presses a key.
    """
    clear_screen()
    draw_title(title)

    y = 32
    for line in lines:
        if y > MENU_Y - 16:
            break
        draw_text(10, y, line, FONT_MD, colors['text'])
        y += 16

    if wait:
        draw_menu(["", "", "", "", "", ("OK", ICON_CHECK)])
        _wait_for_input()


def show_error(message):
    """Show error message."""
    show_message("Error", [message])


def _wait_for_input():
    """Block until key press or screen tap."""
    while True:
        hp.eval('wait(0.1)')
        key = hp.eval('GETKEY()')
        if key >= 0:
            return key
        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            return -1


def popup_menu(items, anchor_x=0, item_colors=None):
    """Draw a custom popup menu above the given button x position.

    items:       list of label strings.
    anchor_x:    left edge (px) of the triggering button.
    item_colors: optional list of 0xRRGGBB ints (same length as items).
                 Non-zero entries get a colored dot drawn left of the label.
    Returns:     0-based index of chosen item, or -1 if cancelled.
    """
    _KEY_UP    = 2
    _KEY_DOWN  = 12
    _KEY_ENTER = 30
    _KEY_ESC   = 4

    PAD_X  = 12
    ITEM_H = 22
    PAD_V  = 4        # vertical padding inside box

    # Measure popup width from widest item
    if item_colors is None:
        item_colors = []
    has_dots = len(item_colors) > 0
    dot_pad = 14 if has_dots else 0  # space for color dot
    max_w = 90
    for label in items:
        w = _text_width(label, FONT_LG)
        if w + PAD_X * 2 + dot_pad > max_w:
            max_w = w + PAD_X * 2 + dot_pad

    popup_w = max_w
    popup_h = PAD_V + len(items) * ITEM_H + PAD_V

    # Position: directly above the menu bar, left-anchored to button
    px = anchor_x
    py = MENU_Y - popup_h - 2
    if px + popup_w > SCREEN_W:
        px = SCREEN_W - popup_w
    if py < 0:
        py = 0

    # Save the region we'll overwrite (include 4px shadow bleed)
    save_w = min(popup_w + 4, SCREEN_W - px)
    save_h = min(popup_h + 4, MENU_Y - py)
    hp.dimgrob(5, save_w, save_h, 0)
    hp.eval('BLIT_P(G5,0,0,' + str(save_w) + ',' + str(save_h) +
            ',G0,' + str(px) + ',' + str(py) + ',' +
            str(px + save_w) + ',' + str(py + save_h) + ')')

    def _draw(sel):
        # Drop-shadow
        hp.fillrect(GR_AFF, px + 3, py + 3, popup_w, popup_h,
                    colors['popup_shadow'], colors['popup_shadow'])
        # Background + border
        hp.fillrect(GR_AFF, px, py, popup_w, popup_h,
                    colors['popup_border'], colors['popup_bg'])
        # Items
        for i, label in enumerate(items):
            iy = py + PAD_V + i * ITEM_H
            tx = px + PAD_X + dot_pad
            tw = popup_w - PAD_X - dot_pad
            if i == sel:
                hp.fillrect(GR_AFF, px + 1, iy, popup_w - 2, ITEM_H,
                            colors['accent'], colors['accent'])
                if has_dots and i < len(item_colors) and item_colors[i]:
                    c = item_colors[i]
                    hp.fillrect(GR_AFF, px + PAD_X, iy + 5,
                                10, ITEM_H - 10, c, c)
                _textout(GR_AFF, tx, iy + 4,
                         label, FONT_LG, colors['sel_text'], tw)
            else:
                # Subtle separator between items
                if i > 0:
                    hp.line(GR_AFF, px + 4, iy, px + popup_w - 4, iy,
                            colors['popup_sep'])
                if has_dots and i < len(item_colors) and item_colors[i]:
                    c = item_colors[i]
                    hp.fillrect(GR_AFF, px + PAD_X, iy + 5,
                                10, ITEM_H - 10, c, c)
                _textout(GR_AFF, tx, iy + 4,
                         label, FONT_LG, colors['text'], tw)

    def _restore():
        hp.eval('BLIT_P(G0,' + str(px) + ',' + str(py) + ',' +
                str(px + save_w) + ',' + str(py + save_h) +
                ',G5,0,0,' + str(save_w) + ',' + str(save_h) + ')')

    sel = 0
    _draw(sel)
    while hp.eval('mouse(1)') >= 0: pass  # drain stale tap events

    while True:
        hp.eval('wait(0.05)')
        key = hp.eval('GETKEY()')
        if key == _KEY_UP:
            sel = (sel - 1) % len(items)
            _draw(sel)
        elif key == _KEY_DOWN:
            sel = (sel + 1) % len(items)
            _draw(sel)
        elif key == _KEY_ENTER:
            _restore()
            return sel
        elif key == _KEY_ESC:
            _restore()
            return -1

        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            tx = int(f1[0])
            ty = int(f1[1])
            evt = f1[4] if len(f1) > 4 else 3
            if evt == 4:
                continue
            # Tap outside → cancel
            if tx < px or tx > px + popup_w or ty < py or ty > py + popup_h:
                if evt != 1:
                    _restore()
                    return -1
            else:
                rel_y = ty - py - PAD_V
                idx = rel_y // ITEM_H
                if 0 <= idx < len(items):
                    if idx != sel:
                        sel = idx
                        _draw(sel)
                    if evt != 1:
                        _restore()
                        return sel


def input_equation(initial='', category='', cat_names=None, cat_colors=None):
    """Prompt for chemical equation using periodic table editor.

    initial:    pre-fill equation (for editing).
    category:   current category name.
    cat_names:  list of category names for the picker.
    cat_colors: list of 0xRRGGBB colors matching cat_names.
    Returns (equation, category) tuple, or (None, category) if cancelled.
    """
    from editor import edit_equation
    title = 'Edit Equation' if initial else 'New Equation'
    result = edit_equation(title, initial, category, cat_names, cat_colors)
    if result is None:
        eq = initial if initial else None
        return (eq, category)
    text, cat = result
    text = text.strip() if text else ''
    if not text:
        eq = initial if initial else None
        return (eq, category)
    return (text, cat)


def input_formula():
    """Prompt for chemical formula using periodic table editor.

    Returns formula string, or None if cancelled/empty.
    """
    from editor import edit_equation
    result = edit_equation('Molar Mass', '')
    if result is None:
        return None
    text, _cat = result
    text = text.strip() if text else ''
    if not text:
        return None
    return text


def draw_balanced_equation(result, start_y=30):
    """Draw a nicely formatted balanced equation on screen.

    Returns y position after drawing.
    """
    y = start_y

    # Draw each side
    draw_text(10, y, "Balanced Equation:", FONT_MD, colors['gray'])
    y += 18

    # Build and draw LHS
    lhs_parts = []
    for coeff, formula, _ in result['lhs']:
        if coeff == 1:
            lhs_parts.append(formula)
        else:
            lhs_parts.append(str(coeff) + formula)
    lhs_str = ' + '.join(lhs_parts)

    # Build and draw RHS
    rhs_parts = []
    for coeff, formula, _ in result['rhs']:
        if coeff == 1:
            rhs_parts.append(formula)
        else:
            rhs_parts.append(str(coeff) + formula)
    rhs_str = ' + '.join(rhs_parts)

    eq_str = lhs_str + '  ->  ' + rhs_str

    # Check width BEFORE drawing to avoid double-draw overlap
    max_w = SCREEN_W - 20
    tw = _text_width(eq_str, FONT_LG)
    if tw < max_w:
        _draw_equation_colored(10, y, result, FONT_LG)
        y += 20
    elif _text_width(eq_str, FONT_MD) < max_w:
        _draw_equation_colored(10, y, result, FONT_MD)
        y += 16
    else:
        # Too wide even for small font — split LHS / RHS
        y = draw_wrapped_text(10, y, lhs_str, FONT_MD, colors['text'], max_w, 16)
        draw_text(20, y, "->", FONT_MD, colors['arrow'])
        y += 16
        y = draw_wrapped_text(10, y, rhs_str, FONT_MD, colors['text'], max_w, 16)

    return y


def _draw_equation_colored(x, y, result, font):
    """Draw equation with coefficients in red and formulas in blue."""
    cx = x
    # LHS
    for i, (coeff, formula, _) in enumerate(result['lhs']):
        if i > 0:
            draw_text(cx, y, ' + ', font, colors['text'])
            cx += _text_width(' + ', font)
        if coeff > 1:
            cs = str(coeff)
            draw_text(cx, y, cs, font, colors['coeff'])
            cx += _text_width(cs, font)
        draw_text(cx, y, formula, font, colors['element'])
        cx += _text_width(formula, font)

    # Arrow
    draw_text(cx, y, ' -> ', font, colors['arrow'])
    cx += _text_width(' -> ', font)

    # RHS
    for i, (coeff, formula, _) in enumerate(result['rhs']):
        if i > 0:
            draw_text(cx, y, ' + ', font, colors['text'])
            cx += _text_width(' + ', font)
        if coeff > 1:
            cs = str(coeff)
            draw_text(cx, y, cs, font, colors['coeff'])
            cx += _text_width(cs, font)
        draw_text(cx, y, formula, font, colors['element'])
        cx += _text_width(formula, font)


def draw_element_table(result, start_y):
    """Draw element verification table showing atom counts per side.

    Returns y position after table.
    """
    from balancer import verify_balance
    is_ok, lhs_counts, rhs_counts = verify_balance(result)

    y = start_y + 4
    draw_separator(y)
    y += 8

    draw_text(10, y, "Verification:", FONT_MD, colors['gray'])
    y += 16

    # Header
    draw_text(10, y, "Element", FONT_SM, colors['gray'])
    draw_text(100, y, "LHS", FONT_SM, colors['gray'])
    draw_text(160, y, "RHS", FONT_SM, colors['gray'])
    draw_text(220, y, "OK?", FONT_SM, colors['gray'])
    y += 14

    draw_separator(y - 2)

    for el in result['elements']:
        lc = lhs_counts.get(el, 0)
        rc = rhs_counts.get(el, 0)
        ok = lc == rc

        draw_text(10, y, el, FONT_MD, colors['element'])
        draw_text(100, y, str(lc), FONT_MD, colors['text'])
        draw_text(160, y, str(rc), FONT_MD, colors['text'])
        color = colors['success'] if ok else colors['error']
        draw_text(220, y, "Yes" if ok else "NO", FONT_MD, color)
        y += 14

        if _draw_target == GR_AFF and y > MENU_Y - 20:
            break

    y += 4
    status_color = colors['success'] if is_ok else colors['error']
    status_text = "Balanced!" if is_ok else "NOT balanced"
    draw_text(10, y, status_text, FONT_MD, status_color)
    y += 16

    return y


def draw_molar_result(result, start_y=30):
    """Draw molar mass calculation result.

    result: dict from molar.molar_mass()
    Returns y position after drawing.
    """
    y = start_y

    # Title: formula = total mass
    from molar import _fmt
    formula = result['formula']
    total = _fmt(result['total_mass'])

    draw_text(10, y, formula, FONT_XL, colors['element'])
    tw = _text_width(formula, FONT_XL)
    draw_text(10 + tw + 5, y, '= ' + total + ' g/mol', FONT_XL, colors['text'])
    y += 22

    draw_separator(y)
    y += 8

    # Breakdown table
    draw_text(10, y, "Element", FONT_SM, colors['gray'])
    draw_text(80, y, "Count", FONT_SM, colors['gray'])
    draw_text(130, y, "Mass", FONT_SM, colors['gray'])
    draw_text(210, y, "Subtotal", FONT_SM, colors['gray'])
    y += 14

    draw_separator(y - 2)

    for el, count, mass_each, mass_total in result['breakdown']:
        draw_text(10, y, el, FONT_MD, colors['element'])
        draw_text(80, y, str(count), FONT_MD, colors['text'])
        draw_text(130, y, _fmt(mass_each), FONT_MD, colors['text'])
        draw_text(210, y, _fmt(mass_total), FONT_MD, colors['text'])
        y += 14

        if y > MENU_Y - 20:
            break

    y += 4
    draw_separator(y)
    y += 6
    draw_text(10, y, "Total: " + total + " g/mol", FONT_LG, colors['success'])
    y += 18

    return y


def draw_mass_percent(percents, start_y):
    """Draw mass percent breakdown.

    percents: list from molar.mass_percent()
    """
    y = start_y
    draw_text(10, y, "Mass Percent:", FONT_MD, colors['gray'])
    y += 16

    for el, count, pct, mass_total in percents:
        from molar import _fmt
        pct_str = _fmt(pct) + '%'
        draw_text(10, y, el, FONT_MD, colors['element'])
        draw_text(60, y, pct_str, FONT_MD, colors['text'])

        # Draw bar
        bar_x = 130
        bar_w = int(pct * 1.5)  # scale: 100% = 150px
        if bar_w > 0:
            hp.fillrect(GR_AFF, bar_x, y + 2, bar_w, 10,
                        colors['accent'], colors['accent'])
        y += 14

        if y > MENU_Y - 10:
            break

    return y


def show_about():
    """Show about dialog."""
    lines = [
        APP_NAME + ' v' + APP_VERSION,
        'Chemical equation balancer and molar mass calculator',
        'for HP Prime.',
        'Algorithm:',
        'Matrix nullspace method',
        'Coefficients reduced via integer GCD',
        'GitHub:',
        'https://github.com/abaccin/hpprime-stoichiometry',
        'Made with \u2665 by Andrea Baccin',
        'baccin.andrea@gmail.com',
    ]
    show_message("About", lines)


def show_help():
    """Show help on the terminal screen (no clipping)."""
    hp.eval('print')  # Clear terminal
    print('=== Stoichiometry Help ===')
    print('')
    print('BALANCE (F1):')
    print('  Enter equation like:')
    print('  Fe+O2=Fe2O3')
    print('  CH4+O2=CO2+H2O')
    print('')
    print('MOLAR MASS (F2):')
    print('  Enter formula like:')
    print('  H2SO4  Ca(OH)2  NaCl')
    print('')
    print('MASS % (F3):')
    print('  Shows element composition %')
    print('')
    print('Separators: -> => =')
    print('Terms separated by +')
    print('Parentheses: Al2(SO4)3')
    print('')
    print('Press Enter to go back')
    try:
        input('')
    except:
        pass
