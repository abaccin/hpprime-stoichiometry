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

# Colors are managed by theme.py (supports light / dark mode).
# Import and use: from theme import colors; then colors['bg'], colors['text'], etc.

# Fonts
FONT_SM = const(1)    # 10px
FONT_MD = const(2)    # 12px
FONT_LG = const(3)    # 14px
FONT_XL = const(4)    # 16px
FONT_TITLE = const(5) # 18px

# App info
APP_NAME = 'Stoichiometry'
APP_VERSION = '1.0.0'
