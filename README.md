# External Item Descriptions for The Binding of Isaac (Flash)

**Press F2 to hide/show the descriptions!**

An EID-style overlay for the original Flash game
([The Binding of Isaac](https://store.steampowered.com/app/113200/The_Binding_of_Isaac/),
including Wrath of the Lamb/Eternal DLC).

This is an unofficial port based on EID by Wofsauge and contributors. It is not part of the EID mod for
Rebirth / Afterbirth / Repentance. 
For that, see the [original EID project](https://github.com/wofsauge/External-Item-Descriptions).

## Features
- Descriptions for all 196 collectibles, 34 trinkets, 27 cards and all pills of the Flash game
- Stat values checked against the game's own formulas

## Installation
No game files are distributed. The patcher builds the modded game from your own copy:

1. Download `EID_Flash_Patcher.exe` from the [latest release](https://github.com/tomandesMSH/External-Item-Descriptions/releases/latest)
   and put it in an empty folder.
2. Double-click it. A game window appears for a few seconds while it reads your game, then the patcher creates an
   `EID Flash` folder next to itself (and downloads Adobe's Flash Player 32 projector into it).
3. Start the game with `EID Flash\Play EID Flash.bat`.

Prefer not to run an exe? The release also has a zip with the plain Python script (`python eid_flash_patcher.py --get-projector`).

Details: [`flash/patcher/README.txt`](flash/patcher/README.txt). Development and technical notes:
[`flash/README.md`](flash/README.md).

## Credits
See [CREDITS.md](CREDITS.md).
