"""Custom equation editor with periodic table for HP Prime.

Provides:
  edit_equation() - periodic table keyboard for chemical formulas
  edit_text() - simple letter keyboard for aliases/text
"""

import hpprime as hp
from constants import (SCREEN_W, SCREEN_H, MENU_Y, GR_AFF,
    COL_BG, COL_TEXT, COL_ACCENT, COL_GRAY, COL_LIGHT_GRAY,
    COL_TITLE_BG, COL_TITLE_FG, COL_MENU_BG, COL_MENU_FG,
    COL_MENU_SEP, FONT_SM, FONT_MD, FONT_TITLE)


# --- PPL helpers ---

def _esc(t):
    return str(t).replace('\\', '\\\\').replace('"', '\\"')


def _tout(g, x, y, t, f, c, w=320):
    s = _esc(t)
    r = (c >> 16) & 0xFF
    gn = (c >> 8) & 0xFF
    b = c & 0xFF
    hp.eval('TEXTOUT_P("' + s + '",G' + str(g) + ',' +
            str(x) + ',' + str(y) + ',' + str(f) + ',RGB(' +
            str(r) + ',' + str(gn) + ',' + str(b) + '),' +
            str(w) + ')')


def _tw(t, f):
    s = _esc(t)
    try:
        r = hp.eval('TEXTSIZE("' + s + '",' + str(f) + ')')
        return r[0] if isinstance(r, list) else len(t) * 7
    except:
        return len(t) * 7


# --- Periodic table data (periods 1-6) ---
# (row, col, symbol)  row=period-1, col=group-1 in 18-col layout
_PT = [
    (0,0,'H'),(0,17,'He'),
    (1,0,'Li'),(1,1,'Be'),
    (1,12,'B'),(1,13,'C'),(1,14,'N'),(1,15,'O'),
    (1,16,'F'),(1,17,'Ne'),
    (2,0,'Na'),(2,1,'Mg'),
    (2,12,'Al'),(2,13,'Si'),(2,14,'P'),(2,15,'S'),
    (2,16,'Cl'),(2,17,'Ar'),
    (3,0,'K'),(3,1,'Ca'),(3,2,'Sc'),(3,3,'Ti'),
    (3,4,'V'),(3,5,'Cr'),(3,6,'Mn'),(3,7,'Fe'),
    (3,8,'Co'),(3,9,'Ni'),(3,10,'Cu'),(3,11,'Zn'),
    (3,12,'Ga'),(3,13,'Ge'),(3,14,'As'),(3,15,'Se'),
    (3,16,'Br'),(3,17,'Kr'),
    (4,0,'Rb'),(4,1,'Sr'),(4,2,'Y'),(4,3,'Zr'),
    (4,4,'Nb'),(4,5,'Mo'),(4,6,'Tc'),(4,7,'Ru'),
    (4,8,'Rh'),(4,9,'Pd'),(4,10,'Ag'),(4,11,'Cd'),
    (4,12,'In'),(4,13,'Sn'),(4,14,'Sb'),(4,15,'Te'),
    (4,16,'I'),(4,17,'Xe'),
    (5,0,'Cs'),(5,1,'Ba'),(5,2,'La'),(5,3,'Hf'),
    (5,4,'Ta'),(5,5,'W'),(5,6,'Re'),(5,7,'Os'),
    (5,8,'Ir'),(5,9,'Pt'),(5,10,'Au'),(5,11,'Hg'),
    (5,12,'Tl'),(5,13,'Pb'),(5,14,'Bi'),(5,15,'Po'),
    (5,16,'At'),(5,17,'Rn'),
]


# --- Layout constants: Equation Editor ---
_PX = 7       # PT grid x start
_PY = 54      # PT grid y start
_CW = 17      # cell width
_CH = 17      # cell height
_PCOLS = 18
_PROWS = 6

# Symbol row:  (  )  +  =  Space
_SY = _PY + _PROWS * _CH + 3   # 159
_SH = 20
_SYMS = ['(', ')', '+', '=', ' ']
_SYM_LBL = ['(', ')', '+', '=', 'Sp']
_SW = SCREEN_W // 5   # 64

# Number row: 0-9
_NY = _SY + _SH + 2   # 181
_NH = 20
_NW = SCREEN_W // 10  # 32

# Text field
_FX = 8
_FY = 28
_FW = SCREEN_W - 16
_FH = 22


# --- Shared drawing ---

def _draw_title(title):
    hp.fillrect(GR_AFF, 0, 0, SCREEN_W, 24,
                COL_TITLE_BG, COL_TITLE_BG)
    _tout(GR_AFF, 8, 4, title, FONT_TITLE, COL_TITLE_FG)


def _draw_field(text, cursor):
    hp.fillrect(GR_AFF, _FX, _FY, _FW, _FH, COL_GRAY, 0xFFFFFF)
    vis_w = _FW - 8
    start = 0
    if cursor > 0:
        bw = _tw(text[:cursor], FONT_MD)
        if bw > vis_w:
            start = max(0, cursor - vis_w // 7 + 5)
    show = text[start:]
    _tout(GR_AFF, _FX + 4, _FY + 4, show, FONT_MD,
          COL_TEXT, vis_w)
    sb = text[start:cursor]
    cx = _FX + 4 + (_tw(sb, FONT_MD) if sb else 0)
    if _FX + 2 <= cx <= _FX + _FW - 2:
        hp.line(GR_AFF, cx, _FY + 3, cx, _FY + _FH - 3,
                COL_ACCENT)
        hp.line(GR_AFF, cx + 1, _FY + 3, cx + 1,
                _FY + _FH - 3, COL_ACCENT)


def _draw_menu_bar(labels):
    hp.fillrect(GR_AFF, 0, MENU_Y, SCREEN_W, 20,
                COL_MENU_BG, COL_MENU_BG)
    bw = SCREEN_W // 6
    for i in range(6):
        x = i * bw
        if labels[i]:
            tw = _tw(labels[i], FONT_SM)
            tx = x + (bw - tw) // 2
            _tout(GR_AFF, tx, MENU_Y + 5, labels[i],
                  FONT_SM, COL_MENU_FG, bw)
        if i > 0:
            hp.line(GR_AFF, x, MENU_Y, x, SCREEN_H - 1,
                    COL_MENU_SEP)


def _menu_hit(tx, ty):
    if ty < MENU_Y:
        return -1
    return min(tx // (SCREEN_W // 6), 5)


def _drain():
    while hp.eval('mouse(1)') >= 0:
        pass


# --- Periodic table drawing & hit detection ---

def _cell_bg(col):
    """Color by column block: s-block, d-block, p-block."""
    if col <= 1:
        return 0xFFE8E0   # warm (alkali/alkaline)
    if col <= 11:
        return 0xE0E8FF   # cool blue (transition)
    return 0xE0F0E0       # green (p-block)


def _draw_pt():
    for row, col, sym in _PT:
        x = _PX + col * _CW
        y = _PY + row * _CH
        bg = _cell_bg(col)
        hp.fillrect(GR_AFF, x, y, _CW - 1, _CH - 1,
                    COL_LIGHT_GRAY, bg)
        off = 5 if len(sym) == 1 else 1
        _tout(GR_AFF, x + off, y + 3, sym, FONT_SM,
              COL_TEXT, _CW)


def _draw_sym_row():
    for i in range(5):
        x = i * _SW
        hp.fillrect(GR_AFF, x, _SY, _SW - 1, _SH - 1,
                    COL_LIGHT_GRAY, 0xD8E8F8)
        tw = _tw(_SYM_LBL[i], FONT_MD)
        tx = x + (_SW - tw) // 2
        _tout(GR_AFF, tx, _SY + 3, _SYM_LBL[i], FONT_MD,
              COL_TEXT, _SW)


def _draw_num_row():
    for i in range(10):
        x = i * _NW
        hp.fillrect(GR_AFF, x, _NY, _NW - 1, _NH - 1,
                    COL_LIGHT_GRAY, 0xF0F0E8)
        tw = _tw(str(i), FONT_MD)
        tx = x + (_NW - tw) // 2
        _tout(GR_AFF, tx, _NY + 3, str(i), FONT_MD,
              COL_TEXT, _NW)


def _pt_hit(tx, ty):
    if ty < _PY or ty >= _PY + _PROWS * _CH:
        return None
    if tx < _PX or tx >= _PX + _PCOLS * _CW:
        return None
    col = (tx - _PX) // _CW
    row = (ty - _PY) // _CH
    for r, c, s in _PT:
        if r == row and c == col:
            return s
    return None


def _sym_hit(tx, ty):
    if ty < _SY or ty >= _SY + _SH:
        return None
    i = tx // _SW
    if 0 <= i < 5:
        return _SYMS[i]
    return None


def _num_hit(tx, ty):
    if ty < _NY or ty >= _NY + _NH:
        return None
    i = tx // _NW
    if 0 <= i < 10:
        return str(i)
    return None


# Physical key -> digit/symbol (normal mode)
_NK = {
    47: '0', 42: '1', 43: '2', 44: '3', 37: '4',
    38: '5', 39: '6', 32: '7', 33: '8', 34: '9',
    50: '+', 45: '-', 49: ' ',
}
_SK = {48: '='}   # shift mode


# =============================================
# Equation Editor (Periodic Table)
# =============================================

_EQ_MENU = ['<', '>', 'Del', 'Clr', 'Cncl', 'OK']


def edit_equation(title='Equation', initial=''):
    """Equation editor with periodic table soft keyboard.

    Returns edited string, or None if cancelled.
    """
    text = initial if initial else ''
    cursor = len(text)

    hp.fillrect(GR_AFF, 0, 0, SCREEN_W, SCREEN_H, COL_BG, COL_BG)
    _draw_title(title)
    _draw_field(text, cursor)
    _draw_pt()
    _draw_sym_row()
    _draw_num_row()
    _draw_menu_bar(_EQ_MENU)
    _drain()

    prev_kb = hp.keyboard()

    while True:
        hp.eval('wait(0.05)')

        # Physical keyboard
        kb = hp.keyboard()
        changed = kb ^ prev_kb
        pressed = changed & kb
        prev_kb = kb

        if pressed:
            shift = bool(kb & (1 << 41))
            for bit in range(52):
                if not (pressed & (1 << bit)):
                    continue
                if bit in (36, 41):
                    continue
                if bit == 4:    # ESC
                    _drain(); return None
                if bit == 30:   # Enter
                    _drain(); return text
                if bit == 19:   # Backspace
                    if cursor > 0:
                        text = text[:cursor-1] + text[cursor:]
                        cursor -= 1
                        _draw_field(text, cursor)
                    continue
                if bit == 7:    # Left
                    if cursor > 0:
                        cursor -= 1
                        _draw_field(text, cursor)
                    continue
                if bit == 8:    # Right
                    if cursor < len(text):
                        cursor += 1
                        _draw_field(text, cursor)
                    continue
                ch = _SK.get(bit) if shift else _NK.get(bit)
                if not ch and shift:
                    ch = _NK.get(bit)
                if ch:
                    text = text[:cursor] + ch + text[cursor:]
                    cursor += len(ch)
                    _draw_field(text, cursor)
            while hp.eval('GETKEY()') >= 0:
                pass
            continue

        # Touch input
        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            tx, ty = f1[0], f1[1]

            sym = _pt_hit(tx, ty)
            if sym:
                text = text[:cursor] + sym + text[cursor:]
                cursor += len(sym)
                _draw_field(text, cursor)
                _drain()
                continue

            ch = _sym_hit(tx, ty)
            if ch:
                text = text[:cursor] + ch + text[cursor:]
                cursor += 1
                _draw_field(text, cursor)
                _drain()
                continue

            ch = _num_hit(tx, ty)
            if ch:
                text = text[:cursor] + ch + text[cursor:]
                cursor += 1
                _draw_field(text, cursor)
                _drain()
                continue

            btn = _menu_hit(tx, ty)
            if btn == 0:     # <
                if cursor > 0:
                    cursor -= 1
                    _draw_field(text, cursor)
            elif btn == 1:   # >
                if cursor < len(text):
                    cursor += 1
                    _draw_field(text, cursor)
            elif btn == 2:   # Del
                if cursor > 0:
                    text = text[:cursor-1] + text[cursor:]
                    cursor -= 1
                    _draw_field(text, cursor)
            elif btn == 3:   # Clr
                text = ''
                cursor = 0
                _draw_field(text, cursor)
            elif btn == 4:   # Cancel
                _drain(); return None
            elif btn == 5:   # OK
                _drain(); return text
            _drain()


# =============================================
# Text Editor (simple keyboard for aliases)
# =============================================

_TXT_MENU = ['<', '>', 'Del', 'Aa', 'Cncl', 'OK']

_KB_U = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ. -_'
_KB_L = 'abcdefghijklmnopqrstuvwxyz. -_'

_KX = 5
_KY = 56
_KW = 31
_KH = 24
_KCOLS = 10
_KROWS = 3

_KNY = _KY + _KROWS * _KH + 2   # number row y
_KNH = 24

_KSY = _KNY + _KNH + 2          # space bar y
_KSH = 22


def _draw_txt_kb(upper):
    chars = _KB_U if upper else _KB_L
    for i in range(30):
        ch = chars[i]
        row = i // _KCOLS
        col = i % _KCOLS
        x = _KX + col * _KW
        y = _KY + row * _KH
        bg = 0xD8E8F8 if i >= 26 else 0xF0F0F0
        hp.fillrect(GR_AFF, x, y, _KW - 1, _KH - 1,
                    COL_LIGHT_GRAY, bg)
        _tout(GR_AFF, x + 10, y + 6, ch, FONT_MD,
              COL_TEXT, _KW)
    for i in range(10):
        x = _KX + i * _KW
        hp.fillrect(GR_AFF, x, _KNY, _KW - 1, _KNH - 1,
                    COL_LIGHT_GRAY, 0xF0F0E8)
        _tout(GR_AFF, x + 10, _KNY + 6, str(i), FONT_MD,
              COL_TEXT, _KW)
    hp.fillrect(GR_AFF, _KX, _KSY, SCREEN_W - 10, _KSH - 1,
                COL_LIGHT_GRAY, 0xF0F0F0)
    _tout(GR_AFF, 140, _KSY + 4, 'Space', FONT_MD,
          COL_GRAY, 80)


def _txt_kb_hit(tx, ty, upper):
    if _KY <= ty < _KY + _KROWS * _KH:
        if _KX <= tx < _KX + _KCOLS * _KW:
            col = (tx - _KX) // _KW
            row = (ty - _KY) // _KH
            idx = row * _KCOLS + col
            chars = _KB_U if upper else _KB_L
            if idx < 30:
                return chars[idx]
    if _KNY <= ty < _KNY + _KNH:
        if _KX <= tx < _KX + _KCOLS * _KW:
            col = (tx - _KX) // _KW
            if col < 10:
                return str(col)
    if _KSY <= ty < _KSY + _KSH:
        return ' '
    return None


_AK = {
    14: 'a', 15: 'b', 16: 'c', 17: 'd', 18: 'e',
    20: 'f', 21: 'g', 22: 'h', 23: 'i', 24: 'j',
    25: 'k', 26: 'l', 27: 'm', 28: 'n', 29: 'o',
    31: 'p', 32: 'q', 33: 'r', 34: 's', 35: 't',
    37: 'u', 38: 'v', 39: 'w', 40: 'x', 42: 'y', 43: 'z',
}


def edit_text(title='Edit', initial=''):
    """Simple text editor with keyboard for aliases.

    Returns edited string, or None if cancelled.
    """
    text = initial if initial else ''
    cursor = len(text)
    upper = True

    hp.fillrect(GR_AFF, 0, 0, SCREEN_W, SCREEN_H, COL_BG, COL_BG)
    _draw_title(title)
    _draw_field(text, cursor)
    _draw_txt_kb(upper)
    _draw_menu_bar(_TXT_MENU)
    _drain()

    prev_kb = hp.keyboard()

    while True:
        hp.eval('wait(0.05)')

        kb = hp.keyboard()
        changed = kb ^ prev_kb
        pressed = changed & kb
        prev_kb = kb

        if pressed:
            alpha = bool(kb & (1 << 36))
            shift = bool(kb & (1 << 41))
            for bit in range(52):
                if not (pressed & (1 << bit)):
                    continue
                if bit in (36, 41):
                    continue
                if bit == 4:
                    _drain(); return None
                if bit == 30:
                    _drain(); return text
                if bit == 19:
                    if cursor > 0:
                        text = text[:cursor-1] + text[cursor:]
                        cursor -= 1
                        _draw_field(text, cursor)
                    continue
                if bit == 7:
                    if cursor > 0:
                        cursor -= 1
                        _draw_field(text, cursor)
                    continue
                if bit == 8:
                    if cursor < len(text):
                        cursor += 1
                        _draw_field(text, cursor)
                    continue
                ch = None
                if alpha and shift:
                    if bit in _AK:
                        ch = _AK[bit].upper()
                elif alpha:
                    ch = _AK.get(bit)
                elif shift:
                    ch = _SK.get(bit) or _NK.get(bit)
                else:
                    ch = _NK.get(bit)
                if ch:
                    text = text[:cursor] + ch + text[cursor:]
                    cursor += len(ch)
                    _draw_field(text, cursor)
            while hp.eval('GETKEY()') >= 0:
                pass
            continue

        f1, f2 = hp.eval('mouse')
        if len(f1) > 0 and f1[0] >= 0:
            tx, ty = f1[0], f1[1]

            ch = _txt_kb_hit(tx, ty, upper)
            if ch:
                text = text[:cursor] + ch + text[cursor:]
                cursor += len(ch)
                _draw_field(text, cursor)
                _drain()
                continue

            btn = _menu_hit(tx, ty)
            if btn == 0:
                if cursor > 0:
                    cursor -= 1
                    _draw_field(text, cursor)
            elif btn == 1:
                if cursor < len(text):
                    cursor += 1
                    _draw_field(text, cursor)
            elif btn == 2:
                if cursor > 0:
                    text = text[:cursor-1] + text[cursor:]
                    cursor -= 1
                    _draw_field(text, cursor)
            elif btn == 3:   # Aa
                upper = not upper
                _draw_txt_kb(upper)
            elif btn == 4:
                _drain(); return None
            elif btn == 5:
                _drain(); return text
            _drain()
