"""Theme support for Stoichiometry HP Prime app - light and dark color palettes."""

LIGHT = {
    'bg': 0xFFFFFF,
    'text': 0x000000,
    'title_bg': 0x2050A0,
    'title_fg': 0xFFFFFF,
    'accent': 0x2080D0,
    'menu_bg': 0x303030,
    'menu_fg': 0xD0D0D0,
    'menu_hi': 0x505050,
    'menu_sep': 0x181818,
    'input_bg': 0xFFFFFF,
    'input_border': 0x808080,
    'success': 0x008000,
    'error': 0xD00000,
    'element': 0x0060C0,
    'coeff': 0xC00000,
    'arrow': 0x404040,
    'gray': 0x808080,
    'light_gray': 0xD0D0D0,
    'sel_bg': 0x2060C0,
    'sel_text': 0xFFFFFF,
    'sel_date': 0xC0D8FF,
    'alt_row': 0xF4F4F4,
    'header_bg': 0xE0E0E8,
    'star': 0xD0A000,
    'filter_active': 0xD06000,
    'banner_text1': 0x303030,
    'banner_text2': 0x606060,
    'banner_bg': 0x1A4A8A,
    'popup_bg': 0xF8F8F8,
    'popup_border': 0x404040,
    'popup_sep': 0xDDDDDD,
    'popup_shadow': 0x999999,
    'cell_warm': 0xFFE8E0,
    'cell_cool': 0xE0E8FF,
    'cell_green': 0xE0F0E0,
    'cell_sym': 0xD8E8F8,
    'cell_num': 0xF0F0E8,
    'key_bg': 0xF0F0F0,
    'key_special': 0xD8E8F8,
}

DARK = {
    'bg': 0x1E1E1E,
    'text': 0xD4D4D4,
    'title_bg': 0x264F78,
    'title_fg': 0xFFFFFF,
    'accent': 0x4FC1FF,
    'menu_bg': 0x252525,
    'menu_fg': 0xC0C0C0,
    'menu_hi': 0x404040,
    'menu_sep': 0x101010,
    'input_bg': 0x252525,
    'input_border': 0x555555,
    'success': 0x4EC9B0,
    'error': 0xF44747,
    'element': 0x4FC1FF,
    'coeff': 0xCE9178,
    'arrow': 0x808080,
    'gray': 0x808080,
    'light_gray': 0x404040,
    'sel_bg': 0x264F78,
    'sel_text': 0xFFFFFF,
    'sel_date': 0x9CDCFE,
    'alt_row': 0x252525,
    'header_bg': 0x2A2A3A,
    'star': 0xFFD700,
    'filter_active': 0xCE9178,
    'banner_text1': 0xD4D4D4,
    'banner_text2': 0xAAAAAA,
    'banner_bg': 0x1A3A6A,
    'popup_bg': 0x2D2D2D,
    'popup_border': 0x555555,
    'popup_sep': 0x404040,
    'popup_shadow': 0x1A1A1A,
    'cell_warm': 0x3A2A28,
    'cell_cool': 0x1E2838,
    'cell_green': 0x1E2E1E,
    'cell_sym': 0x1E2838,
    'cell_num': 0x2A2818,
    'key_bg': 0x2D2D2D,
    'key_special': 0x1E2838,
}

# Current active theme colors (mutable dict — callers hold a reference to this object)
colors = dict(LIGHT)
_is_dark = False


def _detect_system_theme():
    """Detect calculator system theme via Theme(1). Returns True if dark."""
    try:
        import hpprime
        t = hpprime.eval('Theme(1)')
        return t == 2  # 1=light, 2=dark
    except:
        return False


def init():
    """Initialize theme from system setting. Call once at startup."""
    global _is_dark
    _is_dark = _detect_system_theme()
    if _is_dark:
        colors.update(DARK)
    else:
        colors.update(LIGHT)


def toggle():
    """Toggle between light and dark themes."""
    global _is_dark
    _is_dark = not _is_dark
    if _is_dark:
        colors.update(DARK)
    else:
        colors.update(LIGHT)


def is_dark():
    """Return True if dark theme is active."""
    return _is_dark
