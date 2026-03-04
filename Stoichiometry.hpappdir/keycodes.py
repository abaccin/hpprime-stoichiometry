"""Key code constants for HP Prime keyboard() bitmask bit positions.

These match the physical key layout. Soft menu buttons are
touch-only and handled via get_menu_tap(), not keyboard.

Keyboard map (bit positions):
  Apps=0  Symb=1  Plot=6  Num=11  Home=5  Help=3
  View=9  Menu=13  Esc=4  CAS=10
  Up=2  Left=7  Right=8  Down=12
  Vars=14 Toolbox=15 Template=16 abc=18 Backspace=19
  Enter=30  Plus=50  Minus=45
"""

from micropython import const

# Navigation
KEY_UP = const(2)
KEY_DOWN = const(12)
KEY_LEFT = const(7)
KEY_RIGHT = const(8)

# Actions
KEY_ENTER = const(30)
KEY_ESC = const(4)
KEY_BACKSPACE = const(19)

# Math
KEY_PLUS = const(50)
KEY_MINUS = const(45)

# Top row physical keys (not soft menu buttons)
KEY_APPS = const(0)
KEY_SYMB = const(1)
KEY_HELP = const(3)
KEY_HOME = const(5)
KEY_PLOT = const(6)
KEY_VIEW = const(9)
KEY_CAS = const(10)
KEY_NUM = const(11)
KEY_MENU = const(13)
