External Item Descriptions for The Binding of Isaac (Flash)
============================================================

Shows EID-style descriptions for item pedestals, trinkets, cards and pills in the original
Flash version of The Binding of Isaac (Steam, including Wrath of the Lamb).

This package contains NO game files. The patcher builds the modded game from your own copy.


Requirements
------------
- Windows
- The Binding of Isaac (Flash) installed, e.g. from Steam
- For the script version only: Python 3.8 or newer (https://www.python.org/downloads/),
  no extra packages needed


Install
-------
With the exe (EID_Flash_Patcher.exe):
1. Put EID_Flash_Patcher.exe in an empty folder and double-click it.
2. A game window appears for a few seconds while the patcher reads the game, then closes.
   The patcher creates an "EID Flash" folder next to itself.
3. Start the game with "EID Flash\Play EID Flash.bat".

With the Python script (this zip):
1. Unzip this folder anywhere.
2. Open a command prompt in this folder and run:

       python eid_flash_patcher.py --get-projector

3. Start the game with "EID Flash\Play EID Flash.bat".

If the game is not in your Steam library, add --game "<folder with Isaac.exe>"
(for the exe: run it from a command prompt with that option).

The exe and --get-projector download Adobe's official Flash Player 32 projector
(flashplayer_32_sa.exe) from fpdownload.macromedia.com and check its fingerprint. You can also put
your own copy into the "EID Flash" folder instead (exe: use --no-projector).


Playing
-------
- Walk up to an item, trinket, card or pill to see its description.
- F2 shows/hides the descriptions.
- Pills show "Unidentified Pill" until you have taken a pill of that color.
- The modded game keeps its own save file (separate from the Steam version), and Steam
  achievements are not unlocked while playing it.
- Your Steam installation is never modified. To uninstall, delete the "EID Flash" folder.


Credits
-------
External Item Descriptions by Wofsauge and contributors:
https://github.com/wofsauge/External-Item-Descriptions
Item information based on The Binding of Isaac Wiki (CC BY-SA 3.0) and checked against the game.
The Binding of Isaac (c) Edmund McMillen & Florian Himsl.
