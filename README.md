# External Item Descriptions for The Binding of Isaac (Flash)

An EID-style overlay for the original Flash game
([The Binding of Isaac, Steam app 113200](https://store.steampowered.com/app/113200/The_Binding_of_Isaac/),
including Wrath of the Lamb / Eternal Edition). Walk up to an item pedestal, trinket, card or pill to see what it
does, in the look of [External Item Descriptions](https://github.com/wofsauge/External-Item-Descriptions).

This is an unofficial port based on EID by Wofsauge and contributors. It is not part of the EID mod for
Rebirth / Afterbirth / Repentance; for that, see the [original project](https://github.com/wofsauge/External-Item-Descriptions).

## Features
- Descriptions for all 196 collectibles, 34 trinkets, 27 cards and all pills of the Flash game
- EID's font, inline icons, bullet points, item type and charge icons
- Stat values checked against the game's own formulas
- Pills stay "Unidentified" until you have taken one of that color
- **Press F2 to hide/show the descriptions!**

## Installation
No game files are distributed. The patcher builds the modded game from your own copy:

1. Install [Python 3](https://www.python.org/downloads/) (no extra packages needed).
2. Download the release zip, unzip it and run `python eid_flash_patcher.py --get-projector`.
3. Start the game with `EID Flash\Play EID Flash.bat`.

Details: [`flash/patcher/README.txt`](flash/patcher/README.txt). Development and technical notes:
[`flash/README.md`](flash/README.md).

## Credits
See [CREDITS.md](CREDITS.md).
