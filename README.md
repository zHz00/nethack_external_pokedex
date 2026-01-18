# === NetHack Externak Pokedex ===

This is terminal-based utility to see properties of monsters in NetHack. It uses curses library for beautiful output.

Please note that this utility have nothing to do with Pokemons, it uses Pokedex in title only because everyone knows what Pokedex is.

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

For Linux there is no special requirements. For Windows, though, you must install windows-curses module. Please use this command:

pip install windows-curses

To start using, run main.py. Also, docker image is available, see deploy folder for details.

When script is started, just type monster name and see its properties!

Also, you can type part of name and still find your monster in search results.

## Controls

### Search mode (default)
**F1**			Show quick help  
**Tab**			Switch to LIST mode  
**[, ]**		Switch variant  
**Ctrl+O**		Select variant from list  
**Down**		Show more information  
**Up**			Show less information  
**Esc**			Clear search line  
**Left, Right**	Scroll through search results  
**Ctrl+A**		Show attacks analysis window (Press Esc to return to card)  
**F10**			Exit  
  
**1-6**			Change colors  
**1**			Foreground1 (card, list)  
**2**			Background1 (card, list)  
**3**			Foreground2 (card, list)  
**4**			Background2 (card, list)  
**5**			Foreground (upper zone, menus)  
**6**			Background (upper zone, menus)  

**F3**			Run tests and show results  
**Shift+F2**	Show every card in quick succession. WARNING, this is debug feature. This process cannot be interrupted. You just have to watch.

### List mode
**F1**			Show quick help  
**Tab**			Switch back to SERACH mode  
**UP, DOWN**	Scroll through list  
**PgUp, PgDn**	Scroll, but faster  
**Home, End**	Scroll with the speed of light  
**Enter**		View selected monster's card (Press Esc to return to list)  
**Ctrl+S**		Select sorting field  
**Ctrl+D**		Change sorting direction  
**Shift+S**		Select secondary sorting field (only available if first field is active)  
**Shift+D**		Change secondary sorting direction  
**Ctrl+F**		Show filters menu

**[, ]**		Switch variant  
**Ctrl+O**		Select variant from list  
**F10**			Exit  

## Formats

**mini:**	only essential information shown. Monster card is limited to 5 lines, plus two lines for search results (total: 7). This enables you to place pokedex windows along with main game window. Unfortunately, some words are shrunk, and some attacks don't fit on screen, after all. This is main problem for dNetHack, where many monsters have too many too strange attacks.  
**full:**	you see all attacks and flags, most words are not abbreviated. Omitted information: percentage for conveyed resistances and special information for dNetHack (AC breakdown, damage reduction and wards).  
**ext:**	you see all available information.

## Using filters

Now, only 4 types of filters are supported. Press enter while filter is selected, enter parameter and press enter again. Filter will be applied immediately. If you want to disable a filter, just press space.

**Letter:**		Show only monsters, that have desired letter. You cannot select two or more letters. If you enter some non-monster letter, then you'll get an emtpy list. If you want to switch this filter back to \<any\> state, you must enter asterisk (\*) as a parameter.  
**Name:**		Show monsters, specified by part of their name. This is similar to SEARCH mode, but you see results as a list. To switch this filter to <any> state, you must enter a space in the edit field.  
**Conveyed:**	This filter enables you to view monsters that can give you some intrinsic property. Beware, you'll get a monster even if it does not leave a corpse. You can still get a resist if you eat this monster alive, e.g. if you polymorph yourself to a purple worm.  
**Param:**		You can select any parameter from the table, and also you can select specific dNetHack parameters: insight and light_radius. Then you must enter minimum and maximum values in edit fields, then you get a list containing monsters with selected parameter is in range from first value (included) to second value (also included).

## Screen size

You can reduce output to 7 lines, but the program is designed to run in 80x25 mode. If you make your screen wider, you will still see card in 80 character-width format. Maybe one day i'll make adaptive design for any width, but not today.

## Licence and author information

MIT Licence. See LICENCE.txt file for details.  
(C) 2022-2026 zHz  
You can contact me via Telegram @zHz01  
Also, please visit project's github page:  
https://github.com/zHz00/nethack_external_pokedex

Please note, that monsters databases was parsed using separate project:  
https://github.com/zHz00/nethack_montable_parse