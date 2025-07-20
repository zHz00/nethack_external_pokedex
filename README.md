# === NetHack Externak Pokedex ===

## Variants included
NetHack 3.4.3
NetHack 3.6.7
NetHack 3.7.0-dev
xNetHack 9.0
UnNetHack 6.0.14
EvilHack 0.9.1
SLASH'EM 0.0.7
dNetHack 3.24.0

## Quick Start

For Linux there is no special requirements. For Windows, though, you must install windows-curses module.

To start using, run search.py.

Just type monster name and see its properties!

Also, you can type part of name and still find your monster in search results.

## Controls
**PgUp/PgDn**	Switch variant
**Ctrl+O**		Select variant from list
**Down**		Show more information
**Up**			Show less information
**Esc**			Clear search lines
**Left, Right**	Scroll through search results
**F10**			Exit

**1,2,3,4,**	Change colors
**F1**			Run tests and show results
**Shift+F2**	Show every card in quick succession. WARNING, this is debug feature. This process cannot be interrupted. You just have to watch.

## Formats
**mini:**	only essential information shown. Monster card is limited to 5 lines, plus two lines for search results. This enables you to place pokedex windows along with main game window. Unfortunately, some words are shrunk, and some attacks don't fit on screen, after all. This is main problem for dNetHack, where many monsters have too many too strange attacks.
**full:**	you see all attacks and flags, most words are not abbreviated. Omitted information: percentage for conveyed resistances and special information for dNetHack (AC breakdown, damage reduction and wards).
**ext:**	you see all available information.

## Licence and author information

MIT Licence. See LICENCE.txt file for details.
(C) 2022-2025 zHz
You can contact me via Telegram @zHz01
Also, please visit project's github page:
https://github.com/zHz00/nethack_external_pokedex

Please note, that monsters databases was parsed using separate project:
https://github.com/zHz00/nethack_montable_parse