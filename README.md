# === NetHack External Pokedex ===

This is terminal-based utility to see properties of monsters in NetHack. It uses curses library for beautiful output.

Please note that this utility have nothing to do with Pokemons, it uses Pokedex in title only because everyone knows what Pokedex is.

## Variants included

* NetHack 3.4.3  
* NetHack 3.6.7  
* NetHack 5.0.0  
* xNetHack 9.1  
* UnNetHack 6.0.14  
* EvilHack 0.9.1  
* SLASH'EM 0.0.7  
* dNetHack 3.26.0  

## Quick Start

For Linux there are no special requirements. For Windows, though, you must install windows-curses module. Please use this command:

`pip install windows-curses`

To start using, run main.py. Also, docker image is available, see deploy folder for details.

When script is started, just type monster name and see its properties!

Also, you can type part of name and still find your monster in search results.

## Controls

### Search mode (default)

| Key             |Action                                                       |
|-----------------|-------------------------------------------------------------|
|**Main keys**    |                                                             |
|F1, ?            |Show quick help                                              |
|Tab              |Switch to LIST mode                                          |
|[, ]             |Switch variant                                               |
|Ctrl+O           |Select variant from list                                     |
|Down             |Show more information                                        |
|Up               |Show less information                                        |
|Esc              |Clear search line                                            |
|Ctrl+Z           |Show last viewed card again (works only after Esc)           |
|Left, Right      |Scroll through search results                                |
|Ctrl+A           |Show attacks analysis screen (Press Esc to return to card)   |
|F10, Ctrl+Q      |Exit                                                         |
|**Change colors**|                                                             |
|1                |Foreground1 (card, list)                                     |
|2                |Background1 (card, list)                                     |
|3                |Foreground2 (card, list)                                     |
|4                |Background2 (card, list)                                     |
|5                |Foreground (upper zone, menus)                               |
|6                |Background (upper zone, menus)                               |
|**Debug**        |                                                             |
|F3               |Run tests and show results                                   |
|Shift+F2         |Show every card in quick succession. WARNING, this is debug feature. This process cannot be interrupted. You just have to watch.  |
|Shift+F3         |Show attacks analysis windows for every monster. Warning is same as above.|

### List mode

|Key                |Action                                                                  |
|-------------------|------------------------------------------------------------------------|
|F1                 |Show quick help                                                         |
|Tab                |Switch back to SERACH mode                                              |
|Up, Down           |Scroll through list                                                     |
|PgUp, PgDn         |Scroll, but faster                                                      |
|Home, End          |Scroll with the speed of light                                          |
|Left, Right        |View dNetHack special columns: Insight required and light raduis        |
|Enter              |View selected monster's card (Backspase or Esc to return to list)       |
|Ctrl+S, S          |Select sorting field                                                    |
|Ctrl+D, D          |Change sorting direction                                                |
|Shift+S            |Select secondary sorting field (only available if first field is active)|
|Shift+D            |Change secondary sorting direction                                      |
|Shift+F            |Show filters menu                                                       |
|Ctrl+F             |Quick filter by name                                                    |
|[, ]               |Switch variant                                                          |
|Ctrl+O             |Select variant from list                                                |
|F10, Ctrl+Q        |Exit                                                                    |

Ctrl+S and Ctrl+D are troublesome on some terminals, so you can use lowercase s and d as aliases.

## Formats

**mini:**	only essential information shown. Monster card is limited to 5 lines, plus two lines for search results (total: 7). This enables you to place pokedex windows along with main game window. Unfortunately, some words are shrunk, and some attacks don't fit on screen, after all. This is main problem for dNetHack, where many monsters have too many too strange attacks.  
**full:**	you see all attacks and flags, most words are not abbreviated. Omitted information: percentage for conveyed resistances and special information for dNetHack (AC breakdown, damage reduction and wards).  
**ext:**	you see all available information.

## Using filters

There are now 8 types of filters. First group are parametric filters and requires entering values on keyboard. Press Enter while filter is selected, enter parameter value(s) and press Enter again. Filter will be applied immediately. If you want to disable a filter, just press space.

**Letter:**			Show only monsters, that have desired letter. You cannot select two or more letters. If you enter some non-monster letter, then you'll get an emtpy list. If you want to switch this filter back to \<any\> state, you must enter asterisk (\*) as a value.  
**Name:**			Show monsters, specified by part of their name. This is similar to SEARCH mode, but you see results as a list. To switch this filter to \<any\> state, you must enter a space in the edit field. You can quickly call this filter using Ctrl+F instead of Shift+F.  
**Parameter:**		You can select any parameter from the list, and also you can select specific dNetHack parameters: insight and light_radius. Then you must enter minimum and maximum values in edit fields, then you get a list containing monsters with selected parameter in range from first value (included) to second value (also included).

Second group of filters shows monsters which have specific property. There are several lists of properties:

**Conveyed:**			This filter enables you to view monsters that can give you some intrinsic property. Beware, you'll get a monster even if it does not leave a corpse. You can still get a resist if you eat this monster alive, e.g. if you polymorph yourself to a purple worm.  
**Quest monsters:**		You can view monsters that appears in Quest of each role. Quest nemesis is highlighted. Also, some other monsters can be highlighted, for alignment quests of dNetHack, for example.  
**Dangerous to eat:**	You can view monsters that counts as cannibalism for specific race, are acidic or poisonous to eat etc.  
**Dangerous attacks:**	You can view monsters that can drown, petrify player etc.  
**Other:**				Examine this category by yourself. Please note that not all filters works correctly with forks, because there is some difference in algorithms. For example, "wear all armor" is somewhat meaningless for dNetHack because of armor sizes.

## Screen size

You can reduce output to 7 lines in search mode, but the program is designed to run in 80x25 mode. If you make your screen wider, you will still see card in 80 character-width format. Maybe one day i'll make adaptive design for any width, but not today.

## License and author information

MIT License. See LICENSE.txt file for details.  
(C) 2022-2026 zHz  
You can contact me via Telegram @zHz01  
Also, please visit project's github page:  
https://github.com/zHz00/nethack_external_pokedex

Please note that monsters databases were parsed using separate project:  
https://github.com/zHz00/nethack_montable_parse