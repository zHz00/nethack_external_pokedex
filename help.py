def search_mode(version):
    return f"Quick help: Search mode\n\
\n\
_Ctrl+O_        Select NetHack variant to search\n\
_[, ]_          Switch to next NetHack variant\n\
_Left, Right_   Scroll through search results\n\
_Esc_           Clear search line\n\
_Up_            Show less information\n\
_Down_          Show more information\n\
_Ctrl+A_        Show attacks analysis windows\n\
_Tab_           Switch to **List** mode\n\
_F10, Ctrl+Q_   Exit\n\
_1...6_         Change colors\n\
\n\
Version {version}. (C) **zHz** 2022-2026. MIT Licence.\n\
https://github.com/zHz00/nethack\_external\_pokedex"

def card_mode():
    return "Quick help: Card, opened from list\n\
\n\
_Esc, Backspace_  Return to list\n\
_[, ]_            Switch variant\n\
(Variant will be reverted when you press Esc)\n\
\n\
_Ctrl+O_          Nothing. Use square brackets!\n\
_Up_              Show less information\n\
_Down_            Show more information\n\
_Ctrl+A_          Show attacks analysis windows\n\
_F10, Ctrl+Q_     Exit"

def list_mode():
    return "Quick help: List mode\n\
\n\
_Tab_           Switch to **Search** mode\n\
_Ctrl+O_        Select NetHack variant to view\n\
_[, ]_          Switch to next NetHack variant\n\
_Up, Down_      Scroll through list\n\
_PgUp, PgDn_    Scorll, but faster\n\
_Home, End_     Scroll with speed of light\n\
_Left, Right_   View dNetHack additional parameters\n\
_Enter_         View selected monster's card\n\
_Ctrl+S, S_     Select primary sorting field\n\
_Ctrl+D, D_     Change primary sorting direction\n\
_Shift+S_       Select secondary sorting field\n\
_Shift+D_       Change secondary sorting direction\n\
(You must use primary field first)\n\
\n\
_Shift+F_       Show filters window\n\
_Ctrl+F_        Quick filter by name\n\
_Ctrl+Q, F10_   Exit\n"

def aa_mode():
    return "Quick help: Attacks analysis\n\
\n\
_Esc, Backspace_ Return to card\n\
_[, ]_           Switch variant\n\
(Variant will be reverted when you press Esc)\n\
\n\
_Ctrl+O_         Nothing. Use square brackets!\n\
_Up_             Nothing. Less information on main screen\n\
_Down_           Nothing. More information on main screen\n\
_Space_          Scroll screens if more than one available\n\
_F10 or Ctrl+Q_  Exit"