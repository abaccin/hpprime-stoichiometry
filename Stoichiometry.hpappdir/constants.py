"""Constants for Stoichiometry HP Prime app."""

from micropython import const

# Graphics buffers
GR_AFF = const(0)       # Visible screen
GR_BACK = const(1)      # Off-screen buffer
GR_TMP = const(5)

# Screen dimensions
SCREEN_W = const(320)
SCREEN_H = const(240)

# Menu bar
MENU_Y = const(220)
MENU_H = const(20)
CONTENT_H = const(220)

# Colors (0xRRGGBB)
COL_BG = 0xFFFFFF
COL_TEXT = 0x000000
COL_TITLE_BG = 0x2050A0
COL_TITLE_FG = 0xFFFFFF
COL_ACCENT = 0x2080D0
COL_MENU_BG = 0x303030
COL_MENU_FG = 0xFFFFFF
COL_MENU_SEP = 0x606060
COL_INPUT_BG = 0xF0F0F0
COL_INPUT_BORDER = 0x808080
COL_SUCCESS = 0x008000
COL_ERROR = 0xD00000
COL_ELEMENT = 0x0060C0
COL_COEFF = 0xC00000
COL_ARROW = 0x404040
COL_GRAY = 0x808080
COL_LIGHT_GRAY = 0xD0D0D0

# Fonts
FONT_SM = const(1)    # 10px
FONT_MD = const(2)    # 12px
FONT_LG = const(3)    # 14px
FONT_XL = const(4)    # 16px
FONT_TITLE = const(5) # 18px

# App info
APP_NAME = 'Stoichiometry'
APP_VERSION = '1.0.0'
